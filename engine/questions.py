"""
Component 2 — Deterministic Fact-to-Question Lookup Table
Generates follow-up questions from missing facts without using an LLM.
Includes bilingual labels (English and Sinhala).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from engine.schemas import FollowUpQuestion

FACT_QUESTION_MAP: Dict[str, Dict[str, Any]] = {
    "operates_kitchen": {
        "fact": "operates_kitchen",
        "question": "Does the business operate a commercial kitchen or on-site food preparation area?",
        "question_si": "ව්‍යාපාරය පරිශ්‍රය තුළ මුළුතැන්ගෙයක් හෝ ආහාර පිළියෙළ කිරීමේ ස්ථානයක් පවත්වාගෙන යන්නේද?",
        "type": "boolean",
        "options": [True, False],
    },
    "physical_premises": {
        "fact": "physical_premises",
        "question": "Does the business operate from a fixed physical commercial facility or storefront?",
        "question_si": "ව්‍යාපාරය ස්ථිර භෞතික වාණිජ පරිශ්‍රයක පවත්වාගෙන යන්නේද?",
        "type": "boolean",
        "options": [True, False],
    },
    "sells_alcohol": {
        "fact": "sells_alcohol",
        "question": "Does or will the business store, dispense, or retail alcoholic beverages?",
        "question_si": "පරිශ්‍රය තුළ මත්පැන් ගබඩා කිරීම හෝ අලෙවි කිරීම සිදු කරන්නේද?",
        "type": "boolean",
        "options": [True, False],
    },
    "imports_goods": {
        "fact": "imports_goods",
        "question": "Does the business directly import commercial goods, products, or ingredients from overseas?",
        "question_si": "ව්‍යාපාරය විදේශයන්ගෙන් වාණිජ භාණ්ඩ හෝ අමුද්‍රව්‍ය ආනයනය කරන්නේද?",
        "type": "boolean",
        "options": [True, False],
    },
    "handles_waste_oil_or_batteries": {
        "fact": "handles_waste_oil_or_batteries",
        "question": "Does the business store, dismantle, or generate waste engine oil or spent lead-acid batteries?",
        "question_si": "ව්‍යාපාරය භාවිත කළ මෝටර් තෙල් හෝ බැටරි ගබඩා කිරීම හෝ හැසිරවීම කරන්නේද?",
        "type": "boolean",
        "options": [True, False],
    },
    "uses_chemicals_or_cosmetics": {
        "fact": "uses_chemicals_or_cosmetics",
        "question": "Does the salon use chemical cosmetics, hair dyes, bleaches, or skin treatment agents?",
        "question_si": "රූපලාවණ්‍යාගාරය රසායනික ද්‍රව්‍ය, හිසකෙස් සායම් හෝ සම ප්‍රතිකාර ද්‍රව්‍ය භාවිතා කරන්නේද?",
        "type": "boolean",
        "options": [True, False],
    },
    "estimated_turnover_band": {
        "fact": "estimated_turnover_band",
        "question": "What is the projected annual business revenue or turnover tier?",
        "question_si": "ඇස්තමේන්තුගත වාර්ෂික පිරිවැටුම් මට්ටම කුමක්ද?",
        "type": "select",
        "options": ["under_1m", "1m_10m", "10m_50m", "over_50m"],
    },
    "turnover_band": {
        "fact": "turnover_band",
        "question": "What is the projected annual business revenue or turnover tier?",
        "question_si": "ඇස්තමේන්තුගත වාර්ෂික පිරිවැටුම් මට්ටම කුමක්ද?",
        "type": "select",
        "options": ["under_1m", "1m_10m", "10m_50m", "over_50m"],
    },
    "location.local_authority": {
        "fact": "location.local_authority",
        "question": "Which local municipal council or pradeshiya sabha governs your business premises?",
        "question_si": "ඔබගේ ප්‍රදේශය පාලනය වන පළාත් පාලන ආයතනය කුමක්ද?",
        "type": "select",
        "options": [
            "Colombo Municipal Council",
            "Dehiwala-Mount Lavinia Municipal Council",
            "Sri Jayawardenepura Kotte Municipal Council",
            "Moratuwa Municipal Council",
            "Other",
        ],
    },
    "location.province": {
        "fact": "location.province",
        "question": "In which province is your business registered or operating?",
        "question_si": "ඔබගේ ව්‍යාපාරය ලියාපදිංචි කර හෝ ක්‍රියාත්මක වන්නේ කුමන පළාතේද?",
        "type": "select",
        "options": ["Western Province", "Central Province", "Southern Province", "Other"],
    },
    "legal_structure": {
        "fact": "legal_structure",
        "question": "What is the registered legal ownership structure of the business?",
        "question_si": "ව්‍යාපාරයේ ලියාපදිංචි නීතිමය ස්වරූපය කුමක්ද?",
        "type": "select",
        "options": ["sole_proprietorship", "partnership", "private_limited"],
    },
    "employee_count": {
        "fact": "employee_count",
        "question": "How many permanent or contractual employees are employed by the business?",
        "question_si": "ව්‍යාපාරයේ සේවය කරන සේවකයින් ගණන කීයද?",
        "type": "number",
        "options": [],
    },
    # Aliases
    "has_physical_premises": {
        "fact": "physical_premises",
        "question": "Does the business operate from a fixed physical commercial facility or storefront?",
        "question_si": "ව්‍යාපාරය ස්ථිර භෞතික වාණිජ පරිශ්‍රයක පවත්වාගෙන යන්නේද?",
        "type": "boolean",
        "options": [True, False],
    },
    "legal_form": {
        "fact": "legal_structure",
        "question": "What is the registered legal ownership structure of the business?",
        "question_si": "ව්‍යාපාරයේ ලියාපදිංචි නීතිමය ස්වරූපය කුමක්ද?",
        "type": "select",
        "options": ["sole_proprietorship", "partnership", "private_limited"],
    },
    "number_of_employees": {
        "fact": "employee_count",
        "question": "How many permanent or contractual employees are employed by the business?",
        "question_si": "ව්‍යාපාරයේ සේවය කරන සේවකයින් ගණන කීයද?",
        "type": "number",
        "options": [],
    },
    "handles_food": {
        "fact": "handles_food",
        "question": "Does the business prepare, handle, store, or sell food items to the public?",
        "question_si": "ව්‍යාපාරය ආහාර පිළියෙළ කිරීම, හැසිරවීම, ගබඩා කිරීම හෝ විකිණීම සිදු කරන්නේද?",
        "type": "boolean",
        "options": [True, False],
    },
}


def generate_follow_up_questions(missing_facts: List[str]) -> List[Dict[str, Any]]:
    """
    Given a list of missing facts, returns deterministic follow-up questions
    as dictionaries (JSON-serializable) using a static lookup table. No LLM generation is involved.
    """
    questions: List[Dict[str, Any]] = []
    seen: set = set()

    for fact in missing_facts:
        if fact in seen:
            continue
        seen.add(fact)

        mapping = FACT_QUESTION_MAP.get(fact)
        if mapping:
            questions.append({
                "fact": mapping["fact"],
                "question": mapping["question"],
                "question_en": mapping.get("question", ""),
                "question_si": mapping.get("question_si"),
                "type": mapping.get("type", "boolean"),
                "options": mapping.get("options", []),
            })
        else:
            # Deterministic clean fallback for any unmapped fact
            clean_name = fact.replace(".", " ").replace("_", " ").title()
            questions.append({
                "fact": fact,
                "question": f"Please specify information for '{clean_name}'.",
                "question_en": f"Please specify information for '{clean_name}'.",
                "question_si": f"කරුණාකර '{clean_name}' පිළිබඳ තොරතුරු සපයන්න.",
                "type": "text",
                "options": [],
            })

    return questions
