import json

import datasets
from lmms_eval.api.registry import register_aggregation
from lmms_eval.api.task import ConfigurableTask

from .catalog import COUNTS, REPOSITORY, REVISION, task_name
from .parsing import choices, label, target


def doc_to_text(doc):
    return doc["Question"]


def doc_to_visual(doc):
    return [doc[k] for k in ("Image", "Images", "Video") if doc.get(k) is not None]


def process_results(doc, results):
    result = json.loads(results[0])
    answer = result.get("prediction")
    valid = isinstance(answer, str) and answer in {label(i) for i in range(len(choices(doc)))}
    expected = target(doc)
    return {"accuracy": float(answer == expected) if valid else None, "coverage": float(valid)}


@register_aggregation("agentvqa_answered_accuracy")
def answered_accuracy(scores):
    answered = [score for score in scores if score is not None]
    return sum(answered) / len(answered) if answered else None


def load_subset(subset, revision=REVISION):
    data = datasets.load_dataset(REPOSITORY, subset, revision=revision, split="train")
    for column in ("Image", "Images", "Video"):
        if column not in data.column_names:
            continue
        if column == "Image":
            data = data.cast_column(column, datasets.Image(decode=False))
        elif column == "Images":
            data = data.cast_column(column, datasets.List(datasets.Image(decode=False)))
        elif column == "Video":
            data = data.cast_column(column, datasets.Video(decode=False))
    return data


def validate_subset(subset, data, revision=REVISION, strict=True):
    if revision == REVISION and len(data) != COUNTS[subset]:
        raise ValueError(f"{subset}: expected {COUNTS[subset]} rows, got {len(data)}")
    metadata = data.remove_columns(
        [k for k in ("Image", "Images", "Video") if k in data.column_names]
    )
    distribution = {}
    errors = []
    for index, doc in enumerate(metadata):
        try:
            count = len(choices(doc))
            distribution[str(count)] = distribution.get(str(count), 0) + 1
            target(doc)
            if not isinstance(doc.get("Question"), str) or not doc["Question"].strip():
                raise ValueError("Missing question")
        except (ValueError, KeyError, TypeError) as error:
            errors.append({"row_index": index, "error": str(error)})
    if errors and strict:
        raise ValueError(f"{subset}: invalid dataset records: {errors}")
    return {
        "rows": len(data),
        "option_counts": distribution,
        "fingerprint": data._fingerprint,
        "errors": errors,
    }


class AgentVQATask(ConfigurableTask):
    def __init__(self, subset, revision=REVISION):
        self.subset = subset
        self.revision = revision
        super().__init__(
            config={
                "task": task_name(subset),
                "dataset_path": REPOSITORY,
                "dataset_name": subset,
                "dataset_kwargs": {"revision": revision},
                "test_split": "train",
                "output_type": "generate_until",
                "num_fewshot": 0,
                "doc_to_text": doc_to_text,
                "doc_to_visual": doc_to_visual,
                "doc_to_target": target,
                "process_results": process_results,
                "generation_kwargs": {"until": []},
                "metric_list": [
                    {
                        "metric": "accuracy",
                        "aggregation": "agentvqa_answered_accuracy",
                        "higher_is_better": True,
                    },
                    {"metric": "coverage", "aggregation": "mean", "higher_is_better": True},
                ],
                "metadata": {"version": 2},
            }
        )
        self.validation = validate_subset(subset, self.dataset["train"], revision)
        self.set_fewshot_seed(1234)

    def download(self, dataset_kwargs=None):
        data = load_subset(self.subset, self.revision)
        self.dataset = datasets.DatasetDict(train=data)
        media = [k for k in ("Image", "Images", "Video") if k in data.column_names]
        self.dataset_no_image = datasets.DatasetDict(train=data.remove_columns(media))
