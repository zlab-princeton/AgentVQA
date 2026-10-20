import base64
import os
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx

from .prompts import is_qwen25

ENDPOINTS = {
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "openai-chat": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "anthropic": ("https://api.anthropic.com/v1", "ANTHROPIC_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com", "GEMINI_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "dashscope": ("https://dashscope-intl.aliyuncs.com/compatible-mode/v1", "DASHSCOPE_API_KEY"),
    "moonshot": ("https://api.moonshot.ai/v1", "MOONSHOT_API_KEY"),
    "together": ("https://api.together.xyz/v1", "TOGETHER_API_KEY"),
    "zai": ("https://api.z.ai/api/paas/v4", "ZAI_API_KEY"),
    "compatible": ("", "MODEL_API_KEY"),
}


@dataclass
class RunConfig:
    model: str
    provider: str
    base_url: str | None = None
    api_key_env: str | None = None
    request_reasoning: bool = False
    extract_reasoning: bool = False
    reasoning_effort: str | None = None
    thinking: str | None = None
    thinking_budget: int | None = None
    max_tokens: int = 4096
    temperature: float | None = None
    coordinate_format: str = "auto"
    num_frames: int = 32
    video_mode: str = "auto"
    native_max_mb: float = 8.0
    max_side: int = 0
    qwen_max_pixels: int = 1003520
    jpeg_quality: int = 80
    image_limit: int | None = None
    native_supported: bool | None = None
    max_attempts: int = 3
    timeout: float = 900.0
    retry_delay: float = 5.0
    request_delay: float = 0.0
    retry_invalid: bool = False
    shrink_on_oversize: bool = False
    extra_body: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.provider not in ENDPOINTS:
            raise ValueError(f"Unknown provider: {self.provider}")
        default_url, default_key = ENDPOINTS[self.provider]
        self.base_url = (self.base_url or default_url).rstrip("/")
        self.api_key_env = self.api_key_env or default_key
        parsed = urlparse(self.base_url)
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
        ):
            raise ValueError("Provide a base URL without credentials or query parameters")
        if parsed.scheme == "http" and parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("Non-local API endpoints require HTTPS")
        for field_name in ("num_frames", "max_attempts", "max_tokens"):
            if getattr(self, field_name) < 1:
                raise ValueError(f"{field_name} must be positive")
        if (
            not 1 <= self.jpeg_quality <= 95
            or self.max_side < 0
            or (self.image_limit is not None and self.image_limit < 1)
        ):
            raise ValueError("Invalid image preprocessing settings")
        if not 3136 <= self.qwen_max_pixels <= 12845056:
            raise ValueError("qwen_max_pixels must be between 3136 and 12845056")
        if self.video_mode not in ("frames", "native", "auto"):
            raise ValueError("Invalid video mode")
        if self.thinking not in (None, "enabled", "disabled", "adaptive"):
            raise ValueError("Invalid thinking setting")
        if not isinstance(self.extra_body, dict):
            raise ValueError("--extra-body must be a JSON object")
        if self.provider == "gemini" and self.thinking_budget is not None and self.reasoning_effort:
            raise ValueError(
                "Gemini requires either a thinking budget or a thinking level, not both"
            )
        if (
            self.provider == "anthropic"
            and self.thinking == "enabled"
            and (self.thinking_budget is None or not 1024 <= self.thinking_budget < self.max_tokens)
        ):
            raise ValueError(
                "Manual Anthropic thinking requires 1024 <= thinking budget < max tokens"
            )
        if (
            self.timeout <= 0
            or self.native_max_mb <= 0
            or min(self.retry_delay, self.request_delay) < 0
        ):
            raise ValueError("Invalid timeout, media limit, or delay")
        forbidden = {
            "model",
            "messages",
            "input",
            "contents",
            "stream",
            "api_key",
            "authorization",
            "headers",
            "tools",
        }
        if forbidden & {key.lower() for key in self.extra_body}:
            raise ValueError(
                "extra_body cannot override model, inputs, credentials, tools, or streaming"
            )


class ProviderError(RuntimeError):
    def __init__(self, message, status=None, retry_after=None, oversize=False):
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after
        self.oversize = oversize

    @property
    def transient(self):
        return self.status is None or self.status in (408, 409, 429, 500, 502, 503, 504, 529)


@dataclass
class ProviderResponse:
    text: str
    reasoning: str | None = None
    usage: dict = field(default_factory=dict)
    model: str | None = None
    finish_reason: str | None = None
    response_id: str | None = None


def text_content(content):
    if isinstance(content, str):
        return content
    return "\n".join(part.get("text", "") for part in content or [] if isinstance(part, dict))


class Provider:
    def __init__(self, config, client=None):
        self.config = config
        self.key = os.environ.get(config.api_key_env, "")
        if not self.key:
            raise ValueError(f"Set {config.api_key_env} before making API requests")
        self.client = client or httpx.Client(timeout=config.timeout, follow_redirects=False)

    def close(self):
        self.client.close()

    def generate(self, prompt, images, video=None, video_uri=None):
        if self.config.provider == "gemini":
            return self._gemini(prompt, images, video)
        if self.config.provider == "moonshot" and video:
            return self._moonshot_video(prompt, images, video)
        route, payload, headers = self.build_request(prompt, images, video, video_uri)
        response = self._post(route, payload, headers)
        try:
            return self.parse_response(response.json())
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise ProviderError("Malformed provider response", status=502) from error

    def _post(self, route, payload, headers):
        try:
            response = self.client.post(self.config.base_url + route, headers=headers, json=payload)
        except httpx.TransportError as error:
            raise ProviderError(type(error).__name__) from error
        if response.status_code >= 400:
            delay = response.headers.get("retry-after", "")
            try:
                delay = max(0, min(float(delay), 300))
            except ValueError:
                delay = None
            body = response.text.lower()
            oversize = (
                response.status_code == 413
                or response.status_code == 400
                and any(s in body for s in ("too large", "too many images", "payload size", "1261"))
            )
            raise ProviderError(
                f"Provider HTTP {response.status_code}", response.status_code, delay, oversize
            )
        return response

    def build_request(self, prompt, images, video=None, video_uri=None):
        config = self.config
        headers = {"Content-Type": "application/json"}
        if config.provider == "anthropic":
            headers.update({"x-api-key": self.key, "anthropic-version": "2023-06-01"})
        else:
            headers["Authorization"] = f"Bearer {self.key}"
        encoded = [base64.b64encode(image).decode("ascii") for image in images]
        if config.provider == "openai":
            if video:
                raise ValueError("OpenAI Responses uses sampled video frames")
            content = [
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image}"}
                for image in encoded
            ]
            content.append({"type": "input_text", "text": prompt})
            payload = {
                "model": config.model,
                "input": [{"role": "user", "content": content}],
                "max_output_tokens": config.max_tokens,
                "store": False,
            }
            reasoning = {}
            if config.reasoning_effort is not None:
                reasoning["effort"] = config.reasoning_effort
            if config.extract_reasoning:
                reasoning["summary"] = "auto"
            if reasoning:
                payload["reasoning"] = reasoning
            route = "/responses"
        elif config.provider == "anthropic":
            if video:
                raise ValueError("Anthropic uses sampled video frames")
            content = [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": image},
                }
                for image in encoded
            ]
            content.append({"type": "text", "text": prompt})
            payload = {
                "model": config.model,
                "max_tokens": config.max_tokens,
                "messages": [{"role": "user", "content": content}],
            }
            if config.thinking:
                thinking = {"type": config.thinking}
                if config.thinking != "disabled":
                    thinking["display"] = "summarized" if config.extract_reasoning else "omitted"
                if config.thinking == "enabled":
                    if config.thinking_budget is None:
                        raise ValueError("Manual Anthropic thinking requires --thinking-budget")
                    thinking["budget_tokens"] = config.thinking_budget
                payload["thinking"] = thinking
            if config.reasoning_effort:
                payload["output_config"] = {"effort": config.reasoning_effort}
            route = "/messages"
        else:
            content = [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
                for image in encoded
            ]
            if config.provider == "dashscope" and is_qwen25(config.model):
                for part in content:
                    part.update(min_pixels=3136, max_pixels=config.qwen_max_pixels)
            if video:
                if isinstance(video, str) and video.startswith("ms://"):
                    url = video
                elif config.provider in ("dashscope", "zai") and video_uri:
                    from huggingface_hub import hf_hub_url

                    from .catalog import REPOSITORY

                    revision, filename = video_uri.split("@", 1)[1].split("/", 1)
                    url = hf_hub_url(REPOSITORY, filename, repo_type="dataset", revision=revision)
                else:
                    raw = base64.b64encode(video.read_bytes()).decode("ascii")
                    url = raw if config.provider == "zai" else f"data:video/mp4;base64,{raw}"
                content.append({"type": "video_url", "video_url": {"url": url}})
            content.append({"type": "text", "text": prompt})
            payload = {"model": config.model, "messages": [{"role": "user", "content": content}]}
            token_key = (
                "max_completion_tokens"
                if config.model.lower().startswith(("gpt-5", "gpt-6", "o1", "o3", "o4"))
                else "max_tokens"
            )
            payload[token_key] = config.max_tokens
            if config.reasoning_effort is not None:
                if config.provider == "openrouter":
                    payload["reasoning"] = {
                        "effort": config.reasoning_effort,
                        "exclude": not config.extract_reasoning,
                    }
                else:
                    payload["reasoning_effort"] = config.reasoning_effort
            if config.thinking and config.provider == "dashscope":
                payload["enable_thinking"] = config.thinking != "disabled"
                if config.thinking_budget is not None:
                    payload["thinking_budget"] = config.thinking_budget
            elif config.thinking:
                payload["thinking"] = {"type": config.thinking}
                if config.thinking_budget is not None:
                    payload["thinking"]["budget_tokens"] = config.thinking_budget
            route = "/chat/completions"
        if config.temperature is not None:
            payload["temperature"] = config.temperature
        payload.update(config.extra_body)
        return route, payload, headers

    def parse_response(self, response):
        provider = self.config.provider
        if provider == "openai":
            outputs = response.get("output", [])
            text = "\n".join(
                part.get("text", "")
                for item in outputs
                if item.get("type") == "message"
                for part in item.get("content", [])
                if part.get("type") == "output_text"
            )
            reasoning = "\n".join(
                part.get("text", "")
                for item in outputs
                if item.get("type") == "reasoning"
                for part in item.get("summary", [])
            )
            finish = response.get("status")
        elif provider == "anthropic":
            blocks = response["content"]
            text = "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text")
            reasoning = "\n".join(
                b.get("thinking", "") for b in blocks if b.get("type") == "thinking"
            )
            finish = response.get("stop_reason")
        else:
            choice = response["choices"][0]
            message = choice["message"]
            text = text_content(message.get("content"))
            reasoning = message.get("reasoning_content") or message.get("reasoning") or ""
            if not reasoning:
                reasoning = "\n".join(
                    d.get("text", d.get("summary", ""))
                    for d in message.get("reasoning_details", [])
                    if d.get("type") in ("reasoning.text", "reasoning.summary")
                )
            finish = choice.get("finish_reason")
        return ProviderResponse(
            text,
            reasoning if self.config.extract_reasoning else None,
            response.get("usage") or {},
            response.get("model"),
            finish,
            response.get("id"),
        )

    def _moonshot_video(self, prompt, images, video):
        headers = {"Authorization": f"Bearer {self.key}"}
        uploaded_id = None
        try:
            with video.open("rb") as handle:
                response = self.client.post(
                    self.config.base_url + "/files",
                    headers=headers,
                    data={"purpose": "video"},
                    files={"file": (video.name, handle, "video/mp4")},
                )
            if response.status_code >= 400:
                raise ProviderError(
                    f"Moonshot file upload HTTP {response.status_code}",
                    response.status_code,
                    oversize=response.status_code == 413,
                )
            uploaded_id = response.json()["id"]
            route, payload, headers = self.build_request(
                prompt, images, video=f"ms://{uploaded_id}"
            )
            response = self._post(route, payload, headers)
            return self.parse_response(response.json())
        except httpx.TransportError as error:
            raise ProviderError(type(error).__name__) from error
        finally:
            if uploaded_id:
                try:
                    response = self.client.delete(
                        self.config.base_url + "/files/" + uploaded_id,
                        headers={"Authorization": f"Bearer {self.key}"},
                    )
                    response.raise_for_status()
                except httpx.HTTPError:
                    import warnings

                    warnings.warn(
                        "Moonshot temporary file deletion failed; remove it through the provider Files API",
                        RuntimeWarning,
                    )

    def _gemini(self, prompt, images, video):
        from google import genai
        from google.genai import types

        config = self.config
        client = genai.Client(
            api_key=self.key,
            http_options=types.HttpOptions(
                base_url=config.base_url,
                timeout=int(config.timeout * 1000),
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
        uploaded = None
        try:
            parts = [types.Part.from_bytes(data=image, mime_type="image/jpeg") for image in images]
            if video:
                if video.stat().st_size <= config.native_max_mb * 1_000_000:
                    parts.append(
                        types.Part.from_bytes(data=video.read_bytes(), mime_type="video/mp4")
                    )
                else:
                    uploaded = client.files.upload(
                        file=str(video), config=types.UploadFileConfig(mime_type="video/mp4")
                    )
                    deadline = time.monotonic() + config.timeout
                    while str(uploaded.state.name) == "PROCESSING":
                        if time.monotonic() >= deadline:
                            raise ProviderError("Gemini video processing timed out")
                        time.sleep(2)
                        uploaded = client.files.get(name=uploaded.name)
                    if str(uploaded.state.name) != "ACTIVE":
                        raise ProviderError("Gemini video processing failed", status=422)
                    parts.append(types.Part.from_uri(file_uri=uploaded.uri, mime_type="video/mp4"))
            parts.append(types.Part.from_text(text=prompt))
            generation = {"max_output_tokens": config.max_tokens}
            if config.temperature is not None:
                generation["temperature"] = config.temperature
            thinking = {"include_thoughts": config.extract_reasoning}
            if config.reasoning_effort:
                thinking["thinking_level"] = config.reasoning_effort
            if config.thinking_budget is not None:
                thinking["thinking_budget"] = config.thinking_budget
            if config.thinking == "disabled":
                thinking["thinking_budget"] = 0
            generation["thinking_config"] = types.ThinkingConfig(**thinking)
            generation.update(config.extra_body)
            result = client.models.generate_content(
                model=config.model,
                contents=[types.Content(role="user", parts=parts)],
                config=types.GenerateContentConfig(**generation),
            )
            candidate = (result.candidates or [None])[0]
            parts = candidate.content.parts if candidate and candidate.content else []
            text = "\n".join(p.text for p in parts if p.text and not p.thought)
            reasoning = "\n".join(p.text for p in parts if p.text and p.thought)
            usage = result.usage_metadata.model_dump(mode="json") if result.usage_metadata else {}
            return ProviderResponse(
                text,
                reasoning if config.extract_reasoning else None,
                usage,
                result.model_version,
                str(candidate.finish_reason) if candidate else None,
                result.response_id,
            )
        except ProviderError:
            raise
        except Exception as error:
            status = getattr(error, "code", None)
            status = status if isinstance(status, int) else None
            raise ProviderError(f"Gemini {type(error).__name__}", status=status) from error
        finally:
            if uploaded:
                try:
                    client.files.delete(name=uploaded.name)
                except Exception:
                    import warnings

                    warnings.warn(
                        "Gemini temporary file deletion failed; remove it through the provider Files API",
                        RuntimeWarning,
                    )
            client.close()
