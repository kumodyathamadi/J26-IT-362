"""
Component 2 — Business Plan PDF Extractor & Profile Identification Service
Extracts rich business profile information from Component 1 SME360 AI Business Plan PDFs
or external SME business plans (both digital text and scanned/OCR).
"""

from __future__ import annotations

import io
import re
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try importing PyMuPDF
try:
    import pymupdf as fitz  # PyMuPDF 1.24+
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

# Sector mapping to Component 2 valid sectors: "food", "clothing", "salon", "vehicle_parts"
SECTOR_KEYWORDS = {
    "food": [
        "grocery", "mini-mart", "minimart", "supermarket", "food", "bakery", "bake house",
        "cake", "pastry", "restaurant", "cafe", "beverage", "sweets", "catering", "dining",
        "snack", "tea", "spices", "coffee", "fruit", "vegetable", "dairy", "meat", "poultry",
        "eatery", "takeaway", "confectionery", "provisions", "juice", "kitchen", "agro"
    ],
    "clothing": [
        "clothing", "garment", "apparel", "textile", "fashion", "boutique", 
        "tailor", "tailoring", "dresses", "t-shirts", "wear", "fabric", "saree",
        "shoes", "footwear", "outfit", "attire", "sewing", "embroidery"
    ],
    "salon": [
        "salon", "saloon", "beauty", "hair", "spa", "cosmetics", "parlour", 
        "barber", "grooming", "bridal", "facial", "skincare", "skin care",
        "makeup", "manicure", "pedicure", "nail", "massage", "aesthetic"
    ],
    "vehicle_parts": [
        "vehicle", "auto", "automobile", "spare parts", "parts", "garage", 
        "motor", "repair", "mechanic", "tyre", "tire", "battery", "lubricant",
        "motorcycle", "bike", "workshop", "engine", "service station"
    ],
}

# Domain goods & offerings database for intelligent context scanning
DOMAIN_PRODUCTS_CATALOG = {
    "food": [
        "Essential Groceries", "Packaged Food", "Fresh Produce", "Dairy Products",
        "Bakery Items & Bread", "Cakes & Pastries", "Sweets & Confectionery", "Cooked Meals & Dining",
        "Beverages & Soft Drinks", "Tea & Herbal Infusions", "Spices & Condiments",
        "Snacks & Finger Food", "Fresh Fruits & Vegetables", "WhatsApp Delivery Orders",
        "Takeaway Food Service", "Organic Food Products", "Catering Packages"
    ],
    "clothing": [
        "T-Shirts", "Trousers & Jeans", "Dresses & Gowns", "Casual Wear", "Office Wear",
        "Sarees & Traditional Wear", "Shirts & Blouses", "Skirts & Tops", "Children's Wear",
        "Boutique Fashion Items", "Custom Tailoring Services", "Seasonal Clothing",
        "Fashion Accessories", "Footwear & Shoes", "Sportswear"
    ],
    "salon": [
        "Hair Cutting & Styling", "Bridal Dressing & Packages", "Facials & Skin Care",
        "Hair Coloring & Highlights", "Manicure & Pedicure", "Beard Grooming & Shaving",
        "Hair Straightening & Perming", "Makeup Artistry", "Head & Body Massage",
        "Nail Art & Care", "Cosmetics & Beauty Products", "Skin Rejuvenation Treatments"
    ],
    "vehicle_parts": [
        "Automotive Spare Parts", "Engine Lubricants & Motor Oil", "Automotive Batteries",
        "Tyres & Tubes", "Brake Pads & Braking Systems", "Vehicle Accessories",
        "Filters (Air, Oil, Fuel)", "Suspension & Steering Parts", "Electrical Spares & Bulbs",
        "Mechanical Repair Services", "Periodic Vehicle Servicing", "Wheel Balancing & Alignment"
    ]
}

# Sri Lankan District & Local Authority Mapping
SRI_LANKA_DISTRICTS = {
    "colombo": {
        "province": "Western Province",
        "district": "Colombo",
        "default_la": "Colombo Municipal Council",
        "las": {
            "colombo": "Colombo Municipal Council",
            "kotte": "Kotte Municipal Council",
            "sri jayawardenepura": "Kotte Municipal Council",
            "dehiwala": "Dehiwala-Mount Lavinia Municipal Council",
            "mount lavinia": "Dehiwala-Mount Lavinia Municipal Council",
            "moratuwa": "Moratuwa Municipal Council",
            "kaduwela": "Kaduwela Municipal Council",
            "maharagama": "Maharagama Urban Council",
            "kesbewa": "Kesbewa Urban Council",
            "boralesgamuwa": "Boralesgamuwa Urban Council",
            "kolonnawa": "Kolonnawa Urban Council",
            "homagama": "Homagama Pradeshiya Sabha",
            "seethawaka": "Seethawaka Pradeshiya Sabha",
        }
    },
    "gampaha": {
        "province": "Western Province",
        "district": "Gampaha",
        "default_la": "Gampaha Municipal Council",
        "las": {
            "gampaha": "Gampaha Municipal Council",
            "negombo": "Negombo Municipal Council",
            "kelaniya": "Kelaniya Pradeshiya Sabha",
            "wattala": "Wattala-Mabole Urban Council",
            "ja-ela": "Ja-Ela Urban Council",
            "katunayake": "Katunayake-Seeduwa Urban Council",
            "minuwangoda": "Minuwangoda Urban Council",
            "biyagama": "Biyagama Pradeshiya Sabha",
            "mahara": "Mahara Pradeshiya Sabha",
            "mirigama": "Mirigama Pradeshiya Sabha",
        }
    },
    "kalutara": {
        "province": "Western Province",
        "district": "Kalutara",
        "default_la": "Kalutara Urban Council",
        "las": {
            "kalutara": "Kalutara Urban Council",
            "panadura": "Panadura Urban Council",
            "horana": "Horana Urban Council",
            "beruwala": "Beruwala Urban Council",
            "bandaragama": "Bandaragama Pradeshiya Sabha",
            "wadduwa": "Panadura Pradeshiya Sabha",
            "aluthgama": "Beruwala Pradeshiya Sabha",
        }
    },
    "kandy": {"province": "Central Province", "district": "Kandy", "default_la": "Kandy Municipal Council", "las": {}},
    "galle": {"province": "Southern Province", "district": "Galle", "default_la": "Galle Municipal Council", "las": {}},
    "matara": {"province": "Southern Province", "district": "Matara", "default_la": "Matara Municipal Council", "las": {}},
    "kurunegala": {"province": "North Western Province", "district": "Kurunegala", "default_la": "Kurunegala Municipal Council", "las": {}},
    "anuradhapura": {"province": "North Central Province", "district": "Anuradhapura", "default_la": "Anuradhapura Municipal Council", "las": {}},
    "jaffna": {"province": "Northern Province", "district": "Jaffna", "default_la": "Jaffna Municipal Council", "las": {}},
    "ratnapura": {"province": "Sabaragamuwa Province", "district": "Ratnapura", "default_la": "Ratnapura Municipal Council", "las": {}},
    "badulla": {"province": "Uva Province", "district": "Badulla", "default_la": "Badulla Municipal Council", "las": {}},
    "hambantota": {"province": "Southern Province", "district": "Hambantota", "default_la": "Hambantota Urban Council", "las": {}},
    "nuwara eliya": {"province": "Central Province", "district": "Nuwara Eliya", "default_la": "Nuwara Eliya Municipal Council", "las": {}},
    "kegalle": {"province": "Sabaragamuwa Province", "district": "Kegalle", "default_la": "Kegalle Urban Council", "las": {}},
    "puttalam": {"province": "North Western Province", "district": "Puttalam", "default_la": "Puttalam Urban Council", "las": {}},
    "matale": {"province": "Central Province", "district": "Matale", "default_la": "Matale Municipal Council", "las": {}},
    "batticaloa": {"province": "Eastern Province", "district": "Batticaloa", "default_la": "Batticaloa Municipal Council", "las": {}},
    "trincomalee": {"province": "Eastern Province", "district": "Trincomalee", "default_la": "Trincomalee Urban Council", "las": {}},
    "ampara": {"province": "Eastern Province", "district": "Ampara", "default_la": "Ampara Urban Council", "las": {}},
    "polonnaruwa": {"province": "North Central Province", "district": "Polonnaruwa", "default_la": "Polonnaruwa Municipal Council", "las": {}},
    "monaragala": {"province": "Uva Province", "district": "Monaragala", "default_la": "Monaragala Pradeshiya Sabha", "las": {}},
}


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Tuple[str, List[str], bool, bool]:
    """
    Extracts text from PDF bytes using PyMuPDF.
    
    Returns:
        (full_text, pages_text, is_scanned, ocr_used)
    """
    if not fitz:
        raise RuntimeError("PyMuPDF (fitz) is not installed in the python environment.")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text: List[str] = []
    total_chars = 0
    has_images = False

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text") or ""
        pages_text.append(text)
        total_chars += len(text.strip())
        if page.get_images():
            has_images = True

    is_scanned = total_chars < 50 and has_images
    ocr_used = False

    # Scanned PDF handling: if text is negligible but images exist, attempt OCR if supported
    if is_scanned:
        ocr_pages: List[str] = []
        try:
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                textpage = page.get_textpage_ocr(flags=0, language="eng", dpi=150)
                ocr_text = page.get_text("text", textpage=textpage)
                ocr_pages.append(ocr_text)
            if sum(len(t.strip()) for t in ocr_pages) > 50:
                pages_text = ocr_pages
                total_chars = sum(len(t.strip()) for t in ocr_pages)
                ocr_used = True
        except Exception as ocr_err:
            logger.warning("PyMuPDF OCR not available or failed: %s", ocr_err)

    full_text = "\n\n--- Page Break ---\n\n".join(pages_text)
    doc.close()
    return full_text, pages_text, is_scanned, ocr_used


def _clean_str(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    val = re.sub(r"\s+", " ", val).strip()
    # Strip any trailing colons, pipes, or punctuation
    val = re.sub(r"^[\s:|\-]+|[\s:|\-]+$", "", val).strip()
    return val or None


def _clean_num(val_str: Optional[str]) -> Optional[float]:
    if not val_str:
        return None
    cleaned = re.sub(r"[^\d.]", "", val_str)
    try:
        return float(cleaned)
    except ValueError:
        return None


def _extract_business_name(full_text: str, filename: str, first_page_text: str = "") -> str:
    """
    Intelligently identifies the business name from Component 1 cover tables,
    headers, titles, or general document patterns.
    """
    # 1. Component 1 table pattern: "BUSINESS NAME:" followed by value
    m = re.search(r"BUSINESS\s+NAME:\s*\n*\s*([^\n\r\|]{2,80})", full_text, re.IGNORECASE)
    if m:
        candidate = _clean_str(m.group(1))
        if candidate and len(candidate) > 2 and not any(skip in candidate.lower() for skip in ["category:", "date:", "sme360"]):
            return candidate

    # 2. Explicit label patterns
    labels = [
        r"(?:Business\s+Name|Company\s+Name|Enterprise\s+Name|Firm\s+Name|Trading\s+Name|Name\s+of\s+Business|Name\s+of\s+Enterprise|Project\s+Name|Prepared\s+For):\s*([^\n\r\|]{2,80})",
        r"(?:Business\s+Name|Company\s+Name|Enterprise\s+Name|Trading\s+Name|Prepared\s+For)\s*\n+\s*([^\n\r\|]{2,80})",
        r"(?:Business|Growth)\s+Plan\s+(?:for|of|:|-)\s*([^\n\r\|]{2,80})",
        r"([A-Z0-9][A-Za-z0-9\s&'\.,\-]{2,50})\s+(?:Business\s+Plan|Growth\s+Plan|Feasibility\s+Report|Project\s+Proposal)",
    ]
    for pat in labels:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            candidate = _clean_str(m.group(1))
            if candidate and len(candidate) > 2:
                # filter out non-names
                if not any(bad in candidate.lower() for bad in ["management", "the user", "sme360", "table of contents", "executive summary", "page 1"]):
                    return candidate

    # 3. First page header scan
    if first_page_text:
        lines = [line.strip() for line in first_page_text.splitlines() if line.strip()]
        for line in lines[:8]:
            line_clean = _clean_str(line)
            if not line_clean or len(line_clean) < 3 or len(line_clean) > 60:
                continue
            lower_l = line_clean.lower()
            if any(stop in lower_l for stop in [
                "sme360", "business plan", "growth plan", "executive summary", "confidential",
                "table of contents", "feasibility", "decision support", "page", "prepared",
                "author", "version", "date", "report", "ai-assisted"
            ]):
                continue
            # Likely a real title line!
            words = line_clean.split()
            if 1 <= len(words) <= 7:
                return line_clean

    # 4. Clean fallback from filename
    clean_fn = re.sub(r"^(?:SME360_AI_)?(?:Business_Plan_)?", "", filename, flags=re.IGNORECASE)
    clean_fn = re.sub(r"[_\-]", " ", clean_fn.replace(".pdf", "").replace(".PDF", ""))
    clean_fn = _clean_str(clean_fn) or "SME Business"
    return clean_fn.title()


def _extract_category_and_sector(full_text: str, biz_name: str) -> Tuple[str, str]:
    """
    Extracts the business category text and maps it to one of the 4 Component 2 sectors:
    'food', 'clothing', 'salon', 'vehicle_parts'.
    """
    raw_category = None

    # 1. Match Component 1 cover table & explicit category headers
    cat_patterns = [
        r"CATEGORY:\s*\n*\s*([^\n\r\|]{2,70})",
        r"Business\s+Category:\s*\n*\s*([^\n\r\|]{2,70})",
        r"Industry\s+Category:\s*\n*\s*([^\n\r\|]{2,70})",
        r"(?:Industry|Sector|Nature\s+of\s+Business|Business\s+Type):\s*\n*\s*([^\n\r\|]{2,70})",
    ]
    for pat in cat_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            cand = _clean_str(m.group(1))
            if cand and len(cand) > 2 and not any(bad in cand.lower() for bad in ["business stage", "prepared", "district"]):
                raw_category = cand
                break

    # 2. Sector scoring based on corpus keywords
    search_corpus = f"{raw_category or ''} {biz_name} {full_text[:5000]}".lower()

    scores = {sector: 0 for sector in SECTOR_KEYWORDS}
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            # Word boundary matching
            matches = len(re.findall(r"\b" + re.escape(kw) + r"\b", search_corpus))
            if matches > 0:
                # Extra weight if in raw_category or biz_name
                weight = 5 if (raw_category and kw in raw_category.lower()) or (kw in biz_name.lower()) else 1
                scores[sector] += matches * weight

    best_sector = max(scores, key=scores.get)
    if scores[best_sector] == 0:
        # Default fallback if genuinely no domain keywords found
        best_sector = "food"

    display_category = raw_category or best_sector.replace("_", " ").title()
    return display_category, best_sector


def _extract_location(full_text: str) -> Dict[str, str]:
    """
    Identifies district, province, and local authority from text or Sri Lankan geography mapping.
    """
    loc_corpus = full_text[:4000].lower()

    # Default to Western Province Colombo
    detected_district = "Colombo"
    detected_province = "Western Province"
    detected_la = "Colombo Municipal Council"

    # Search for explicit DISTRICT: or Location: tag
    m = re.search(r"DISTRICT:\s*\n*\s*([^\n\r\|]+)", full_text, re.IGNORECASE)
    if not m:
        m = re.search(r"Operating\s+District:\s*\n*\s*([^\n\r\|]+)", full_text, re.IGNORECASE)
    if not m:
        m = re.search(r"(?:Operating\s+Location|Location):\s*\n*\s*([^\n\r\|]+)", full_text, re.IGNORECASE)

    raw_loc = _clean_str(m.group(1)) if m else ""

    # Check for Sri Lankan districts in raw_loc first, then in loc_corpus
    check_text = f"{raw_loc} {loc_corpus}".lower()
    for d_name, d_info in SRI_LANKA_DISTRICTS.items():
        if re.search(r"\b" + re.escape(d_name) + r"\b", check_text):
            detected_district = d_info["district"]
            detected_province = d_info["province"]
            detected_la = d_info["default_la"]

            # Sub-check for specific towns/local authorities
            for town, la_name in d_info.get("las", {}).items():
                if re.search(r"\b" + re.escape(town) + r"\b", check_text):
                    detected_la = la_name
                    break
            break

    location_display = f"{detected_district}, {detected_province}, Sri Lanka"

    return {
        "location": location_display,
        "province": detected_province,
        "district": detected_district,
        "local_authority": detected_la,
    }


def _extract_proposed_activity(full_text: str, biz_name: str, category: str, district: str) -> str:
    """
    Extracts the actual executive summary or business overview sentence without disclaimers.
    """
    # 1. Component 1 Executive Summary: Section 1. Executive Summary & Feasibility Snapshot
    m = re.search(
        r"1\.\s+Executive\s+Summary\s*(?:&\s*Feasibility\s*Snapshot)?\s*\n+([^\n\r]+(?:\n[^\n\r]+){0,4}?)",
        full_text,
        re.IGNORECASE,
    )
    if m:
        candidate = _clean_str(m.group(1))
        if candidate and len(candidate) > 25 and not any(bad in candidate.lower() for bad in ["predicted feasibility", "confidential", "sme360"]):
            return candidate

    # 2. General Executive Summary / Overview headers
    patterns = [
        r"(?:Executive\s+Summary|Business\s+Summary|Business\s+Overview|Business\s+Concept)\s*\n+([^\n\r]+(?:\n[^\n\r]+){0,3}?)",
        r"(?:1\.1\s+Business\s+Overview)\s*\n+([^\n\r]+(?:\n[^\n\r]+){0,3}?)",
        r"Based\s+on\s+the\s+operational\s+details\s+provided:?\s*([^\n\r]+(?:\n[^\n\r]+){0,2}?)",
    ]
    for pat in patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            cand = _clean_str(m.group(1))
            if cand and len(cand) > 30 and not any(bad in cand.lower() for bad in ["confidential", "sme360", "table of contents", "page "]):
                return cand

    # 3. Clean fallback synthesized from detected attributes
    return f"{biz_name} is a {category.lower()} enterprise operating in {district}, providing commercial retail and service operations to local customers."


def _is_valid_product(item: str) -> bool:
    if not item or len(item) < 3 or len(item) > 40:
        return False
    lower = item.lower().strip()
    bad_tokens = [
        "page break", "page ", "filing date", "date", "---", "sme360", "confidential",
        "score", "topsis", "feasibility", "target customer", "risk", "financial",
        "projection", "buffer", "roadmap", "phase", "lkr", "rs.", "table of", "contents",
        "chapter", "section", "tel:", "phone", "email", "address", "registered",
        "registration", "statute", "ordinance", "act no", "western province", "wider selection",
        "high quality", "affordable", "district", "customers", "operation", "service in", "market",
        "report", "overview", "executive", "summary"
    ]
    if any(b in lower for b in bad_tokens):
        return False
    letters = sum(1 for c in item if c.isalpha())
    digits = sum(1 for c in item if c.isdigit())
    if letters < 3 or digits >= letters:
        return False
    if re.search(r"\d+[-/\.]\d+", item):
        return False
    return True


def _extract_products_services(
    full_text: str, biz_name: str, business_type: str, proposed_activity: str
) -> List[str]:
    """
    Extracts real domain products & services dynamically from the uploaded document text.
    Never dumps document metadata, page breaks, or filing dates.
    """
    products: List[str] = []

    # Clean document text to eliminate page breaks, headers and filing date footers
    clean_text = re.sub(r"-{2,}\s*Page\s+Break\s*-{2,}\s*\d*", " ", full_text, flags=re.IGNORECASE)
    clean_text = re.sub(r"Page\s+\d+\s*(?:of\s*\d+)?", " ", clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r"(?:Filing\s+Date|Date|Registration\s+No|Reg\s+No)\s*:\s*[^\n\r]+", " ", clean_text, flags=re.IGNORECASE)

    # Strategy A: Extract from explicit verbs: "provides X, Y, and Z", "will sell X, Y, Z", "products include X, Y"
    action_text = f"{proposed_activity} {clean_text[:4000]}"
    sell_match = re.search(
        r"(?:provides|providing|offers|offering|will\s+sell|selling|specializes\s+in|products\s+include|services\s+include|commercial\s+offerings\s+include)\s+([^\.\n\r]+)",
        action_text,
        re.IGNORECASE,
    )
    if sell_match:
        raw_items = sell_match.group(1)
        items = re.split(r",|\band\b|;|&", raw_items)
        for item in items:
            clean_item = _clean_str(item)
            if _is_valid_product(clean_item):
                products.append(clean_item.title())

    # Strategy B: Extract bullet points under offerings / products
    for line in clean_text[:4000].splitlines():
        line = line.strip()
        m_bullet = re.match(r"^[•\*\-]\s+([A-Za-z][A-Za-z0-9\s,&'\(\)\-]{2,40})$", line)
        if m_bullet:
            cand = _clean_str(m_bullet.group(1))
            if _is_valid_product(cand):
                products.append(cand.title())

    # Strategy C: Check which items from our domain catalog are ACTUALLY MENTIONED in the uploaded document
    corpus_lower = clean_text.lower()
    domain_catalog = DOMAIN_PRODUCTS_CATALOG.get(business_type, [])
    for item in domain_catalog:
        # Check if key words of this product item exist in the document
        keywords = [w.lower() for w in re.findall(r"\w+", item) if len(w) > 3]
        if any(kw in corpus_lower for kw in keywords):
            if item not in products:
                products.append(item)

    # Clean & Deduplicate preserving order
    seen = set()
    cleaned_products = []
    for p in products:
        norm = p.lower()
        if norm not in seen and _is_valid_product(p):
            seen.add(norm)
            cleaned_products.append(p)

    # If still fewer than 2 items detected, seed with tailored products from the matched sector
    if len(cleaned_products) < 2:
        cleaned_products = domain_catalog[:4]

    return cleaned_products[:12]


def _extract_staff_count(full_text: str) -> int:
    """Extracts employee/staff count from Component 1 tables or general patterns."""
    # Component 1 table: "Available Staffing:\n3 Person(s)"
    m = re.search(r"Available\s+Staffing:\s*\n*\s*(\d+)", full_text, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # Pattern: "Available Staff Count (3 Staff)"
    m = re.search(r"Available\s+Staff\s+Count\s*\((\d+)\s*Staff\)", full_text, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # Pattern: "deploys 3 active staff"
    m = re.search(r"deploys\s+(\d+)\s+active\s+staff", full_text, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # General: "Staff Count: 3" or "3 Person(s)" or "Team of 3"
    patterns = [
        r"(\d+)\s+Person\(s\)",
        r"(?:Employees|Staff|Team|Workers|Staffing|Workforce)\s*(?:Count|Size)?:\s*(\d+)",
        r"(?:employing|employs|staff\s+of|team\s+of|hire)\s*(\d+)",
        r"(\d+)\s+(?:full-time|part-time|active|hired)?\s*(?:employees|staff|workers)",
    ]
    for pat in patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 0 <= val <= 500:
                return val

    return 2  # default fallback


def _extract_financials(full_text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Extracts available starting capital, monthly operating budget, and requested loan."""
    capital_lkr = None
    monthly_budget = None
    loan_lkr = None

    # Capital
    cap_patterns = [
        r"Available\s+Starting\s+Capital\s*\n*\s*LKR\s*([\d,]+)",
        r"Available\s+Capital\s*\n*LKR\s*([\d,]+)",
        r"Available\s+Capital\s*\(Lkr\)\s*\([^\d]*([\d,]+)\)",
        r"(?:Starting\s+Capital|Initial\s+Capital|Available\s+Capital|Startup\s+Capital|Total\s+Investment|Capital\s+Investment|Capital):\s*(?:LKR|Rs\.?|USD)?\s*([\d,]+)",
        r"(?:invest|investment\s+of)\s*(?:approximately)?\s*(?:LKR|Rs\.?)\s*([\d,]+)",
    ]
    for pat in cap_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            val = _clean_num(m.group(1))
            if val and val > 0:
                capital_lkr = val
                break

    # Monthly Budget
    budget_patterns = [
        r"Monthly\s+Operating\s+Budget\s*\n*\s*LKR\s*([\d,]+)",
        r"Monthly\s+Budget:\s*LKR\s*([\d,]+)",
        r"(?:Monthly\s+Budget|Monthly\s+Expenses|Operating\s+Budget):\s*(?:LKR|Rs\.?|USD)?\s*([\d,]+)",
    ]
    for pat in budget_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            val = _clean_num(m.group(1))
            if val and val > 0:
                monthly_budget = val
                break

    # Requested Loan
    loan_patterns = [
        r"Requested\s+Loan\s+Amount\s*\(Lkr\)\s*\([^\d]*([\d,]+)\)",
        r"Requested\s+Loan\s+Amount:\s*LKR\s*([\d,]+)",
        r"(?:Requested\s+Loan|Loan\s+Amount):\s*(?:LKR|Rs\.?|USD)?\s*([\d,]+)",
    ]
    for pat in loan_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            val = _clean_num(m.group(1))
            if val and val > 0:
                loan_lkr = val
                break

    return capital_lkr, monthly_budget, loan_lkr


def _extract_strategy(full_text: str) -> Optional[str]:
    """Extracts top recommended business or operating strategy."""
    strat_patterns = [
        r"Top\s+Recommended\s+Direction:\s*([^\n\r\(]+)",
        r"Top\s+Recommended\s+Strategy:\s*([^\n\r\(]+)",
        r"ACTIVE\s+OPERATING\s+STRATEGY:\s*([^\n\r\(]+)",
        r"(?:Strategic\s+Focus|Operating\s+Strategy|Core\s+Strategy|Primary\s+Strategy):\s*([^\n\r]+)",
    ]
    for pat in strat_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            cand = _clean_str(m.group(1))
            if cand and len(cand) > 3 and not any(bad in cand.lower() for bad in ["score", "rank"]):
                return cand

    return None


def extract_business_profile_from_text(
    full_text: str, filename: str = ""
) -> Dict[str, Any]:
    """
    Parses full text of a Business Plan PDF and identifies structured business attributes.
    Works robustly with SME360 AI standard reports and general business plans.
    """
    profile: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {
        "filename": filename,
        "extraction_confidence": "high",
        "detected_sections": [],
    }

    first_page_text = full_text.split("--- Page Break ---")[0] if "--- Page Break ---" in full_text else full_text[:2000]

    # 1. Business Name
    biz_name = _extract_business_name(full_text, filename, first_page_text)
    profile["business_name"] = biz_name

    # 2. Industry Category & Mapped Sector
    display_category, business_type = _extract_category_and_sector(full_text, biz_name)
    profile["business_category"] = display_category
    profile["business_type"] = business_type
    profile["sector"] = business_type

    # 3. Business Stage
    stage = "New Startup"
    m_stage = re.search(r"BUSINESS\s+STAGE:\s*\n*\s*([^\n\r\|\(\)]+)", full_text, re.IGNORECASE)
    if not m_stage:
        m_stage = re.search(r"Business\s+Stage:\s*\n*\s*([^\n\r\|\(\)]+)", full_text, re.IGNORECASE)
    if m_stage:
        cand_stage = _clean_str(m_stage.group(1))
        if cand_stage:
            stage = "Existing Business" if "existing" in cand_stage.lower() else "New Startup"
    else:
        text_lower = full_text[:4000].lower()
        if "existing business" in text_lower or "operating since" in text_lower or "expansion plan" in text_lower:
            stage = "Existing Business"
        else:
            stage = "New Startup"

    profile["business_stage"] = stage

    # 4. Location: Province, District, Local Authority
    loc_info = _extract_location(full_text)
    profile["location"] = loc_info["location"]
    profile["province"] = loc_info["province"]
    profile["district"] = loc_info["district"]
    profile["local_authority"] = loc_info["local_authority"]

    # 5. Proposed Activity & Business Overview
    proposed_activity = _extract_proposed_activity(full_text, biz_name, display_category, loc_info["district"])
    profile["proposed_activity"] = proposed_activity

    # 6. Products / Commercial Offerings
    products_services = _extract_products_services(full_text, biz_name, business_type, proposed_activity)
    profile["products_services"] = products_services

    # 7. Staff & Employees
    employees_count = _extract_staff_count(full_text)
    profile["number_of_employees"] = employees_count
    profile["employees"] = employees_count

    # 8. Physical Premises
    has_physical_premises = True
    full_lower = full_text.lower()
    if any(k in full_lower for k in ["online-only", "no physical premises", "virtual business", "ecommerce only"]):
        has_physical_premises = False

    profile["has_physical_premises"] = has_physical_premises

    # 9. Capital & Financials
    capital_lkr, monthly_budget, loan_lkr = _extract_financials(full_text)
    profile["available_capital_lkr"] = capital_lkr
    profile["requested_loan_lkr"] = loan_lkr
    profile["monthly_budget_lkr"] = monthly_budget

    # 10. Active Operating Strategy
    strategy = _extract_strategy(full_text)
    profile["selected_strategy"] = strategy

    # 11. Decision System Reference UUID
    decision_ref = None
    m_ref = re.search(r"(?:Decision\s+System\s+Reference|Record\s+ID):\s*([a-f0-9\-]+)", full_text, re.IGNORECASE)
    if m_ref:
        decision_ref = _clean_str(m_ref.group(1))

    profile["decision_system_reference"] = decision_ref

    # 12. Component 2 Operational Compliance Conditions
    # Smart legal form detection from PDF text (not hardcoded)
    detected_legal_form = "sole_proprietorship"  # sensible fallback
    _lf_text = full_text.lower()

    # Pattern 1: Explicit label extraction (e.g. "Legal Form: Partnership")
    _lf_match = re.search(
        r"(?:legal\s+form|ownership\s+structure|business\s+structure|entity\s+type|registration\s+type)"
        r"\s*[:\-]\s*([^\n\r,\.\|]{3,60})",
        full_text,
        re.IGNORECASE,
    )
    if _lf_match:
        _lf_raw = _lf_match.group(1).strip().lower()
        if any(k in _lf_raw for k in ["private limited", "pvt ltd", "pvt. ltd", "(pvt)", "company", "incorporated", "inc."]):
            detected_legal_form = "private_limited"
        elif any(k in _lf_raw for k in ["partnership", "partners", "co-founder", "joint venture"]):
            detected_legal_form = "partnership"
        elif any(k in _lf_raw for k in ["sole", "proprietor", "individual", "single owner"]):
            detected_legal_form = "sole_proprietorship"

    # Pattern 2: Keyword scan across the full document
    if detected_legal_form == "sole_proprietorship":
        if any(k in _lf_text for k in ["private limited company", "(pvt) ltd", "pvt. ltd.", "private ltd", "registered as a company"]):
            detected_legal_form = "private_limited"
        elif any(k in _lf_text for k in ["partnership agreement", "business partners", "co-founders", "joint venture", "partnership firm"]):
            detected_legal_form = "partnership"

    profile["legal_form"] = detected_legal_form
    profile["ownership"] = detected_legal_form
    
    # Food checks
    profile["handles_food"] = (business_type == "food")
    profile["serves_cooked_food"] = False
    if business_type == "food":
        if any(w in full_lower for w in ["restaurant", "cooked food", "cafe", "dining", "hot food", "eatery", "kitchen", "bakery", "bake house", "meals"]):
            profile["serves_cooked_food"] = True

    # Alcohol check
    profile["sells_alcohol"] = any(w in full_lower for w in ["alcohol", "liquor", "wine", "beer", "pub", "bar"])

    # Salon & Cosmetics check
    profile["uses_chemicals_or_cosmetics"] = (business_type == "salon") or any(w in full_lower for w in ["cosmetic", "hair dye", "chemical", "facial bleach"])

    # Vehicle Waste Oil & Batteries check
    profile["handles_waste_oil_or_batteries"] = (business_type == "vehicle_parts") or any(w in full_lower for w in ["waste oil", "engine oil", "battery", "batteries", "lubricant disposal"])

    # Manufacturing / Importing
    profile["is_manufacturing"] = any(w in full_lower for w in ["manufacturing", "factory", "processing plant", "industrial"])
    profile["is_importing"] = any(w in full_lower for w in ["importing", "importer", "direct import", "customs clearance"])

    # Turnover band estimate
    if capital_lkr and capital_lkr > 10_000_000:
        profile["turnover_band"] = "10m_50m"
    elif capital_lkr and capital_lkr >= 1_000_000:
        profile["turnover_band"] = "1m_10m"
    else:
        profile["turnover_band"] = "under_1m"

    metadata["summary"] = (
        f"Extracted profile for '{biz_name}' ({display_category}), "
        f"Stage: {stage}, Location: {loc_info['district']} ({loc_info['province']}), "
        f"Employees: {employees_count}, Strategy: {strategy or 'N/A'}."
    )

    return {
        "profile": profile,
        "metadata": metadata,
    }
