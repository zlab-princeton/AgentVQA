import csv
import io
import json
from types import SimpleNamespace

import datasets
import pytest
from PIL import Image

from agentvqa_eval.catalog import task_name
from agentvqa_eval.data import AgentVQATask, answered_accuracy, process_results
from agentvqa_eval.media import Media
from agentvqa_eval.model import AgentVQAModel, CallBudgetReached
from agentvqa_eval.parsing import label
from agentvqa_eval.providers import ProviderError, ProviderResponse, RunConfig
from agentvqa_eval.reporting import report, summarize
from agentvqa_eval.storage import Store


def image_bytes():
    out = io.BytesIO()
    Image.new("RGB", (64, 32), "red").save(out, format="PNG")
    return out.getvalue()


def data_rows(count=2):
    return datasets.Dataset.from_dict(
        {
            "Question": ["Which item?"] * count,
            "Options": [[f"choice {i}" for i in range(8)]] * count,
            "Answer": ["G", "A"][:count],
            "Image": [{"bytes": image_bytes(), "path": None}] * count,
        },
        features=datasets.Features(
            {
                "Question": datasets.Value("string"),
                "Options": datasets.List(datasets.Value("string")),
                "Answer": datasets.Value("string"),
                "Image": datasets.Image(decode=False),
            }
        ),
    )


class FakeProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def generate(self, prompt, images, video=None, video_uri=None):
        self.calls.append((prompt, images, video, video_uri))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        pass


def config(**kwargs):
    return RunConfig(
        model="gpt-5.6-sol",
        provider="openai",
        image_limit=500,
        native_supported=False,
        retry_delay=0,
        **kwargs,
    )


@pytest.mark.parametrize(
    "responses,correct,answered,accuracy",
    [
        ([ProviderResponse("G"), ProviderResponse("invalid response")], 1, 1, 1.0),
        ([ProviderResponse("B"), ProviderResponse("invalid response")], 0, 1, 0.0),
        ([ProviderResponse("G"), ProviderResponse("A")], 2, 2, 1.0),
        ([ProviderResponse("G"), ProviderResponse("B")], 1, 2, 0.5),
        (
            [ProviderError("request rejected", 400), ProviderResponse("invalid response")],
            0,
            0,
            None,
        ),
        ([ProviderError("request rejected", 400), ProviderResponse("A")], 1, 1, 1.0),
    ],
)
def test_lmms_end_to_end_and_independent_scoring(
    monkeypatch, tmp_path, responses, correct, answered, accuracy
):
    from lmms_eval.evaluator import evaluate

    monkeypatch.setattr("agentvqa_eval.data.load_subset", lambda *args: data_rows())
    task = AgentVQATask("GameQA", revision="test-fixture")
    store = Store(tmp_path, {"dry_run": False})
    provider = FakeProvider(responses)
    model = AgentVQAModel(config=config(), store=store, provider_client=provider)
    tasks = {task_name("GameQA"): task}
    model.task_dict = {task_name("GameQA"): task.dataset}
    result = evaluate(model, tasks, bootstrap_iters=0, log_samples=False, process_docs_parallel=1)
    summary = report(store, tasks, lmms_results=result, complete=True)
    assert summary["overall"]["accuracy"] == accuracy
    assert summary["overall"]["correct"] == correct
    assert summary["overall"]["answered"] == answered
    assert summary["overall"]["excluded"] == 2 - answered
    assert summary["overall"]["coverage"] == answered / 2
    assert summary["lmms_scores_verified"]
    assert len(provider.calls) == 2
    assert all("H. choice 7" in call[0] for call in provider.calls)
    assert len(json.loads((tmp_path / "lmms_results.json").read_text())["results"]) == 1


def test_ground_truth_never_crosses_model_boundary(monkeypatch):
    provider = FakeProvider([ProviderResponse("G")])
    model = AgentVQAModel(config=config(), provider_client=provider)
    row = {
        "Question": "Which?",
        "Options": ["one", "two"],
        "Answer": "SECRET_TARGET",
        "Image": {"bytes": image_bytes(), "path": None},
    }
    model.task_dict = {task_name("GameQA"): {"train": [row]}}
    seen = []

    def predict(doc, subset, index):
        seen.append(doc)
        return {"prediction": "A", "status": "ok"}

    monkeypatch.setattr(model, "predict", predict)
    request = SimpleNamespace(
        args=("context might contain a target", {}, None, 0, task_name("GameQA"), "train")
    )
    model.generate_until([request])
    assert "Answer" not in seen[0]
    assert "SECRET_TARGET" not in repr(seen)


@pytest.mark.parametrize("request_reasoning", [False, True])
@pytest.mark.parametrize("extract_reasoning", [False, True])
def test_reasoning_flags_independent(request_reasoning, extract_reasoning):
    provider = FakeProvider(
        [
            ProviderResponse(
                '{"answer":"B","reasoning":"brief explanation"}', reasoning="provider summary"
            )
        ]
    )
    model = AgentVQAModel(
        config=config(request_reasoning=request_reasoning, extract_reasoning=extract_reasoning),
        provider_client=provider,
    )
    doc = {
        "Question": "Which?",
        "Options": ["one", "two"],
        "Image": {"bytes": image_bytes(), "path": None},
    }
    result = model.predict(doc, "GameQA", 0)
    assert result["prediction"] == "B"
    assert result["rationale"] == ("brief explanation" if request_reasoning else None)
    assert result["provider_reasoning"] == ("provider summary" if extract_reasoning else None)
    assert ("Return JSON" in provider.calls[0][0]) == request_reasoning


def test_transient_retry_and_fatal_auth():
    doc = {
        "Question": "Which?",
        "Options": ["one", "two"],
        "Image": {"bytes": image_bytes(), "path": None},
    }
    provider = FakeProvider([ProviderError("rate limit", 429), ProviderResponse("B")])
    model = AgentVQAModel(config=config(), provider_client=provider)
    result = model.predict(doc, "GameQA", 0)
    assert result["prediction"] == "B" and len(result["attempts"]) == 2
    provider = FakeProvider([ProviderError("unauthorized", 401)])
    model = AgentVQAModel(config=config(), provider_client=provider)
    result = model.predict(doc, "GameQA", 0)
    assert result["fatal"] and len(result["attempts"]) == 1


def test_native_fallback_preserves_32_frames(monkeypatch, tmp_path):
    video = tmp_path / "fake.mp4"
    video.write_bytes(b"video")
    media = Media(video=video, mode="native", audit={})
    monkeypatch.setattr("agentvqa_eval.model.prepare_media", lambda *args: media)
    frames = [Image.new("RGB", (16, 8), "red") for _ in range(32)]
    monkeypatch.setattr(
        "agentvqa_eval.media.sample_frames", lambda *args: (frames, {"timestamps": list(range(32))})
    )
    provider = FakeProvider([ProviderError("video unsupported", 415), ProviderResponse("B")])
    settings = RunConfig(
        model="glm-4.6v", provider="zai", image_limit=10, native_supported=True, retry_delay=0
    )
    model = AgentVQAModel(config=settings, provider_client=provider)
    result = model.predict({"Question": "Which?", "Options": ["one", "two"]}, "MarioQA", 0)
    assert result["prediction"] == "B"
    assert len(provider.calls[1][1]) == 8
    assert provider.calls[1][2] is None
    assert sum(len(p) for p in result["media"]["panels"]) == 32


def test_resume_identity_and_no_double_calls(monkeypatch, tmp_path):
    store = Store(tmp_path, {"dry_run": False, "model": "exact-version"})
    store.write({"subset": "GameQA", "row_index": 0, "prediction": "H", "status": "ok"})
    provider = FakeProvider([])
    model = AgentVQAModel(config=config(), store=store, provider_client=provider)
    request = SimpleNamespace(args=("prompt", {}, None, 0, task_name("GameQA"), "train"))
    assert json.loads(model.generate_until([request])[0])["prediction"] == "H"
    assert not provider.calls
    with pytest.raises(ValueError, match="Resume refused"):
        Store(tmp_path, {"dry_run": False, "model": "other-version"}, resume=True)


def test_micro_average_excludes_failures_but_counts_valid_wrong_answers():
    rows = [{"correct": True, "valid_answer": True, "status": "ok"}] * 40
    rows += [{"correct": False, "valid_answer": True, "status": "ok"}] * 10
    rows += [{"correct": False, "valid_answer": False, "status": "api_error"}] * 50
    metrics = summarize(rows)
    assert metrics["accuracy"] == 0.8
    assert metrics["accuracy_percent"] == 80
    assert metrics["coverage"] == 0.5
    assert metrics["total"] == 100
    assert metrics["answered"] == metrics["excluded"] == 50


@pytest.mark.parametrize(
    "scores,expected", [([1, 0, None], 0.5), ([0, None], 0.0), ([None], None), ([], None)]
)
def test_answered_accuracy(scores, expected):
    assert answered_accuracy(scores) == expected


@pytest.mark.parametrize("count", [2, 8, 30])
def test_scoring_uses_the_actual_option_count(count):
    doc = {"Options": [f"choice {i}" for i in range(count)], "Answer": label(count - 1)}
    assert process_results(doc, [json.dumps({"prediction": label(count - 1)})]) == {
        "accuracy": 1.0,
        "coverage": 1.0,
    }
    assert process_results(doc, [json.dumps({"prediction": "A"})]) == {
        "accuracy": 0.0,
        "coverage": 1.0,
    }
    for prediction in (label(count), "", None, 0, True, ["A"], {"answer": "A"}):
        assert process_results(doc, [json.dumps({"prediction": prediction})]) == {
            "accuracy": None,
            "coverage": 0.0,
        }


def test_zero_valid_answers_are_unavailable():
    for rows in ([], [{"correct": True, "valid_answer": False, "status": "invalid_answer"}]):
        metrics = summarize(rows)
        assert metrics["accuracy"] is None
        assert metrics["accuracy_percent"] is None
        assert metrics["correct"] == metrics["answered"] == 0


def test_lmms_dry_run_has_no_accuracy(monkeypatch, tmp_path):
    from lmms_eval.evaluator import evaluate

    monkeypatch.setattr("agentvqa_eval.data.load_subset", lambda *args: data_rows())
    task = AgentVQATask("GameQA", revision="test-fixture")
    tasks = {task_name("GameQA"): task}
    store = Store(tmp_path, {"dry_run": True})
    provider = FakeProvider([])
    model = AgentVQAModel(config=config(), store=store, provider_client=provider, dry_run=True)
    model.task_dict = {task_name("GameQA"): task.dataset}
    result = evaluate(model, tasks, bootstrap_iters=0, log_samples=False, process_docs_parallel=1)
    summary = report(store, tasks, lmms_results=result, complete=True)
    assert summary["overall"]["accuracy"] is None
    assert summary["overall"]["coverage"] == 0
    assert summary["overall"]["status_counts"] == {"dry_run": 2}
    assert not provider.calls


def test_interrupted_run_excludes_unattempted_samples(monkeypatch, tmp_path):
    from lmms_eval.evaluator import evaluate

    monkeypatch.setattr("agentvqa_eval.data.load_subset", lambda *args: data_rows())
    task = AgentVQATask("GameQA", revision="test-fixture")
    tasks = {task_name("GameQA"): task}
    store = Store(tmp_path, {"dry_run": False})
    provider = FakeProvider([ProviderResponse("G")])
    model = AgentVQAModel(config=config(), store=store, provider_client=provider, max_api_calls=1)
    model.task_dict = {task_name("GameQA"): task.dataset}
    with pytest.raises(CallBudgetReached):
        evaluate(model, tasks, bootstrap_iters=0, log_samples=False, process_docs_parallel=1)
    summary = report(store, tasks)
    assert summary["complete"] is False
    assert summary["overall"]["accuracy"] == 1
    assert summary["overall"]["coverage"] == 0.5
    assert summary["overall"]["status_counts"] == {"ok": 1, "unattempted": 1}
    assert len(provider.calls) == 1


@pytest.mark.parametrize("first,expected", [("G", 1.0), ("B", 0.5)])
def test_retry_failed_preserves_valid_answers(monkeypatch, tmp_path, first, expected):
    from lmms_eval.evaluator import evaluate

    monkeypatch.setattr("agentvqa_eval.data.load_subset", lambda *args: data_rows())
    task = AgentVQATask("GameQA", revision="test-fixture")
    tasks = {task_name("GameQA"): task}
    manifest = {"dry_run": False}
    store = Store(tmp_path, manifest)
    store.write({"subset": "GameQA", "row_index": 0, "prediction": first, "status": "ok"})
    store.write(
        {"subset": "GameQA", "row_index": 1, "prediction": None, "status": "invalid_answer"}
    )
    before = store.path("GameQA", 0).read_bytes()
    provider = FakeProvider([ProviderResponse("A")])
    model = AgentVQAModel(
        config=config(),
        store=Store(tmp_path, manifest, resume=True),
        provider_client=provider,
        retry_failed=True,
    )
    model.task_dict = {task_name("GameQA"): task.dataset}
    result = evaluate(model, tasks, bootstrap_iters=0, log_samples=False, process_docs_parallel=1)
    summary = report(store, tasks, lmms_results=result, complete=True)
    assert summary["overall"]["accuracy"] == expected
    assert summary["overall"]["answered"] == 2
    assert summary["overall"]["coverage"] == 1
    assert store.path("GameQA", 0).read_bytes() == before
    assert len(provider.calls) == 1


def test_report_pools_valid_answers_across_subsets_and_domains(tmp_path):
    store = Store(tmp_path, {"dry_run": False})
    tasks = {}
    for subset, predictions in {
        "GameQA": ["A", "B", None],
        "Atari": ["A", "A", "A", None],
        "Share-Robot": ["C", None],
    }.items():
        docs = [{"Options": ["yes", "no"], "Answer": "A"}] * len(predictions)
        tasks[task_name(subset)] = SimpleNamespace(subset=subset, dataset_no_image={"train": docs})
        for index, prediction in enumerate(predictions):
            if subset == "Share-Robot" and index == 1:
                continue
            store.write(
                {
                    "subset": subset,
                    "row_index": index,
                    "prediction": prediction,
                    "status": "ok" if prediction else "api_error",
                    "correct": True,
                    "valid_answer": True,
                }
            )
    summary = report(store, tasks)
    assert summary["overall"]["accuracy"] == summary["domains"]["Games"]["accuracy"] == 0.8
    assert summary["overall"]["coverage"] == 5 / 9
    assert summary["overall"]["correct"] == 4
    assert summary["overall"]["answered"] == 5
    assert summary["overall"]["excluded"] == 4
    assert summary["subsets"]["GameQA"]["accuracy"] == 0.5
    assert summary["subsets"]["Atari"]["accuracy"] == 1
    assert summary["domains"]["Robotics"]["accuracy"] is None
    assert summary["accuracy_denominator"] == "valid_answers"
    rows = [json.loads(line) for line in (tmp_path / "predictions.jsonl").read_text().splitlines()]
    assert sum(row["valid_answer"] for row in rows) == 5
    assert sum(row["correct"] for row in rows) == 4
    with (tmp_path / "accuracy.csv").open() as handle:
        exported = list(csv.DictReader(handle))
    assert exported[0]["accuracy_percent"] == "80.0"
    assert exported[0]["excluded"] == "4"
    assert next(row for row in exported if row["name"] == "Robotics")["accuracy_percent"] == ""


@pytest.mark.parametrize("upstream", [0.5, None, float("nan")])
def test_independent_verification_rejects_old_or_invalid_denominators(tmp_path, upstream):
    store = Store(tmp_path, {"dry_run": False})
    store.write({"subset": "GameQA", "row_index": 0, "prediction": "A", "status": "ok"})
    task = SimpleNamespace(
        subset="GameQA",
        dataset_no_image={"train": [{"Options": ["yes", "no"], "Answer": "A"}] * 2},
    )
    tasks = {task_name("GameQA"): task}
    results = {"results": {task_name("GameQA"): {"accuracy,none": upstream, "coverage,none": 0.5}}}
    with pytest.raises(ValueError, match="Independent score verification failed"):
        report(store, tasks, lmms_results=results)


def test_qwen25_prompt_coordinates_match_encoded_image():
    output = io.BytesIO()
    Image.new("RGB", (1920, 1080), "white").save(output, format="PNG")
    doc = {
        "Question": "Where should the user click?",
        "Options": ["[960, 540]", "[480, 270]"],
        "Image": {"bytes": output.getvalue(), "path": None},
    }
    settings = RunConfig(
        model="qwen2.5-vl-72b-instruct",
        provider="dashscope",
        image_limit=10,
        native_supported=True,
    )
    fake = FakeProvider([ProviderResponse("B")])
    model = AgentVQAModel(config=settings, provider_client=fake)
    result = model.predict(doc, "Screenspot", 0)
    sent = Image.open(io.BytesIO(fake.calls[0][1][0]))
    width, height = sent.size
    assert result["sent_sizes"] == [sent.size]
    assert result["options"] == [
        f"[{round(width / 2)}, {round(height / 2)}]",
        f"[{round(width / 4)}, {round(height / 4)}]",
    ]
    assert width % 28 == height % 28 == 0
    assert width * height <= settings.qwen_max_pixels
    assert result["prediction"] == "B"
