import json
import re
from dataclasses import dataclass


def label(index):
    result = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def clean_choice(text, original_index):
    return re.sub(
        rf"^\s*(?:\({label(original_index)}\)|{label(original_index)}[.)])\s+",
        "",
        str(text).strip(),
        count=1,
    ).strip()


def choices(doc):
    values = doc.get("Options")
    if not isinstance(values, (list, tuple)):
        raise ValueError("Options must be a sequence")
    result = [
        (i, clean_choice(v, i)) for i, v in enumerate(values) if v is not None and str(v).strip()
    ]
    if len(result) < 2:
        raise ValueError("At least two nonempty options are required")
    return result


def target(doc):
    options = choices(doc)
    answer = doc["Answer"]
    if isinstance(answer, int) and not isinstance(answer, bool):
        original = answer
    else:
        answer = str(answer).strip()
        original_labels = {label(i): i for i in range(len(doc["Options"]))}
        if answer.upper() in original_labels:
            original = original_labels[answer.upper()]
        else:
            matches = [
                i
                for i, text in options
                if answer.casefold() in (text.casefold(), str(doc["Options"][i]).strip().casefold())
            ]
            if len(matches) != 1:
                raise ValueError(f"Answer does not identify one option: {answer!r}")
            original = matches[0]
    for displayed, (i, _) in enumerate(options):
        if i == original:
            return label(displayed)
    raise ValueError("Answer points to an absent option")


def split_thinking(text):
    reasoning = []
    for tag in ("think", "thinking", "analysis"):
        pattern = rf"<{tag}>(.*?)</{tag}>"
        reasoning.extend(re.findall(pattern, text, re.S | re.I))
        text = re.sub(pattern, "", text, flags=re.S | re.I)
        match = re.search(rf"<{tag}>", text, re.I)
        if match:
            reasoning.append(text[match.end() :])
            text = text[: match.start()]
    return text.strip(), "\n".join(reasoning).strip()


@dataclass(frozen=True)
class ParsedAnswer:
    answer: str | None
    rationale: str | None = None


def parse_answer(text, option_texts):
    allowed = {label(i) for i in range(len(option_texts))}
    text, _ = split_thinking(text or "")
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)

    def normalize(value):
        if not isinstance(value, str):
            return None
        value = value.strip().strip("`* ")
        direct = re.fullmatch(r"\(?([A-Za-z]+)\)?[.!]?", value)
        if direct and direct[1].upper() in allowed:
            return direct[1].upper()
        matches = [
            label(i)
            for i, option in enumerate(option_texts)
            if value.casefold() == option.strip().casefold()
        ]
        return matches[0] if len(matches) == 1 else None

    objects = []
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text):
        try:
            obj, _ = decoder.raw_decode(text[match.start() :])
            if isinstance(obj, dict) and "answer" in obj:
                objects.append(obj)
        except ValueError:
            pass
    if objects:
        answers = {normalize(o["answer"]) for o in objects}
        answer = next(iter(answers)) if len(answers) == 1 else None
        rationale = objects[-1].get("reasoning", objects[-1].get("rationale"))
        return ParsedAnswer(answer, rationale if isinstance(rationale, str) else None)
    patterns = (
        r"\\boxed\{\s*([A-Za-z]+)\s*\}",
        r"<\|begin_of_box\|>\s*([A-Za-z]+)\s*<\|end_of_box\|>",
        r"<answer>\s*([A-Za-z]+)\s*</answer>",
        r"\b(?:final\s+answer|answer|correct\s+option)\s*(?:is\s+|[:=]\s*)(?:option\s+)?[(*`]*([A-Za-z]+)\b",
        r"\bI\s+(?:choose|select)\s+(?:option\s+)?([A-Za-z]+)\b",
    )
    found = [x.upper() for pattern in patterns for x in re.findall(pattern, text, re.I)]
    if found:
        unique = set(found)
        return ParsedAnswer(next(iter(unique)) if len(unique) == 1 and unique <= allowed else None)
    direct = normalize(text)
    if direct:
        return ParsedAnswer(direct)
    named = re.fullmatch(r"(?:option|choice)\s+([A-Za-z]+)[.!]?", text, re.I)
    if named:
        return ParsedAnswer(named[1].upper() if named[1].upper() in allowed else None)
    marked = re.fullmatch(r"([A-Za-z]+)[.)]\s+(.+)", text, re.S)
    if marked and marked[1].upper() in allowed:
        i = next(i for i in range(len(option_texts)) if label(i) == marked[1].upper())
        if marked[2].strip().casefold() == option_texts[i].strip().casefold():
            return ParsedAnswer(marked[1].upper())
    return ParsedAnswer(None)
