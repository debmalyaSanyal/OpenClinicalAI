from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

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
    "dexamethasone": {
        "use": "Corticosteroid used to reduce inflammation in selected conditions.",
        "caution": "Use only as prescribed. Review infection, diabetes, stomach irritation, and steroid side-effect risks with a clinician.",
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
    "stamlo": {
        "use": "Brand commonly containing amlodipine, used for high blood pressure and some angina/heart blood-flow conditions.",
        "caution": "Verify the generic name and strength. Amlodipine can cause dizziness, flushing, or ankle swelling in some people.",
        "source": "DailyMed amlodipine labeling",
        "source_url": "https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=886a7f97-60a4-4206-a6c7-5206069ed487",
    },
    "tazloc": {
        "use": "Brand commonly containing telmisartan, used for high blood pressure and cardiovascular risk reduction in selected patients.",
        "caution": "Verify the generic name and strength. Telmisartan needs extra review in pregnancy, kidney disease, high potassium, or dehydration.",
        "source": "DailyMed telmisartan labeling",
        "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=beaaf383-730f-4411-b5e7-15c32b53a338",
    },
    "atrovas": {
        "use": "Brand commonly containing atorvastatin, used to lower cholesterol and reduce heart attack or stroke risk in selected patients.",
        "caution": "Verify the generic name and strength. Report severe muscle pain, weakness, dark urine, or liver-related symptoms to a clinician.",
        "source": "MedlinePlus atorvastatin",
        "source_url": "https://medlineplus.gov/druginfo/meds/a600045.html",
    },
    "pregabid": {
        "use": "Brand commonly containing pregabalin, used for selected nerve-pain conditions and sometimes seizure-related indications.",
        "caution": "Verify the generic name and strength. Pregabalin can cause sleepiness or dizziness and should not be stopped suddenly without advice.",
        "source": "MedlinePlus pregabalin",
        "source_url": "https://medlineplus.gov/druginfo/meds/a605045.html",
    },
    "lumia": {
        "use": "Likely a vitamin D3/cholecalciferol preparation when written as 60K; used to treat or prevent vitamin D deficiency.",
        "caution": "Verify the exact product. High-dose vitamin D should be taken only as prescribed, especially with kidney disease or high calcium.",
        "source": "MedlinePlus vitamin D deficiency",
        "source_url": "https://medlineplus.gov/vitaminddeficiency.html",
    },
    "primolut-n": {
        "use": "Brand containing norethisterone, used for selected menstrual or hormone-related problems such as irregular/heavy periods when prescribed.",
        "caution": "Verify it is appropriate before use, especially with pregnancy possibility, clot risk, liver disease, or unexplained bleeding.",
        "source": "Australian Commission Primolut-N medicine finder",
        "source_url": "https://www.safetyandquality.gov.au/medicine-finder/primolut-n",
    },
    "lupoxa": {
        "use": "Brand commonly listed as oxaceprol, used for osteoarthritis or rheumatoid-arthritis-related pain and swelling.",
        "caution": "Verify the generic name. Review stomach upset, dizziness, ulcer history, and other pain medicines with a clinician.",
        "source": "Apollo Pharmacy Lupoxa OD",
        "source_url": "https://www.apollopharmacy.in/medicine/lupoxa-od-tablet-10-s",
    },
    "lupoxa od": {
        "use": "Brand commonly listed as oxaceprol, used for osteoarthritis or rheumatoid-arthritis-related pain and swelling.",
        "caution": "Verify the generic name. Review stomach upset, dizziness, ulcer history, and other pain medicines with a clinician.",
        "source": "Apollo Pharmacy Lupoxa OD",
        "source_url": "https://www.apollopharmacy.in/medicine/lupoxa-od-tablet-10-s",
    },
    "collashot c2": {
        "use": "Joint-health supplement containing collagen-related ingredients; commonly marketed for joint pain, stiffness, or cartilage support.",
        "caution": "Treat as a supplement, not a replacement for RA treatment. Verify ingredients if there is allergy, kidney disease, pregnancy, or other medicines.",
        "source": "1mg Collashot C2",
        "source_url": "https://www.1mg.com/otc/collashot-c2-capsule-otc441037",
    },
    "macvestin": {
        "use": "Joint-support/anti-inflammatory supplement product used for osteoarthritis or rheumatoid-arthritis symptom support in some prescriptions.",
        "caution": "Verify the exact formulation and avoid assuming it replaces prescribed RA medicines. Review interactions and stomach issues with a clinician.",
        "source": "MIMS India Macvestin Total",
        "source_url": "https://www.mims.com/india/drug/info/macvestin%20total",
    },
}

PURPOSE_EXPLANATIONS = {
    "htn": "The scanned PURPOSE column says HTN, which usually means hypertension/high blood pressure.",
    "chol": "The scanned PURPOSE column says chol, which usually means cholesterol/lipid control.",
    "ra": "The scanned PURPOSE column says RA, which usually means rheumatoid arthritis.",
    "pain": "The scanned PURPOSE column says pain, so the medicine may have been prescribed for pain control.",
    "menstruation": "The scanned PURPOSE column says menstruation, so the medicine may relate to menstrual bleeding or cycle control.",
    "vitd3": "The scanned PURPOSE column says vitd3, which points to vitamin D3 supplementation.",
    "vit d3": "The scanned PURPOSE column says vit d3, which points to vitamin D3 supplementation.",
    "diabetes": "The scanned PURPOSE column says diabetes, so the medicine may relate to blood sugar care.",
    "dm": "The scanned PURPOSE column says DM, which often means diabetes mellitus.",
}


RED_FLAGS = {
    "chest pain": "Chest pain can be urgent, especially with sweating, breathlessness, or arm/jaw pain.",
    "breathless": "Breathlessness can need urgent medical assessment.",
    "shortness of breath": "Shortness of breath can need urgent medical assessment.",
    "unconscious": "Unconsciousness is an emergency.",
    "seizure": "Seizure symptoms need prompt medical attention.",
    "severe allergy": "Severe allergy symptoms can become an emergency.",
}


LAB_TESTS = {
    "hemoglobin": {"aliases": ["hemoglobin", "haemoglobin", "hb"], "unit": "g/dL", "low": 12.0, "high": 17.5},
    "wbc": {"aliases": ["wbc", "white blood cells", "total leukocyte count", "tlc"], "unit": "10^3/uL", "low": 4.0, "high": 11.0},
    "platelets": {"aliases": ["platelet", "platelets"], "unit": "10^3/uL", "low": 150.0, "high": 450.0},
    "glucose": {"aliases": ["glucose", "blood sugar", "fbs", "fasting glucose"], "unit": "mg/dL", "low": 70.0, "high": 126.0},
    "hba1c": {"aliases": ["hba1c", "hb a1c"], "unit": "%", "low": 4.0, "high": 5.7},
    "creatinine": {"aliases": ["creatinine"], "unit": "mg/dL", "low": 0.6, "high": 1.3},
    "urea": {"aliases": ["urea", "blood urea"], "unit": "mg/dL", "low": 7.0, "high": 20.0},
    "cholesterol": {"aliases": ["total cholesterol", "cholesterol"], "unit": "mg/dL", "low": 0.0, "high": 200.0},
    "ldl": {"aliases": ["ldl"], "unit": "mg/dL", "low": 0.0, "high": 100.0},
    "hdl": {"aliases": ["hdl"], "unit": "mg/dL", "low": 40.0, "high": 999.0, "higher_is_better": True},
    "triglycerides": {"aliases": ["triglycerides", "tg"], "unit": "mg/dL", "low": 0.0, "high": 150.0},
    "tsh": {"aliases": ["tsh"], "unit": "uIU/mL", "low": 0.4, "high": 4.0},
    "alt": {"aliases": ["alt", "sgpt"], "unit": "U/L", "low": 0.0, "high": 45.0},
    "ast": {"aliases": ["ast", "sgot"], "unit": "U/L", "low": 0.0, "high": 40.0},
}
REFERENCE_PROFILES = {
    "generic": {
        "name": "Generic adult demo ranges",
        "overrides": {},
    },
    "india": {
        "name": "India-oriented adult demo ranges",
        "overrides": {
            "ldl": {"high": 130.0},
            "hdl": {"low": 40.0},
        },
    },
}


LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "es": "Spanish",
}

UI_LABELS = {
    "en": {
        "confidence": "Confidence",
        "dose": "Dose",
        "frequency": "Frequency",
        "duration": "Duration",
        "timing_explanation": "Timing meaning",
        "use": "Use",
        "caution": "Caution",
        "risk": "Risk",
        "no_medicines": "No medicines were confidently detected.",
        "no_safety_flags": "No urgent demo safety flags detected.",
        "no_questions": "No questions generated.",
    },
    "hi": {
        "confidence": "विश्वास स्तर",
        "dose": "खुराक",
        "frequency": "कब लेना है",
        "duration": "अवधि",
        "timing_explanation": "शॉर्ट फॉर्म का अर्थ",
        "use": "उपयोग",
        "caution": "सावधानी",
        "risk": "जोखिम",
        "no_medicines": "कोई दवा भरोसेमंद तरीके से नहीं मिली।",
        "no_safety_flags": "डेमो नियमों में कोई तुरंत चेतावनी नहीं मिली।",
        "no_questions": "कोई सवाल नहीं बना।",
    },
    "bn": {
        "confidence": "নিশ্চয়তার মাত্রা",
        "dose": "ডোজ",
        "frequency": "কখন খাবেন",
        "duration": "সময়কাল",
        "timing_explanation": "সংক্ষিপ্ত রূপের অর্থ",
        "use": "ব্যবহার",
        "caution": "সতর্কতা",
        "risk": "ঝুঁকি",
        "no_medicines": "নিশ্চিতভাবে কোনো ওষুধ শনাক্ত হয়নি।",
        "no_safety_flags": "ডেমো নিয়মে জরুরি সতর্কতা পাওয়া যায়নি।",
        "no_questions": "কোনো প্রশ্ন তৈরি হয়নি।",
    },
    "es": {
        "confidence": "Confianza",
        "dose": "Dosis",
        "frequency": "Frecuencia",
        "duration": "Duración",
        "timing_explanation": "Significado de la abreviatura",
        "use": "Uso",
        "caution": "Precaución",
        "risk": "Riesgo",
        "no_medicines": "No se detectaron medicamentos con confianza.",
        "no_safety_flags": "No se detectaron alertas urgentes en esta demo.",
        "no_questions": "No se generaron preguntas.",
    },
}

PHRASE_TRANSLATIONS = {
    "hi": {
        "once daily": "दिन में एक बार",
        "twice daily": "दिन में दो बार",
        "three times daily": "दिन में तीन बार",
        "four times daily": "दिन में चार बार",
        "at bedtime": "सोने से पहले",
        "when needed": "जरूरत होने पर",
        "before food": "खाने से पहले",
        "after food": "खाने के बाद",
        "morning and night": "सुबह और रात",
        "morning, afternoon, and night": "सुबह, दोपहर और रात",
        "morning": "सुबह",
        "night": "रात",
        "routine": "सामान्य",
        "high": "उच्च",
        "medium": "मध्यम",
        "limited": "सीमित",
        "low": "कम",
        "Pain and fever medicine.": "दर्द और बुखार की दवा।",
        "Corticosteroid used to reduce inflammation in selected conditions.": "कुछ स्थितियों में सूजन कम करने के लिए उपयोग की जाने वाली स्टेरॉयड दवा।",
        "Medicine detected, but no built-in explanation is available in this demo.": "दवा मिली, लेकिन इस डेमो में इसकी पूरी जानकारी उपलब्ध नहीं है।",
        "Verify the medicine name, dose, and instructions with a clinician or pharmacist.": "दवा का नाम, खुराक और निर्देश डॉक्टर या फार्मासिस्ट से जरूर मिलाएं।",
    },
    "bn": {
        "once daily": "দিনে একবার",
        "twice daily": "দিনে দুবার",
        "three times daily": "দিনে তিনবার",
        "four times daily": "দিনে চারবার",
        "at bedtime": "ঘুমানোর আগে",
        "when needed": "প্রয়োজনে",
        "before food": "খাবারের আগে",
        "after food": "খাবারের পরে",
        "morning and night": "সকাল ও রাতে",
        "morning, afternoon, and night": "সকাল, দুপুর ও রাতে",
        "morning": "সকালে",
        "night": "রাতে",
        "routine": "সাধারণ",
        "high": "উচ্চ",
        "medium": "মাঝারি",
        "limited": "সীমিত",
        "low": "কম",
        "Pain and fever medicine.": "ব্যথা ও জ্বরের ওষুধ।",
        "Corticosteroid used to reduce inflammation in selected conditions.": "কিছু অবস্থায় প্রদাহ কমাতে ব্যবহৃত স্টেরয়েড ওষুধ।",
        "Medicine detected, but no built-in explanation is available in this demo.": "ওষুধ শনাক্ত হয়েছে, তবে এই ডেমোতে বিস্তারিত ব্যাখ্যা নেই।",
        "Verify the medicine name, dose, and instructions with a clinician or pharmacist.": "ওষুধের নাম, ডোজ ও নির্দেশনা ডাক্তার বা ফার্মাসিস্টের সঙ্গে মিলিয়ে নিন।",
    },
    "es": {
        "once daily": "una vez al día",
        "twice daily": "dos veces al día",
        "three times daily": "tres veces al día",
        "four times daily": "cuatro veces al día",
        "at bedtime": "a la hora de dormir",
        "when needed": "cuando sea necesario",
        "before food": "antes de comer",
        "after food": "después de comer",
        "morning and night": "mañana y noche",
        "morning, afternoon, and night": "mañana, tarde y noche",
        "morning": "mañana",
        "night": "noche",
        "routine": "rutina",
        "high": "alto",
        "medium": "medio",
        "limited": "limitado",
        "low": "bajo",
        "Pain and fever medicine.": "Medicamento para dolor y fiebre.",
        "Corticosteroid used to reduce inflammation in selected conditions.": "Corticosteroide usado para reducir inflamación en algunas condiciones.",
        "Medicine detected, but no built-in explanation is available in this demo.": "Medicamento detectado, pero esta demo no tiene una explicación incorporada.",
        "Verify the medicine name, dose, and instructions with a clinician or pharmacist.": "Verifique el nombre, la dosis y las instrucciones con un profesional de salud o farmacéutico.",
    },
}


def analyze_prescription_text(text: str, language: str = "en") -> dict:
    language = normalize_language(language)
    parsed = parse_prescription_text(text)
    medicines = parsed["medicines"]
    knowledge = [lookup_medicine(medicine["name"], medicine.get("purpose")) for medicine in medicines]
    safety = evaluate_safety(text, medicines)
    clinical_values = extract_lab_tests(text, "generic")
    patient_summary = build_patient_summary(parsed, knowledge, safety)
    if clinical_values:
        names = ", ".join(f"{value['name']} {value['value']:g} {value['unit']}" for value in clinical_values)
        patient_summary += f" Also detected clinical value(s): {names}."
    result = {
        "status": "complete",
        "document_type": "prescription",
        "language": language,
        "parsed_prescription": parsed,
        "clinical_values": clinical_values,
        "medicine_knowledge": knowledge,
        "safety_review": safety,
        "patient_summary": patient_summary,
        "questions_for_doctor": build_questions(parsed, safety),
        "confidence": estimate_confidence(text, medicines),
        "ui_labels": UI_LABELS[language],
    }
    return localize_result(result, language)


def analyze_lab_report_text(text: str, language: str = "en", reference_profile: str = "generic") -> dict:
    language = normalize_language(language)
    reference_profile = normalize_reference_profile(reference_profile)
    tests = extract_lab_tests(text, reference_profile)
    abnormal = [test for test in tests if test["status"] in {"low", "high"}]
    summary = build_lab_summary(tests, abnormal)
    return {
        "status": "complete",
        "document_type": "lab_report",
        "language": language,
        "reference_profile": REFERENCE_PROFILES[reference_profile]["name"],
        "ocr_text": text.strip(),
        "lab_tests": tests,
        "patient_summary": summary,
        "safety_review": build_lab_safety_review(abnormal),
        "questions_for_doctor": build_lab_questions(abnormal),
        "confidence": {
            "level": "medium" if len(tests) >= 2 else "limited" if tests else "low",
            "reason": "Lab values were extracted from readable report text." if tests else "No known lab values were detected.",
        },
        "ui_labels": UI_LABELS[language],
    }


def answer_lab_report_question(
    text: str,
    question: str,
    language: str = "en",
    reference_profile: str = "generic",
) -> dict:
    analysis = analyze_lab_report_text(text, language, reference_profile)
    lowered = question.lower()
    tests = analysis["lab_tests"]
    abnormal = [test for test in tests if test["status"] in {"low", "high"}]
    if not text.strip():
        answer = "Please analyze or paste a blood report first."
    elif is_diet_question(lowered):
        answer = build_lab_diet_answer(lowered, tests, abnormal, analysis["reference_profile"])
    elif any(word in lowered for word in ("high", "low", "abnormal", "problem", "bad", "danger", "risk")):
        answer = build_lab_abnormal_answer(abnormal)
    elif any(word in lowered for word in ("value", "level", "result", "how much", "reading")):
        answer = build_lab_values_answer(tests)
    elif any(word in lowered for word in ("mean", "meaning", "explain", "what is")):
        answer = build_lab_meaning_answer(tests)
    else:
        answer = analysis["patient_summary"]
    return {
        "status": "complete",
        "language": analysis["language"],
        "question": question,
        "answer": answer,
        "safety_note": "",
    }


def answer_document_question(
    text: str,
    question: str,
    document_type: str = "prescription",
    language: str = "en",
    reference_profile: str = "generic",
) -> dict:
    if document_type == "lab_report":
        return answer_lab_report_question(text, question, language, reference_profile)
    return answer_prescription_question(text, question, language)


def answer_prescription_question(text: str, question: str, language: str = "en") -> dict:
    analysis = analyze_prescription_text(text, language)
    lowered = question.lower()
    medicines = analysis["parsed_prescription"]["medicines"]
    knowledge = analysis["medicine_knowledge"]
    include_safety_note = False
    if not text.strip():
        answer = "Please analyze or paste a prescription first, then ask a question about it."
    elif is_food_timing_question(lowered):
        answer = build_food_timing_chat_answer(medicines)
    elif is_dose_question(lowered):
        answer = build_dose_chat_answer(medicines)
    elif any(word in lowered for word in ("emergency", "urgent", "danger", "safe", "warning", "risk")):
        answer = build_safety_chat_answer(analysis)
        include_safety_note = True
    elif any(word in lowered for word in ("when", "time", "timing", "od", "bd", "tds", "hs", "sos", "prn", "ac", "pc")):
        answer = build_timing_chat_answer(medicines)
    elif any(word in lowered for word in ("use", "for", "why", "purpose", "medicine")):
        answer = build_medicine_chat_answer(medicines, knowledge)
    else:
        answer = build_general_chat_answer(analysis)
    return {
        "status": "complete",
        "language": analysis["language"],
        "question": question,
        "answer": localize_chat_answer(answer, analysis["language"]),
        "safety_note": analysis["safety_review"]["safe_use_note"] if include_safety_note else "",
    }


def extract_lab_tests(text: str, reference_profile: str = "generic") -> list[dict]:
    normalized = text.replace("|", " ")
    found: list[dict] = []
    seen: set[str] = set()
    for name, config in LAB_TESTS.items():
        config = apply_reference_profile(name, config, reference_profile)
        for alias in config["aliases"]:
            pattern = rf"\b{re.escape(alias)}\b\s*[:\-]?\s*(\d+(?:\.\d+)?)"
            match = re.search(pattern, normalized, re.I)
            if match and name not in seen:
                value = float(match.group(1))
                found.append(build_lab_result(name, value, config))
                seen.add(name)
                break
    return found


def build_lab_result(name: str, value: float, config: dict) -> dict:
    low = config["low"]
    high = config["high"]
    if config.get("higher_is_better"):
        status = "low" if value < low else "normal"
    elif value < low:
        status = "low"
    elif value > high:
        status = "high"
    else:
        status = "normal"
    return {
        "name": format_lab_name(name),
        "value": value,
        "unit": config["unit"],
        "reference_range": f"{low:g}-{high:g} {config['unit']}",
        "status": status,
        "explanation": lab_explanation(name, status),
    }


def normalize_reference_profile(reference_profile: str) -> str:
    return reference_profile if reference_profile in REFERENCE_PROFILES else "generic"


def format_lab_name(name: str) -> str:
    if name in {"hba1c", "wbc", "ldl", "hdl", "tsh", "alt", "ast"}:
        return name.upper()
    return name.title()


def apply_reference_profile(name: str, config: dict, reference_profile: str) -> dict:
    adjusted = dict(config)
    adjusted.update(REFERENCE_PROFILES[reference_profile]["overrides"].get(name, {}))
    return adjusted


def lab_explanation(name: str, status: str) -> str:
    if status == "normal":
        return "Within the built-in demo reference range."
    if name in {"hemoglobin", "wbc", "platelets"}:
        return "CBC value is outside the built-in demo range. Review with a clinician."
    if name in {"glucose", "hba1c"}:
        return "Blood sugar marker is outside the built-in demo range. Review diabetes risk/control."
    if name in {"creatinine", "urea"}:
        return "Kidney marker is outside the built-in demo range. Review hydration, kidney function, and medicines."
    if name in {"alt", "ast"}:
        return "Liver enzyme is outside the built-in demo range. Review with a clinician."
    return "Value is outside the built-in demo reference range."


def build_lab_summary(tests: list[dict], abnormal: list[dict]) -> str:
    if not tests:
        return "No known blood report values were detected. Paste clearer report text or upload a sharper image."
    summary = f"Detected {len(tests)} lab value(s)."
    if abnormal:
        names = ", ".join(f"{test['name']} {test['status']}" for test in abnormal)
        summary += f" Values needing review: {names}."
    else:
        summary += " No values were outside the built-in demo ranges."
    return summary


def build_lab_safety_review(abnormal: list[dict]) -> dict:
    flags = []
    for test in abnormal:
        flags.append({"type": "lab_range", "message": f"{test['name']} is {test['status']} at {test['value']:g} {test['unit']}."})
    return {
        "risk_level": "review_needed" if flags else "routine",
        "flags": flags,
        "safe_use_note": "Lab reports must be interpreted with symptoms, age, sex, medical history, and clinician advice.",
    }


def build_lab_questions(abnormal: list[dict]) -> list[str]:
    questions = [
        "Do these values match my age, sex, symptoms, and medical history?",
        "Do I need a repeat test or follow-up test?",
    ]
    if abnormal:
        questions.insert(0, "Which abnormal values need medical follow-up?")
    return questions


def build_lab_abnormal_answer(abnormal: list[dict]) -> str:
    if not abnormal:
        return "No abnormal values were detected by the built-in demo ranges."
    return " ".join(f"{test['name']}: {test['value']:g} {test['unit']} is {test['status']}." for test in abnormal)


def build_lab_values_answer(tests: list[dict]) -> str:
    if not tests:
        return "No lab values were detected yet."
    return " ".join(f"{test['name']}: {test['value']:g} {test['unit']} ({test['status']})." for test in tests)


def build_lab_meaning_answer(tests: list[dict]) -> str:
    if not tests:
        return "No known lab test was detected to explain."
    return " ".join(f"{test['name']}: {test['explanation']}" for test in tests)


def is_diet_question(question: str) -> bool:
    return any(
        word in question
        for word in (
            "eat",
            "have",
            "drink",
            "mango",
            "sweet",
            "sugar",
            "juice",
            "rice",
            "lunch",
            "dinner",
            "breakfast",
            "fruit",
        )
    )


def build_lab_diet_answer(question: str, tests: list[dict], abnormal: list[dict], profile_name: str) -> str:
    high_sugar = [
        test for test in tests if test["name"] in {"Glucose", "HBA1C"} and test["status"] == "high"
    ]
    sugary_food = any(word in question for word in ("mango", "sweet", "sugar", "juice"))
    abnormal_text = build_lab_abnormal_answer(abnormal) if abnormal else "No abnormal values detected."
    if high_sugar and sugary_food:
        values = ", ".join(f"{test['name']} {test['value']:g} {test['unit']}" for test in high_sugar)
        return (
            f"Negative. Your sugar value is high ({values}) as per {profile_name}, "
            f"so avoid mangoes/sugary foods for now. Other abnormal values: {abnormal_text}"
        )
    if high_sugar:
        values = ", ".join(f"{test['name']} {test['value']:g} {test['unit']}" for test in high_sugar)
        return (
            f"Be careful. Your sugar value is high ({values}) as per {profile_name}. "
            f"Prefer low-sugar, high-fiber meals. Other abnormal values: {abnormal_text}"
        )
    return "No high sugar marker was detected in the report by the demo rules. Keep portions sensible and follow your clinician's diet advice."


def lookup_medicine(name: str, purpose: str | None = None) -> dict:
    key = name.lower()
    info = MEDICINE_KNOWLEDGE.get(key) or lookup_partial_medicine_key(key)
    info = info or lookup_remote_medicine(name)
    purpose_note = purpose_explanation(purpose)
    if info:
        info = dict(info)
        if purpose_note and purpose_note not in info["use"]:
            info["use"] = f"{info['use']} {purpose_note}"
    else:
        info = {
            "use": purpose_note or "Medicine detected, but no built-in explanation is available in this demo.",
            "caution": "Verify the medicine name, dose, and instructions with a clinician or pharmacist.",
        }
    return {"name": name, **info}


def lookup_partial_medicine_key(key: str) -> dict | None:
    for known_key, info in MEDICINE_KNOWLEDGE.items():
        if known_key in key or key in known_key:
            return info
    return None


@lru_cache(maxsize=256)
def lookup_remote_medicine(name: str) -> dict | None:
    for candidate in medicine_lookup_candidates(name):
        info = lookup_openfda_label(candidate)
        if info:
            return info
    return None


def medicine_lookup_candidates(name: str) -> tuple[str, ...]:
    cleaned = re.sub(r"\b(?:cr|sr|er|xr|od|bd|tds|tablet|tab|capsule|cap)\b", " ", name, flags=re.I)
    cleaned = re.sub(r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|iu|k)?\b", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    candidates = [name.strip(), cleaned]
    if cleaned:
        candidates.append(cleaned.split()[0])
    unique = []
    for candidate in candidates:
        candidate = candidate.strip(" -:")
        if candidate and candidate.lower() not in {item.lower() for item in unique}:
            unique.append(candidate)
    return tuple(unique)


def lookup_openfda_label(name: str) -> dict | None:
    query = f'openfda.brand_name:"{name}" OR openfda.generic_name:"{name}"'
    url = f"https://api.fda.gov/drug/label.json?search={quote(query)}&limit=1"
    try:
        request = Request(url, headers={"User-Agent": "OpenClinicalAI demo medicine lookup"})
        with urlopen(request, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    results = payload.get("results") or []
    if not results:
        return None
    label = results[0]
    indication = first_label_text(label, "indications_and_usage") or first_label_text(label, "purpose")
    if not indication:
        return None
    openfda = label.get("openfda") or {}
    generic = first_list_value(openfda.get("generic_name"))
    brand = first_list_value(openfda.get("brand_name"))
    display = generic or brand or name
    return {
        "use": f"Public FDA label data for {display} says it is used for: {brief_label_text(indication)}",
        "caution": "This is a live public-label lookup. Verify the exact brand/generic, dose, country-specific product, and patient suitability with a clinician or pharmacist.",
        "source": "openFDA drug label",
        "source_url": url,
    }


def first_label_text(label: dict, field: str) -> str:
    values = label.get(field) or []
    return first_list_value(values)


def first_list_value(values: object) -> str:
    if isinstance(values, list) and values:
        return str(values[0]).strip()
    if isinstance(values, str):
        return values.strip()
    return ""


def brief_label_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    brief = " ".join(sentences[:2]).strip()
    return brief[:520].rstrip(" ,;:") + ("..." if len(brief) > 520 else "")


def purpose_explanation(purpose: str | None) -> str:
    if not purpose:
        return ""
    return PURPOSE_EXPLANATIONS.get(purpose.lower(), f"The scanned PURPOSE column says {purpose}.")


def build_medicine_chat_answer(medicines: list[dict], knowledge: list[dict]) -> str:
    if not medicines:
        return "I could not confidently detect medicines from the prescription text."
    parts = []
    for medicine, info in zip(medicines, knowledge):
        parts.append(f"{medicine['name']}: {info['use']}")
    return " ".join(parts)


def build_timing_chat_answer(medicines: list[dict]) -> str:
    if not medicines:
        return "No medicine timings were detected yet."
    parts = []
    for medicine in medicines:
        frequency = medicine.get("frequency") or "timing not detected"
        explanation = medicine.get("frequency_explanation") or "No abbreviation explanation detected."
        parts.append(f"{medicine['name']}: {frequency}. {explanation}")
    return " ".join(parts)


def build_dose_chat_answer(medicines: list[dict]) -> str:
    if not medicines:
        return "No medicine doses were detected yet."
    parts = []
    for medicine in medicines:
        duration = f" for {medicine['duration']}" if medicine.get("duration") else ""
        parts.append(f"{medicine['name']}: {medicine.get('dose') or 'dose not detected'}{duration}.")
    return " ".join(parts)


def build_food_timing_chat_answer(medicines: list[dict]) -> str:
    if not medicines:
        return "No medicine food timing was detected yet."
    parts = []
    for medicine in medicines:
        instruction = medicine.get("instruction", "").lower()
        name = medicine["name"]
        if " ac" in f" {instruction}" or "before food" in instruction:
            parts.append(f"{name}: take before food.")
        elif " pc" in f" {instruction}" or "after food" in instruction:
            parts.append(f"{name}: take after food.")
        else:
            parts.append(f"{name}: the prescription does not say before or after food.")
    return " ".join(parts)


def build_safety_chat_answer(analysis: dict) -> str:
    flags = analysis["safety_review"]["flags"]
    if not flags:
        return "No urgent demo safety flags were detected. Still verify the prescription with a clinician or pharmacist."
    return " ".join(flag["message"] for flag in flags)


def build_general_chat_answer(analysis: dict) -> str:
    medicines = analysis["parsed_prescription"]["medicines"]
    if medicines:
        names = ", ".join(medicine["name"] for medicine in medicines)
        return f"I detected: {names}. Ask me about dose, timing, food timing, use, or safety."
    return "I could not detect a medicine clearly. Please edit the OCR text and try again."


def is_food_timing_question(question: str) -> bool:
    return any(word in question for word in ("food", "meal", "breakfast", "lunch", "dinner", "after eating", "before eating"))


def is_dose_question(question: str) -> bool:
    return any(word in question for word in ("dose", "dosage", "strength", "mg", "ml", "how much", "amount", "quantity"))


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


def normalize_language(language: str) -> str:
    return language if language in LANGUAGE_NAMES else "en"


def localize_result(result: dict, language: str) -> dict:
    if language == "en":
        return result
    localized = deepcopy(result)
    localized["patient_summary"] = build_localized_summary(localized, language)
    localized["questions_for_doctor"] = build_localized_questions(localized, language)
    localized["confidence"]["level"] = translate(localized["confidence"]["level"], language)
    localized["safety_review"]["risk_level"] = translate(localized["safety_review"]["risk_level"], language)
    localized["safety_review"]["safe_use_note"] = localized_safe_use_note(language)
    for medicine in localized["parsed_prescription"]["medicines"]:
        if medicine.get("frequency"):
            medicine["frequency"] = translate(medicine["frequency"], language)
        if medicine.get("frequency_explanation"):
            medicine["frequency_explanation"] = localize_frequency_explanation(medicine, language)
    for item in localized["medicine_knowledge"]:
        item["use"] = translate(item["use"], language)
        item["caution"] = translate(item["caution"], language)
    return localized


def translate(value: str, language: str) -> str:
    return PHRASE_TRANSLATIONS.get(language, {}).get(value, value)


def build_localized_summary(result: dict, language: str) -> str:
    medicines = result["parsed_prescription"]["medicines"]
    if not medicines:
        return UI_LABELS[language]["no_medicines"]
    names = ", ".join(medicine["name"] for medicine in medicines)
    if language == "hi":
        return f"{len(medicines)} दवा मिली: {names}. सभी खुराक और समय मूल पर्चे से जरूर मिलाएं।"
    if language == "bn":
        return f"{len(medicines)}টি ওষুধ শনাক্ত হয়েছে: {names}. সব ডোজ ও সময় মূল প্রেসক্রিপশনের সঙ্গে মিলিয়ে নিন।"
    if language == "es":
        return f"Se detectaron {len(medicines)} medicamento(s): {names}. Verifique todas las dosis y horarios con la receta original."
    return result["patient_summary"]


def build_localized_questions(result: dict, language: str) -> list[str]:
    if language == "hi":
        return [
            "क्या दवा का नाम और ताकत सही पढ़ी गई है?",
            "हर दवा भोजन से पहले या बाद में कब लेनी है?",
            "कौन से दुष्प्रभावों पर ध्यान देना चाहिए?",
        ]
    if language == "bn":
        return [
            "ওষুধের নাম ও শক্তি ঠিকভাবে পড়া হয়েছে কি?",
            "প্রতিটি ওষুধ খাবারের আগে না পরে কখন খাবেন?",
            "কোন পার্শ্বপ্রতিক্রিয়ার দিকে খেয়াল রাখতে হবে?",
        ]
    if language == "es":
        return [
            "¿Los nombres y concentraciones de los medicamentos se leyeron correctamente?",
            "¿Cuándo debe tomarse cada medicamento con respecto a la comida?",
            "¿Qué efectos secundarios debo vigilar?",
        ]
    return result["questions_for_doctor"]


def localized_safe_use_note(language: str) -> str:
    if language == "hi":
        return "डॉक्टर की सलाह के बिना दवा शुरू, बंद या बदलें नहीं।"
    if language == "bn":
        return "যোগ্য চিকিৎসকের পরামর্শ ছাড়া ওষুধ শুরু, বন্ধ বা পরিবর্তন করবেন না।"
    if language == "es":
        return "No empiece, suspenda ni cambie medicamentos sin un profesional de salud calificado."
    return "Do not start, stop, or change medicines without a qualified medical professional."


def localize_chat_answer(answer: str, language: str) -> str:
    return answer


def localize_frequency_explanation(medicine: dict, language: str) -> str:
    abbreviation = medicine.get("frequency_abbreviation")
    frequency = medicine.get("frequency")
    if language == "hi":
        return f"{abbreviation} का अर्थ है: {frequency}."
    if language == "bn":
        return f"{abbreviation} এর অর্থ: {frequency}."
    if language == "es":
        return f"{abbreviation} significa: {frequency}."
    return medicine.get("frequency_explanation", "")
