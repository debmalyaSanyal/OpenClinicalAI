from __future__ import annotations

import re
from dataclasses import dataclass


DOSE_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|iu|units?|tab|tabs?|cap|caps?))\b", re.I)
DURATION_PATTERN = re.compile(r"\b(?:x|for)\s*(\d+\s*(?:day(?:s|\(s\))?|week(?:s|\(s\))?|month(?:s|\(s\))?))\b", re.I)
FREQUENCY_MAP = {
    "od": "once daily",
    "daily": "once daily",
    "once daily": "once daily",
    "bd": "twice daily",
    "bid": "twice daily",
    "tds": "three times daily",
    "tid": "three times daily",
    "qid": "four times daily",
    "hs": "at bedtime",
    "sos": "when needed",
    "prn": "when needed",
}
KNOWN_MEDICINES = {
    "amoxicillin",
    "azithromycin",
    "cetirizine",
    "metformin",
    "omeprazole",
    "pantoprazole",
    "paracetamol",
    "atorvastatin",
    "amlodipine",
    "levocetirizine",
    "dolo",
    "calpol",
    "dexamethasone",
}
NON_MEDICINE_TOKENS = {
    "address",
    "date",
    "dr",
    "for",
    "healthcare",
    "quantity",
    "refills",
    "rx",
    "send",
    "signature",
}


@dataclass(frozen=True)
class ParsedMedicine:
    name: str
    dose: str | None
    frequency: str | None
    duration: str | None
    instruction: str


def parse_prescription_text(text: str) -> dict:
    lines = [clean_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]
    lines = merge_instruction_continuations(lines)
    medicines = [medicine for line in lines if (medicine := parse_medicine_line(line))]
    symptoms = extract_symptoms(text)
    warnings = []
    if not medicines:
        warnings.append("No medicine lines were confidently detected. Try a clearer printed sample.")
    if any("allergy" in line.lower() for line in lines):
        warnings.append("Allergy information was mentioned. Review before using any medicine.")
    return {
        "status": "parsed",
        "ocr_text": text.strip(),
        "medicines": [medicine.__dict__ for medicine in medicines],
        "symptoms_or_diagnosis": symptoms,
        "warnings": warnings,
        "disclaimer": "For demo use only. A clinician or pharmacist must verify prescription results.",
    }


def clean_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^[\-\*\u2022\s]+", "", line)
    line = re.sub(r"\s+", " ", line)
    return line


def parse_medicine_line(line: str) -> ParsedMedicine | None:
    normalized = line.lower()
    if not looks_like_medicine_line(normalized):
        return None
    name = extract_medicine_name(line)
    if not name:
        return None
    dose_match = DOSE_PATTERN.search(line)
    duration_match = DURATION_PATTERN.search(line)
    frequency = extract_frequency(normalized)
    return ParsedMedicine(
        name=name,
        dose=dose_match.group(1) if dose_match else None,
        frequency=frequency,
        duration=normalize_duration(duration_match.group(1)) if duration_match else None,
        instruction=line,
    )


def looks_like_medicine_line(line: str) -> bool:
    if any(medicine in line for medicine in KNOWN_MEDICINES):
        return True
    return bool(re.search(r"\b(tab|tablet|cap|capsule|syr|syrup|inj|injection|rx)\b", line, re.I))


def extract_medicine_name(line: str) -> str | None:
    cleaned = re.sub(r"^(rx|tab|tablet|cap|capsule|syr|syrup|inj|injection)\s*[:.\-]?\s+", "", line, flags=re.I)
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]*", cleaned)
    for index, token in enumerate(tokens):
        if token.lower() in KNOWN_MEDICINES:
            return token.title()
        if token.lower() in {"tab", "tablet", "cap", "capsule", "syr", "syrup", "inj", "injection"} and index + 1 < len(tokens):
            return tokens[index + 1].title()
    for token in tokens:
        if token.lower() not in NON_MEDICINE_TOKENS and len(token) > 2:
            return token.title()
    return None


def extract_frequency(line: str) -> str | None:
    for short_form, meaning in FREQUENCY_MAP.items():
        if re.search(rf"\b{short_form}\b", line, re.I):
            return meaning
    if re.search(r"\b1-0-1\b", line):
        return "morning and night"
    if re.search(r"\b1-1-1\b", line):
        return "morning, afternoon, and night"
    if re.search(r"\b1-0-0\b", line):
        return "morning"
    if re.search(r"\b0-0-1\b", line):
        return "night"
    return None


def merge_instruction_continuations(lines: list[str]) -> list[str]:
    merged: list[str] = []
    for line in lines:
        if merged and is_continuation_line(line):
            merged[-1] = f"{merged[-1]} {line}"
        else:
            merged.append(line)
    return merged


def is_continuation_line(line: str) -> bool:
    return bool(re.search(r"^(for|x)\s+\d+|^quantity\b|^refills?\b", line, re.I))


def normalize_duration(duration: str) -> str:
    return re.sub(r"\bday$", "days", duration.replace("(s)", "s"), flags=re.I)


def extract_symptoms(text: str) -> list[str]:
    found = []
    for label in ("diagnosis", "complaint", "symptoms"):
        match = re.search(rf"{label}\s*[:\-]\s*(.+)", text, re.I)
        if match:
            found.append(match.group(1).strip())
    return found
