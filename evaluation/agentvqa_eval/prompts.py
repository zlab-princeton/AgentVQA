import re

from .catalog import POINT_SUBSETS, SUBSETS
from .parsing import choices, label

POINT = re.compile(r"\[\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]")
FORMATS = ("auto", "pixel-xy", "unit-xy", "1000-xy", "1000-yx", "999-xy", "999-yx")


def is_qwen25(model):
    return bool(re.search(r"qwen[-_/]?2\.5(?:[-_/]|$)", model.lower()))


def coordinate_format(model, requested="auto", provider=None):
    if requested != "auto":
        if requested not in FORMATS:
            raise ValueError(f"Unknown coordinate format: {requested}")
        return requested
    model = model.lower()
    if "gemini" in model:
        return "1000-yx"
    if "qwen" in model:
        if is_qwen25(model):
            return "pixel-xy"
        return "999-xy" if provider == "dashscope" else "1000-xy"
    return "unit-xy"


def convert_points(text, original_size, sent_size, mode):
    width, height = original_size
    sent_width, sent_height = sent_size
    warnings = []

    def replace(match):
        x, y = map(float, match.groups())
        if not (0 <= x < width and 0 <= y < height):
            warnings.append(
                f"Out-of-image source point [{x:g}, {y:g}] in {width}x{height}; not clipped"
            )
        if mode == "pixel-xy":
            values = (round(x * sent_width / width), round(y * sent_height / height))
        elif mode == "unit-xy":
            return f"[{x / width:.3f}, {y / height:.3f}]"
        else:
            scale = int(mode.split("-")[0])
            values = (round(x / width * scale), round(y / height * scale))
            if mode.endswith("yx"):
                values = values[::-1]
        return f"[{values[0]}, {values[1]}]"

    return POINT.sub(replace, text), warnings


def build_prompt(
    doc, subset, mode, original_sizes, sent_sizes, request_reasoning=False, media_note=""
):
    option_texts = [v for _, v in choices(doc)]
    warnings = []
    note = ""
    if subset in POINT_SUBSETS and any(POINT.search(v) for v in option_texts):
        if len(original_sizes) != 1 or len(sent_sizes) != 1:
            raise ValueError("Image-point choices require one unambiguous source image")
        transformed = []
        for option in option_texts:
            value, issues = convert_points(option, original_sizes[0], sent_sizes[0], mode)
            transformed.append(value)
            warnings.extend(issues)
        option_texts = transformed
        order = "y, x" if mode.endswith("yx") else "x, y"
        units = (
            "absolute pixels of the supplied image"
            if mode == "pixel-xy"
            else (
                "normalized to 0–1"
                if mode == "unit-xy"
                else f"normalized to 0–{mode.split('-')[0]}"
            )
        )
        note = f"Image-point coordinates in the Options section are [{order}], {units}, with origin at the top-left."
        if mode == "pixel-xy":
            note += f" The supplied image is {sent_sizes[0][0]} pixels wide and {sent_sizes[0][1]} pixels high."
        if warnings:
            note += " An out-of-image option remains outside the image and is not clipped."
    sections = [f"Answer this AgentVQA multiple-choice question in the {SUBSETS[subset]} domain."]
    for field in ("Episode Goal", "Action History"):
        value = doc.get(field)
        if value:
            sections.append(f"{field}:\n{value}")
    sections.append(f"Question:\n{doc['Question']}")
    if note:
        sections.append(note)
    if media_note:
        sections.append(media_note)
    sections.append(
        "Options (use this list as authoritative):\n"
        + "\n".join(f"{label(i)}. {v}" for i, v in enumerate(option_texts))
    )
    labels = ", ".join(label(i) for i in range(len(option_texts)))
    if request_reasoning:
        sections.append(
            f'Return JSON with "reasoning" (a brief explanation, at most 30 words) and "answer" (one option label from {labels}).'
        )
    else:
        sections.append(f"Return only the correct option label from {labels}.")
    return "\n\n".join(sections), option_texts, sorted(set(warnings))
