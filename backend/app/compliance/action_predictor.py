"""
ML-Driven Action Guidance Predictor Module
Predicts concrete institutional authority, required licences, procedural steps,
and required documents for an SME profile and for individual legal rules/policies.
"""

import os
import json
import logging
import re
from typing import Dict, Any, List, Optional
import joblib

logger = logging.getLogger("ActionPredictor")

MODEL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "action_guidance_model")
)
PIPELINE_PATH = os.path.join(MODEL_DIR, "action_guidance_pipeline.joblib")
KNOWLEDGE_PATH = os.path.join(MODEL_DIR, "action_knowledge_index.json")

_pipeline = None
_knowledge_index: Dict[str, Any] = {}

# Purpose explanations grounded in Sri Lankan statutory frameworks
RULE_PURPOSE_EXPLANATIONS = {
    "food_business": (
        "Regulates food premises hygiene, sanitation standards, and food-handler medical fitness "
        "before preparing, handling, or selling food items to the public."
    ),
    "environmental_waste": (
        "Regulates industrial emissions, waste disposal, effluent treatment, and environmental clearances "
        "to prevent environmental pollution under the Central Environmental Authority."
    ),
    "business_registration": (
        "Establishes legal identity and commercial entity registration for sole proprietors, partnerships, "
        "or companies, required before opening business bank accounts or issuing commercial invoices."
    ),
    "vehicle_repair_motor_trade": (
        "Regulates automotive garage operations, vehicle modifications, spare parts retail, and "
        "waste oil disposal under local council by-laws and motor traffic guidelines."
    ),
    "cosmetics_salon": (
        "Regulates cosmetic chemical application, skin/hair chemical safety, practitioner sanitation, "
        "and equipment sterilization standards under NMRA and Municipal Health by-laws."
    ),
    "data_protection_digital": (
        "Regulates lawful processing, storage, and confidentiality of customer personal data, "
        "online orders, and employee records under the Personal Data Protection Act No. 9 of 2022."
    ),
}


def _load_artifacts(force_reload: bool = False):
    global _pipeline, _knowledge_index
    if force_reload or _pipeline is None:
        if os.path.exists(PIPELINE_PATH):
            try:
                _pipeline = joblib.load(PIPELINE_PATH)
                logger.info("Action guidance pipeline loaded successfully.")
            except Exception as exc:
                logger.error("Failed to load action guidance pipeline: %s", exc)

    if force_reload or not _knowledge_index:
        if os.path.exists(KNOWLEDGE_PATH):
            try:
                with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                    _knowledge_index = json.load(f)
                logger.info("Action knowledge index loaded successfully.")
            except Exception as exc:
                logger.error("Failed to load action knowledge index: %s", exc)


def predict_action_for_rule(
    rule_title: str,
    source_id: str = "",
    excerpt: str = "",
    business_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Predicts:
    1. 'මේ නීතියෙන් වෙන්නේ මොකක්ද?' (Rule Purpose)
    2. 'යන්න ඕනෙ ස්ථානය / කාර්යාලය කොහෙද?' (Where to Go / Target Authority & Office)
    3. 'ගත යුතු පියවර / බලපත්‍රය කුමක්ද?' (Required Action & Documents)
    4. 'පියවරෙන් පියවර උපදෙස්' (Procedural Steps)
    grounded in Western Province institutional structures.
    """
    _load_artifacts()
    business_context = business_context or {}

    b_type = str(business_context.get("business_type") or business_context.get("sector") or "")
    
    loc = business_context.get("location")
    if isinstance(loc, dict):
        district = str(loc.get("district") or "Colombo")
    elif isinstance(business_context.get("district"), str) and business_context.get("district"):
        district = str(business_context.get("district"))
    elif isinstance(loc, str) and loc:
        district = loc
    else:
        district = "Colombo"

    # Default to Western Province district if not Colombo/Gampaha/Kalutara
    if district not in ["Colombo", "Gampaha", "Kalutara"]:
        district = "Colombo"

    rule_text = f"{rule_title} {source_id} {excerpt}".lower()

    # Rule-specific query aligned with trained feature format
    query = (
        f"Rules & Legal Sources: {rule_title}. "
        f"Business Type: {b_type}. "
        f"Scale: micro. "
        f"District: {district}. "
        f"Physical Premises: True. "
        f"Context: {rule_title}. "
        f"Activity: {rule_title}. "
        f"Inquiry: What authority, office, documents, and steps are required for {rule_title}?"
    )

    predicted_action = None

    # First check explicit domain keywords from the rule title/act itself:
    if any(w in rule_text for w in ["environment", "epl", "waste", "pollution", "47 of 1980", "153316", "prescribed activities", "cea"]):
        predicted_action = "VERIFY_ENVIRONMENTAL_APPLICABILITY"
    elif any(w in rule_text for w in ["food", "hygiene", "food control", "lunch sheet", "polystyrene", "polythene", "restaurant", "bakery", "kitchen"]):
        predicted_action = "VERIFY_FOOD_PREMISES_REQUIREMENTS"
    elif any(w in rule_text for w in ["motor", "traffic", "vehicle", "garage", "garaj", "spare part", "dmt"]):
        predicted_action = "VERIFY_MOTOR_TRADE_PATHWAY"
    elif any(w in rule_text for w in ["salon", "cosmetic", "hair", "beauty", "nmra"]):
        predicted_action = "DISTINGUISH_SALON_VS_PRODUCT_APPROVAL"
    elif any(w in rule_text for w in ["data", "privacy", "protection", "digital", "dpa"]):
        predicted_action = "ASSESS_DATA_PROTECTION_DUTIES"
    elif any(w in rule_text for w in ["business name", "companies act", "eroc", "incorporation", "statute 1990"]):
        predicted_action = "CONFIRM_REGISTRATION_PATHWAY"

    # If not matched by statutory keywords, use champion ML pipeline
    if not predicted_action and _pipeline is not None:
        try:
            predicted_action = _pipeline.predict([query])[0]
        except Exception as exc:
            logger.warning("Pipeline prediction error for rule %s: %s", rule_title, exc)

    if not predicted_action:
        predicted_action = "CONFIRM_REGISTRATION_PATHWAY"

    action_data = _knowledge_index.get(predicted_action, {})
    category = action_data.get("category", "business_registration")
    purpose = RULE_PURPOSE_EXPLANATIONS.get(
        category,
        f"Statutory compliance requirement applicable to commercial activities under {rule_title}."
    )

    # Concrete target authority from Western Province dataset
    target_auth = action_data.get("target_authority") or "Relevant Competent Local Authority"

    # District-specific Western Province office routing
    wp_office_by_cat = {
        "business_registration": f"Divisional Secretariat ({district}) / Registrar of Companies (eROC), Colombo 10",
        "food_business": f"Local Authority Health Department (CMC / Municipal / Urban Council / Pradeshiya Sabha) & MOH Office ({district})",
        "environmental_waste": f"Central Environmental Authority (CEA Head Office Battaramulla / {district} District Office)",
        "vehicle_repair_motor_trade": f"Department of Motor Traffic (Werahera / Narahenpita) & Local Council Trade Unit ({district})",
        "cosmetics_salon": f"National Medicines Regulatory Authority (NMRA Colombo 10) & Local Council Health Dept ({district})",
        "data_protection_digital": "Data Protection Authority of Sri Lanka (DPA SL), Colombo",
    }
    office_loc = wp_office_by_cat.get(category, action_data.get("office_location", f"District Secretariat / Local Authority ({district})"))


    return {
        "rule_title": rule_title,
        "category": category,
        "predicted_action_type": predicted_action,
        "rule_purpose": purpose,
        "where_to_go": target_auth,
        "office_location": office_loc,
        "action_needed": action_data.get(
            "required_action_name",
            f"Registration / Clearance under {rule_title}"
        ),
        "action_urgency": action_data.get("action_urgency", "Prior to commercial operations"),
        "required_documents": action_data.get("required_documents", [
            "National Identity Card (NIC) / Business Registration Certificate",
            "Proof of premises (Lease Agreement or Title Deed)",
            "Official Application Form with prescribed processing fee"
        ]),
        "procedural_steps": action_data.get("procedural_steps", [
            "Step 1: Obtain official prescribed application form from the responsible office.",
            "Step 2: Compile necessary premises proofs, layout sketch, and identification.",
            "Step 3: Submit application for officer inspection / clearance.",
            "Step 4: Pay regulatory inspection fees and collect official licence / certificate."
        ]),
    }


def predict_action_roadmap(business_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Takes business profile attributes, runs the trained ML action guidance model,
    and returns a structured procedural action roadmap for the overall business.
    """
    _load_artifacts()

    if _pipeline is None or not _knowledge_index:
        logger.warning("Action guidance model or knowledge index not loaded.")
        return None

    b_type = str(business_context.get("business_type") or business_context.get("sector") or "general_sme")
    b_scale = str(business_context.get("business_scale") or business_context.get("business_size") or "small")
    district = str(business_context.get("district") or business_context.get("location") or "Colombo")
    premises = str(bool(business_context.get("has_physical_premises", True)))
    stage = str(business_context.get("business_stage") or "new business")
    
    products = business_context.get("products_services") or []
    prod_str = ", ".join(products) if isinstance(products, list) else str(products)

    composite_text = (
        f"Business Type: {b_type}. "
        f"Scale: {b_scale}. "
        f"District: {district}. "
        f"Physical Premises: {premises}. "
        f"Context: {stage}. "
        f"Activity: {prod_str}. "
        f"Inquiry: I operate a {b_type} in {district} and need to know the required action, authority, and documents."
    )

    try:
        predicted_action = _pipeline.predict([composite_text])[0]
        action_data = _knowledge_index.get(predicted_action)

        if not action_data:
            for act_key, data in _knowledge_index.items():
                if b_type in act_key.lower():
                    action_data = data
                    predicted_action = act_key
                    break

        if not action_data:
            action_data = list(_knowledge_index.values())[0]

        return {
            "model_status": "active",
            "predicted_action_type": predicted_action,
            "category": action_data.get("category", ""),
            "target_authority": action_data.get("target_authority", "Relevant Competent Authority"),
            "office_location": action_data.get("office_location", "Local Authority / District Office"),
            "required_action_name": action_data.get("required_action_name", "Statutory Compliance Registration"),
            "action_urgency": action_data.get("action_urgency", "Before starting commercial operations"),
            "required_documents": action_data.get("required_documents", []),
            "procedural_steps": action_data.get("procedural_steps", []),
            "governing_laws": action_data.get("legal_sources", []),
            "estimated_cost_lkr": action_data.get("estimated_cost_lkr"),
            "estimated_timeline_days": action_data.get("estimated_timeline_days"),
        }
    except Exception as exc:
        logger.exception("Error predicting action roadmap: %s", exc)
        return None


def build_registration_guidance(business_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs an authoritative, AI-assisted Business Registration Guidance module
    tailored specifically for Western Province SMEs (Colombo, Gampaha, Kalutara).
    Grounds legal form selection, 5-stage procedural roadmap, document readiness audit,
    and official Form 1 completion assistance.
    """
    legal_form_input = business_context.get("legal_form")
    num_employees = business_context.get("number_of_employees") or 0
    scale = str(business_context.get("business_scale") or business_context.get("business_size") or "micro").lower()
    b_type = str(business_context.get("business_type") or business_context.get("sector") or "retail").lower()
    district = str(business_context.get("district") or business_context.get("location") or "Colombo")
    
    if district not in ["Colombo", "Gampaha", "Kalutara"]:
        district = "Colombo"

    # 1. AI Legal Entity Recommendation Logic
    if legal_form_input in ["sole_proprietorship", "individual"]:
        recommended_form = "Sole Proprietorship (තනි පුද්ගල ව්‍යාපාරය)"
        pathway_key = "sole_proprietorship"
        legal_basis = "Business Names Statute of the Western Province No. 04 of 1990 (Section 3)"
        governing_body = "Department of Business Names (Western Provincial Council) via Divisional Secretariat"
        reasoning = "Optimal for a single entrepreneur with low-to-moderate starting capital, offering straightforward registration with minimal statutory reporting burdens."
    elif legal_form_input in ["partnership"]:
        recommended_form = "Partnership (හවුල් ව්‍යාපාරය)"
        pathway_key = "partnership"
        legal_basis = "Business Names Statute of the Western Province No. 04 of 1990 & Partnership Ordinance of 1890"
        governing_body = "Department of Business Names (Western Provincial Council) via Divisional Secretariat"
        reasoning = "Suitable for 2 to 20 co-founders sharing management, capital, profits, and personal liability under a formal partnership agreement."
    elif legal_form_input in ["private_limited", "company"]:
        recommended_form = "Private Limited Company (පුද්ගලික සීමිත සමාගම - Pvt Ltd)"
        pathway_key = "private_limited"
        legal_basis = "Companies Act No. 07 of 2007 (incorporation through eROC)"
        governing_body = "Department of Registrar of Companies (eROC, 'Samagam Medura', Colombo 10)"
        reasoning = "Provides limited liability protection for shareholders, separate legal personality, and credibility for institutional borrowing or investor equity."
    else:
        # Autonomous AI inference based on scale, sector & employees
        if num_employees > 10 or scale in ["medium", "large"] or "import" in b_type or "export" in b_type:
            recommended_form = "Private Limited Company (පුද්ගලික සීමිත සමාගම - Pvt Ltd)"
            pathway_key = "private_limited"
            legal_basis = "Companies Act No. 07 of 2007 (incorporation through eROC)"
            governing_body = "Department of Registrar of Companies (eROC, 'Samagam Medura', Colombo 10)"
            reasoning = "Given the commercial scale, workforce size, and external trading exposure, a corporate entity provides necessary limited liability and tax efficiency."
        else:
            recommended_form = "Sole Proprietorship (තනි පුද්ගල ව්‍යාපාරය)"
            pathway_key = "sole_proprietorship"
            legal_basis = "Business Names Statute of the Western Province No. 04 of 1990 (Section 3)"
            governing_body = "Department of Business Names (Western Provincial Council) via Divisional Secretariat"
            reasoning = "Recommended for micro/small operations to commence commercial operations rapidly with low statutory fee outlay."

    # 2. Responsible Western Province Offices
    ds_offices = {
        "Colombo": "Colombo Divisional Secretariat (e.g., Thimbirigasyaya, Colombo, Kaduwela, Maharagama, Dehiwala-Mount Lavinia)",
        "Gampaha": "Gampaha Divisional Secretariat (e.g., Gampaha, Negombo, Kelaniya, Ja-Ela, Mahara)",
        "Kalutara": "Kalutara Divisional Secretariat (e.g., Kalutara, Panadura, Horana, Beruwala, Wadduwa)",
    }
    target_office = ds_offices.get(district, "Divisional Secretariat in Western Province")
    if pathway_key == "private_limited":
        target_office = "Department of Registrar of Companies (Samagam Medura, 400 D.R. Wijewardena Mawatha, Colombo 10 / https://eroc.drc.gov.lk)"

    # 3. 5-Stage Institutional Registration Stepper
    if pathway_key == "private_limited":
        stages = [
            {
                "stage_number": 1,
                "title": "Company Name Reservation",
                "title_si": "සමාගම් නාමය වෙන්කර ගැනීම (Name Search)",
                "authority": "Registrar of Companies (eROC Online)",
                "action": "Search and reserve proposed company name through the eROC portal; obtain Name Approval Reference.",
                "duration": "1 - 2 business days",
                "statutory_fee": "LKR 2,000 + taxes",
            },
            {
                "stage_number": 2,
                "title": "Articles of Association & Pre-incorporation Documents",
                "title_si": "සමාගම් ව්‍යවස්ථාව සහ Form 1/18/19 සකස් කිරීම",
                "authority": "Company Secretary / Qualified Legal Practitioner",
                "action": "Prepare Form 1 (Incorporation), Form 18 (Consent of Directors), Form 19 (Consent of Secretary), and Articles of Association.",
                "duration": "1 - 3 business days",
                "statutory_fee": "Legal / Secretarial costs apply",
            },
            {
                "stage_number": 3,
                "title": "eROC Submission & Filing",
                "title_si": "eROC ඔස්සේ අයදුම්පත ඉදිරිපත් කිරීම",
                "authority": "Department of Registrar of Companies (Colombo 10)",
                "action": "Upload signed forms, director identification, and pay incorporation charges on eROC system.",
                "duration": "2 - 4 business days",
                "statutory_fee": "Approx. LKR 15,000 - 20,000",
            },
            {
                "stage_number": 4,
                "title": "Certificate of Incorporation Issuance",
                "title_si": "සංස්ථාගත කිරීමේ සහතිකය (Certificate of Incorporation) ලබාගැනීම",
                "authority": "Registrar of Companies, Sri Lanka",
                "action": "Download the official digital Certificate of Incorporation containing the unique PV number.",
                "duration": "Instant upon approval",
                "statutory_fee": "Included in filing",
            },
            {
                "stage_number": 5,
                "title": "Post-Incorporation Compliance (TIN & EPF/ETF)",
                "title_si": "පසු-සංස්ථාගත නීතිමය ලියාපදිංචි (TIN, EPF/ETF)",
                "authority": "Inland Revenue Department (IRD) & Department of Labour",
                "action": "Register corporate TIN at IRD within 30 days, register employer number at EPF/ETF, open corporate bank account.",
                "duration": "Within 14 - 30 days",
                "statutory_fee": "Free of charge",
            },
        ]
        form_name = "eROC Form 1 (Application for Registration of a Company)"
        fee_range = "LKR 15,000 - 25,000"
        est_days = "3 - 7 Business Days"
    else:
        stages = [
            {
                "stage_number": 1,
                "title": "Business Name Availability & Scope Check",
                "title_si": "ව්‍යාපාර නාමය තහවුරු කරගැනීම",
                "authority": f"Divisional Secretariat ({district}) - Business Names Unit",
                "action": "Verify that the proposed name does not conflict with existing registered businesses in the province and avoids restricted words.",
                "duration": "1 day",
                "statutory_fee": "Free / Stamp duty approx. LKR 100",
            },
            {
                "stage_number": 2,
                "title": "Grama Niladhari Verification & Proof of Premises",
                "title_si": "ග්‍රාම නිලධාරී වාර්තාව සහ පරිශ්‍රය තහවුරු කිරීම",
                "authority": "Grama Niladhari Division of Business Address",
                "action": "Obtain Grama Niladhari residence & commercial operation report; compile title deed or valid lease agreement.",
                "duration": "1 - 2 days",
                "statutory_fee": "Nominal stamp duty",
            },
            {
                "stage_number": 3,
                "title": "Form 1 Application Lodgement",
                "title_si": "ආකෘති පත්‍ර අංක 1 (Form 1) ඉදිරිපත් කිරීම",
                "authority": f"Department of Business Names, Divisional Secretariat ({district})",
                "action": "Submit completed Form 1 signed by owner/partners together with NIC copies and premises evidence.",
                "duration": "1 day",
                "statutory_fee": "LKR 250 - 2,500 (depending on initial capital)",
            },
            {
                "stage_number": 4,
                "title": "Issuance of Business Registration (BR) Certificate",
                "title_si": "ව්‍යාපාර ලියාපදිංචි සහතිකය (BR Certificate) නිකුත් කිරීම",
                "authority": "Divisional Secretary (Registrar of Business Names, Western Province)",
                "action": "Subject to officer verification, the official Business Registration Certificate under Statute No. 04 of 1990 is issued.",
                "duration": "1 - 3 business days",
                "statutory_fee": "Included in initial payment",
            },
            {
                "stage_number": 5,
                "title": "Post-Registration Mandatory Compliance",
                "title_si": "ලියාපදිංචියෙන් පසු අනිවාර්ය පියවර (TIN, Trade Tax, EPF/ETF)",
                "authority": f"Inland Revenue Department (IRD) & Local Council ({district})",
                "action": "Obtain business TIN from IRD, pay municipal trade tax / trade license, register employees with EPF/ETF within 14 days of hiring.",
                "duration": "Within 14 - 30 days",
                "statutory_fee": "Varies by local authority trade tax schedule",
            },
        ]
        form_name = "Western Provincial Council Form 1 (ආකෘති පත්‍ර අංක 1 - ව්‍යාපාර නාම ලියාපදිංචි අයදුම්පත)"
        fee_range = "LKR 500 - LKR 2,500"
        est_days = "1 - 3 Business Days"

    # 4. Mandatory Document Readiness Checklist
    checklist = [
        {
            "document_id": "doc_nic",
            "name": "National Identity Card (NIC) / Passport Copy",
            "name_si": "අයිතිකරුගේ / හවුල්කරුවන්ගේ ජාතික හැඳුනුම්පත් පිටපත",
            "is_mandatory": True,
            "purpose": "Verification of Sri Lankan citizenship and age of majority (over 18 years).",
            "status": "READY",
        },
        {
            "document_id": "doc_premises",
            "name": "Proof of Commercial Premises (Deed / Lease / No-Objection Letter)",
            "name_si": "ව්‍යාපාරික ස්ථානයේ ඔප්පුව හෝ නීත්‍යානුකූල බදු ගිවිසුම",
            "is_mandatory": True,
            "purpose": "Verifies that the business has legal standing to operate from the stated physical address in Western Province.",
            "status": "READY" if business_context.get("has_physical_premises") else "ACTION_REQUIRED",
        },
        {
            "document_id": "doc_gn",
            "name": "Grama Niladhari Residence & Activity Report",
            "name_si": "ග්‍රාම නිලධාරී වාර්තාව (පදිංචිය සහ ව්‍යාපාරික ස්ථානය තහවුරු කිරීම)",
            "is_mandatory": True,
            "purpose": "Statutory requirement under Western Province Statute No. 04 of 1990 to verify identity and non-prohibited zoning.",
            "status": "ACTION_REQUIRED",
        },
        {
            "document_id": "doc_form1",
            "name": f"Official Prescribed Application ({form_name})",
            "name_si": "නිල අයදුම්පත් ආකෘතිය (සම්පූර්ණ කර අත්සන් කරන ලද)",
            "is_mandatory": True,
            "purpose": "The primary legal declaration for registering the commercial entity.",
            "status": "READY",
        },
    ]

    if pathway_key == "partnership":
        checklist.append({
            "document_id": "doc_partnership_deed",
            "name": "Partnership Deed / Formal Agreement (Certified Copy)",
            "name_si": "හවුල් ගිවිසුමේ සහතික කළ පිටපත",
            "is_mandatory": True,
            "purpose": "Governs profit sharing, capital contributions, and partner powers under Partnership Ordinance of 1890.",
            "status": "ACTION_REQUIRED",
        })

    # 5. Form 1 Assistant & Field-by-Field Breakdown
    form_fields_guide = [
        {
            "field_label": "1. Business Name (යෝජිත ව්‍යාපාර නාමය)",
            "description": "Enter the exact name. Must not contain deceptive terms or reserved government emblems.",
            "suggested_value": business_context.get("business_name") or f"{b_type.replace('_', ' ').title()} Enterprise",
        },
        {
            "field_label": "2. General Nature of Business (ව්‍යාපාරයේ ස්වභාවය)",
            "description": "Clearly state primary commercial activities (e.g. Retail of food and beverages, manufacturing, automotive servicing).",
            "suggested_value": b_type.replace('_', ' ').title(),
        },
        {
            "field_label": "3. Principal Place of Business (ව්‍යාපාරික ස්ථානයේ ලිපිනය)",
            "description": "Exact physical street address within Western Province where books and operations are maintained.",
            "suggested_value": f"Commercial Premises, {district} District, Western Province",
        },
        {
            "field_label": "4. Date of Commencement (ව්‍යාපාරය ආරම්භ කළ හෝ ආරම්භ කරන දිනය)",
            "description": "Must be within 14 days before or at the time of filing under Section 7 of Statute No. 04 of 1990.",
            "suggested_value": "Prior to / at commencement of commercial transactions",
        },
        {
            "field_label": "5. Initial Capital Invested (ආරම්භක මූලධනය)",
            "description": "Total initial capital in LKR (determines provincial stamp duty rate).",
            "suggested_value": "As per financial plan (e.g., LKR 250,000 - 1,000,000)",
        },
    ]

    return {
        "recommended_legal_form": recommended_form,
        "pathway_key": pathway_key,
        "legal_basis": legal_basis,
        "governing_body": governing_body,
        "target_office": target_office,
        "district": district,
        "reasoning": reasoning,
        "official_form_name": form_name,
        "estimated_fees": fee_range,
        "estimated_timeline": est_days,
        "stages": stages,
        "document_checklist": checklist,
        "form_fields_guide": form_fields_guide,
    }
