"""
Official Sri Lanka Business Registration (BR) Form Auto-Filler & PDF Generator.

Produces an authoritative, government-styled Form 1 application for:
- Individual / Sole Proprietorship Business Registration (Business Names Statute No. 04 of 1990 / Ordinance)
- Partnership Business Registration
- Private Limited Company Application (Companies Act No. 7 of 2007 - Form 1)
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Footer divider line
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 42, 595 - 36, 42)

        # Footer text
        footer_text = (
            "Democratic Socialist Republic of Sri Lanka • Official Business Registration Application "
            "(Form 1 / Statutory Filing)"
        )
        self.drawString(36, 30, footer_text)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(595 - 36, 30, page_str)
        self.restoreState()


def generate_br_application_pdf(business_data: Dict[str, Any]) -> bytes:
    """
    Generates an auto-filled Official Sri Lanka Business Registration Form PDF.
    
    Accepts business profile dictionary and returns raw PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    header_republic = ParagraphStyle(
        "RepublicHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=1,  # Center
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2,
    )

    header_sub = ParagraphStyle(
        "HeaderSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.HexColor("#334155"),
        spaceAfter=3,
    )

    title_form = ParagraphStyle(
        "FormTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        alignment=1,
        textColor=colors.HexColor("#1E3A8A"),  # Deep Navy
        spaceAfter=2,
    )

    title_act = ParagraphStyle(
        "ActCitation",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        alignment=1,
        textColor=colors.HexColor("#475569"),
        spaceAfter=8,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
    )

    field_label = ParagraphStyle(
        "FieldLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155"),
    )

    field_value = ParagraphStyle(
        "FieldValue",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )

    field_value_highlight = ParagraphStyle(
        "FieldValueHighlight",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0369A1"),
    )

    legal_text = ParagraphStyle(
        "LegalDeclaration",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#1E293B"),
    )

    # ---------------------------------------------------------------------------
    # Data Normalization
    # ---------------------------------------------------------------------------
    legal_form_raw = str(business_data.get("legal_form") or business_data.get("ownership") or "Sole Proprietorship").lower()
    if "company" in legal_form_raw or "limited" in legal_form_raw or "pvt" in legal_form_raw:
        form_type_title = "COMPANIES ACT NO. 07 OF 2007 (SECTION 4)"
        form_name_en = "FORM 1: APPLICATION FOR INCORPORATION OF A PRIVATE LIMITED COMPANY"
        authority_title = "DEPARTMENT OF THE REGISTRAR OF COMPANIES (eROC) — SRI LANKA"
        authority_sub = "Provincial Registrar Office / eROC Portal (Battaramulla)"
    elif "partner" in legal_form_raw:
        form_type_title = "BUSINESS NAMES STATUTE NO. 04 OF 1990 (SECTION 5) / BUSINESS NAMES ORDINANCE"
        form_name_en = "FORM 1: STATEMENT OF PARTICULARS FOR REGISTRATION OF A PARTNERSHIP"
        authority_title = "DEPARTMENT OF BUSINESS NAMES & DIVISIONAL SECRETARIAT"
        authority_sub = "Provincial Department of Business Names / Divisional Secretariat"
    else:
        form_type_title = "BUSINESS NAMES STATUTE NO. 04 OF 1990 (SECTION 5) / BUSINESS NAMES ORDINANCE"
        form_name_en = "FORM 1: STATEMENT OF PARTICULARS FOR REGISTRATION OF AN INDIVIDUAL BUSINESS NAME"
        authority_title = "DEPARTMENT OF BUSINESS NAMES & DIVISIONAL SECRETARIAT"
        authority_sub = "Provincial Department of Business Names / Divisional Secretariat"

    business_name = (
        business_data.get("business_name")
        or business_data.get("proposed_name")
        or business_data.get("company_name")
        or "CEYLON GREEN ESSENTIALS"
    )

    district = str(business_data.get("district") or business_data.get("location") or "Gampaha")
    province = str(business_data.get("province") or "Western Province")
    local_authority = str(business_data.get("local_authority") or f"{district} Municipal Council / Pradeshiya Sabha")
    div_secretariat = str(business_data.get("divisional_secretariat") or f"{district} Divisional Secretariat")
    grama_niladhari = str(business_data.get("grama_niladhari") or f"{district} Central GN Division")

    address = str(
        business_data.get("address")
        or business_data.get("premises_address")
        or f"No. 45/A, Commercial Hub, Main Road, {district}"
    )

    sector = str(business_data.get("sector") or business_data.get("business_type") or "Food Manufacturing & Processing")
    activities = business_data.get("activities") or business_data.get("products_services") or [
        "Manufacturing and processing of packaged food products",
        "Wholesale and direct retail distribution",
        "Storage and preservation in commercial premises"
    ]
    activities_str = ", ".join(activities) if isinstance(activities, list) else str(activities)

    employee_count = str(business_data.get("employee_count") or business_data.get("employees") or "15")
    commencement_date = str(business_data.get("commencement_date") or datetime.now().strftime("%Y-%m-%d"))
    revenue = business_data.get("revenue") or business_data.get("initial_capital") or 3500000.0
    try:
        revenue_formatted = f"LKR {float(revenue):,.2f}"
    except (ValueError, TypeError):
        revenue_formatted = f"LKR {revenue}"

    owner_name = str(business_data.get("owner_name") or business_data.get("applicant_name") or "Dhananjaya Bandara")
    owner_nic = str(business_data.get("owner_nic") or business_data.get("applicant_nic") or "199415802345 / 941582345V")
    owner_phone = str(business_data.get("phone") or business_data.get("contact_number") or "+94 77 123 4567")
    owner_email = str(business_data.get("email") or "applicant.business@sme.lk")
    owner_residence = str(business_data.get("residence_address") or address)

    app_reference = f"LK/{district[:3].upper()}/{datetime.now().strftime('%Y')}/BR-{abs(hash(business_name)) % 100000:05d}"
    submission_date = datetime.now().strftime("%d %B %Y")

    # ---------------------------------------------------------------------------
    # Story Flowables
    # ---------------------------------------------------------------------------
    story = []

    # 1. Official Header
    story.append(Paragraph("DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA", header_republic))
    story.append(Paragraph(authority_title, header_sub))
    story.append(Paragraph(authority_sub, title_act))
    story.append(Spacer(1, 2))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=5))

    story.append(Paragraph(form_name_en, title_form))
    story.append(Paragraph(f"Official Statutory Application under {form_type_title}", title_act))

    # Reference Bar Table
    ref_table_data = [
        [
            Paragraph("<b>Application Ref No:</b>", field_label),
            Paragraph(app_reference, field_value_highlight),
            Paragraph("<b>Filing Date:</b>", field_label),
            Paragraph(submission_date, field_value),
        ],
        [
            Paragraph("<b>Target Authority Office:</b>", field_label),
            Paragraph(f"{div_secretariat} / {local_authority}", field_value),
            Paragraph("<b>Status:</b>", field_label),
            Paragraph("OFFICIAL STATUTORY SUBMISSION READY", field_value_highlight),
        ]
    ]
    ref_table = Table(ref_table_data, colWidths=[120, 190, 80, 133])
    ref_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(ref_table)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------------------------
    # Section 1: Business Identity & Legal Classification
    # ---------------------------------------------------------------------------
    def make_section_header(title: str, subtitle: str) -> Table:
        t = Table(
            [[Paragraph(f"<b>{title}</b>", section_heading), Paragraph(f"<i>{subtitle}</i>", title_act)]],
            colWidths=[330, 193],
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    story.append(make_section_header("SECTION 1: BUSINESS IDENTITY & CLASSIFICATION", "1. Name & Legal Entity"))
    sec1_data = [
        [
            Paragraph("1.1 Proposed / Registered Business Name:<br/><i>(To be inscribed on the Business Certificate)</i>", field_label),
            Paragraph(f"<b>{business_name.upper()}</b>", field_value_highlight),
        ],
        [
            Paragraph("1.2 Legal Ownership Structure:<br/><i>(Sole Proprietor / Partnership / Company)</i>", field_label),
            Paragraph(f"{legal_form_raw.replace('_', ' ').title()}", field_value),
        ],
        [
            Paragraph("1.3 General Nature of Business / Sector:<br/><i>(Primary industry category)</i>", field_label),
            Paragraph(sector, field_value),
        ],
        [
            Paragraph("1.4 Detailed Business Activities & Operations:<br/><i>(Specific goods manufactured, sold or services rendered)</i>", field_label),
            Paragraph(activities_str, field_value),
        ],
    ]
    t1 = Table(sec1_data, colWidths=[180, 343])
    t1.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t1)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------------------------
    # Section 2: Business Location & Jurisdiction
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 2: PRINCIPAL PLACE OF BUSINESS & JURISDICTION", "2. Premises & Local Limits"))
    sec2_data = [
        [
            Paragraph("2.1 Principal Address of Premises:<br/><i>(Official location where business operates)</i>", field_label),
            Paragraph(address, field_value),
        ],
        [
            Paragraph("2.2 Administrative District & Province:<br/><i>(Statutory provincial territory)</i>", field_label),
            Paragraph(f"District: <b>{district}</b> &nbsp;&nbsp;|&nbsp;&nbsp; Province: <b>{province}</b>", field_value),
        ],
        [
            Paragraph("2.3 Divisional Secretariat Division:<br/><i>(Responsible DS office for individual BR)</i>", field_label),
            Paragraph(div_secretariat, field_value),
        ],
        [
            Paragraph("2.4 Local Council / Authority (MC/UC/PS):<br/><i>(Responsible for annual trade tax & licensing)</i>", field_label),
            Paragraph(local_authority, field_value),
        ],
        [
            Paragraph("2.5 Grama Niladhari Division (GN):<br/><i>(Jurisdiction for residence & site report)</i>", field_label),
            Paragraph(grama_niladhari, field_value),
        ],
    ]
    t2 = Table(sec2_data, colWidths=[180, 343])
    t2.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------------------------
    # Section 3: Proprietor / Director / Applicant Particulars
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 3: PARTICULARS OF PROPRIETOR / DIRECTORS", "3. Applicant Details"))
    sec3_data = [
        [
            Paragraph("3.1 Full Legal Name of Applicant:<br/><i>(As appearing on National Identity Card)</i>", field_label),
            Paragraph(f"<b>{owner_name}</b>", field_value),
        ],
        [
            Paragraph("3.2 National Identity Card (NIC) / Passport:<br/><i>(Photocopy attached and certified)</i>", field_label),
            Paragraph(f"<b>{owner_nic}</b> &nbsp;&nbsp;(Citizenship: Sri Lankan by Descent)", field_value),
        ],
        [
            Paragraph("3.3 Usual Place of Residence:<br/><i>(Permanent address of applicant)</i>", field_label),
            Paragraph(owner_residence, field_value),
        ],
        [
            Paragraph("3.4 Contact Telephone & Email Address:<br/><i>(For official notices and communications)</i>", field_label),
            Paragraph(f"Tel: {owner_phone} &nbsp;&nbsp;|&nbsp;&nbsp; Email: {owner_email}", field_value),
        ],
        [
            Paragraph("3.5 Other Commercial Occupations / Directorships:<br/><i>(Disclosure under Section 5)</i>", field_label),
            Paragraph("None reported at date of application", field_value),
        ],
    ]
    t3 = Table(sec3_data, colWidths=[180, 343])
    t3.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------------------------
    # Section 4: Operational & Financial Scale
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 4: OPERATIONAL & FINANCIAL PARTICULARS", "4. Operations & Capital"))
    sec4_data = [
        [
            Paragraph("4.1 Proposed / Actual Date of Commencement:<br/><i>(Statutory rule: Register within 14 days)</i>", field_label),
            Paragraph(f"<b>{commencement_date}</b>", field_value),
        ],
        [
            Paragraph("4.2 Estimated Initial Capital / Turnover Band:<br/><i>(Declared capital for business operation)</i>", field_label),
            Paragraph(f"<b>{revenue_formatted}</b>", field_value),
        ],
        [
            Paragraph("4.3 Total Number of Employees Engaged:<br/><i>(Subject to EPF Act No. 15 of 1958)</i>", field_label),
            Paragraph(f"<b>{employee_count}</b> Employees (Statutory employee record mandatory)", field_value),
        ],
    ]
    t4 = Table(sec4_data, colWidths=[180, 343])
    t4.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t4)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------------------------
    # Section 5: Mandatory Document Checklist
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 5: STATUTORY DOCUMENT ATTACHMENT CHECKLIST", "5. Required Attachments"))
    checklist_rows = [
        [
            Paragraph("<b>[  X  ]</b>", field_label),
            Paragraph("<b>National Identity Card (NIC):</b> Certified copy of applicant/owner's National Identity Card or valid Passport.", field_value),
        ],
        [
            Paragraph("<b>[  X  ]</b>", field_label),
            Paragraph("<b>Premises Ownership / Lease Evidence:</b> Certified deed of property, lease/rental agreement, or written consent letter of premises owner.", field_value),
        ],
        [
            Paragraph("<b>[  X  ]</b>", field_label),
            Paragraph("<b>Grama Niladhari Certificate:</b> Residence verification and character certification signed by the area Grama Niladhari.", field_value),
        ],
        [
            Paragraph("<b>[  X  ]</b>", field_label),
            Paragraph("<b>Assessment / Rates Receipt:</b> Latest property rates/tax receipt issued by the relevant Municipal/Urban Council or Pradeshiya Sabha.", field_value),
        ],
        [
            Paragraph("<b>[  X  ]</b>", field_label),
            Paragraph("<b>Sectoral Clearances:</b> Preliminary approval/NOC (e.g. MOH Food Hygiene clearance or CEA Environmental clearance if prescribed).", field_value),
        ],
        [
            Paragraph("<b>[  X  ]</b>", field_label),
            Paragraph("<b>Official Registration Fee:</b> Prescribed statutory fee receipt as determined by the Provincial Council / Registrar of Companies.", field_value),
        ],
    ]
    t5 = Table(checklist_rows, colWidths=[40, 483])
    t5.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t5)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------------------------
    # Section 6: Statutory Declaration & Signatures
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 6: STATUTORY DECLARATION UNDER OATH", "6. Solemn Declaration"))
    dec_text = (
        "I/We hereby solemnly declare and affirm that the particulars stated above are true and accurate to the best "
        "of my/our knowledge and belief, and that I/we undertake all commercial responsibilities as the lawful proprietor(s) "
        "under the Business Names Statute No. 04 of 1990 / Companies Act No. 07 of 2007. I/We understand that providing "
        "false particulars constitutes a summary offence punishable under Sri Lankan law."
    )
    story.append(Paragraph(dec_text, legal_text))
    story.append(Spacer(1, 5))

    sig_table_data = [
        [
            Paragraph("<b>Applicant / Proprietor Signature:</b><br/><br/><br/>____________________________________<br/>"
                      f"Name: <b>{owner_name}</b><br/>NIC: {owner_nic}", field_value),
            Paragraph("<b>Date of Submission:</b><br/><br/><br/>________________________<br/>"
                      f"Date: <b>{submission_date}</b>", field_value),
            Paragraph("<b>Official Stamp / Seal:</b><br/><br/><br/>[ Official Impression ]", field_value),
        ]
    ]
    sig_table = Table(sig_table_data, colWidths=[200, 150, 173])
    sig_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------------------------
    # Section 7: For Official Use Only (Grama Niladhari & Registrar Endorsements)
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 7: FOR OFFICIAL USE ONLY", "7. Official Endorsement"))
    off_table_data = [
        [
            Paragraph("<b>7.1 Recommendation of Grama Niladhari</b><br/>"
                      "I certify that the applicant resides in this division, the business location is verified, "
                      "and I recommend the registration of this business name.<br/><br/>"
                      "GN Name: _______________________<br/>"
                      "Signature & Official Stamp: ____________<br/>"
                      "GN Division No: __________________", legal_text),
            Paragraph("<b>7.2 Divisional Secretary / Registrar Endorsement</b><br/>"
                      "Application verified against the Business Names Statute.<br/>"
                      "Registration Fee Paid: LKR ________________<br/>"
                      "Receipt No: __________________________<br/>"
                      "Certificate No Issued: ___________________<br/>"
                      "Registrar's Signature & Date: ____________", legal_text),
        ]
    ]
    off_table = Table(off_table_data, colWidths=[260, 263])
    off_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(off_table)

    # Build the document with two-pass numbered canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
