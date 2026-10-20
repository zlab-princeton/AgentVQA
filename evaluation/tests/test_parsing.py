import json

import pytest

from agentvqa_eval.parsing import choices, label, parse_answer, split_thinking, target


@pytest.mark.parametrize("size", [2, 3, 4, 5, 8, 12, 26, 28])
def test_every_offered_label(size):
    options = [f"choice {i}" for i in range(size)]
    for i in range(size):
        answer = label(i)
        for text in (
            answer,
            answer.lower(),
            f"({answer})",
            f"Answer: {answer}",
            json.dumps({"reasoning": "A brief explanation.", "answer": answer}),
            f'```json\n{{"answer": "{answer}"}}\n```',
            f"\\boxed{{{answer}}}",
            f"<|begin_of_box|>{answer}<|end_of_box|>",
        ):
            assert parse_answer(text, options).answer == answer


@pytest.mark.parametrize(
    "text",
    [
        "Elephants are visible",
        "A cat is visible",
        "Because it matches",
        "A or B",
        "Answer: Z",
        '{"answer":"Z"}',
        "Answer: A\nAnswer: B",
        "<think>Answer: A</think>",
        "<think>Answer: A",
        '{"answer": 0}',
        "",
    ],
)
def test_no_accidental_first_letter_or_reasoning_answers(text):
    assert parse_answer(text, ["cat", "dog"]).answer is None


def test_thinking_and_rationale_are_distinct():
    text = '<think>private provider field</think>{"answer":"E","reasoning":"brief"}'
    visible, thinking = split_thinking(text)
    assert thinking == "private provider field"
    parsed = parse_answer(visible, [str(i) for i in range(8)])
    assert (parsed.answer, parsed.rationale) == ("E", "brief")


def test_options_and_ground_truth_after_padding():
    doc = {"Options": ["A. first", None, "C. third", "null", ""], "Answer": "C"}
    assert choices(doc) == [(0, "first"), (2, "third"), (3, "null")]
    assert target(doc) == "B"
    assert target({**doc, "Answer": 3}) == "C"
    assert target({**doc, "Answer": "null"}) == "C"
    with pytest.raises(ValueError):
        target({**doc, "Answer": "B"})


def test_exact_option_text_only():
    doc = {"Options": ["red", "red and blue"], "Answer": "red and blue"}
    assert target(doc) == "B"
    assert parse_answer("red and blue", doc["Options"]).answer == "B"
    assert parse_answer("red", ["red", "red"]).answer is None
    with pytest.raises(ValueError):
        target({**doc, "Answer": "blue"})


def test_option_label_prefix_is_positional():
    assert choices({"Options": ["A useful object", "B. correct", "A. semantic label"]}) == [
        (0, "A useful object"),
        (1, "correct"),
        (2, "A. semantic label"),
    ]
