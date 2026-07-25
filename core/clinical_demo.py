from __future__ import annotations

from core.prescription_parser import parse_prescription_text


MEDICINE_KNOWLEDGE = {
    "amoxicillin": {
        "use": "Antibiotic commonly used for bacterial infections.",
        "caution": "Check penicillin allergy. Complete the course if prescribed.",
    },
    "azithromycin": {
        "use": "Antibiotic commonly used for selected respiratory and throat infections.",
        "caution": "Review heart rhythm risk and medicine interactions with a clinician.",
    },
    "cetirizine": {
        "use": "Antihistamine used for allergy, cold symptoms, itching, or sneezing.",
        "caution": "May cause sleepiness in some people.",
    },
    "levocetirizine": {
        "use": "Antihistamine used for allergy symptoms.",
        "caution": "May cause sleepiness. Avoid driving if drowsy.",
    },
    "metformin": {
        "use": "Medicine used for type 2 diabetes.",
        "caution": "Use with clinician guidance in kidney disease or severe dehydration.",
    },
    "omeprazole": {
        "use": "Acid-reducing medicine used for acidity, reflux, or ulcer symptoms.",
        "caution": "Long-term use should be reviewed by a clinician.",
    },
    "pantoprazole": {
        "use": "Acid-reducing medicine used for acidity, reflux, or stomach protection.",
        "caution": "Take as directed, often before food when prescribed.",
    },
    "paracetamol": {
        "use": "Pain and fever medicine.",
        "caution": "Avoid overdose and avoid combining multiple products containing paracetamol.",
    },
    "dolo": {
        "use": "Brand commonly containing paracetamol for pain or fever.",
        "caution": "Confirm strength and avoid duplicate paracetamol products.",
    },
    "calpol": {
        "use": "Brand commonly containing paracetamol for pain or fever.",
        "caution": "Confirm dose carefully, especially for children.",
    },
    "atorvastatin": {
        "use": "Cholesterol-lowering medicine.",
        "caution": "Report unexplained severe muscle pain or weakness.",
    },
    "amlodipine": {
        "use": "Blood pressure medicine.",
        "caution": "May cause ankle swelling or dizziness in some people.",
    },
}


RED_FLAGS = {
    "chest pain": "Chest pain can be urgent, especially with sweating, breathlessness, or arm/jaw pain.",
    "breathless": "Breathlessness can need urgent medical assessment.",
    "shortness of breath": "Shortness of breath can need urgent medical assessment.",
    "unconscious": "Unconsciousness is an emergency.",
    "seizure": "Seizure symptoms need prompt medical attention.",
    "severe allergy": "Severe allergy symptoms can become an emergency.",
}


def analyze_prescription_text(text: str) -> dict:
    parsed = parse_prescription_text(text)
    medicines = parsed["medicines"]
    knowledge = [lookup_medicine(medicine["name"]) for medicine in medicines]
    safety = evaluate_safety(text, medicines)
    return {
        "status": "complete",
        "parsed_prescription": parsed,
        "medicine_knowledge": knowledge,
        "safety_review": safety,
        "patient_summary": build_patient_summary(parsed, knowledge, safety),
        "questions_for_doctor": build_questions(parsed, safety),
        "confidence": estimate_confidence(text, medicines),
    }


def lookup_medicine(name: str) -> dict:
    key = name.lower()
    info = MEDICINE_KNOWLEDGE.get(
        key,
        {
            "use": "Medicine detected, but no built-in explanation is available in this demo.",
            "caution": "Verify the medicine name, dose, and instructions with a clinician or pharmacist.",
        },
    )
    return {"name": name, **info}


def evaluate_safety(text: str, medicines: list[dict]) -> dict:
    lowered = text.lower()
    flags = [{"type": "urgent_symptom", "message": message} for phrase, message in RED_FLAGS.items() if phrase in lowered]
    medicine_names = {medicine["name"].lower() for medicine in medicines}
    if {"paracetamol", "dolo"} <= medicine_names or {"paracetamol", "calpol"} <= medicine_names:
        flags.append(
            {
                "type": "duplicate_ingredient",
                "message": "Possible duplicate paracetamol products detected. Confirm before taking both.",
            }
        )
    if "pregnant" in lowered or "pregnancy" in lowered:
        flags.append(
            {
                "type": "special_population",
                "message": "Pregnancy mentioned. Medicine safety should be verified by a clinician.",
            }
        )
    if "child" in lowered or "pediatric" in lowered or "paediatric" in lowered:
        flags.append(
            {
                "type": "dose_review",
                "message": "Child/pediatric context mentioned. Dose must be age and weight appropriate.",
            }
        )
    return {
        "risk_level": "high" if flags else "routine",
        "flags": flags,
        "safe_use_note": "Do not start, stop, or change medicines without a qualified medical professional.",
    }


def build_patient_summary(parsed: dict, knowledge: list[dict], safety: dict) -> str:
    medicines = parsed["medicines"]
    if not medicines:
        return "No medicines were confidently detected. Please upload a clearer image or paste typed prescription text."
    names = ", ".join(medicine["name"] for medicine in medicines)
    summary = f"Detected {len(medicines)} medicine(s): {names}."
    if parsed["symptoms_or_diagnosis"]:
        summary += f" Mentioned condition: {parsed['symptoms_or_diagnosis'][0]}."
    if safety["flags"]:
        summary += " Safety items need review before use."
    else:
        summary += " No urgent safety flags were detected by the demo rules."
    if knowledge:
        summary += " Verify all doses and timings with the original prescription."
    return summary


def build_questions(parsed: dict, safety: dict) -> list[str]:
    questions = [
        "Are the medicine names and strengths read correctly?",
        "When exactly should each medicine be taken with respect to food?",
        "What side effects should I watch for?",
    ]
    if safety["flags"]:
        questions.insert(0, "Do any of the safety warnings change how I should take these medicines?")
    if not parsed["medicines"]:
        questions.insert(0, "Can you confirm the medicine names from the original prescription?")
    return questions


def estimate_confidence(text: str, medicines: list[dict]) -> dict:
    if not text.strip():
        return {"level": "low", "reason": "No text was provided."}
    if len(medicines) >= 2:
        return {"level": "medium", "reason": "Multiple medicine-like lines were parsed from readable text."}
    if medicines:
        return {"level": "limited", "reason": "One medicine-like line was detected."}
    return {"level": "low", "reason": "No medicine-like lines were detected."}
