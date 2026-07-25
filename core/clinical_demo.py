from __future__ import annotations

from copy import deepcopy

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
}


RED_FLAGS = {
    "chest pain": "Chest pain can be urgent, especially with sweating, breathlessness, or arm/jaw pain.",
    "breathless": "Breathlessness can need urgent medical assessment.",
    "shortness of breath": "Shortness of breath can need urgent medical assessment.",
    "unconscious": "Unconsciousness is an emergency.",
    "seizure": "Seizure symptoms need prompt medical attention.",
    "severe allergy": "Severe allergy symptoms can become an emergency.",
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
    knowledge = [lookup_medicine(medicine["name"]) for medicine in medicines]
    safety = evaluate_safety(text, medicines)
    result = {
        "status": "complete",
        "language": language,
        "parsed_prescription": parsed,
        "medicine_knowledge": knowledge,
        "safety_review": safety,
        "patient_summary": build_patient_summary(parsed, knowledge, safety),
        "questions_for_doctor": build_questions(parsed, safety),
        "confidence": estimate_confidence(text, medicines),
        "ui_labels": UI_LABELS[language],
    }
    return localize_result(result, language)


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
