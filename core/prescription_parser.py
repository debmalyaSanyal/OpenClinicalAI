from __future__ import annotations

import re
from dataclasses import dataclass


DOSE_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|iu|units?|tab|tabs?|cap|caps?))\b", re.I)
TABLE_DOSE_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)\b")
DURATION_PATTERN = re.compile(r"\b(?:x|for)\s*(\d+\s*(?:day(?:s|\(s\))?|week(?:s|\(s\))?|month(?:s|\(s\))?))\b", re.I)
FREQUENCY_DETAILS = {
    "od": {
        "frequency": "once daily",
        "explanation": "OD means once daily, usually one dose in a day.",
    },
    "daily": {
        "frequency": "once daily",
        "explanation": "Daily means one dose in a day.",
    },
    "once daily": {
        "frequency": "once daily",
        "explanation": "Once daily means one dose in a day.",
    },
    "bd": {
        "frequency": "twice daily",
        "explanation": "BD means twice daily, usually morning and evening.",
    },
    "bid": {
        "frequency": "twice daily",
        "explanation": "BID means twice daily, usually morning and evening.",
    },
    "tds": {
        "frequency": "three times daily",
        "explanation": "TDS means three times daily, usually morning, afternoon, and night.",
    },
    "tid": {
        "frequency": "three times daily",
        "explanation": "TID means three times daily, usually morning, afternoon, and night.",
    },
    "qid": {
        "frequency": "four times daily",
        "explanation": "QID means four times daily.",
    },
    "hs": {
        "frequency": "at bedtime",
        "explanation": "HS means at bedtime.",
    },
    "sos": {
        "frequency": "when needed",
        "explanation": "SOS means take only when needed, as prescribed.",
    },
    "prn": {
        "frequency": "when needed",
        "explanation": "PRN means take only when needed, as prescribed.",
    },
    "ac": {
        "frequency": "before food",
        "explanation": "AC means before food.",
    },
    "pc": {
        "frequency": "after food",
        "explanation": "PC means after food.",
    },
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
    "atrovas",
    "collashot",
    "lumia",
    "lupoxa",
    "macvestin",
    "pregabid",
    "primolut",
    "primolut-n",
    "stamlo",
    "tazloc",
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
    frequency_abbreviation: str | None
    frequency_explanation: str | None
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
    if table_medicine := parse_table_medicine_line(line):
        return table_medicine
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
        frequency=frequency["frequency"] if frequency else None,
        frequency_abbreviation=frequency["abbreviation"] if frequency else None,
        frequency_explanation=frequency["explanation"] if frequency else None,
        duration=normalize_duration(duration_match.group(1)) if duration_match else None,
        instruction=line,
    )


def looks_like_medicine_line(line: str) -> bool:
    if any(medicine in line for medicine in KNOWN_MEDICINES):
        return True
    if extract_frequency(line) and re.search(r"\b[a-z][a-z0-9\-]{2,}\b", line, re.I):
        return not re.search(r"\b(date|pulse|weight|spo2|purpose|dose|medicine|history)\b", line, re.I)
    return bool(re.search(r"\b(tab|tablet|cap|capsule|syr|syrup|inj|injection|rx)\b", line, re.I))


def parse_table_medicine_line(line: str) -> ParsedMedicine | None:
    cleaned = re.sub(r"^\d+\s+", "", line.strip())
    if re.match(r"^(rx|tab|tablet|cap|capsule|syr|syrup|inj|injection)\s*[:.\-]?\s+", cleaned, re.I):
        return None
    if re.search(r"\b(other medicine|medicine|dose|purpose|sln?o)\b", cleaned, re.I):
        return None
    frequency_matches = list(re.finditer(r"\b(od|bd|bid|tds|tid|qid|hs|sos|prn|ac|pc|daily|once monthly|monthly)\b", cleaned, re.I))
    if not frequency_matches:
        return None
    frequency_match = frequency_matches[-1]
    left = cleaned[: frequency_match.start()].strip(" :-")
    if not left:
        return None
    dose = None
    dose_match = list(DOSE_PATTERN.finditer(left)) or list(TABLE_DOSE_PATTERN.finditer(left))
    if dose_match:
        last_dose = dose_match[-1]
        dose = last_dose.group(1)
        name = left[: last_dose.start()].strip(" :-")
    else:
        name = left
    name = normalize_table_medicine_name(name)
    if not name:
        return None
    frequency = extract_frequency(frequency_match.group(1))
    return ParsedMedicine(
        name=name,
        dose=dose,
        frequency=frequency["frequency"] if frequency else None,
        frequency_abbreviation=frequency["abbreviation"] if frequency else None,
        frequency_explanation=frequency["explanation"] if frequency else None,
        duration=None,
        instruction=line,
    )


def normalize_table_medicine_name(name: str) -> str | None:
    name = re.sub(r"\b(plus|tablet|tab|cap|capsule)\b", "", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip(" :-")
    if not name or name.lower() in NON_MEDICINE_TOKENS:
        return None
    return " ".join(part.upper() if part.lower() in {"cr", "od"} else part.title() for part in name.split())


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


def extract_frequency(line: str) -> dict | None:
    for short_form, detail in FREQUENCY_DETAILS.items():
        if re.search(rf"\b{short_form}\b", line, re.I):
            return {"abbreviation": short_form.upper(), **detail}
    if re.search(r"\b1-0-1\b", line):
        return {
            "abbreviation": "1-0-1",
            "frequency": "morning and night",
            "explanation": "1-0-1 means take in the morning and at night.",
        }
    if re.search(r"\b1-1-1\b", line):
        return {
            "abbreviation": "1-1-1",
            "frequency": "morning, afternoon, and night",
            "explanation": "1-1-1 means take in the morning, afternoon, and night.",
        }
    if re.search(r"\b1-0-0\b", line):
        return {
            "abbreviation": "1-0-0",
            "frequency": "morning",
            "explanation": "1-0-0 means take in the morning.",
        }
    if re.search(r"\b0-0-1\b", line):
        return {
            "abbreviation": "0-0-1",
            "frequency": "night",
            "explanation": "0-0-1 means take at night.",
        }
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
