import hashlib
import json
import time

from lmms_eval.api.model import lmms

from .capabilities import capabilities
from .catalog import PUBLIC_FIELDS, SUBSETS, task_name
from .media import prepare_media
from .parsing import parse_answer, split_thinking
from .prompts import build_prompt, coordinate_format, is_qwen25
from .providers import Provider, ProviderError, RunConfig


class CallBudgetReached(RuntimeError):
    pass


class AgentVQAModel(lmms):
    def __init__(
        self,
        config=None,
        store=None,
        provider_client=None,
        dry_run=False,
        retry_failed=False,
        max_api_calls=None,
        **kwargs,
    ):
        super().__init__()
        kwargs.pop("batch_size", None)
        kwargs.pop("device", None)
        self.config = config or RunConfig(**kwargs)
        if self.config.image_limit is None or self.config.native_supported is None:
            found = capabilities(self.config)
            self.config.image_limit = found["image_limit"]
            self.config.native_supported = found["native_video"]
        self.store = store
        self.dry_run = dry_run
        self.retry_failed = retry_failed
        self.max_api_calls = max_api_calls
        self.calls = 0
        self.provider = (
            provider_client
            if provider_client is not None
            else (None if dry_run else Provider(self.config))
        )
        self.records = {}
        self.mode = coordinate_format(
            self.config.model, self.config.coordinate_format, self.config.provider
        )
        self.subsets = {task_name(s): s for s in SUBSETS}

    def loglikelihood(self, requests):
        raise NotImplementedError("AgentVQA uses generative multiple-choice evaluation")

    def generate_until_multi_round(self, requests):
        raise NotImplementedError("AgentVQA is a single-turn benchmark")

    def clean(self):
        return None

    def close(self):
        if self.provider:
            self.provider.close()

    def generate_until(self, requests):
        output = []
        for request in requests:
            _, _, _, index, task, split = request.args
            subset = self.subsets[task]
            cached = self.store.read(subset, index) if self.store else None
            if cached and (not self.retry_failed or cached["status"] == "ok"):
                record = cached
            else:
                if (
                    not self.dry_run
                    and self.max_api_calls is not None
                    and self.calls >= self.max_api_calls
                ):
                    raise CallBudgetReached("API call limit reached; resume to continue")
                full_doc = self.task_dict[task][split][index]
                doc = {key: full_doc[key] for key in PUBLIC_FIELDS if key in full_doc}
                del full_doc
                record = self.predict(doc, subset, index)
                if cached:
                    record["previous_attempts"] = cached.get("previous_attempts", []) + cached.get(
                        "attempts", []
                    )
                if self.store:
                    self.store.write(record)
                if record.get("fatal"):
                    raise RuntimeError(
                        record["error"] + "; run stopped to avoid repeated invalid requests"
                    )
            self.records[(subset, index)] = record
            output.append(json.dumps({"prediction": record["prediction"]}))
        return output

    def predict(self, doc, subset, index):
        config = self.config
        started = time.monotonic()
        record = {
            "subset": subset,
            "row_index": index,
            "status": "pending",
            "prediction": None,
            "coordinate_format": self.mode,
            "attempts": [],
        }
        try:
            media = prepare_media(doc, config)
            max_side, quality = config.max_side, config.jpeg_quality
            for attempt in range(1, config.max_attempts + 1):
                grid_factor = 28 if is_qwen25(config.model) else 1
                encoded, sizes = media.encoded(
                    max_side, quality, grid_factor, config.qwen_max_pixels
                )
                original_sizes = media.audit.get(
                    "original_sizes", [image.size for image in media.images]
                )
                prompt, options, warnings = build_prompt(
                    doc,
                    subset,
                    self.mode,
                    original_sizes,
                    sizes,
                    config.request_reasoning,
                    media.note(),
                )
                record.update(
                    {
                        "prompt": prompt,
                        "options": options,
                        "warnings": warnings,
                        "media_mode": media.mode,
                        "media": media.audit,
                        "sent_sizes": sizes,
                        "image_sha256": [hashlib.sha256(image).hexdigest() for image in encoded],
                        "jpeg_quality": quality,
                        "image_grid_factor": grid_factor,
                    }
                )
                if self.dry_run:
                    record["status"] = "dry_run"
                    break
                if self.max_api_calls is not None and self.calls >= self.max_api_calls:
                    record.update(status="budget_exhausted", error="API call limit reached")
                    break
                if config.request_delay:
                    time.sleep(config.request_delay)
                self.calls += 1
                detail = {
                    "attempt": attempt,
                    "media_mode": media.mode,
                    "image_count": len(encoded),
                    "jpeg_quality": quality,
                    "sent_sizes": sizes,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "image_sha256": record["image_sha256"],
                }
                record["attempts"].append(detail)
                try:
                    result = self.provider.generate(
                        prompt,
                        encoded,
                        media.video if media.mode == "native" else None,
                        media.audit.get("source", {}).get("uri"),
                    )
                    visible, tagged = split_thinking(result.text)
                    parsed = parse_answer(visible, options)
                    detail.update(
                        usage=result.usage,
                        finish_reason=result.finish_reason,
                        response_id=result.response_id,
                        returned_model=result.model,
                    )
                    record.update(
                        prediction=parsed.answer,
                        response=visible,
                        rationale=parsed.rationale if config.request_reasoning else None,
                        provider_reasoning=(result.reasoning or tagged or None)
                        if config.extract_reasoning
                        else None,
                        status="ok" if parsed.answer else "invalid_answer",
                    )
                    record.pop("error", None)
                    if parsed.answer or not config.retry_invalid:
                        break
                except ProviderError as error:
                    detail.update(error=str(error), status_code=error.status)
                    record.update(status="api_error", error=str(error))
                    if error.status in (401, 402, 403, 404):
                        record["fatal"] = True
                        break
                    if media.mode == "native" and (
                        error.oversize or error.transient or error.status in (400, 415, 422)
                    ):
                        media.use_frames(config.num_frames, config.image_limit)
                        detail["fallback"] = "uniform_frames"
                    elif error.oversize and config.shrink_on_oversize:
                        current = max_side or max(max(image.size) for image in media.images)
                        max_side = max(256, current // 2)
                        quality = max(35, quality - 15)
                        detail["fallback"] = "image_resize"
                    elif not error.transient:
                        break
                    if attempt < config.max_attempts:
                        time.sleep(
                            error.retry_after
                            if error.retry_after is not None
                            else min(config.retry_delay * 2 ** (attempt - 1), 60)
                        )
                    continue
                if attempt < config.max_attempts:
                    time.sleep(min(config.retry_delay * 2 ** (attempt - 1), 60))
        except (ValueError, OSError, RuntimeError) as error:
            record.update(status="preprocessing_error", error=str(error))
        record["elapsed_seconds"] = round(time.monotonic() - started, 4)
        return record
