import argparse
import json
import os
import sys
from dataclasses import asdict, fields
from pathlib import Path

from filelock import FileLock
from huggingface_hub import HfApi

from .capabilities import capabilities
from .catalog import DOMAINS, REPOSITORY, REVISION, SUBSETS, select_subsets
from .prompts import FORMATS, coordinate_format
from .providers import ENDPOINTS, RunConfig
from .storage import Store, atomic_json, provenance


def parser():
    root = argparse.ArgumentParser(
        prog="python -m agentvqa_eval",
        description="Evaluate AgentVQA through model APIs with lmms-eval",
    )
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog", help="List the 23 subsets and five domains")
    for name in ("validate", "evaluate"):
        command = commands.add_parser(name)
        command.add_argument("--subset", action="append", choices=SUBSETS)
        command.add_argument("--domain", action="append", choices=DOMAINS)
        command.add_argument("--revision", default=REVISION)
        command.add_argument("--output", type=Path, required=True)
        if name == "validate":
            command.add_argument(
                "--media-limit",
                type=int,
                default=0,
                help="Decode this many media rows per subset; zero validates all metadata only",
            )
            continue
        command.add_argument(
            "--model", required=True, help="Exact provider model ID; no aliases are substituted"
        )
        command.add_argument("--provider", choices=ENDPOINTS, required=True)
        command.add_argument("--base-url")
        command.add_argument("--api-key-env")
        command.add_argument("--request-reasoning", action="store_true")
        command.add_argument("--extract-reasoning", action="store_true")
        command.add_argument("--reasoning-effort")
        command.add_argument("--thinking", choices=("enabled", "disabled", "adaptive"))
        command.add_argument("--thinking-budget", type=int)
        command.add_argument("--max-tokens", type=int, default=4096)
        command.add_argument("--temperature", type=float)
        command.add_argument("--coordinate-format", choices=FORMATS, default="auto")
        command.add_argument("--num-frames", type=int, default=32)
        command.add_argument("--video-mode", choices=("auto", "native", "frames"), default="auto")
        command.add_argument(
            "--native-max-mb",
            type=float,
            default=8.0,
            help="Inline-video cap; Files API or public Hub URLs are used when supported",
        )
        command.add_argument(
            "--native-supported",
            action=argparse.BooleanOptionalAction,
            default=None,
            help="Explicit capability override for a custom API endpoint",
        )
        command.add_argument("--image-limit", type=int)
        command.add_argument(
            "--max-side",
            type=int,
            default=0,
            help="Maximum transmitted image side; zero retains original resolution",
        )
        command.add_argument("--jpeg-quality", type=int, default=80)
        command.add_argument("--qwen-max-pixels", type=int, default=1003520)
        command.add_argument("--max-attempts", type=int, default=3)
        command.add_argument("--timeout", type=float, default=900)
        command.add_argument("--retry-delay", type=float, default=5)
        command.add_argument("--request-delay", type=float, default=0)
        command.add_argument("--retry-invalid", action="store_true")
        command.add_argument("--shrink-on-oversize", action="store_true")
        command.add_argument(
            "--extra-body",
            type=json.loads,
            default={},
            help="Provider-specific generation parameters as a JSON object",
        )
        command.add_argument("--limit", type=int, help="Maximum samples per selected subset")
        command.add_argument("--offset", type=int, default=0)
        command.add_argument(
            "--max-api-calls",
            type=int,
            help="Maximum inference attempts in this invocation, including retries",
        )
        command.add_argument("--resume", action="store_true")
        command.add_argument(
            "--retry-failed",
            action="store_true",
            help="On resume, retry failed or invalid rows, never valid answers",
        )
        command.add_argument(
            "--dry-run",
            action="store_true",
            help="Prepare actual Hub media and prompts without model API calls",
        )
    return root


def validate(args, subsets, revision):
    from .data import load_subset, validate_subset
    from .media import prepare_media

    if args.media_limit < 0:
        raise ValueError("--media-limit cannot be negative")
    if args.output.exists():
        raise ValueError("Validation output already exists; choose a new filename")
    result = {"repository": REPOSITORY, "revision": revision, "split": "train", "subsets": {}}
    config = RunConfig(
        model="validation",
        provider="openai",
        video_mode="frames",
        image_limit=100,
        native_supported=False,
    )
    for subset in subsets:
        data = load_subset(subset, revision)
        entry = validate_subset(subset, data, revision, strict=False)
        entry["media_checks"] = []
        for index in range(min(args.media_limit, len(data))):
            media = prepare_media(data[index], config)
            encoded, sizes = media.encoded(config.max_side, config.jpeg_quality)
            entry["media_checks"].append(
                {
                    "row_index": index,
                    "mode": media.mode,
                    "images": len(encoded),
                    "sizes": sizes,
                    "audit": media.audit,
                }
            )
        result["subsets"][subset] = entry
        print(f"{subset}: {entry['rows']} rows; options {entry['option_counts']}", flush=True)
    result["total"] = sum(v["rows"] for v in result["subsets"].values())
    atomic_json(args.output, result)
    print(f"Validated {result['total']} rows; report: {args.output}")
    errors = {s: r["errors"] for s, r in result["subsets"].items() if r["errors"]}
    if errors:
        raise ValueError(f"Dataset validation failed: {errors}")


def evaluate(args, subsets, revision):
    from lmms_eval.evaluator import evaluate as lmms_evaluate

    from .data import AgentVQATask
    from .model import AgentVQAModel
    from .reporting import report, selected_indices

    if int(os.environ.get("WORLD_SIZE", "1")) != 1:
        raise ValueError("Use one process; distributed launches would duplicate paid requests")
    if args.limit is not None and args.limit < 1 or args.offset < 0:
        raise ValueError("--limit must be positive and --offset nonnegative")
    if args.max_api_calls is not None and args.max_api_calls < 1:
        raise ValueError("--max-api-calls must be positive")
    if args.retry_failed and not args.resume:
        raise ValueError("--retry-failed requires --resume")
    config = RunConfig(**{field.name: getattr(args, field.name) for field in fields(RunConfig)})
    capability = capabilities(config)
    config.image_limit = capability["image_limit"]
    config.native_supported = capability["native_video"]
    config.coordinate_format = coordinate_format(
        config.model, config.coordinate_format, config.provider
    )
    if not args.dry_run and not os.environ.get(config.api_key_env):
        raise ValueError(f"Set {config.api_key_env}; use --dry-run for a no-cost check")
    args.output.mkdir(parents=True, exist_ok=True)
    with FileLock(str(args.output / ".lock"), timeout=0):
        tasks = {}
        for subset in subsets:
            task = AgentVQATask(subset, revision)
            if not selected_indices(len(task.dataset["train"]), args.limit, args.offset):
                raise ValueError(f"No rows selected for {subset}")
            tasks[task.config.task] = task
        validations = {t.subset: t.validation for t in tasks.values()}
        manifest = provenance(
            asdict(config),
            revision,
            subsets,
            args.limit,
            args.offset,
            args.dry_run,
            capability,
            validations,
        )
        store = Store(args.output, manifest, resume=args.resume)
        model = AgentVQAModel(
            config=config,
            store=store,
            dry_run=args.dry_run,
            retry_failed=args.retry_failed,
            max_api_calls=args.max_api_calls,
        )
        model.task_dict = {name: task.dataset for name, task in tasks.items()}
        complete, result = False, None
        try:
            result = lmms_evaluate(
                model,
                tasks,
                limit=args.limit,
                offset=args.offset,
                bootstrap_iters=0,
                log_samples=False,
                process_docs_parallel=1,
            )
            complete = not any(
                record["status"] == "budget_exhausted" for record in model.records.values()
            )
        finally:
            model.close()
            summary = report(store, tasks, args.limit, args.offset, result, complete)
            print(
                json.dumps(
                    {
                        "output": str(args.output),
                        "complete": complete,
                        "dry_run": args.dry_run,
                        "overall": summary["overall"],
                    },
                    indent=2,
                )
            )


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == "catalog":
        print(json.dumps(DOMAINS, indent=2))
        return
    try:
        subsets = select_subsets(args.subset, args.domain)
        revision = HfApi().dataset_info(REPOSITORY, revision=args.revision).sha
        if args.command == "validate":
            validate(args, subsets, revision)
        else:
            evaluate(args, subsets, revision)
    except KeyboardInterrupt:
        print(
            "Interrupted. Completed rows are checkpointed; resume with the same settings.",
            file=sys.stderr,
        )
        raise SystemExit(130)
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1)
