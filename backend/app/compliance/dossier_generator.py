"""
SME Legal Compliance & Business Registration Guidance Dossier Generator
AI-Driven Business Lifecycle Decision Support System — Component 2
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


class DossierNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for page numbers, running header, and legal footer."""

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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Top Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(36, 810, "SME360 AI LegalTech — Compliance & Registration Dossier (Western Province)")
            self.drawRightString(595 - 36, 810, "Official Institutional Decision-Support")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 804, 595 - 36, 804)

        # Bottom Footer Divider & Text
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 42, 595 - 36, 42)

        footer_text = "CONFIDENTIAL & PRIVILEGED — Generated for Sri Lankan SME Institutional Regulatory Navigation"
        self.drawString(36, 30, footer_text)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(595 - 36, 30, page_str)
        self.restoreState()


def generate_compliance_dossier_pdf(evaluation_data: Dict[str, Any]) -> bytes:
    """
    Constructs an authoritative, publication-quality Legal Compliance & 
    Business Registration Guidance Dossier in PDF format.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        alignment=0,
        textColor=colors.HexColor("#0F172A"),
    )
    sub_title_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    sec_header = ParagraphStyle(
        "SecHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E3A8A"),
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
    )
    cell_normal = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#334155"),
    )
    cell_badge_ready = ParagraphStyle(
        "BadgeReady",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#065F46"),
    )
    cell_badge_req = ParagraphStyle(
        "BadgeReq",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#92400E"),
    )

    context = evaluation_data.get("business_context") or {}
    reg_guidance = evaluation_data.get("registration_guidance") or {}
    sources = evaluation_data.get("source_discovery") or []
    summary = evaluation_data.get("summary") or {}

    b_type = str(context.get("business_type") or context.get("sector") or "General SME").title()
    district = str(context.get("district") or reg_guidance.get("district") or "Colombo")
    scale = str(context.get("business_scale") or context.get("business_size") or "Micro").title()
    legal_form = reg_guidance.get("recommended_legal_form", "Sole Proprietorship")
    target_office = reg_guidance.get("target_office", "Divisional Secretariat")
    statute = reg_guidance.get("legal_basis", "Business Names Statute of the Western Province No. 04 of 1990")
    est_fees = reg_guidance.get("estimated_fees", "LKR 500 - 2,500")
    est_time = reg_guidance.get("estimated_timeline", "1 - 3 Business Days")

    story = []

    # ---------------------------------------------------------------------------
    # HEADER BANNER
    # ---------------------------------------------------------------------------
    banner_data = [
        [
            Paragraph("<b>DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA — WESTERN PROVINCE</b><br/>"
                      "<b>AI-ASSISTED SME REGULATORY COMPLIANCE &amp; REGISTRATION GUIDANCE DOSSIER</b>", title_style),
            Paragraph(f"<b>Issue Date:</b> {datetime.now().strftime('%Y-%m-%d')}<br/>"
                      f"<b>Jurisdiction:</b> Western Province<br/>"
                      f"<b>Status:</b> Official Advisory Record", cell_normal)
        ]
    ]
    banner_table = Table(banner_data, colWidths=[380, 143])
    banner_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#2563EB")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------
    # SECTION 1: BUSINESS PROFILE & AI RECOMMENDATION SUMMARY
    # ---------------------------------------------------------------------------
    story.append(Paragraph("<b>1. BUSINESS IDENTITY &amp; RECOMMENDED LEGAL PATHWAY</b>", sec_header))
    story.append(Spacer(1, 3))

    profile_data = [
        [
            Paragraph("<b>Business Activity:</b>", cell_bold), Paragraph(b_type, cell_normal),
            Paragraph("<b>Administrative District:</b>", cell_bold), Paragraph(f"{district} (Western Province)", cell_normal),
        ],
        [
            Paragraph("<b>Business Scale:</b>", cell_bold), Paragraph(scale, cell_normal),
            Paragraph("<b>Physical Premises:</b>", cell_bold), Paragraph("Yes (Commercial Address Declared)", cell_normal),
        ],
        [
            Paragraph("<b>AI-Recommended Legal Form:</b>", cell_bold), Paragraph(f"<b>{legal_form}</b>", cell_bold),
            Paragraph("<b>Governing Statute:</b>", cell_bold), Paragraph(statute, cell_normal),
        ],
        [
            Paragraph("<b>Target Authority &amp; Office:</b>", cell_bold), Paragraph(target_office, cell_normal),
            Paragraph("<b>Est. Cost &amp; Timeline:</b>", cell_bold), Paragraph(f"{est_fees} | {est_time}", cell_normal),
        ]
    ]
    profile_table = Table(profile_data, colWidths=[120, 140, 120, 143])
    profile_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------
    # SECTION 2: 5-STAGE OFFICIAL REGISTRATION PROCEDURE
    # ---------------------------------------------------------------------------
    story.append(Paragraph("<b>2. 5-STAGE OFFICIAL BUSINESS REGISTRATION ROADMAP</b>", sec_header))
    story.append(Spacer(1, 3))

    stages = reg_guidance.get("stages") or []
    stage_rows = [
        [
            Paragraph("<b>Stage</b>", cell_bold),
            Paragraph("<b>Procedure / Action Required</b>", cell_bold),
            Paragraph("<b>Competent Authority</b>", cell_bold),
            Paragraph("<b>Statutory Fee</b>", cell_bold),
            Paragraph("<b>Timeline</b>", cell_bold),
        ]
    ]
    for stg in stages:
        stage_rows.append([
            Paragraph(f"<b>Stage {stg.get('stage_number')}</b>", cell_bold),
            Paragraph(f"<b>{stg.get('title')}</b><br/>{stg.get('action')}", cell_normal),
            Paragraph(stg.get("authority", ""), cell_normal),
            Paragraph(stg.get("statutory_fee", ""), cell_normal),
            Paragraph(stg.get("duration", ""), cell_normal),
        ])

    stage_table = Table(stage_rows, colWidths=[50, 190, 140, 80, 63])
    stage_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(stage_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------
    # SECTION 3: PRE-FILING DOCUMENT READINESS CHECKLIST
    # ---------------------------------------------------------------------------
    story.append(Paragraph("<b>3. PRE-FILING MANDATORY DOCUMENTATION CHECKLIST</b>", sec_header))
    story.append(Spacer(1, 3))

    docs = reg_guidance.get("document_checklist") or []
    doc_rows = [
        [
            Paragraph("<b>Mandatory Document</b>", cell_bold),
            Paragraph("<b>Statutory Purpose / Regulatory Requirement</b>", cell_bold),
            Paragraph("<b>Audit Status</b>", cell_bold),
        ]
    ]
    for d in docs:
        badge = Paragraph("<b>[✓ READY]</b>", cell_badge_ready) if d.get("status") == "READY" else Paragraph("<b>[⚠ REQUIRED]</b>", cell_badge_req)
        doc_rows.append([
            Paragraph(f"<b>{d.get('name')}</b><br/><i>{d.get('name_si', '')}</i>", cell_normal),
            Paragraph(d.get("purpose", ""), cell_normal),
            badge,
        ])

    doc_table = Table(doc_rows, colWidths=[180, 263, 80])
    doc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------
    # SECTION 4: APPLICABLE STATUTORY RULES & INSTITUTIONAL GUIDANCE
    # ---------------------------------------------------------------------------
    story.append(Paragraph("<b>4. GROUND-TRUTH LEGAL RULES &amp; INSTITUTIONAL DIRECTIVES</b>", sec_header))
    story.append(Spacer(1, 3))

    rule_rows = [
        [
            Paragraph("<b>Statutory Act / Law</b>", cell_bold),
            Paragraph("<b>Mandate &amp; Regulatory Purpose</b>", cell_bold),
            Paragraph("<b>Action Required / Target Office</b>", cell_bold),
        ]
    ]

    for s in sources[:4]:
        ag = s.get("action_guidance") or {}
        rule_rows.append([
            Paragraph(f"<b>{s.get('title')}</b><br/>Ref: {s.get('source_id')}", cell_normal),
            Paragraph(ag.get("rule_purpose", "Statutory compliance mandate."), cell_normal),
            Paragraph(f"<b>Action:</b> {ag.get('action_needed')}<br/><b>Target:</b> {ag.get('where_to_go')}<br/><b>Office:</b> {ag.get('office_location')}", cell_normal),
        ])

    rule_table = Table(rule_rows, colWidths=[150, 203, 170])
    rule_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(rule_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------
    # SECTION 5: LEGAL DISCLAIMER & SUBMISSION SIGN-OFF
    # ---------------------------------------------------------------------------
    sign_data = [
        [
            Paragraph("<b>Legal Decision-Support Disclaimer:</b><br/>"
                      "This compliance dossier is generated by SME360 AI LegalTech based on verified statutory enactments "
                      "and provincial datasets. It serves as institutional guidance for pre-submission readiness and does not "
                      "substitute for formal statutory certification issued by the Divisional Secretary or Registrar of Companies.", cell_normal),
            Paragraph("<b>Applicant Verification Signature:</b><br/><br/>"
                      "____________________________________<br/>"
                      f"Date: {datetime.now().strftime('%Y-%m-%d')}<br/>"
                      f"Location: {district}, Western Province", cell_normal)
        ]
    ]
    sign_table = Table(sign_data, colWidths=[330, 193])
    sign_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(sign_table)

    doc.build(story, canvasmaker=DossierNumberedCanvas)
    return buffer.getvalue()
