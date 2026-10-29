import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from backend.services.business_plan_generator.chart_generator import BusinessPlanChartGenerator
from backend.services.business_plan_generator.cover_image_handler import CoverImageHandler

# Path to logo asset
LOGO_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "frontend", "src", "assets", "logo", "sme360-ai-logo.png"
))

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw total page count, 
    running header with logo, running footer, and user-provided cover page if present.
    """
    def __init__(self, *args, **kwargs):
        self.cover_info = kwargs.pop("cover_info", None)
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()  # type: ignore[attr-defined]

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        current_page = self.getPageNumber()

        # If custom cover page is provided, Page 1 is the full A4 cover page
        if self.cover_info and current_page == 1:
            self.saveState()
            try:
                img_reader = ImageReader(io.BytesIO(self.cover_info["image_bytes"]))
                geom = self.cover_info["pdf_geometry"]
                self.drawImage(
                    img_reader,
                    geom["x"],
                    geom["y"],
                    width=geom["width"],
                    height=geom["height"],
                    preserveAspectRatio=True
                )
            except Exception:
                pass
            self.restoreState()
            # Suppress headers, footers, and page numbers on cover page
            return

        # Suppress running header/footer on the business plan title page
        title_page_num = 2 if self.cover_info else 1
        if current_page <= title_page_num:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header on A4 (margins 27.6pt, usable width 540pt -> 28 to 568)
        self.setLineWidth(0.5)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.line(28, 800, 568, 800)
        
        self.drawString(28, 806, "SME360 AI — Strategic Business Plan & Decision Support Report")
        
        if os.path.exists(LOGO_PATH):
            try:
                self.drawImage(LOGO_PATH, 522, 802, width=46, height=18, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        # Running Footer
        self.line(28, 45, 568, 45)
        self.drawString(28, 32, "Confidential — Prepared by SME360 AI Decision Support Engine")
        
        if self.cover_info:
            display_page = current_page - 1
            display_total = page_count - 1
            page_text = f"Page {display_page} of {display_total}"
        else:
            page_text = f"Page {current_page} of {page_count}"
            
        self.drawRightString(568, 32, page_text)

        self.restoreState()


class BusinessPlanPDFGenerator:
    """
    Generates a professional, consultancy-grade, research-grounded PDF document
    for SME360 AI Business Plans. Follows a natural narrative structure:
    'BUSINESS STORY -> ANALYSIS -> EXPLANATION -> RECOMMENDATION -> ACTION'
    with structured comparison tables used only where genuinely necessary.
    """

    @staticmethod
    def generate_pdf(report_data: dict) -> bytes:
        raw_cover = report_data.get("cover_image") or "default"
        cover_info = None
        try:
            cover_info = CoverImageHandler.process_cover_image(raw_cover)
        except Exception:
            try:
                cover_info = CoverImageHandler.process_cover_image("default")
            except Exception:
                cover_info = None

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=27.6,
            rightMargin=27.6,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        # Professional Corporate Palette
        primary_color = colors.HexColor("#1e3a8a")  # Deep Navy Blue
        accent_blue = colors.HexColor("#2563eb")    # Vibrant Executive Blue
        dark_text = colors.HexColor("#0f172a")      # Slate 900
        muted_text = colors.HexColor("#475569")     # Slate 600
        card_bg = colors.HexColor("#f8fafc")        # Slate 50
        card_border = colors.HexColor("#cbd5e1")    # Slate 300
        grid_border = colors.HexColor("#e2e8f0")    # Slate 200

        title_style = ParagraphStyle(
            'CoverTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=30,
            textColor=primary_color,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=accent_blue,
            spaceAfter=14
        )

        h1_style = ParagraphStyle(
            'SectionH1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=primary_color,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True
        )

        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14,
            textColor=accent_blue,
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True
        )

        h3_style = ParagraphStyle(
            'SectionH3',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=7,
            spaceAfter=3,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12.5,
            textColor=dark_text,
            spaceAfter=5
        )

        bullet_style = ParagraphStyle(
            'BulletDark',
            parent=body_style,
            leftIndent=14,
            firstLineIndent=-9,
            spaceAfter=3.5
        )

        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=body_style,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            fontSize=8,
            leading=10.5
        )

        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=body_style,
            fontSize=8,
            leading=11,
            spaceAfter=0
        )

        story = []

        if cover_info:
            # Page 1 is reserved for the full-page cover image drawn by canvas
            story.append(PageBreak())

        # Helper: Creates a styled callout box
        def create_callout_box(flowables, bg=card_bg, border=card_border, padding=8):
            t = Table([[flowables]], colWidths=[540])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), bg),
                ('BOX', (0,0), (-1,-1), 1, border),
                ('PADDING', (0,0), (-1,-1), padding),
                ('TOPPADDING', (0,0), (-1,-1), padding),
                ('BOTTOMPADDING', (0,0), (-1,-1), padding),
            ]))
            return t

        # Helper: Creates a multi-metric horizontal strip (e.g. 4 metrics)
        def create_metric_strip(metrics):
            num = len(metrics)
            w = 540.0 / num
            cells = []
            for label, val, sub in metrics:
                c = [
                    Paragraph(f"<font color='#64748b' size='7'><b>{label.upper()}</b></font>", body_style),
                    Spacer(1, 1),
                    Paragraph(f"<font color='#1e3a8a' size='10.5'><b>{val}</b></font>", body_style),
                    Spacer(1, 1),
                    Paragraph(f"<font color='#475569' size='7'>{sub}</font>", body_style)
                ]
                cells.append(c)
            t = Table([cells], colWidths=[w]*num)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            return t

        # =========================================================================
        # COVER PAGE
        # =========================================================================
        story.append(Spacer(1, 20))
        if os.path.exists(LOGO_PATH):
            try:
                story.append(Image(LOGO_PATH, width=150, height=60))
            except Exception:
                pass
        
        story.append(Spacer(1, 25))
        story.append(HRFlowable(width="100%", thickness=4, color=accent_blue, spaceBefore=0, spaceAfter=18))

        metadata = report_data.get("metadata", {})
        biz_id = report_data.get("business_identity", {})
        biz_name = biz_id.get("business_name", "Enterprise")
        category = biz_id.get("business_category", "SME Business")
        stage = biz_id.get("business_stage", "New Startup")
        district = biz_id.get("district", "Colombo")
        province = biz_id.get("province", "Western")

        is_new_startup = "new" in stage.lower() or "start" in stage.lower()
        doc_title = metadata.get("document_title") or ("STRATEGIC BUSINESS PLAN" if is_new_startup else "PERSONALIZED BUSINESS GROWTH PLAN")
        doc_subtitle = metadata.get("document_subtitle") or (
            "A Comprehensive Feasibility, Strategic Direction & Implementation Blueprint"
            if is_new_startup else
            "A Tailored Strategic Growth & Decision Support Blueprint"
        )

        story.append(Paragraph(metadata.get("system_brand", "SME360 AI"), subtitle_style))
        story.append(Paragraph(doc_title, title_style))
        story.append(Paragraph(doc_subtitle, ParagraphStyle('CoverSub2', parent=body_style, fontSize=10, textColor=muted_text, spaceAfter=25)))

        # Metadata Card (Executive Presentation, not a database dump)
        clean_stage_display = "New Startup" if "new" in stage.lower() else "Existing Business"
        meta_items = [
            Paragraph(f"<b>Prepared For:</b> {biz_name}", body_style),
            Paragraph(f"<b>Industry Category:</b> {category} | <b>Business Stage:</b> {clean_stage_display}", body_style),
            Paragraph(f"<b>Operating Location:</b> {district}, {province} Province, Sri Lanka", body_style),
            Paragraph(f"<b>Prepared Date:</b> {metadata.get('generated_date', 'Current')}", body_style),
            Paragraph(f"<b>Decision System Reference:</b> <font color='#64748b'>{metadata.get('record_id', 'N/A')}</font>", body_style)
        ]
        story.append(create_callout_box(meta_items, bg=colors.HexColor("#f8fafc"), border=card_border, padding=12))

        story.append(Spacer(1, 40))
        story.append(Paragraph(
            "<i>This document synthesizes machine-learned feasibility assessment, explainable SHAP feature attribution, "
            "TOPSIS multi-criteria strategic prioritization, and sensitivity scenario stress-testing into an actionable strategic roadmap "
            "prepared specifically for the entrepreneur.</i>",
            ParagraphStyle('Disclaimer', parent=body_style, fontSize=8, leading=11.5, textColor=muted_text)
        ))

        story.append(PageBreak())

        ctx = {
            "h1_style": h1_style,
            "h2_style": h2_style,
            "h3_style": h3_style,
            "body_style": body_style,
            "bullet_style": bullet_style,
            "table_header_style": table_header_style,
            "table_cell_style": table_cell_style,
            "primary_color": primary_color,
            "accent_blue": accent_blue,
            "dark_text": dark_text,
            "muted_text": muted_text,
            "card_bg": card_bg,
            "card_border": card_border,
            "grid_border": grid_border,
            "create_callout_box": create_callout_box,
            "create_metric_strip": create_metric_strip,
        }

        new_startup_sections = report_data.get("new_startup_sections")
        if is_new_startup and new_startup_sections:
            BusinessPlanPDFGenerator._render_new_startup_sections(story, report_data, ctx)
        else:
            BusinessPlanPDFGenerator._render_unified_growth_sections(story, report_data, ctx)

        # Build PDF document
        def canvas_maker(*args, **kwargs):
            kwargs["cover_info"] = cover_info
            return NumberedCanvas(*args, **kwargs)

        doc.build(story, canvasmaker=canvas_maker)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def _render_new_startup_sections(story, report_data: dict, ctx: dict):
        h1_style = ctx["h1_style"]
        h2_style = ctx["h2_style"]
        h3_style = ctx["h3_style"]
        body_style = ctx["body_style"]
        bullet_style = ctx["bullet_style"]
        table_header_style = ctx["table_header_style"]
        table_cell_style = ctx["table_cell_style"]
        primary_color = ctx["primary_color"]
        accent_blue = ctx["accent_blue"]
        dark_text = ctx["dark_text"]
        muted_text = ctx["muted_text"]
        card_border = ctx["card_border"]
        grid_border = ctx["grid_border"]
        create_callout_box = ctx["create_callout_box"]
        create_metric_strip = ctx["create_metric_strip"]

        sec_dict = report_data.get("new_startup_sections", {})
        biz_id = report_data.get("business_identity", {})
        biz_name = biz_id.get("business_name", "Enterprise")
        category = biz_id.get("business_category", "SME Business")
        district = biz_id.get("district", "Colombo")
        province = biz_id.get("province", "Western")

        # =====================================================================
        # SECTION 01 — EXECUTIVE SUMMARY
        # =====================================================================
        s1 = sec_dict.get("section_1_executive_summary", {})
        story.append(Paragraph("SECTION 01 — EXECUTIVE SUMMARY", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 1.1 Business Idea Overview
        story.append(Paragraph("<b>1.1 Business Idea Overview</b>", h2_style))
        s1_bio = s1.get("business_idea_overview", {})
        story.append(Paragraph(
            f"<b>{biz_name}</b> is a proposed new startup venture within the <b>{category}</b> industry, "
            f"planned for commercial launch in {district}, {province} Province, Sri Lanka. "
            f"{s1_bio.get('summary_text', '')}",
            body_style
        ))

        # 1.2 AI Feasibility Result
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>1.2 AI Feasibility Result</b>", h2_style))
        s1_feas = s1.get("ai_feasibility_result", {})
        pred_label = s1_feas.get("predicted_label", "Conditionally Feasible")
        conf_pct = s1_feas.get("confidence_percentage", "65.0%")
        probs = s1_feas.get("probabilities", {})
        prob_feas = probs.get("Feasible", 0.0)
        prob_cond = probs.get("Conditionally Feasible", 0.0)
        prob_infeas = probs.get("Infeasible", 0.0)
        badge_color = "#166534" if pred_label == "Feasible" else "#854d0e" if "Conditionally" in pred_label else "#991b1b"

        feas_box_content = [
            Paragraph(f"<font color='{badge_color}' size='11'><b>ASSESSMENT VERDICT: {pred_label.upper()} (Predicted Class Probability: {conf_pct})</b></font>", body_style),
            Spacer(1, 2),
            Paragraph(f"<font color='#475569'>Multi-Class Model Distribution: Feasible: <b>{prob_feas:.1%}</b>  |  Conditionally Feasible: <b>{prob_cond:.1%}</b>  |  Infeasible: <b>{prob_infeas:.1%}</b></font>", body_style),
            Spacer(1, 2),
            Paragraph(s1_feas.get("interpretation", ""), body_style)
        ]
        story.append(create_callout_box(feas_box_content, bg=colors.HexColor("#f8fafc"), border=card_border, padding=8))

        # 1.3 Recommended Strategy
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>1.3 Recommended Strategy</b>", h2_style))
        s1_strat = s1.get("recommended_strategy", {})
        strat_name = s1_strat.get("strategy_name", "Lean Bootstrapped Start")
        strat_focus = s1_strat.get("strategic_focus", "Capital Protection & Phased Scale")
        topsis_score = s1_strat.get("topsis_score", "N/A")
        align_note = s1_strat.get("alignment_note", "")
        story.append(Paragraph(
            f"Based on algorithmic multi-criteria ranking, the system identifies <b>{strat_name}</b> "
            f"(TOPSIS Closeness Score: <b>{topsis_score}</b>) as the strategic direction for this venture. "
            f"<b>Strategic Focus:</b> {strat_focus}. {align_note}",
            body_style
        ))

        # 1.4 Required Investment and Funding Summary
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>1.4 Required Investment and Funding Summary</b>", h2_style))
        s1_fund = s1.get("investment_funding_summary", {})
        target_cap = s1_fund.get("strategy_target_capital_lkr", 0.0)
        avail_cap = s1_fund.get("available_capital_lkr", 0.0)
        loan_amt = s1_fund.get("loan_amount_lkr", 0.0)
        total_funds = s1_fund.get("total_available_funds_lkr", avail_cap + loan_amt)
        monthly_budget = s1_fund.get("monthly_operating_budget_lkr", 0.0)
        runway = s1_fund.get("capital_runway_months", 0.0)
        fund_status = s1_fund.get("funding_status", "Fully funded")

        fin_metrics = [
            ("Target Capital", f"LKR {target_cap:,.0f}", "Baseline Allocation"),
            ("Available Capital", f"LKR {avail_cap:,.0f}", f"Loan: LKR {loan_amt:,.0f}"),
            ("Monthly Budget", f"LKR {monthly_budget:,.0f}", "Operating Ceiling"),
            ("Budget Coverage", f"{runway} Months", "Capital-to-Budget Ratio")
        ]
        story.append(create_metric_strip(fin_metrics))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            f"The initial target capital requirement is <b>LKR {target_cap:,.0f}</b>. With <b>LKR {avail_cap:,.0f}</b> in recorded available capital "
            f"and <b>LKR {loan_amt:,.0f}</b> in external loan financing, total available liquidity stands at <b>LKR {total_funds:,.0f}</b> ({fund_status}). "
            f"Under the baseline operating budget ceiling of <b>LKR {monthly_budget:,.0f}/month</b>, this provides approximately <b>{runway} months</b> "
            f"of simplified budget coverage.",
            body_style
        ))

        # PageBreak at end of Section 1
        story.append(PageBreak())

        # =====================================================================
        # SECTION 02 — BUSINESS OVERVIEW
        # =====================================================================
        s2 = sec_dict.get("section_2_business_overview", {})
        story.append(Paragraph("SECTION 02 — BUSINESS OVERVIEW", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 2.1 Business Concept and Objectives
        story.append(Paragraph("<b>2.1 Business Concept & Objectives</b>", h2_style))
        s2_co = s2.get("concept_and_objectives", {})
        concept_desc = s2_co.get("business_concept", "")
        biz_model = s2_co.get("business_model", "Direct Retail / Service")
        story.append(Paragraph(
            f"<b>{biz_name}</b> is structured under a <b>{biz_model}</b> operational model. {concept_desc}",
            body_style
        ))
        story.append(Paragraph("<b>Core Foundational Objectives:</b>", h3_style))
        for obj in s2_co.get("primary_objectives", []):
            story.append(Paragraph(f"• {obj}", bullet_style))

        # 2.2 Business Location Analysis
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>2.2 Business Location Analysis</b>", h2_style))
        s2_loc = s2.get("business_location", {})
        loc_type = s2_loc.get("location_type", "Commercial Hub")
        loc_score = s2_loc.get("location_suitability_score", "3/5")
        loc_ctx = s2_loc.get("location_context", "")
        loc_addr = s2_loc.get("address", "Information not provided in intake")
        story.append(Paragraph(
            f"The venture is proposed for operation in <b>{district}, {province} Province, Sri Lanka</b>, "
            f"situated within a <b>{loc_type}</b> environment. The location holds a suitability score of <b>{loc_score}</b>. "
            f"{loc_ctx} Registered premise reference: <i>{loc_addr}</i>.",
            body_style
        ))

        # 2.3 Products or Services
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>2.3 Products or Services</b>", h2_style))
        s2_prod = s2.get("products_or_services", {})
        offering = s2_prod.get("offerings_summary", "")
        op_details = s2_prod.get("operational_details", "")
        exp_price = s2_prod.get("expected_price_lkr", 0.0)
        story.append(Paragraph(
            f"{offering} Operations are designed to deliver reliable customer satisfaction through consistent service execution: {op_details} "
            f"Initial offerings are priced around an expected baseline transaction value of <b>LKR {exp_price:,.2f}</b>.",
            body_style
        ))

        # 2.4 Target Customers
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>2.4 Target Customers & Demand Assessment</b>", h2_style))
        s2_cust = s2.get("target_customers", {})
        target_prof = s2_cust.get("target_profile", f"Consumers in {district}")
        cust_dem_score = s2_cust.get("customer_demand_score", "50/100")
        dem_assess = s2_cust.get("demand_assessment", "")
        story.append(Paragraph(
            f"The primary target clientele comprises <b>{target_prof}</b>. "
            f"The recorded customer demand score for this profile is <b>{cust_dem_score}</b>. {dem_assess}",
            body_style
        ))

        # 2.5 Relevant Market Context
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>2.5 Relevant Market Context & Competitive Landscape</b>", h2_style))
        s2_mkt = s2.get("relevant_market_context", {})
        comp_level = s2_mkt.get("competition_level", "Moderate")
        comp_cnt = s2_mkt.get("competitor_count_nearby")
        comp_info = s2_mkt.get("competitor_information", "")
        pos_strat = s2_mkt.get("positioning_strategy", "")
        story.append(Paragraph(
            f"Local market competition is characterized as <b>{comp_level}</b>. Nearby competitor count is recorded as "
            f"<b>{comp_cnt}</b> ({comp_info}). To establish a viable market share, {pos_strat}",
            body_style
        ))

        # PageBreak at end of Section 2
        story.append(PageBreak())

        # =====================================================================
        # SECTION 03 — FEASIBILITY ASSESSMENT AND KEY FINDINGS
        # =====================================================================
        s3 = sec_dict.get("section_3_feasibility_findings", {})
        story.append(Paragraph("SECTION 03 — FEASIBILITY ASSESSMENT AND KEY FINDINGS", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 3.1 ML Feasibility Prediction
        story.append(Paragraph("<b>3.1 Machine Learning Feasibility Classification</b>", h2_style))
        s3_pred = s3.get("ml_feasibility_prediction", {})
        pred_label_s3 = s3_pred.get("predicted_label", pred_label)
        conf_pct_s3 = s3_pred.get("confidence_percentage", conf_pct)
        probs_s3 = s3_pred.get("probabilities", probs)
        p_feas_s3 = probs_s3.get("Feasible", 0.0)
        p_cond_s3 = probs_s3.get("Conditionally Feasible", 0.0)
        p_inf_s3 = probs_s3.get("Infeasible", 0.0)
        method_disc = s3_pred.get("methodology_disclosure", "")

        story.append(Paragraph(
            f"The business profile was evaluated using SME360 AI's trained Random Forest classification model. "
            f"The model classifies <b>{biz_name}</b> as <b>{pred_label_s3}</b> with a predicted class probability of <b>{conf_pct_s3}</b> "
            f"(Feasible: <b>{p_feas_s3:.1%}</b>, Conditionally Feasible: <b>{p_cond_s3:.1%}</b>, Infeasible: <b>{p_inf_s3:.1%}</b>). "
            f"<i>{method_disc}</i>",
            body_style
        ))

        # Embedded Probability Chart
        try:
            chart_bytes = BusinessPlanChartGenerator.generate_probability_chart(probs_s3)
            chart_img = Image(io.BytesIO(chart_bytes), width=480, height=125)
            story.append(Spacer(1, 3))
            story.append(chart_img)
            story.append(Spacer(1, 3))
        except Exception:
            pass

        # 3.2 Factors Influencing the Prediction (SHAP)
        story.append(Paragraph("<b>3.2 Factors Influencing Prediction (SHAP Explainable AI)</b>", h2_style))
        story.append(Paragraph(
            "To understand what features drove this classification, SHAP (SHapley Additive exPlanations) values decompose the model's output into specific positive enablers and operational hurdles:",
            body_style
        ))
        s3_factors = s3.get("factors_influencing_prediction", {})
        pos_enablers = s3_factors.get("positive_enablers", [])
        hurdles = s3_factors.get("operational_hurdles", [])

        story.append(Paragraph("<b>Positive Enablers Supporting Feasibility:</b>", h3_style))
        if pos_enablers:
            for item in pos_enablers[:3]:
                feat = item.get("feature", "Factor")
                val = item.get("feature_value", "N/A")
                exp = item.get("impact_explanation", "Contributed positive support.")
                story.append(Paragraph(f"• <b>{feat} ({val}):</b> {exp}", bullet_style))
        else:
            story.append(Paragraph("• Baseline capital and operating assumptions align with initial industry requirements.", bullet_style))

        story.append(Paragraph("<b>Operational Hurdles Requiring Management Attention:</b>", h3_style))
        if hurdles:
            for item in hurdles[:3]:
                feat = item.get("feature", "Constraint")
                val = item.get("feature_value", "N/A")
                exp = item.get("impact_explanation", "Contributed downward pressure.")
                story.append(Paragraph(f"• <b>{feat} ({val}):</b> {exp}", bullet_style))
        else:
            story.append(Paragraph("• Operating budget discipline and customer footfall should be closely monitored during early trading.", bullet_style))

        # 3.3 Available-Resource and Affordability Gaps
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>3.3 Available-Resource & Affordability Gaps</b>", h2_style))
        s3_gaps = s3.get("resource_and_affordability_gaps", {})
        story.append(Paragraph(s3_gaps.get("affordability_assessment", ""), body_style))

        # 3.4 Key Findings
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>3.4 Key Findings Summary</b>", h2_style))
        for kf in s3.get("key_findings", []):
            story.append(Paragraph(f"• {kf}", bullet_style))

        # PageBreak at end of Section 3
        story.append(PageBreak())

        # =====================================================================
        # SECTION 04 — PERSONALIZED BUSINESS STRATEGY
        # =====================================================================
        s4 = sec_dict.get("section_4_personalized_strategy", {})
        story.append(Paragraph("SECTION 04 — PERSONALIZED BUSINESS STRATEGY", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 4.1 Recommended Strategy Direction
        story.append(Paragraph("<b>4.1 Recommended Strategy Direction</b>", h2_style))
        s4_rec = s4.get("recommended_strategy", {})
        rec_name = s4_rec.get("strategy_name", strat_name)
        rec_focus = s4_rec.get("strategic_focus", "Operational Discipline")
        rec_cust = s4_rec.get("target_daily_customers", 35)
        rec_cap = s4_rec.get("estimated_capital_required_lkr", target_cap)
        rec_bud = s4_rec.get("estimated_monthly_budget_lkr", monthly_budget)
        rec_app = s4_rec.get("operational_approach", "")

        strat_card = [
            Paragraph(f"<b>RECOMMENDED OPERATING PATH: {rec_name.upper()}</b>", ParagraphStyle('RecHead', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=primary_color)),
            Spacer(1, 2),
            Paragraph(f"<b>Strategic Focus:</b> {rec_focus}", body_style),
            Paragraph(f"<b>Operational Approach:</b> {rec_app}", body_style),
            Spacer(1, 2),
            Paragraph(
                f"<font color='#1e3a8a'><b>Target Capital:</b> LKR {rec_cap:,.0f}</font>  |  "
                f"<b>Monthly Operating Budget:</b> LKR {rec_bud:,.0f}  |  "
                f"<b>Target Daily Footfall:</b> {rec_cust} Customers/Day",
                ParagraphStyle('RecMeta', parent=body_style, fontSize=8, textColor=dark_text)
            )
        ]
        story.append(create_callout_box(strat_card, bg=colors.HexColor("#f8fafc"), border=card_border, padding=8))

        # 4.2 Reasons for Recommendation (TOPSIS)
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>4.2 Multi-Criteria Evaluation & Selection Rationale (TOPSIS Method)</b>", h2_style))
        s4_reasons = s4.get("reasons_for_recommendation", {})
        story.append(Paragraph(s4_reasons.get("topsis_rationale", ""), body_style))
        story.append(Paragraph(s4_reasons.get("alignment_summary", ""), body_style))

        # 4.3 Practical Actions Tailored to the Business
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>4.3 Tailored Implementation Actions</b>", h2_style))
        for act in s4.get("practical_actions", []):
            story.append(Paragraph(f"• {act}", bullet_style))

        # 4.4 Alternative Strategies Considered
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>4.4 Alternative Strategies Evaluated (TOPSIS Ranking Table)</b>", h2_style))
        story.append(Paragraph("The system evaluated four distinct strategic pathways against the five multi-criteria dimensions. Below is the comparative ranking:", body_style))

        alt_strats = s4.get("alternative_strategies", [])
        if alt_strats:
            topsis_table_data = [
                [
                    Paragraph("<b>Rank</b>", table_header_style),
                    Paragraph("<b>Strategy Alternative</b>", table_header_style),
                    Paragraph("<b>Strategic Focus</b>", table_header_style),
                    Paragraph("<b>Target Capital</b>", table_header_style),
                    Paragraph("<b>TOPSIS Score</b>", table_header_style)
                ]
            ]
            for s in alt_strats[:4]:
                s_rank = s.get("rank", "-")
                s_n = s.get("strategy_name", "")
                s_f = s.get("strategic_focus", "")
                s_c = s.get("estimated_capital_required_lkr", 0.0)
                s_sc = str(s.get("topsis_score", "N/A"))
                topsis_table_data.append([
                    Paragraph(f"<b>#{s_rank}</b>", table_cell_style),
                    Paragraph(f"<b>{s_n}</b>", table_cell_style),
                    Paragraph(s_f, table_cell_style),
                    Paragraph(f"LKR {s_c:,.0f}", table_cell_style),
                    Paragraph(s_sc, table_cell_style)
                ])
            t_tbl = Table(topsis_table_data, colWidths=[35, 175, 155, 105, 70])
            t_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(t_tbl)

        # PageBreak at end of Section 4
        story.append(PageBreak())

        # =====================================================================
        # SECTION 05 — MARKETING AND SALES PLAN
        # =====================================================================
        s5 = sec_dict.get("section_5_marketing_sales", {})
        story.append(Paragraph("SECTION 05 — MARKETING AND SALES PLAN", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 5.1 Customer Acquisition Methods
        story.append(Paragraph("<b>5.1 Customer Acquisition Methods</b>", h2_style))
        story.append(Paragraph(f"Customer acquisition activities focus on establishing immediate awareness and localized trial in {district}:", body_style))
        for m in s5.get("customer_acquisition_methods", []):
            story.append(Paragraph(f"• {m}", bullet_style))

        # 5.2 Suitable Promotional Activities
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>5.2 Promotional Activities & Launch Campaign</b>", h2_style))
        for p in s5.get("suitable_promotional_activities", []):
            story.append(Paragraph(f"• {p}", bullet_style))

        # 5.3 Pricing Approach
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>5.3 Pricing Approach & Commercial Rationale</b>", h2_style))
        s5_price = s5.get("pricing_approach", {})
        exp_u_price = s5_price.get("expected_unit_price_lkr", 0.0)
        p_strat = s5_price.get("pricing_strategy", "Competitive Value-Based Pricing")
        p_rat = s5_price.get("rationale", "")
        story.append(Paragraph(
            f"The business adopts a <b>{p_strat}</b> methodology with a target average spend of <b>LKR {exp_u_price:,.2f}</b> per customer. {p_rat}",
            body_style
        ))

        # 5.4 Sales and Distribution Channels
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>5.4 Sales & Distribution Channels</b>", h2_style))
        for ch in s5.get("sales_distribution_channels", []):
            story.append(Paragraph(f"• {ch}", bullet_style))

        # 5.5 Initial Sales Targets and Milestones
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>5.5 Initial Sales Targets & Gross Sales Calculation</b>", h2_style))
        s5_sales = s5.get("initial_sales_targets", {})
        cust_d = s5_sales.get("target_customers_per_day", 0)
        op_d = s5_sales.get("operating_days_per_month", 26)
        tot_interactions = s5_sales.get("monthly_customer_interactions", cust_d * op_d)
        est_m_sales = s5_sales.get("estimated_monthly_gross_sales_lkr", 0.0)
        formula_str = s5_sales.get("calculation_formula", "")
        disc_str = s5_sales.get("assumption_disclosure", "")

        sales_box = [
            Paragraph(f"<b>Estimated Monthly Gross Sales Target:</b> <font color='#1e3a8a' size='11'><b>LKR {est_m_sales:,.2f}</b></font>", body_style),
            Spacer(1, 2),
            Paragraph(f"<b>Operating Parameters:</b> {cust_d} Customers/Day × {op_d} Operating Days/Month = <b>{tot_interactions:,} Customer Interactions/Month</b>", body_style),
            Paragraph(f"<b>Calculation Formula:</b> <i>{formula_str}</i>", body_style),
            Spacer(1, 2),
            Paragraph(f"<i>Disclosure: {disc_str}</i>", ParagraphStyle('SalesDisc', parent=body_style, fontSize=7.5, textColor=muted_text))
        ]
        story.append(create_callout_box(sales_box, bg=colors.HexColor("#f8fafc"), border=card_border, padding=8))

        # PageBreak at end of Section 5
        story.append(PageBreak())

        # =====================================================================
        # SECTION 06 — FINANCIAL AND RESOURCE PLAN
        # =====================================================================
        s6 = sec_dict.get("section_6_financial_resource", {})
        story.append(Paragraph("SECTION 06 — FINANCIAL AND RESOURCE PLAN", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 6.1 Estimated Startup Costs
        story.append(Paragraph("<b>6.1 Estimated Startup Costs Breakdown</b>", h2_style))
        s6_costs = s6.get("estimated_startup_costs", {})
        inv_c = s6_costs.get("initial_inventory_cost_lkr", 0.0)
        eq_c = s6_costs.get("equipment_and_setup_lkr", 0.0)
        res_c = s6_costs.get("working_capital_reserve_lkr", 0.0)
        tot_c = s6_costs.get("total_initial_startup_cost_lkr", 0.0)

        cost_tbl_data = [
            [Paragraph("<b>Cost Category</b>", table_header_style), Paragraph("<b>Estimated Amount (LKR)</b>", table_header_style), Paragraph("<b>Budget Allocation Notes</b>", table_header_style)],
            [Paragraph("Initial Opening Inventory Stock", table_cell_style), Paragraph(f"LKR {inv_c:,.2f}", table_cell_style), Paragraph("Opening wholesale inventory procured prior to launch", table_cell_style)],
            [Paragraph("Equipment, Fixtures & Premise Setup", table_cell_style), Paragraph(f"LKR {eq_c:,.2f}", table_cell_style), Paragraph("Essential counter, shelving, and operational tools", table_cell_style)],
            [Paragraph("Working Capital Reserve Buffer", table_cell_style), Paragraph(f"LKR {res_c:,.2f}", table_cell_style), Paragraph("Liquidity buffer covering baseline operational ramp-up", table_cell_style)],
            [Paragraph("<b>Total Initial Startup Cost</b>", table_cell_style), Paragraph(f"<b>LKR {tot_c:,.2f}</b>", table_cell_style), Paragraph("<b>Calibrated baseline startup requirement</b>", table_cell_style)],
        ]
        cost_tbl = Table(cost_tbl_data, colWidths=[180, 140, 220])
        cost_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
            ('PADDING', (0,0), (-1,-1), 4.5),
            ('BOX', (0,0), (-1,-1), 1, card_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(cost_tbl)

        # 6.2 Available Capital and Funding Requirements
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.2 Available Capital & Funding Requirements</b>", h2_style))
        s6_fund = s6.get("available_capital_and_funding", {})
        story.append(Paragraph(
            f"The venture is supported by <b>LKR {s6_fund.get('available_capital_lkr', 0):,.2f}</b> in recorded available equity capital and "
            f"<b>LKR {s6_fund.get('loan_amount_lkr', 0):,.2f}</b> in external loan financing, providing total available funding of "
            f"<b>LKR {s6_fund.get('total_available_funds_lkr', 0):,.2f}</b> against a target capital requirement of "
            f"<b>LKR {s6_fund.get('strategy_target_capital_lkr', 0):,.2f}</b> ({s6_fund.get('funding_gap_status', 'Fully funded')}).",
            body_style
        ))

        # 6.3 Equipment and Resource Requirements
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.3 Equipment & Resource Requirements</b>", h2_style))
        s6_eq = s6.get("equipment_and_resource_requirements", {})
        story.append(Paragraph(
            f"Equipment readiness is scored at <b>{s6_eq.get('available_equipment_score', '3/5')}</b> against a required baseline of "
            f"<b>{s6_eq.get('required_equipment_score', '3/5')}</b> ({s6_eq.get('readiness_status', '')}). Regional supplier availability score is "
            f"<b>{s6_eq.get('supplier_availability_score', '')}</b>.",
            body_style
        ))

        # 6.4 Staffing Requirements
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.4 Staffing Requirements & Roles</b>", h2_style))
        s6_st = s6.get("staffing_requirements", {})
        story.append(Paragraph(
            f"Current available workforce stands at <b>{s6_st.get('available_staff_count', 1)} staff member(s)</b> against an estimated requirement of "
            f"<b>{s6_st.get('required_staff_count', 1)}</b> ({s6_st.get('capacity_status', '')}).",
            body_style
        ))
        for r in s6_st.get("key_roles", []):
            story.append(Paragraph(f"• {r}", bullet_style))

        # 6.5 Operating Expenses
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.5 Operating Expenses & Working Capital Runway</b>", h2_style))
        s6_exp = s6.get("operating_expenses", {})
        story.append(Paragraph(
            f"Monthly operating budget is established at <b>LKR {s6_exp.get('monthly_operating_budget_lkr', 0):,.2f}</b>. "
            f"This provides approximately <b>{s6_exp.get('strategy_capital_runway_months', 0)} months</b> of strategy budget coverage and "
            f"<b>{s6_exp.get('total_funds_runway_months', 0)} months</b> of total funds liquidity runway. "
            f"{s6_exp.get('expense_guidance', '')}",
            body_style
        ))

        # 6.6 Financial Projections Table
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.6 Financial Projections Summary</b>", h2_style))
        s6_proj = s6.get("financial_projections", [])
        if s6_proj:
            proj_tbl_data = [
                [Paragraph("<b>Financial Metric</b>", table_header_style), Paragraph("<b>Projected Target</b>", table_header_style), Paragraph("<b>Basis of Projection</b>", table_header_style)]
            ]
            for p in s6_proj:
                proj_tbl_data.append([
                    Paragraph(f"<b>{p.get('metric', '')}</b>", table_cell_style),
                    Paragraph(p.get("value", ""), table_cell_style),
                    Paragraph(p.get("basis", ""), table_cell_style)
                ])
            proj_tbl = Table(proj_tbl_data, colWidths=[160, 140, 240])
            proj_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(proj_tbl)

        # PageBreak at end of Section 6
        story.append(PageBreak())

        # =====================================================================
        # SECTION 07 — IMPLEMENTATION ROADMAP
        # =====================================================================
        s7 = sec_dict.get("section_7_implementation_roadmap", {})
        story.append(Paragraph("SECTION 07 — IMPLEMENTATION ROADMAP", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 7.1 Prioritized Actions
        story.append(Paragraph("<b>7.1 Prioritized Pre-Launch Actions</b>", h2_style))
        for act in s7.get("prioritized_actions", []):
            story.append(Paragraph(f"• {act}", bullet_style))

        # 7.2 Implementation Timeline (4 Phases)
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>7.2 Implementation Timeline (Four Operational Horizons)</b>", h2_style))
        for ph in s7.get("implementation_timeline", []):
            story.append(Paragraph(f"<b>{ph.get('phase_name', '')} ({ph.get('timeframe', '')}):</b>", h3_style))
            story.append(Paragraph(ph.get("focus_actions", ""), body_style))

        # 7.3 Launch Milestones Table
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>7.3 Launch Milestones & Success Criteria</b>", h2_style))
        s7_ms = s7.get("launch_milestones", [])
        if s7_ms:
            ms_tbl_data = [
                [Paragraph("<b>Milestone Name</b>", table_header_style), Paragraph("<b>Target Timeline</b>", table_header_style), Paragraph("<b>Measurable Success Criteria</b>", table_header_style)]
            ]
            for m in s7_ms:
                ms_tbl_data.append([
                    Paragraph(f"<b>{m.get('milestone', '')}</b>", table_cell_style),
                    Paragraph(m.get("target_timeframe", ""), table_cell_style),
                    Paragraph(m.get("success_criteria", ""), table_cell_style)
                ])
            ms_tbl = Table(ms_tbl_data, colWidths=[150, 90, 300])
            ms_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(ms_tbl)

        # 7.4 Operational Responsibilities
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>7.4 Operational Responsibilities Matrix</b>", h2_style))
        s7_resp = s7.get("responsibilities", [])
        if s7_resp:
            resp_tbl_data = [
                [Paragraph("<b>Operating Role</b>", table_header_style), Paragraph("<b>Core Accountabilities & Responsibilities</b>", table_header_style)]
            ]
            for r in s7_resp:
                resp_tbl_data.append([
                    Paragraph(f"<b>{r.get('role', '')}</b>", table_cell_style),
                    Paragraph(r.get("accountabilities", ""), table_cell_style)
                ])
            resp_tbl = Table(resp_tbl_data, colWidths=[160, 380])
            resp_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(resp_tbl)

        # PageBreak at end of Section 7
        story.append(PageBreak())

        # =====================================================================
        # SECTION 08 — EXPECTED OUTCOMES AND KEY ASSUMPTIONS
        # =====================================================================
        s8 = sec_dict.get("section_8_outcomes_assumptions", {})
        story.append(Paragraph("SECTION 08 — EXPECTED OUTCOMES AND KEY ASSUMPTIONS", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 8.1 Expected Business Outcomes
        story.append(Paragraph("<b>8.1 Expected Business Outcomes</b>", h2_style))
        for eo in s8.get("expected_business_outcomes", []):
            story.append(Paragraph(f"• {eo}", bullet_style))

        # 8.2 Measurable Targets and Monitoring KPIs
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>8.2 Measurable Targets & Key Performance Indicators (KPIs)</b>", h2_style))
        story.append(Paragraph("Management should monitor the following operational indicators regularly (Note: These represent monitoring metrics, not model predictions):", body_style))
        s8_kpis = s8.get("measurable_targets", [])
        if s8_kpis:
            kpi_tbl_data = [
                [Paragraph("<b>KPI / Monitoring Metric</b>", table_header_style), Paragraph("<b>Target Metric</b>", table_header_style), Paragraph("<b>Frequency</b>", table_header_style), Paragraph("<b>Focus Area</b>", table_header_style)]
            ]
            for k in s8_kpis:
                kpi_tbl_data.append([
                    Paragraph(f"<b>{k.get('kpi_name', '')}</b>", table_cell_style),
                    Paragraph(str(k.get("target_value", "")), table_cell_style),
                    Paragraph(k.get("monitoring_frequency", "Monthly"), table_cell_style),
                    Paragraph(k.get("focus_area", "Operations"), table_cell_style)
                ])
            kpi_tbl = Table(kpi_tbl_data, colWidths=[140, 150, 100, 150])
            kpi_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(kpi_tbl)

        # 8.3 Important Business Assumptions
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>8.3 Important Business Assumptions</b>", h2_style))
        for asm in s8.get("important_business_assumptions", []):
            story.append(Paragraph(f"• {asm}", bullet_style))

        # 8.4 Data Limitations and Validation Disclosures
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>8.4 Data Limitations & Methodological Disclosures</b>", h2_style))
        for lim in s8.get("data_limitations_and_validation", []):
            story.append(Paragraph(f"• {lim}", bullet_style))

    @staticmethod
    def _render_unified_growth_sections(story, report_data: dict, ctx: dict):
        h1_style = ctx["h1_style"]
        h2_style = ctx["h2_style"]
        h3_style = ctx["h3_style"]
        body_style = ctx["body_style"]
        bullet_style = ctx["bullet_style"]
        table_header_style = ctx["table_header_style"]
        table_cell_style = ctx["table_cell_style"]
        primary_color = ctx["primary_color"]
        accent_blue = ctx["accent_blue"]
        dark_text = ctx["dark_text"]
        muted_text = ctx["muted_text"]
        card_border = ctx["card_border"]
        grid_border = ctx["grid_border"]
        create_callout_box = ctx["create_callout_box"]
        create_metric_strip = ctx["create_metric_strip"]

        sec_dict = report_data.get("unified_growth_sections") or report_data.get("existing_growth_sections") or {}
        biz_id = report_data.get("business_identity", {})
        biz_name = biz_id.get("business_name", "Enterprise")
        category = biz_id.get("business_category", "SME Business")
        district = biz_id.get("district", "Colombo")
        province = biz_id.get("province", "Western")

        # =====================================================================
        # EXECUTIVE SUMMARY
        # =====================================================================
        s_exec = sec_dict.get("executive_summary", {})
        story.append(Paragraph("EXECUTIVE SUMMARY", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # Business & Growth Purpose
        story.append(Paragraph("<b>Existing Enterprise Overview & Growth Purpose</b>", h2_style))
        story.append(Paragraph(s_exec.get("business_summary", f"{biz_name} is an established enterprise operating in {district}."), body_style))
        story.append(Paragraph(f"<b>Core Growth Objectives:</b> {s_exec.get('growth_objectives', '')}", body_style))

        # AI Feasibility Finding
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>AI Feasibility Assessment & Model Confidence</b>", h2_style))
        feas = s_exec.get("ai_feasibility_result", {})
        pred_label = feas.get("predicted_label", "Conditionally Feasible")
        conf_pct = feas.get("confidence_percentage", "65.0%")
        probs = feas.get("probabilities", {})
        prob_feas = probs.get("Feasible", 0.0)
        prob_cond = probs.get("Conditionally Feasible", 0.0)
        prob_infeas = probs.get("Infeasible", 0.0)
        badge_color = "#166534" if pred_label == "Feasible" else "#854d0e" if "Conditionally" in pred_label else "#991b1b"

        feas_box_content = [
            Paragraph(f"<font color='{badge_color}' size='11'><b>ASSESSMENT VERDICT: {pred_label.upper()} (Predicted Class Probability: {conf_pct})</b></font>", body_style),
            Spacer(1, 2),
            Paragraph(f"<font color='#475569'>Multi-Class Model Distribution: Feasible: <b>{prob_feas:.1%}</b>  |  Conditionally Feasible: <b>{prob_cond:.1%}</b>  |  Infeasible: <b>{prob_infeas:.1%}</b></font>", body_style),
            Spacer(1, 2),
            Paragraph(feas.get("interpretation", ""), body_style)
        ]
        story.append(create_callout_box(feas_box_content, bg=colors.HexColor("#f8fafc"), border=card_border, padding=8))

        # Recommended Growth Strategy & Investment Summary
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Recommended Growth Strategy & Capital Plan</b>", h2_style))
        s_strat = s_exec.get("recommended_strategy", {})
        strat_name = s_strat.get("strategy_name", "Capital-Protected Phased Growth")
        strat_focus = s_strat.get("strategic_focus", "Operational Efficiency")
        topsis_score = s_strat.get("topsis_score", "N/A")
        align_note = s_strat.get("alignment_note", "")
        story.append(Paragraph(
            f"Based on multi-criteria TOPSIS evaluation and algorithmic decision support, the system identifies <b>{strat_name}</b> "
            f"(TOPSIS Closeness Score: <b>{topsis_score}</b>) as the optimal growth pathway. "
            f"<b>Strategic Focus:</b> {strat_focus}. {align_note}",
            body_style
        ))

        s_fund = s_exec.get("investment_funding_summary", {})
        target_cap = s_fund.get("estimated_growth_capital_lkr", 0.0)
        avail_cap = s_fund.get("available_capital_lkr", 0.0)
        loan_amt = s_fund.get("loan_amount_lkr", 0.0)
        total_funds = s_fund.get("total_available_funds_lkr", avail_cap + loan_amt)
        monthly_exp = s_fund.get("monthly_operating_budget_lkr", 0.0)
        gap_status = s_fund.get("funding_gap_status", "Fully funded")

        story.append(Spacer(1, 2))
        exec_metrics = [
            ("Target Growth Capital", f"LKR {target_cap:,.0f}", "Baseline Requirement"),
            ("Available Capital", f"LKR {avail_cap:,.0f}", f"+ LKR {loan_amt:,.0f} Loan"),
            ("Monthly Budget", f"LKR {monthly_exp:,.0f}", "Operating Ceiling"),
            ("Funding Status", gap_status, f"Total Funds: LKR {total_funds:,.0f}")
        ]
        story.append(create_metric_strip(exec_metrics))

        # Expected Outcomes Summary
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Expected Key Outcomes</b>", h2_style))
        for out in s_exec.get("expected_outcomes", []):
            story.append(Paragraph(f"• {out}", bullet_style))

        # Every section starts on a new page!
        story.append(PageBreak())

        # =====================================================================
        # 1. EXISTING BUSINESS OVERVIEW AND GROWTH OBJECTIVES
        # =====================================================================
        s1 = sec_dict.get("section_1_overview_objectives", {})
        story.append(Paragraph("1. EXISTING BUSINESS OVERVIEW AND GROWTH OBJECTIVES", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 1.1 Business Profile & Operating Background
        story.append(Paragraph("<b>1.1 Business Profile & Operating Background</b>", h2_style))
        b_id = s1.get("business_identity", {})
        story.append(Paragraph(
            f"<b>{biz_name}</b> is an established enterprise operating within the <b>{category}</b> industry, "
            f"located in {district}, {province} Province, Sri Lanka (Location: {b_id.get('location_address', district)}). "
            f"The business operates in a <b>{b_id.get('location_type', 'Commercial Hub')}</b> setting with a location suitability score of "
            f"<b>{b_id.get('location_suitability_score', '3/5')}</b>. Unlike a startup venture, {biz_name} possesses active operational history, "
            f"an existing customer base, and established supplier linkages.",
            body_style
        ))

        # 1.2 Existing Products & Services
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>1.2 Existing Products & Services</b>", h2_style))
        story.append(Paragraph(s1.get("existing_products_and_services", ""), body_style))

        # 1.3 Current Operating Situation & Available Resources
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>1.3 Current Operating Situation & Available Resources</b>", h2_style))
        res = s1.get("current_business_situation_and_resources", {})
        story.append(Paragraph(
            f"The business currently operates with <b>{res.get('current_staff_count', 1)} active staff member(s)</b> against an estimated requirement of "
            f"<b>{res.get('required_staff_count', 1)}</b>. Equipment readiness is scored at <b>{res.get('equipment_readiness_score', '3/5')}</b> (target requirement: {res.get('required_equipment_score', '3/5')}), "
            f"while local supplier availability is rated at <b>{res.get('supplier_availability_score', '3/5')}</b>. "
            f"The business owner brings <b>{res.get('entrepreneur_experience_years', '3 Years')}</b> of commercial experience, supporting operational resilience.",
            body_style
        ))
        res_metrics = [
            ("Available Capital", f"LKR {res.get('available_capital_lkr', 0):,.0f}", "Owner Equity"),
            ("Monthly Budget", f"LKR {res.get('monthly_operating_budget_lkr', 0):,.0f}", "Current Working Cap"),
            ("Active Workforce", f"{res.get('current_staff_count', 1)} Staff", f"Req: {res.get('required_staff_count', 1)}"),
            ("Equipment Score", res.get('equipment_readiness_score', '3/5'), f"Target: {res.get('required_equipment_score', '3/5')}")
        ]
        story.append(create_metric_strip(res_metrics))

        # 1.4 Business Owner's Growth Objectives & Intended Outcomes
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>1.4 Business Owner's Growth Objectives & Intended Outcomes</b>", h2_style))
        story.append(Paragraph(s1.get("growth_objectives", ""), body_style))
        story.append(Paragraph("<b>Intended Outcomes of Proposed Growth:</b>", h3_style))
        for io_item in s1.get("intended_outcomes", []):
            story.append(Paragraph(f"• {io_item}", bullet_style))

        # 1.5 Important Business Constraints & Improvement Needs
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>1.5 Important Business Constraints & Improvement Needs</b>", h2_style))
        for cn in s1.get("constraints_and_improvement_needs", []):
            story.append(Paragraph(f"• {cn}", bullet_style))

        # Every section starts on a new page!
        story.append(PageBreak())

        # =====================================================================
        # 2. MARKET AND GROWTH OPPORTUNITY ANALYSIS
        # =====================================================================
        s2 = sec_dict.get("section_2_market_opportunities", {})
        story.append(Paragraph("2. MARKET AND GROWTH OPPORTUNITY ANALYSIS", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 2.1 Market Catchment & Baseline Demand Dynamics
        story.append(Paragraph("<b>2.1 Market Catchment & Baseline Demand Dynamics</b>", h2_style))
        mkt = s2.get("market_catchment", {})
        cust_per_day = mkt.get("expected_customers_per_day", 0)
        unit_price = mkt.get("expected_selling_price_lkr", 0.0)
        op_days = mkt.get("operating_days_per_month", 26)
        monthly_vol = cust_per_day * op_days
        demand_score = mkt.get("customer_demand_score", "50/100")
        gross_sales = mkt.get("monthly_gross_sales_estimate", 0.0)

        story.append(Paragraph(
            f"The business serves the <b>{mkt.get('target_market', district)}</b> commercial catchment area, targeting <b>{mkt.get('customer_profile', 'local patrons')}</b>. "
            f"Baseline operations capture approximately <b>{cust_per_day} customer transactions per day</b> at an average unit price of "
            f"<b>LKR {unit_price:,.2f}</b> across <b>{op_days} operating days per month</b>. This generates an estimated monthly throughput of "
            f"<b>{monthly_vol:,} customer interactions</b> and an estimated monthly gross sales volume of <b>LKR {gross_sales:,.2f}</b>. "
            f"The evaluated customer demand index stands at <b>{demand_score}</b>.",
            body_style
        ))

        # 2.2 Relevant Growth Opportunities
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>2.2 Identification of Relevant Growth Opportunities</b>", h2_style))
        story.append(Paragraph(
            "Rather than assuming a mandatory expansion pathway or enforcing a branch/product dichotomy, SME360 AI evaluated seven "
            "potential growth avenues against the business's actual capital runway, equipment readiness, staffing, and local demand score. "
            "The opportunities below are prioritized based on verified data suitability:",
            body_style
        ))

        for opp in s2.get("identified_growth_opportunities", []):
            opp_name = opp.get("opportunity_area", "Growth Avenue")
            opp_app = opp.get("applicability", "Relevant")
            opp_act = opp.get("strategic_action", "")
            
            app_color = "#166534" if "Primary" in opp_app or "Immediate" in opp_app else "#854d0e" if "Secondary" in opp_app or "Disciplined" in opp_app else "#64748b"
            
            opp_box = [
                Paragraph(f"<b>{opp_name}</b> — <font color='{app_color}'><b>[{opp_app.upper()}]</b></font>", ParagraphStyle('OppHead', parent=body_style, fontName='Helvetica-Bold', fontSize=9, textColor=primary_color)),
                Spacer(1, 1),
                Paragraph(opp_act, body_style)
            ]
            story.append(create_callout_box(opp_box, bg=colors.HexColor("#f8fafc"), border=card_border, padding=6))
            story.append(Spacer(1, 3))

        # 2.3 Competitive Dynamics & Local Market Positioning
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>2.3 Competitive Dynamics & Local Market Positioning</b>", h2_style))
        comp = s2.get("competitive_environment", {})
        story.append(Paragraph(
            f"The local competitive environment is recorded at a <b>{comp.get('competition_level', 'Moderate')}</b> competition level "
            f"({comp.get('competitor_count_nearby', 'Nearby competitor count')} | {comp.get('competitor_information', '')}). "
            f"To secure patron retention and defend gross margins, the enterprise's recommended market positioning is: "
            f"<i>{comp.get('positioning_strategy', 'Consistent operational execution and service differentiation.')}</i>",
            body_style
        ))

        # Every section starts on a new page!
        story.append(PageBreak())

        # =====================================================================
        # 3. FEASIBILITY ASSESSMENT AND KEY FINDINGS
        # =====================================================================
        s3 = sec_dict.get("section_3_feasibility_findings", {})
        story.append(Paragraph("3. FEASIBILITY ASSESSMENT AND KEY FINDINGS", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 3.1 AI Feasibility Classification & Model Prediction
        story.append(Paragraph("<b>3.1 AI Feasibility Classification & Model Prediction</b>", h2_style))
        ml_feas = s3.get("ml_feasibility_classification", {})
        f_pred = ml_feas.get("predicted_label", pred_label)
        f_conf = ml_feas.get("confidence_percentage", conf_pct)
        f_probs = ml_feas.get("probabilities", probs)
        f_badge_color = "#166534" if f_pred == "Feasible" else "#854d0e" if "Conditionally" in f_pred else "#991b1b"

        f_box = [
            Paragraph(f"<font color='{f_badge_color}' size='11'><b>ASSESSMENT VERDICT: {f_pred.upper()} (Model Confidence: {f_conf})</b></font>", body_style),
            Spacer(1, 2),
            Paragraph(f"<font color='#475569'>Probability Distribution: Feasible: <b>{f_probs.get('Feasible', 0.0):.1%}</b> | Conditionally Feasible: <b>{f_probs.get('Conditionally Feasible', 0.0):.1%}</b> | Infeasible: <b>{f_probs.get('Infeasible', 0.0):.1%}</b></font>", body_style),
            Spacer(1, 2),
            Paragraph(ml_feas.get("interpretation", ""), body_style)
        ]
        story.append(create_callout_box(f_box, bg=colors.HexColor("#f8fafc"), border=card_border, padding=8))

        # Chart
        try:
            chart_bytes = BusinessPlanChartGenerator.generate_probability_chart(f_probs)
            chart_img = Image(io.BytesIO(chart_bytes), width=480, height=125)
            story.append(Spacer(1, 4))
            story.append(chart_img)
        except Exception:
            pass

        # 3.2 Key Factors Influencing the Prediction (SHAP Explainability)
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>3.2 Key Factors Influencing the Prediction (SHAP Explainability)</b>", h2_style))
        story.append(Paragraph(
            "To ensure transparent decision support, SHAP (SHapley Additive exPlanations) values decompose the model's prediction into "
            "individual feature contributions, highlighting positive business strengths versus operational friction points:",
            body_style
        ))

        story.append(Paragraph("<b>Primary Positive Supporting Factors:</b>", h3_style))
        pos_drivers = s3.get("key_positive_drivers", [])
        if pos_drivers:
            for p_drv in pos_drivers:
                story.append(Paragraph(f"• <b>{p_drv.get('feature', '')} ({p_drv.get('feature_value', '')}):</b> {p_drv.get('business_interpretation', '')}", bullet_style))
        else:
            story.append(Paragraph("• Available capital and customer demand score align positively with baseline operational requirements.", bullet_style))

        story.append(Spacer(1, 2))
        story.append(Paragraph("<b>Operational Hurdles Requiring Management Attention:</b>", h3_style))
        neg_hurdles = s3.get("key_negative_hurdles", [])
        if neg_hurdles:
            for n_hrd in neg_hurdles:
                story.append(Paragraph(f"• <b>{n_hrd.get('feature', '')} ({n_hrd.get('feature_value', '')}):</b> {n_hrd.get('business_interpretation', '')}", bullet_style))
        else:
            story.append(Paragraph("• Working capital buffer and peak customer throughput should be monitored to avoid cash strain.", bullet_style))

        # 3.3 Resource Availability & Operational Readiness
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>3.3 Resource Availability & Operational Readiness</b>", h2_style))
        res_avail = s3.get("resource_availability_assessment", {})
        story.append(Paragraph(f"• <b>Staffing Balance:</b> {res_avail.get('staffing_balance', '')}", bullet_style))
        story.append(Paragraph(f"• <b>Equipment Readiness:</b> {res_avail.get('equipment_readiness', '')}", bullet_style))
        story.append(Paragraph(f"• <b>Supplier Access:</b> {res_avail.get('supplier_access', '')}", bullet_style))
        story.append(Paragraph(f"• <b>Location Suitability:</b> {res_avail.get('location_suitability', '')}", bullet_style))

        # 3.4 Identified Affordability Gaps & Strategic Findings
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>3.4 Identified Affordability Gaps & Key Findings</b>", h2_style))
        aff_gaps = s3.get("affordability_gaps_and_findings", {})
        story.append(Paragraph(
            f"The business growth strategy targets a capital requirement of <b>LKR {aff_gaps.get('strategy_target_capital_lkr', 0):,.2f}</b>. "
            f"Recorded available funding equals <b>LKR {aff_gaps.get('total_available_funds_lkr', 0):,.2f}</b> (Available Equity: LKR {aff_gaps.get('available_capital_lkr', 0):,.2f} + Loan: LKR {aff_gaps.get('loan_amount_lkr', 0):,.2f}), "
            f"placing the enterprise in a <b>{aff_gaps.get('funding_gap_status', 'Fully funded')}</b> position. "
            f"Liquidity runway provides approximately <b>{aff_gaps.get('capital_runway_months', 0)} months</b> of strategy budget coverage. "
            f"{aff_gaps.get('key_findings_summary', '')}",
            body_style
        ))

        # Every section starts on a new page!
        story.append(PageBreak())

        # =====================================================================
        # 4. PERSONALIZED GROWTH STRATEGY
        # =====================================================================
        s4 = sec_dict.get("section_4_growth_strategy", {})
        story.append(Paragraph("4. PERSONALIZED GROWTH STRATEGY", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 4.1 Recommended Growth Approach
        story.append(Paragraph("<b>4.1 Recommended Strategic Growth Approach</b>", h2_style))
        rec_app = s4.get("recommended_growth_approach", {})
        story.append(Paragraph(
            f"SME360 AI recommends <b>{rec_app.get('strategy_name', 'Capital-Protected Phased Growth')}</b> "
            f"(Strategic Focus: <i>{rec_app.get('strategic_focus', 'Controlled Phased Growth')}</i>, "
            f"TOPSIS Closeness Score: <b>{rec_app.get('topsis_score', 'N/A')}</b>) as the primary growth vehicle for {biz_name}. "
            f"{rec_app.get('selection_status', '')}",
            body_style
        ))
        story.append(Paragraph(rec_app.get("operational_approach", ""), body_style))

        # Strategy Suitability Rationale
        story.append(Spacer(1, 3))
        story.append(Paragraph("<b>Strategic Suitability Rationale:</b>", h3_style))
        story.append(Paragraph(s4.get("strategy_suitability_rationale", ""), body_style))

        # 4.2 Multi-Criteria Comparison of Strategic Alternatives (TOPSIS Ranking)
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>4.2 Multi-Criteria Comparison of Strategic Alternatives (TOPSIS Ranking)</b>", h2_style))
        story.append(Paragraph(
            "To avoid subjective bias, four strategic pathways were evaluated using the Technique for Order of Preference by "
            "Similarity to Ideal Solution (TOPSIS). The evaluation balanced five validated dimensions: "
            "<b>Financial Viability (25%)</b>, <b>Market Demand Alignment (25%)</b>, <b>Implementation Feasibility (20%)</b>, "
            "<b>Operational Risk (15%)</b>, and <b>Resource Efficiency (15%)</b>:",
            body_style
        ))

        strat_table_data = [
            [
                Paragraph("<b>Rank</b>", table_header_style),
                Paragraph("<b>Strategy Pathway</b>", table_header_style),
                Paragraph("<b>Strategic Focus</b>", table_header_style),
                Paragraph("<b>Target Capital</b>", table_header_style),
                Paragraph("<b>TOPSIS Score</b>", table_header_style),
            ]
        ]
        alt_comp = s4.get("alternatives_comparison", {})
        for r_strat in alt_comp.get("ranked_strategies", []):
            strat_table_data.append([
                Paragraph(f"<b>#{r_strat.get('rank', '-')}</b>", table_cell_style),
                Paragraph(f"<b>{r_strat.get('strategy_name', '')}</b>", table_cell_style),
                Paragraph(r_strat.get("strategic_focus", "Growth"), table_cell_style),
                Paragraph(f"LKR {r_strat.get('estimated_capital_required_lkr', 0):,.0f}", table_cell_style),
                Paragraph(str(r_strat.get("topsis_score", "N/A")), table_cell_style),
            ])
        strat_table = Table(strat_table_data, colWidths=[35, 175, 155, 105, 70])
        strat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('PADDING', (0,0), (-1,-1), 4.5),
            ('BOX', (0,0), (-1,-1), 1, card_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(strat_table)

        # 4.3 Practical & Prioritized Actions
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>4.3 Practical & Prioritized Growth Actions</b>", h2_style))
        for act in s4.get("prioritized_practical_actions", []):
            story.append(Paragraph(f"• {act}", bullet_style))

        # 4.4 Addressing Identified Resource & Operational Gaps
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>4.4 Addressing Resource & Operational Gaps</b>", h2_style))
        for gap in s4.get("gap_mitigation_plan", []):
            story.append(Paragraph(f"• {gap}", bullet_style))

        # Every section starts on a new page!
        story.append(PageBreak())

        # =====================================================================
        # 5. FINANCIAL AND RESOURCE PLAN
        # =====================================================================
        s5 = sec_dict.get("section_5_financial_resource", {})
        story.append(Paragraph("5. FINANCIAL AND RESOURCE PLAN", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 5.1 Estimated Cost of Recommended Growth Actions
        story.append(Paragraph("<b>5.1 Estimated Cost of Recommended Growth Actions</b>", h2_style))
        costs = s5.get("estimated_growth_costs", {})
        capex_val = costs.get("capex_and_tooling_upgrades_lkr", 0.0)
        inv_val = costs.get("inventory_replenishment_cost_lkr", 0.0)
        buf_val = costs.get("working_capital_reserve_lkr", 0.0)
        tot_val = costs.get("total_estimated_growth_capital_lkr", 0.0)

        cost_tbl_data = [
            [Paragraph("<b>Growth Investment Component</b>", table_header_style), Paragraph("<b>Estimated Capital (LKR)</b>", table_header_style), Paragraph("<b>Strategic Purpose & Description</b>", table_header_style)],
            [Paragraph("CapEx & Fixture/Tooling Upgrades", table_cell_style), Paragraph(f"LKR {capex_val:,.2f}", table_cell_style), Paragraph("Physical workspace optimization and equipment upgrades", table_cell_style)],
            [Paragraph("Initial Inventory & Wholesale Stock", table_cell_style), Paragraph(f"LKR {inv_val:,.2f}", table_cell_style), Paragraph("Stock replenishment to support anticipated customer footfall", table_cell_style)],
            [Paragraph("Working Capital Reserve Buffer", table_cell_style), Paragraph(f"LKR {buf_val:,.2f}", table_cell_style), Paragraph("Liquidity buffer covering baseline operational ramp-up", table_cell_style)],
            [Paragraph("<b>Total Estimated Growth Capital</b>", table_cell_style), Paragraph(f"<b>LKR {tot_val:,.2f}</b>", table_cell_style), Paragraph("<b>Calibrated baseline target growth allocation</b>", table_cell_style)],
        ]
        cost_tbl = Table(cost_tbl_data, colWidths=[180, 140, 220])
        cost_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
            ('PADDING', (0,0), (-1,-1), 4.5),
            ('BOX', (0,0), (-1,-1), 1, card_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(cost_tbl)

        # 5.2 Capital Structure & Funding Requirements
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>5.2 Capital Structure, Funding Requirements & Liquidity Runway</b>", h2_style))
        fund_data = s5.get("available_capital_and_funding", {})
        story.append(Paragraph(
            f"The business is supported by <b>LKR {fund_data.get('available_capital_lkr', 0):,.2f}</b> in recorded available capital and "
            f"<b>LKR {fund_data.get('loan_amount_lkr', 0):,.2f}</b> in external debt financing, delivering total available funds of "
            f"<b>LKR {fund_data.get('total_available_funds_lkr', 0):,.2f}</b> against a target growth capital requirement of "
            f"<b>LKR {fund_data.get('strategy_target_capital_lkr', 0):,.2f}</b> ({fund_data.get('funding_gap_status', 'Fully funded')}).",
            body_style
        ))

        # 5.3 Resource & Staffing Requirements
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>5.3 Staffing & Equipment Resource Plan</b>", h2_style))
        st_data = s5.get("resource_and_staffing_requirements", {})
        story.append(Paragraph(
            f"Current staff allocation stands at <b>{st_data.get('available_staff_count', 1)} staff member(s)</b> against an estimated requirement of "
            f"<b>{st_data.get('required_staff_count', 1)}</b> ({st_data.get('capacity_status', '')}). "
            f"Equipment readiness status: <b>{st_data.get('equipment_status', '3/5')}</b>. Local supplier access: <b>{st_data.get('supplier_access', '')}</b>.",
            body_style
        ))

        # 5.4 Operating Expenses & Revenue Projections
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>5.4 Operating Expenses & Financial Projections</b>", h2_style))
        op_data = s5.get("operating_expenses", {})
        story.append(Paragraph(
            f"Monthly operating budget is established at <b>LKR {op_data.get('monthly_operating_budget_lkr', 0):,.2f}</b>, providing approximately "
            f"<b>{op_data.get('strategy_capital_runway_months', 0)} months</b> of strategy budget coverage and "
            f"<b>{op_data.get('total_funds_runway_months', 0)} months</b> of total funds liquidity runway. "
            f"{op_data.get('expense_guidance', '')}",
            body_style
        ))

        # Financial Projections Table
        story.append(Spacer(1, 3))
        f_proj = s5.get("financial_projections", [])
        if f_proj:
            proj_tbl_data = [
                [Paragraph("<b>Financial Metric</b>", table_header_style), Paragraph("<b>Projected Target</b>", table_header_style), Paragraph("<b>Basis of Projection</b>", table_header_style)]
            ]
            for p in f_proj:
                proj_tbl_data.append([
                    Paragraph(f"<b>{p.get('metric', '')}</b>", table_cell_style),
                    Paragraph(p.get("value", ""), table_cell_style),
                    Paragraph(p.get("basis", ""), table_cell_style)
                ])
            proj_tbl = Table(proj_tbl_data, colWidths=[160, 140, 240])
            proj_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(proj_tbl)

        # 5.5 Investment Recovery & Payback Analysis
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>5.5 Investment Recovery & Payback Safeguards</b>", h2_style))
        pb = s5.get("payback_and_affordability_analysis", {})
        if pb.get("is_calculated"):
            p_pb = (
                f"Based on stated one-time growth CapEx and operating net cash flow baseline, the target investment "
                f"payback period is estimated at approximately <b>~{pb.get('estimated_payback_months')} months</b>. "
                f"<i>(Note: Assumes sustained monthly net profit without unexpected commodity cost inflation.)</i>"
            )
        else:
            p_pb = (
                f"<b>Payback Calculation Status:</b> <font color='#854d0e'><b>Baseline Net Profit Input Pending</b></font>. "
                f"To maintain professional accounting integrity, payback period and ROI are not fabricated or derived from gross sales turnover alone. "
                f"{pb.get('affordability_note', '')}"
            )
        story.append(Paragraph(p_pb, body_style))

        # Every section starts on a new page!
        story.append(PageBreak())

        # =====================================================================
        # 6. IMPLEMENTATION ROADMAP
        # =====================================================================
        s6 = sec_dict.get("section_6_implementation_roadmap", {})
        story.append(Paragraph("6. IMPLEMENTATION ROADMAP", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 6.1 Prioritized Growth Implementation Actions
        story.append(Paragraph("<b>6.1 Prioritized Growth Implementation Actions</b>", h2_style))
        for p_act in s6.get("prioritized_actions", []):
            story.append(Paragraph(f"• {p_act}", bullet_style))

        # 6.2 Recommended Implementation Stages (Four Horizons)
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.2 Recommended Implementation Stages (Four Operational Horizons)</b>", h2_style))
        for stg in s6.get("implementation_stages", []):
            story.append(Paragraph(f"<b>{stg.get('stage_name', '')} ({stg.get('timeframe', '')}):</b>", h3_style))
            story.append(Paragraph(stg.get("focus_actions", ""), body_style))

        # 6.3 Key Growth Milestones & Success Criteria
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.3 Key Growth Milestones & Success Criteria</b>", h2_style))
        ms_list = s6.get("launch_milestones", [])
        if ms_list:
            ms_tbl_data = [
                [Paragraph("<b>Milestone Name</b>", table_header_style), Paragraph("<b>Target Timeline</b>", table_header_style), Paragraph("<b>Measurable Success Criteria</b>", table_header_style)]
            ]
            for m in ms_list:
                ms_tbl_data.append([
                    Paragraph(f"<b>{m.get('milestone', '')}</b>", table_cell_style),
                    Paragraph(m.get("target_timeframe", ""), table_cell_style),
                    Paragraph(m.get("success_criteria", ""), table_cell_style)
                ])
            ms_tbl = Table(ms_tbl_data, colWidths=[150, 90, 300])
            ms_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(ms_tbl)

        # 6.4 Operational Responsibilities Matrix
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.4 Operational Responsibilities Matrix</b>", h2_style))
        resp_list = s6.get("responsibilities", [])
        if resp_list:
            resp_tbl_data = [
                [Paragraph("<b>Operating Role</b>", table_header_style), Paragraph("<b>Core Accountabilities & Responsibilities</b>", table_header_style)]
            ]
            for r in resp_list:
                resp_tbl_data.append([
                    Paragraph(f"<b>{r.get('role', '')}</b>", table_cell_style),
                    Paragraph(r.get("accountabilities", ""), table_cell_style)
                ])
            resp_tbl = Table(resp_tbl_data, colWidths=[160, 380])
            resp_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(resp_tbl)

        # 6.5 Progress Monitoring & Governance
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>6.5 Progress Monitoring & Governance Cadence</b>", h2_style))
        story.append(Paragraph(s6.get("progress_monitoring", "Management should conduct regular cash reconciliations and strategy reviews."), body_style))

        # Every section starts on a new page!
        story.append(PageBreak())

        # =====================================================================
        # 7. EXPECTED OUTCOMES AND SUCCESS INDICATORS
        # =====================================================================
        s7 = sec_dict.get("section_7_outcomes_indicators", {})
        story.append(Paragraph("7. EXPECTED OUTCOMES AND SUCCESS INDICATORS", h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=8))

        # 7.1 Expected Business Improvements & Outcomes
        story.append(Paragraph("<b>7.1 Expected Business Improvements & Outcomes</b>", h2_style))
        for outcome in s7.get("expected_business_outcomes", []):
            story.append(Paragraph(f"• {outcome}", bullet_style))

        # 7.2 Measurable Business Targets & KPIs
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>7.2 Measurable Business Targets & Key Performance Indicators</b>", h2_style))
        kpi_list = s7.get("measurable_targets_kpis", [])
        if kpi_list:
            kpi_tbl_data = [
                [Paragraph("<b>Performance Indicator</b>", table_header_style), Paragraph("<b>Target Objective</b>", table_header_style), Paragraph("<b>Tracking Frequency</b>", table_header_style), Paragraph("<b>Focus Area</b>", table_header_style)]
            ]
            for k in kpi_list:
                kpi_tbl_data.append([
                    Paragraph(f"<b>{k.get('kpi_name', '')}</b>", table_cell_style),
                    Paragraph(str(k.get("target_value", "")), table_cell_style),
                    Paragraph(k.get("monitoring_frequency", "Monthly"), table_cell_style),
                    Paragraph(k.get("focus_area", "Operational"), table_cell_style)
                ])
            kpi_tbl = Table(kpi_tbl_data, colWidths=[140, 160, 110, 130])
            kpi_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('PADDING', (0,0), (-1,-1), 4.5),
                ('BOX', (0,0), (-1,-1), 1, card_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, grid_border),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(kpi_tbl)

        # 7.3 Suggested Methods for Tracking Progress
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>7.3 Suggested Methods for Tracking Progress</b>", h2_style))
        for mth in s7.get("suggested_methods_for_tracking_progress", []):
            story.append(Paragraph(f"• {mth}", bullet_style))

        # 7.4 Important Business Assumptions & Methodological Disclosures
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>7.4 Important Business Assumptions & Planning Limitations</b>", h2_style))
        story.append(Paragraph("<b>Planning Assumptions:</b>", h3_style))
        for asm in s7.get("important_business_assumptions", []):
            story.append(Paragraph(f"• {asm}", bullet_style))

        story.append(Spacer(1, 2))
        story.append(Paragraph("<b>Data Limitations & Methodological Disclosures:</b>", h3_style))
        for lim in s7.get("data_limitations_and_validation", []):
            story.append(Paragraph(f"• {lim}", bullet_style))

    _render_existing_business_sections = _render_unified_growth_sections

