"""
Official Sri Lanka Institutional Registration Stage-Specific PDF Generator.
Produces authentic, government-styled statutory forms for:
- Stage 1: Form WP/BN/01 (Business Name Search & Reservation Inquiry Application)
- Stage 2: Grama Niladhari Assessment & Residence Verification Report (වසමේ වාර්තාව)
- Stage 3: Statutory Form 1 (Statement of Particulars)
- Stage 4: Municipal / Urban Council Trade Tax & Health License Application
- Stage 5: RAMIS Taxpayer Registration & Department of Labour Form D (EPF/ETF)
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict

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

from backend.app.compliance.br_form_generator import generate_br_application_pdf


class StageNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for running page numbers, header, and official watermark/footer."""

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
        self.setFillColor(colors.HexColor("#475569"))

        # Footer divider line
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 42, 595 - 36, 42)

        # Footer text
        footer_text = (
            "Democratic Socialist Republic of Sri Lanka • Official Institutional Registration Dossier "
            "(Western Province • SME360 Decision Support)"
        )
        self.drawString(36, 30, footer_text)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(595 - 36, 30, page_str)
        self.restoreState()


def generate_stage_form_pdf(stage: int, payload: Dict[str, Any]) -> bytes:
    """Generates an official government-styled PDF for stages 1 to 5."""
    if stage == 3:
        return generate_br_application_pdf(payload)

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

    header_republic = ParagraphStyle(
        "RepublicHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=1,
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
        fontSize=13,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#0284C7") if stage == 1 else colors.HexColor("#4338CA") if stage == 2 else colors.HexColor("#D97706") if stage == 4 else colors.HexColor("#7E22CE"),
        spaceAfter=3,
    )

    title_sinhala = ParagraphStyle(
        "TitleSinhala",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#475569"),
        spaceAfter=6,
    )

    sec_hdr_style = ParagraphStyle(
        "SecHdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )

    field_label = ParagraphStyle(
        "FLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#334155"),
    )

    field_value = ParagraphStyle(
        "FValue",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )

    legal_text = ParagraphStyle(
        "LegalText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#475569"),
    )

    story = []

    def make_section_header(title_en: str, title_si: str = ""):
        label = f"<b>{title_en}</b>"
        if title_si:
            label += f" &nbsp;|&nbsp; <font size=7 color='#64748B'>{title_si}</font>"
        t = Table([[Paragraph(label, sec_hdr_style)]], colWidths=[523])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("LINELEFT", (0, 0), (0, -1), 3, colors.HexColor("#0284C7") if stage == 1 else colors.HexColor("#4338CA") if stage == 2 else colors.HexColor("#D97706") if stage == 4 else colors.HexColor("#7E22CE")),
        ]))
        return t

    # Extract common variables
    b_name = payload.get("business_name", "CEYLON ARTISAN BAKEHOUSE")
    legal_form = payload.get("legal_form", "sole_proprietorship").replace("_", " ").title()
    sector = payload.get("sector", "Commercial SME Enterprise")
    ds = payload.get("divisional_secretariat", "Thimbirigasyaya Divisional Secretariat")
    gn = payload.get("grama_niladhari", "Havelock Town (GN Division 512)")
    la = payload.get("local_authority", "Colombo Municipal Council")
    addr = payload.get("address", "Colombo 04, Sri Lanka")
    owner_name = payload.get("owner_name", "Dhananjaya Bandara")
    owner_nic = payload.get("owner_nic", "199415802345")
    phone = payload.get("phone", "+94 77 123 4567")
    email = payload.get("email", "applicant@sme.lk")
    res_addr = payload.get("residence_address", "Colombo, Sri Lanka")
    today_str = datetime.today().strftime("%Y-%m-%d")

    # ---------------------------------------------------------------------------
    # HEADER BANNER
    # ---------------------------------------------------------------------------
    story.append(Paragraph("DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA", header_republic))
    story.append(Paragraph("WESTERN PROVINCIAL COUNCIL — DEPARTMENT OF BUSINESS NAMES", header_sub))

    if stage == 1:
        story.append(Paragraph("APPLICATION FOR BUSINESS NAME SEARCH & RESERVATION (FORM WP/BN/01)", title_form))
        story.append(Paragraph("ව්‍යාපාර නාමය සෙවීම සහ වෙන්කිරීමේ ව්‍යවස්ථාපිත අයදුම්පත (Section 4, WP Statute No. 04 of 1990)", title_sinhala))
    elif stage == 2:
        story.append(Paragraph("GRAMA NILADHARI ASSESSMENT & RESIDENCE VERIFICATION REPORT", title_form))
        story.append(Paragraph("ග්‍රාම නිලධාරී පරිශ්‍ර පරීක්ෂාව සහ පදිංචි සහතික වාර්තාව (වසමේ වාර්තාව)", title_sinhala))
    elif stage == 4:
        story.append(Paragraph("MUNICIPAL / URBAN COUNCIL TRADE TAX & LICENSE APPLICATION", title_form))
        story.append(Paragraph("පළාත් පාලන ආයතන වෙළඳ බද්ද සහ සෞඛ්‍ය බලපත්‍ර අයදුම්පත (Municipal Councils Ordinance No. 29 of 1947)", title_sinhala))
    else:  # stage == 5
        story.append(Paragraph("INLAND REVENUE RAMIS TIN & LABOUR EPF/ETF FORM D REGISTRATION", title_form))
        story.append(Paragraph("දේශීය ආදායම් TIN අංකය සහ කම්කරු දෙපාර්තමේන්තු සේවක අර්ථසාධක ලියාපදිංචි අයදුම්පත", title_sinhala))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=8))

    # ---------------------------------------------------------------------------
    # SECTION 1: APPLICANT & BUSINESS PROFILE
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 1: GENERAL ENTERPRISE & APPLICANT PARTICULARS", "ව්‍යාපාරික හා අයදුම්කරුගේ තොරතුරු"))
    story.append(Spacer(1, 3))

    table_data_s1 = [
        [
            Paragraph("<b>1.1 Proposed Trading Name:</b>", field_label),
            Paragraph(f"<b>{b_name}</b>", field_value),
            Paragraph("<b>1.2 Legal Classification:</b>", field_label),
            Paragraph(legal_form, field_value),
        ],
        [
            Paragraph("<b>1.3 Commercial Sector:</b>", field_label),
            Paragraph(sector, field_value),
            Paragraph("<b>1.4 Target Div. Secretariat:</b>", field_label),
            Paragraph(ds, field_value),
        ],
        [
            Paragraph("<b>1.5 Grama Niladhari Division:</b>", field_label),
            Paragraph(gn, field_value),
            Paragraph("<b>1.6 Local Municipal Council:</b>", field_label),
            Paragraph(la, field_value),
        ],
        [
            Paragraph("<b>1.7 Business Premises Address:</b>", field_label),
            Paragraph(addr, field_value),
            Paragraph("<b>1.8 Owner / Declarant Name:</b>", field_label),
            Paragraph(f"<b>{owner_name}</b>", field_value),
        ],
        [
            Paragraph("<b>1.9 National Identity Card (NIC):</b>", field_label),
            Paragraph(f"<b>{owner_nic}</b>", field_value),
            Paragraph("<b>1.10 Contact Phone & Email:</b>", field_label),
            Paragraph(f"{phone} | {email}", field_value),
        ],
    ]

    t1 = Table(table_data_s1, colWidths=[130, 140, 120, 133])
    t1.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
    ]))
    story.append(t1)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------
    # SECTION 2: STAGE-SPECIFIC PARTICULARS
    # ---------------------------------------------------------------------------
    if stage == 1:
        story.append(make_section_header("SECTION 2: NAME SEARCH & RESERVATION INQUIRY (FORM WP/BN/01)", "නාම සෙවීම හා වෙන්කිරීම"))
        story.append(Spacer(1, 3))
        alt1 = payload.get("alt_name_1", "CEYLON HERITAGE BAKERY")
        alt2 = payload.get("alt_name_2", "ISLAND ARTISAN BAKES")
        meaning = payload.get("name_meaning", "Artisan traditional baking with high standards")
        scripts = payload.get("language_scripts", "English & Sinhala")
        search_date = payload.get("search_date", today_str)

        table_data_stage = [
            [Paragraph("<b>2.1 1st Proposed Trading Name:</b>", field_label), Paragraph(f"<b>{b_name}</b>", field_value)],
            [Paragraph("<b>2.2 2nd Alternative Name Choice:</b>", field_label), Paragraph(alt1, field_value)],
            [Paragraph("<b>2.3 3rd Alternative Name Choice:</b>", field_label), Paragraph(alt2, field_value)],
            [Paragraph("<b>2.4 Meaning & Derivation of Name:</b>", field_label), Paragraph(meaning, field_value)],
            [Paragraph("<b>2.5 Language Medium & Scripts:</b>", field_label), Paragraph(scripts, field_value)],
            [Paragraph("<b>2.6 Reservation Validity Period:</b>", field_label), Paragraph("3 Calendar Months from date of official approval (Section 4)", field_value)],
            [Paragraph("<b>2.7 Prescribed Statutory Duty:</b>", field_label), Paragraph("LKR 250 - 500 (Payable at Divisional Secretariat Cashier)", field_value)],
            [Paragraph("<b>2.8 Inquiry Lodgement Date:</b>", field_label), Paragraph(search_date, field_value)],
        ]
        t_stage = Table(table_data_stage, colWidths=[160, 363])
    elif stage == 2:
        story.append(make_section_header("SECTION 2: PREMISES VERIFICATION & RESIDENCE REPORT", "ග්‍රාම නිලධාරී පරිශ්‍ර පරීක්ෂාව"))
        story.append(Spacer(1, 3))
        own_type = payload.get("ownership_type", "commercial_lease").replace("_", " ").title()
        landlord = payload.get("landlord_name", "Mr. K. A. Perera")
        landlord_phone = payload.get("landlord_phone", "+94 77 345 6789")
        deed_no = payload.get("deed_lease_no", "Lease Agreement No. 2024/481")
        electoral_no = payload.get("electoral_no", "EL/COL/512/048")
        house_no = payload.get("house_no", "No. 12/B")
        res_duration = payload.get("residence_duration", "6 Years")

        table_data_stage = [
            [Paragraph("<b>2.1 Premises Legal Tenancy Title:</b>", field_label), Paragraph(own_type, field_value)],
            [Paragraph("<b>2.2 Property Owner / Landlord:</b>", field_label), Paragraph(f"{landlord} ({landlord_phone})", field_value)],
            [Paragraph("<b>2.3 Title Deed / Lease Agreement Ref:</b>", field_label), Paragraph(deed_no, field_value)],
            [Paragraph("<b>2.4 Assessment House / Premises No:</b>", field_label), Paragraph(house_no, field_value)],
            [Paragraph("<b>2.5 Electoral Register Serial No:</b>", field_label), Paragraph(electoral_no, field_value)],
            [Paragraph("<b>2.6 Applicant Residence Address:</b>", field_label), Paragraph(res_addr, field_value)],
            [Paragraph("<b>2.7 Period of Continuous Residence:</b>", field_label), Paragraph(res_duration, field_value)],
            [Paragraph("<b>2.8 Inspection & Boundary Pass:</b>", field_label), Paragraph("Physical inspection conducted; boundaries and non-residential compliance certified.", field_value)],
        ]
        t_stage = Table(table_data_stage, colWidths=[160, 363])
    elif stage == 4:
        story.append(make_section_header("SECTION 2: MUNICIPAL TRADE TAX & PUBLIC HEALTH ASSESSMENT", "වෙළඳ බදු සහ සෞඛ්‍ය පරීක්ෂාව"))
        story.append(Spacer(1, 3))
        assess_no = payload.get("assessment_no", "CMC/WR/2026/8941")
        br_no = payload.get("br_certificate_no", "WP/COL/2026/10492")
        trade_cat = payload.get("trade_category", "Food Manufacturing & Bakery Products")
        floor_area = payload.get("floor_area", "1,250 Sq. Ft.")
        phi_div = payload.get("phi_division", "PHI Range 03 - Thimbirigasyaya")
        food_handlers = str(payload.get("food_handlers_certified", 5))
        fire = payload.get("fire_safety", "Fire Extinguishers Installed (CO2 + Foam)")
        waste = payload.get("waste_disposal", "Municipal Council Daily Collection & Sealed Grease Trap")

        table_data_stage = [
            [Paragraph("<b>2.1 Municipal Assessment No:</b>", field_label), Paragraph(assess_no, field_value)],
            [Paragraph("<b>2.2 Business Registration (BR) No:</b>", field_label), Paragraph(br_no, field_value)],
            [Paragraph("<b>2.3 Trade License Classification:</b>", field_label), Paragraph(trade_cat, field_value)],
            [Paragraph("<b>2.4 Covered Business Floor Area:</b>", field_label), Paragraph(floor_area, field_value)],
            [Paragraph("<b>2.5 PHI Range Division:</b>", field_label), Paragraph(phi_div, field_value)],
            [Paragraph("<b>2.6 Food Handlers Medical Pass:</b>", field_label), Paragraph(f"{food_handlers} Certified Personnel with Medical Reports", field_value)],
            [Paragraph("<b>2.7 Fire Safety Equipment:</b>", field_label), Paragraph(fire, field_value)],
            [Paragraph("<b>2.8 Solid Waste & Effluent Disposal:</b>", field_label), Paragraph(waste, field_value)],
        ]
        t_stage = Table(table_data_stage, colWidths=[160, 363])
    else:  # stage == 5
        story.append(make_section_header("SECTION 2: RAMIS TAXPAYER TIN & LABOUR EPF/ETF PARTICULARS", "TIN සහ සේවක අර්ථසාධක ලියාපදිංචිය"))
        story.append(Spacer(1, 3))
        tax_type = payload.get("taxpayer_type", "Sole Proprietorship Enterprise")
        ird_unit = payload.get("ird_unit", "Colombo South Metropolitan Unit")
        tin_status = payload.get("tin_status", "New RAMIS TIN Application Required")
        labour = payload.get("labour_office", "Colombo South Labour Office (Narahenpita)")
        payroll = str(payload.get("monthly_payroll", 350000))
        emp_count = str(payload.get("employee_count", 5))
        b_name_bank = payload.get("bank_name", "Commercial Bank of Ceylon")
        b_acc = payload.get("bank_account", "1000849201")

        table_data_stage = [
            [Paragraph("<b>2.1 Taxpayer Classification:</b>", field_label), Paragraph(tax_type, field_value)],
            [Paragraph("<b>2.2 RAMIS TIN Registration Status:</b>", field_label), Paragraph(tin_status, field_value)],
            [Paragraph("<b>2.3 IRD Metropolitan / Regional Unit:</b>", field_label), Paragraph(ird_unit, field_value)],
            [Paragraph("<b>2.4 Department of Labour District:</b>", field_label), Paragraph(labour, field_value)],
            [Paragraph("<b>2.5 Active Employee Headcount:</b>", field_label), Paragraph(f"{emp_count} Liable Employees", field_value)],
            [Paragraph("<b>2.6 Estimated Monthly Payroll:</b>", field_label), Paragraph(f"LKR {payroll} (Subject to 12% + 8% EPF, 3% ETF)", field_value)],
            [Paragraph("<b>2.7 Designated Settlement Bank:</b>", field_label), Paragraph(b_name_bank, field_value)],
            [Paragraph("<b>2.8 Commercial Bank Account No:</b>", field_label), Paragraph(b_acc, field_value)],
        ]
        t_stage = Table(table_data_stage, colWidths=[160, 363])

    t_stage.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
    ]))
    story.append(t_stage)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------
    # SECTION 3: STATUTORY DECLARATION & SIGNATURES
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 3: STATUTORY DECLARATION & SUBMISSION SIGNATURES", "ප්‍රකාශය සහ අත්සන්"))
    story.append(Spacer(1, 3))

    dec_text = (
        "I hereby solemnly declare that the particulars furnished above are true and correct to the best of my knowledge "
        "and belief, and are submitted in compliance with applicable Western Provincial Statutes and Sri Lankan regulations."
    )
    story.append(Paragraph(dec_text, legal_text))
    story.append(Spacer(1, 6))

    sig_data = [
        [
            Paragraph("<b>Applicant / Declarant Signature:</b><br/><br/><br/>____________________________________<br/>"
                      f"Name: <b>{owner_name}</b><br/>NIC: <b>{owner_nic}</b>", field_value),
            Paragraph("<b>Submission Date:</b><br/><br/><br/>________________________<br/>"
                      f"Date: <b>{today_str}</b>", field_value),
            Paragraph("<b>Official Receipt / Stamp:</b><br/><br/><br/>[ Departmental Impression ]", field_value),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[200, 150, 173])
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
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------
    # SECTION 4: OFFICIAL CERTIFICATION & ENDORSEMENT
    # ---------------------------------------------------------------------------
    story.append(make_section_header("SECTION 4: FOR OFFICIAL REGISTRY USE ONLY", "නිල භාවිතය සඳහා පමණි"))
    story.append(Spacer(1, 3))

    if stage == 1:
        off_text_1 = "<b>4.1 Name Availability & Search Officer:</b><br/>Registry verified. Proposed name is distinct and not prohibited under Section 4.<br/><br/>Officer Signature: _______________ &nbsp;&nbsp; Date: _________"
        off_text_2 = "<b>4.2 Approval of Divisional Secretary:</b><br/>Name reserved for three (3) months.<br/>Fee Paid: LKR _______ &nbsp;&nbsp; Receipt No: _________<br/>Secretary Signature: ________________"
    elif stage == 2:
        off_text_1 = "<b>4.1 Grama Niladhari Certification:</b><br/>Premises visited and applicant residence verified within division.<br/><br/>GN Signature: __________________ &nbsp;&nbsp; Stamp: [ Seal ]"
        off_text_2 = "<b>4.2 Divisional Secretariat Registration Unit:</b><br/>GN Assessment report accepted for Form 1 docket.<br/>Officer Signature: _______________ &nbsp;&nbsp; Date: _________"
    elif stage == 4:
        off_text_1 = "<b>4.1 Public Health Inspector (PHI) Pass:</b><br/>Food hygiene / premises safety compliance certified.<br/><br/>PHI Signature: __________________ &nbsp;&nbsp; MOH Seal: [ Seal ]"
        off_text_2 = "<b>4.2 Municipal Revenue Licensing Officer:</b><br/>Trade tax assessed and operating license sanctioned.<br/>Duty Paid: LKR _______ &nbsp;&nbsp; License No: _________"
    else:  # stage == 5
        off_text_1 = "<b>4.1 Inland Revenue Department (RAMIS):</b><br/>Taxpayer file registered. TIN certificate generated.<br/><br/>Assessor Signature: ____________ &nbsp;&nbsp; TIN Issued: _________"
        off_text_2 = "<b>4.2 Department of Labour (EPF Division):</b><br/>Employer Form D verified and registration active.<br/>EPF Reg No: ________________ &nbsp;&nbsp; Officer: _________"

    off_table = Table([[Paragraph(off_text_1, legal_text), Paragraph(off_text_2, legal_text)]], colWidths=[260, 263])
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

    doc.build(story, canvasmaker=StageNumberedCanvas)
    return buffer.getvalue()
