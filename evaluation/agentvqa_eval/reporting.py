import csv
import json
from collections import Counter
from math import isclose

from .catalog import DOMAINS, SUBSETS, task_name
from .parsing import choices, label, target
from .storage import atomic_json


def selected_indices(size, limit, offset):
    stop = size if limit is None else min(size, offset + limit)
    return range(min(offset, size), stop)


def summarize(rows):
    total = len(rows)
    valid_rows = [row for row in rows if row["valid_answer"]]
    correct = sum(row["correct"] for row in valid_rows)
    answered = len(valid_rows)
    status = dict(Counter(row["status"] for row in rows))
    return {
        "total": total,
        "correct": correct,
        "answered": answered,
        "excluded": total - answered,
        "accuracy": correct / answered if answered else None,
        "accuracy_percent": 100 * correct / answered if answered else None,
        "coverage": answered / total if total else None,
        "status_counts": status,
    }


def report(store, tasks, limit=None, offset=0, lmms_results=None, complete=False):
    rows = []
    for task in tasks.values():
        data = task.dataset_no_image["train"]
        for index in selected_indices(len(data), limit, offset):
            record = store.read(task.subset, index) or {
                "subset": task.subset,
                "row_index": index,
                "prediction": None,
                "status": "unattempted",
                "attempts": [],
            }
            expected = target(data[index])
            prediction = record.get("prediction")
            valid = isinstance(prediction, str) and prediction in {
                label(i) for i in range(len(choices(data[index])))
            }
            rows.append(
                {
                    **record,
                    "domain": SUBSETS[task.subset],
                    "target": expected,
                    "valid_answer": valid,
                    "correct": valid and prediction == expected,
                }
            )
    subsets = {
        s: summarize([r for r in rows if r["subset"] == s])
        for s in SUBSETS
        if any(r["subset"] == s for r in rows)
    }
    domains = {
        d: summarize([r for r in rows if r["domain"] == d])
        for d in DOMAINS
        if any(r["domain"] == d for r in rows)
    }
    summary = {
        "run_id": store.run_id,
        "complete": complete,
        "dry_run": store.manifest["dry_run"],
        "accuracy_denominator": "valid_answers",
        "overall": summarize(rows),
        "domains": domains,
        "subsets": subsets,
        "api_attempts": sum(
            len(r.get("attempts", [])) + len(r.get("previous_attempts", [])) for r in rows
        ),
    }
    if lmms_results is not None:
        for subset, metrics in subsets.items():
            upstream = lmms_results["results"][task_name(subset)]
            for metric in ("accuracy", "coverage"):
                actual, expected = upstream[metric + ",none"], metrics[metric]
                matches = (
                    actual is expected
                    if actual is None or expected is None
                    else isclose(actual, expected, rel_tol=0, abs_tol=1e-12)
                )
                if not matches:
                    raise ValueError(f"Independent score verification failed: {subset} {metric}")
        summary["lmms_scores_verified"] = True
        atomic_json(store.root / "lmms_results.json", lmms_results)
    atomic_json(store.root / "summary.json", summary)
    with (store.root / "predictions.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (store.root / "accuracy.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "level",
                "name",
                "total",
                "correct",
                "answered",
                "excluded",
                "accuracy_percent",
                "coverage",
            ),
        )
        writer.writeheader()
        groups = [
            ("overall", {"AgentVQA": summary["overall"]}),
            ("domain", domains),
            ("subset", subsets),
        ]
        for level, values in groups:
            for name, metrics in values.items():
                writer.writerow(
                    {"level": level, "name": name, **{k: metrics[k] for k in writer.fieldnames[2:]}}
                )
    return summary
