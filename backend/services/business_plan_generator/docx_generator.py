import os
import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from backend.services.business_plan_generator.chart_generator import BusinessPlanChartGenerator
from backend.services.business_plan_generator.cover_image_handler import CoverImageHandler

LOGO_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "frontend", "src", "assets", "logo", "sme360-ai-logo.png"
))

class BusinessPlanDocxGenerator:
    """
    Generates an editable, consultancy-grade Microsoft Word (.docx) document
    for SME360 AI Business Plans adhering to a professional narrative structure:
    'BUSINESS STORY -> ANALYSIS -> EXPLANATION -> RECOMMENDATION -> ACTION'
    with structured comparison tables used only where genuinely necessary.
    """

    @staticmethod
    def set_cell_background(cell, fill_hex):
        """Sets XML background color for a table cell."""
        tcPr = cell._element.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    @staticmethod
    def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
        """Sets XML internal cell padding in dxa (1 pt = 20 dxa)."""
        tcPr = cell._element.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    @staticmethod
    def generate_docx(report_data: dict) -> bytes:
        doc = Document()

        raw_cover = report_data.get("cover_image") or "default"
        cover_info = None
        try:
            cover_info = CoverImageHandler.process_cover_image(raw_cover)
        except Exception:
            try:
                cover_info = CoverImageHandler.process_cover_image("default")
            except Exception:
                cover_info = None

        if cover_info:
            # 0. Custom Cover Page Section (Full A4, zero margins)
            sec_cover = doc.sections[0]
            sec_cover.page_width = Inches(cover_info["docx_geometry"]["page_width_in"])
            sec_cover.page_height = Inches(cover_info["docx_geometry"]["page_height_in"])
            sec_cover.top_margin = Inches(0)
            sec_cover.bottom_margin = Inches(0)
            sec_cover.left_margin = Inches(0)
            sec_cover.right_margin = Inches(0)

            p_cover = doc.add_paragraph()
            p_cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cover.paragraph_format.space_before = Pt(cover_info["docx_geometry"]["top_space_pt"])
            p_cover.paragraph_format.space_after = Pt(0)
            run_cov = p_cover.add_run()
            run_cov.add_picture(
                io.BytesIO(cover_info["image_bytes"]),
                width=Inches(cover_info["docx_geometry"]["width_in"]),
                height=Inches(cover_info["docx_geometry"]["height_in"])
            )

            # Section break: Business Plan content begins cleanly on Page 2
            sec_body = doc.add_section()
            sec_body.page_width = Inches(cover_info["docx_geometry"]["page_width_in"])
            sec_body.page_height = Inches(cover_info["docx_geometry"]["page_height_in"])
            sec_body.top_margin = Inches(0.75)
            sec_body.bottom_margin = Inches(0.75)
            sec_body.left_margin = Inches(0.75)
            sec_body.right_margin = Inches(0.75)
        else:
            # Standard Business Plan without custom cover
            sec_body = doc.sections[0]
            sec_body.page_width = Inches(8.27)
            sec_body.page_height = Inches(11.69)
            sec_body.top_margin = Inches(0.75)
            sec_body.bottom_margin = Inches(0.75)
            sec_body.left_margin = Inches(0.75)
            sec_body.right_margin = Inches(0.75)

        # Corporate Color Palette
        COLOR_PRIMARY = RGBColor(30, 58, 138)   # #1e3a8a Deep Navy
        COLOR_ACCENT = RGBColor(37, 99, 235)   # #2563eb Vibrant Blue
        COLOR_DARK = RGBColor(15, 23, 42)      # #0f172a Slate 900
        COLOR_MUTED = RGBColor(100, 116, 139)  # #64748b Slate 600

        metadata = report_data.get("metadata", {})
        biz_id = report_data.get("business_identity", {})
        biz_name = biz_id.get("business_name", "Enterprise")
        category = biz_id.get("business_category", "SME Business")
        stage = biz_id.get("business_stage", "New Startup")
        district = biz_id.get("district", "Colombo")
        province = biz_id.get("province", "Western")

        # Helper: Body Paragraph
        def add_body_p(text, bold_prefix=None, space_after=5):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(space_after)
            p.paragraph_format.line_spacing = 1.15
            if bold_prefix:
                r_b = p.add_run(bold_prefix)
                r_b.font.name = 'Arial'
                r_b.font.size = Pt(9.5)
                r_b.font.bold = True
                r_b.font.color.rgb = COLOR_DARK
            r = p.add_run(text)
            r.font.name = 'Arial'
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_DARK
            return p

        # Helper: Bullet Point
        def add_bullet_p(text, bold_prefix=None, space_after=3.5):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(space_after)
            p.paragraph_format.line_spacing = 1.12
            if bold_prefix:
                r_b = p.add_run(bold_prefix)
                r_b.font.name = 'Arial'
                r_b.font.size = Pt(9.5)
                r_b.font.bold = True
                r_b.font.color.rgb = COLOR_DARK
            r = p.add_run(text)
            r.font.name = 'Arial'
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_DARK
            return p

        # Helper: Heading 1
        def add_h1(text):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            r = p.add_run(text)
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = COLOR_PRIMARY
            return p

        # Helper: Heading 2
        def add_h2(text):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(text)
            r.font.name = 'Arial'
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = COLOR_ACCENT
            return p

        # Helper: Heading 3
        def add_h3(text):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(text)
            r.font.name = 'Arial'
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = COLOR_DARK
            return p

        # Helper: Callout Card Panel
        def add_callout_box(title, lines_list, bg_hex="F8FAFC"):
            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = tbl.cell(0, 0)
            cell.width = Inches(7.0)
            BusinessPlanDocxGenerator.set_cell_background(cell, bg_hex)
            BusinessPlanDocxGenerator.set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            if title:
                r_t = p.add_run(title + "\n")
                r_t.font.name = 'Arial'
                r_t.font.size = Pt(10)
                r_t.font.bold = True
                r_t.font.color.rgb = COLOR_PRIMARY

            for idx, line in enumerate(lines_list):
                if idx > 0 or title:
                    p = cell.add_paragraph()
                    p.paragraph_format.space_after = Pt(2)
                r_l = p.add_run(line)
                r_l.font.name = 'Arial'
                r_l.font.size = Pt(9)
                r_l.font.color.rgb = COLOR_DARK
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

        # Helper: 4-Column Metric Strip
        def add_metric_strip(metrics):
            tbl = doc.add_table(rows=1, cols=len(metrics))
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            col_w = Inches(7.0 / len(metrics))
            for idx, (label, val, sub) in enumerate(metrics):
                cell = tbl.cell(0, idx)
                cell.width = col_w
                BusinessPlanDocxGenerator.set_cell_background(cell, "F8FAFC")
                BusinessPlanDocxGenerator.set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(1)
                
                r_lbl = p.add_run(label.upper() + "\n")
                r_lbl.font.name = 'Arial'
                r_lbl.font.size = Pt(7)
                r_lbl.font.bold = True
                r_lbl.font.color.rgb = COLOR_MUTED

                r_val = p.add_run(str(val) + "\n")
                r_val.font.name = 'Arial'
                r_val.font.size = Pt(11)
                r_val.font.bold = True
                r_val.font.color.rgb = COLOR_PRIMARY

                r_sub = p.add_run(str(sub))
                r_sub.font.name = 'Arial'
                r_sub.font.size = Pt(7)
                r_sub.font.color.rgb = COLOR_MUTED
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

        # =========================================================================
        # 1. COVER PAGE
        # =========================================================================
        if os.path.exists(LOGO_PATH):
            try:
                p_logo = doc.add_paragraph()
                p_logo.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run_logo = p_logo.add_run()
                run_logo.add_picture(LOGO_PATH, width=Inches(1.8))
            except Exception:
                pass

        p_sub = doc.add_paragraph()
        p_sub.paragraph_format.space_before = Pt(16)
        p_sub.paragraph_format.space_after = Pt(2)
        run_sub = p_sub.add_run(metadata.get("system_brand", "SME360 AI"))
        run_sub.font.name = 'Arial'
        run_sub.font.size = Pt(11)
        run_sub.font.bold = True
        run_sub.font.color.rgb = COLOR_ACCENT

        is_new_startup = "new" in stage.lower() or "start" in stage.lower()
        doc_title = metadata.get("document_title") or ("STRATEGIC BUSINESS PLAN" if is_new_startup else "PERSONALIZED BUSINESS GROWTH PLAN")
        doc_desc = metadata.get("document_subtitle") or (
            "A Comprehensive Feasibility, Strategic Direction & Implementation Blueprint"
            if is_new_startup else
            "A Tailored Strategic Growth & Decision Support Blueprint"
        )

        p_title = doc.add_paragraph()
        p_title.paragraph_format.space_after = Pt(4)
        run_title = p_title.add_run(doc_title)
        run_title.font.name = 'Arial'
        run_title.font.size = Pt(24)
        run_title.font.bold = True
        run_title.font.color.rgb = COLOR_PRIMARY

        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.space_after = Pt(22)
        run_desc = p_desc.add_run(doc_desc)
        run_desc.font.name = 'Arial'
        run_desc.font.size = Pt(10)
        run_desc.font.color.rgb = COLOR_MUTED

        # Cover Executive Metadata Panel
        clean_stage_display = "New Startup" if "new" in stage.lower() else "Existing Business"
        cov_lines = [
            f"Prepared For: {biz_name}",
            f"Enterprise Category & Stage: {category} • {clean_stage_display}",
            f"Operating Catchment: {district}, {province} Province, Sri Lanka",
            f"Preparation Date: {metadata.get('generated_date', 'Current')}",
            f"Decision Record Reference: {metadata.get('record_id', 'N/A')}"
        ]
        add_callout_box("ENTERPRISE PROFILE & DOCUMENT METADATA", cov_lines, bg_hex="F8FAFC")

        p_disc = doc.add_paragraph()
        p_disc.paragraph_format.space_before = Pt(30)
        r_disc = p_disc.add_run(
            "This document synthesizes machine-learned feasibility prediction, explainable SHAP feature attribution, "
            "TOPSIS multi-criteria strategy prioritization, and sensitivity scenario stress-testing into an actionable strategic roadmap "
            "tailored specifically to this enterprise."
        )
        r_disc.font.name = 'Arial'
        r_disc.font.size = Pt(8.5)
        r_disc.font.italic = True
        r_disc.font.color.rgb = COLOR_MUTED

        doc.add_page_break()

        def add_styled_table(headers, rows, col_widths=None):
            tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            for idx, h in enumerate(headers):
                cell = tbl.cell(0, idx)
                if col_widths and idx < len(col_widths):
                    cell.width = Inches(col_widths[idx])
                BusinessPlanDocxGenerator.set_cell_background(cell, "1E3A8A")
                BusinessPlanDocxGenerator.set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                r = p.add_run(h)
                r.font.name = 'Arial'
                r.font.size = Pt(8.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
            for r_idx, row in enumerate(rows):
                for c_idx, val in enumerate(row):
                    cell = tbl.cell(r_idx + 1, c_idx)
                    if col_widths and c_idx < len(col_widths):
                        cell.width = Inches(col_widths[c_idx])
                    if r_idx % 2 == 1:
                        BusinessPlanDocxGenerator.set_cell_background(cell, "F8FAFC")
                    BusinessPlanDocxGenerator.set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(2)
                    r = p.add_run(str(val))
                    r.font.name = 'Arial'
                    r.font.size = Pt(8.5)
                    r.font.color.rgb = COLOR_DARK
            doc.add_paragraph().paragraph_format.space_after = Pt(6)

        ctx = {
            "doc": doc,
            "add_h1": add_h1,
            "add_h2": add_h2,
            "add_h3": add_h3,
            "add_body_p": add_body_p,
            "add_bullet_p": add_bullet_p,
            "add_callout_box": add_callout_box,
            "add_metric_strip": add_metric_strip,
            "add_styled_table": add_styled_table,
            "COLOR_PRIMARY": COLOR_PRIMARY,
            "COLOR_ACCENT": COLOR_ACCENT,
            "COLOR_DARK": COLOR_DARK,
            "COLOR_MUTED": COLOR_MUTED,
        }

        new_startup_sections = report_data.get("new_startup_sections")
        is_new_startup = "new" in stage.lower() or "start" in stage.lower()
        if is_new_startup and new_startup_sections:
            BusinessPlanDocxGenerator._render_new_startup_sections(report_data, ctx)
        else:
            BusinessPlanDocxGenerator._render_unified_growth_sections(report_data, ctx)

        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        return bio.getvalue()

    @staticmethod
    def _render_new_startup_sections(report_data: dict, ctx: dict):
        doc = ctx["doc"]
        add_h1 = ctx["add_h1"]
        add_h2 = ctx["add_h2"]
        add_h3 = ctx["add_h3"]
        add_body_p = ctx["add_body_p"]
        add_bullet_p = ctx["add_bullet_p"]
        add_callout_box = ctx["add_callout_box"]
        add_metric_strip = ctx["add_metric_strip"]
        add_styled_table = ctx["add_styled_table"]

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
        add_h1("SECTION 01 — EXECUTIVE SUMMARY")

        # 1.1 Business Idea Overview
        add_h2("1.1 Business Idea Overview")
        s1_bio = s1.get("business_idea_overview", {})
        add_body_p(
            f"{biz_name} is a proposed new startup venture within the {category} industry, "
            f"planned for commercial launch in {district}, {province} Province, Sri Lanka. "
            f"{s1_bio.get('summary_text', '')}"
        )

        # 1.2 AI Feasibility Result
        add_h2("1.2 AI Feasibility Result")
        s1_feas = s1.get("ai_feasibility_result", {})
        pred_label = s1_feas.get("predicted_label", "Conditionally Feasible")
        conf_pct = s1_feas.get("confidence_percentage", "65.0%")
        probs = s1_feas.get("probabilities", {})
        prob_feas = probs.get("Feasible", 0.0)
        prob_cond = probs.get("Conditionally Feasible", 0.0)
        prob_infeas = probs.get("Infeasible", 0.0)

        feas_lines = [
            f"Assessment Verdict: {pred_label.upper()} (Predicted Class Probability: {conf_pct})",
            f"Multi-Class Model Distribution: Feasible: {prob_feas:.1%} | Conditionally Feasible: {prob_cond:.1%} | Infeasible: {prob_infeas:.1%}",
            s1_feas.get("interpretation", "")
        ]
        add_callout_box("AI FEASIBILITY ASSESSMENT OUTCOME", feas_lines, bg_hex="F8FAFC")

        # 1.3 Recommended Strategy
        add_h2("1.3 Recommended Strategy")
        s1_strat = s1.get("recommended_strategy", {})
        strat_name = s1_strat.get("strategy_name", "Lean Bootstrapped Start")
        strat_focus = s1_strat.get("strategic_focus", "Capital Protection & Phased Scale")
        topsis_score = s1_strat.get("topsis_score", "N/A")
        align_note = s1_strat.get("alignment_note", "")
        add_body_p(
            f"Based on algorithmic multi-criteria ranking, the system identifies {strat_name} "
            f"(TOPSIS Closeness Score: {topsis_score}) as the strategic direction for this venture. "
            f"Strategic Focus: {strat_focus}. {align_note}"
        )

        # 1.4 Required Investment and Funding Summary
        add_h2("1.4 Required Investment and Funding Summary")
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
        add_metric_strip(fin_metrics)
        add_body_p(
            f"The initial target capital requirement is LKR {target_cap:,.0f}. With LKR {avail_cap:,.0f} in recorded available capital "
            f"and LKR {loan_amt:,.0f} in external loan financing, total available liquidity stands at LKR {total_funds:,.0f} ({fund_status}). "
            f"Under the baseline operating budget ceiling of LKR {monthly_budget:,.0f}/month, this provides approximately {runway} months "
            f"of simplified budget coverage."
        )

        # =====================================================================
        # SECTION 02 — BUSINESS OVERVIEW (Starts on New Page)
        # =====================================================================
        doc.add_page_break()
        s2 = sec_dict.get("section_2_business_overview", {})
        add_h1("SECTION 02 — BUSINESS OVERVIEW")

        # 2.1 Business Concept and Objectives
        add_h2("2.1 Business Concept & Objectives")
        s2_co = s2.get("concept_and_objectives", {})
        concept_desc = s2_co.get("business_concept", "")
        biz_model = s2_co.get("business_model", "Direct Retail / Service")
        add_body_p(f"{biz_name} is structured under a {biz_model} operational model. {concept_desc}")
        add_h3("Core Foundational Objectives:")
        for obj in s2_co.get("primary_objectives", []):
            add_bullet_p(obj)

        # 2.2 Business Location Analysis
        add_h2("2.2 Business Location Analysis")
        s2_loc = s2.get("business_location", {})
        loc_type = s2_loc.get("location_type", "Commercial Hub")
        loc_score = s2_loc.get("location_suitability_score", "3/5")
        loc_ctx = s2_loc.get("location_context", "")
        loc_addr = s2_loc.get("address", "Information not provided in intake")
        add_body_p(
            f"The venture is proposed for operation in {district}, {province} Province, Sri Lanka, "
            f"situated within a {loc_type} environment. The location holds a suitability score of {loc_score}. "
            f"{loc_ctx} Registered premise reference: {loc_addr}."
        )

        # 2.3 Products or Services
        add_h2("2.3 Products or Services")
        s2_prod = s2.get("products_or_services", {})
        offering = s2_prod.get("offerings_summary", "")
        op_details = s2_prod.get("operational_details", "")
        exp_price = s2_prod.get("expected_price_lkr", 0.0)
        add_body_p(
            f"{offering} Operations are designed to deliver reliable customer satisfaction through consistent service execution: {op_details} "
            f"Initial offerings are priced around an expected baseline transaction value of LKR {exp_price:,.2f}."
        )

        # 2.4 Target Customers
        add_h2("2.4 Target Customers & Demand Assessment")
        s2_cust = s2.get("target_customers", {})
        target_prof = s2_cust.get("target_profile", f"Consumers in {district}")
        cust_dem_score = s2_cust.get("customer_demand_score", "50/100")
        dem_assess = s2_cust.get("demand_assessment", "")
        add_body_p(
            f"The primary target clientele comprises {target_prof}. "
            f"The recorded customer demand score for this profile is {cust_dem_score}. {dem_assess}"
        )

        # 2.5 Relevant Market Context
        add_h2("2.5 Relevant Market Context & Competitive Landscape")
        s2_mkt = s2.get("relevant_market_context", {})
        comp_level = s2_mkt.get("competition_level", "Moderate")
        comp_cnt = s2_mkt.get("competitor_count_nearby")
        comp_info = s2_mkt.get("competitor_information", "")
        pos_strat = s2_mkt.get("positioning_strategy", "")
        add_body_p(
            f"Local market competition is characterized as {comp_level}. Nearby competitor count is recorded as "
            f"{comp_cnt} ({comp_info}). To establish a viable market share, {pos_strat}"
        )

        # =====================================================================
        # SECTION 03 — FEASIBILITY ASSESSMENT AND KEY FINDINGS (Starts on New Page)
        # =====================================================================
        doc.add_page_break()
        s3 = sec_dict.get("section_3_feasibility_findings", {})
        add_h1("SECTION 03 — FEASIBILITY ASSESSMENT AND KEY FINDINGS")

        # 3.1 ML Feasibility Prediction
        add_h2("3.1 Machine Learning Feasibility Classification")
        s3_pred = s3.get("ml_feasibility_prediction", {})
        pred_label_s3 = s3_pred.get("predicted_label", pred_label)
        conf_pct_s3 = s3_pred.get("confidence_percentage", conf_pct)
        probs_s3 = s3_pred.get("probabilities", probs)
        p_feas_s3 = probs_s3.get("Feasible", 0.0)
        p_cond_s3 = probs_s3.get("Conditionally Feasible", 0.0)
        p_inf_s3 = probs_s3.get("Infeasible", 0.0)
        method_disc = s3_pred.get("methodology_disclosure", "")

        add_body_p(
            f"The business profile was evaluated using SME360 AI's trained Random Forest classification model. "
            f"The model classifies {biz_name} as {pred_label_s3} with a predicted class probability of {conf_pct_s3} "
            f"(Feasible: {p_feas_s3:.1%}, Conditionally Feasible: {p_cond_s3:.1%}, Infeasible: {p_inf_s3:.1%}). "
            f"{method_disc}"
        )

        # Embedded Probability Chart
        try:
            chart_bytes = BusinessPlanChartGenerator.generate_probability_chart(probs_s3)
            p_chart = doc.add_paragraph()
            p_chart.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_chart.paragraph_format.space_before = Pt(4)
            p_chart.paragraph_format.space_after = Pt(8)
            run_chart = p_chart.add_run()
            run_chart.add_picture(io.BytesIO(chart_bytes), width=Inches(6.0))
        except Exception:
            pass

        # 3.2 Factors Influencing Prediction (SHAP)
        add_h2("3.2 Factors Influencing Prediction (SHAP Explainable AI)")
        add_body_p(
            "To understand what features drove this classification, SHAP (SHapley Additive exPlanations) values decompose the model's output into specific positive enablers and operational hurdles:"
        )
        s3_factors = s3.get("factors_influencing_prediction", {})
        pos_enablers = s3_factors.get("positive_enablers", [])
        hurdles = s3_factors.get("operational_hurdles", [])

        add_h3("Positive Enablers Supporting Feasibility:")
        if pos_enablers:
            for item in pos_enablers[:3]:
                feat = item.get("feature", "Factor")
                val = item.get("feature_value", "N/A")
                exp = item.get("impact_explanation", "Contributed positive support.")
                add_bullet_p(f"{feat} ({val}): {exp}")
        else:
            add_bullet_p("Baseline capital and operating assumptions align with initial industry requirements.")

        add_h3("Operational Hurdles Requiring Management Attention:")
        if hurdles:
            for item in hurdles[:3]:
                feat = item.get("feature", "Constraint")
                val = item.get("feature_value", "N/A")
                exp = item.get("impact_explanation", "Contributed downward pressure.")
                add_bullet_p(f"{feat} ({val}): {exp}")
        else:
            add_bullet_p("Operating budget discipline and customer footfall should be closely monitored during early trading.")

        # 3.3 Available-Resource and Affordability Gaps
        add_h2("3.3 Available-Resource & Affordability Gaps")
        s3_gaps = s3.get("resource_and_affordability_gaps", {})
        add_body_p(s3_gaps.get("affordability_assessment", ""))

        # 3.4 Key Findings
        add_h2("3.4 Key Findings Summary")
        for kf in s3.get("key_findings", []):
            add_bullet_p(kf)

        # =====================================================================
        # SECTION 04 — PERSONALIZED BUSINESS STRATEGY (Starts on New Page)
        # =====================================================================
        doc.add_page_break()
        s4 = sec_dict.get("section_4_personalized_strategy", {})
        add_h1("SECTION 04 — PERSONALIZED BUSINESS STRATEGY")

        # 4.1 Recommended Strategy Direction
        add_h2("4.1 Recommended Strategy Direction")
        s4_rec = s4.get("recommended_strategy", {})
        rec_name = s4_rec.get("strategy_name", strat_name)
        rec_focus = s4_rec.get("strategic_focus", "Operational Discipline")
        rec_cust = s4_rec.get("target_daily_customers", 35)
        rec_cap = s4_rec.get("estimated_capital_required_lkr", target_cap)
        rec_bud = s4_rec.get("estimated_monthly_budget_lkr", monthly_budget)
        rec_app = s4_rec.get("operational_approach", "")

        strat_lines = [
            f"Strategic Focus: {rec_focus}",
            f"Operational Approach: {rec_app}",
            f"Target Capital: LKR {rec_cap:,.0f} | Monthly Budget: LKR {rec_bud:,.0f} | Target Daily Footfall: {rec_cust} Customers/Day"
        ]
        add_callout_box(f"RECOMMENDED OPERATING PATH: {rec_name.upper()}", strat_lines, bg_hex="F8FAFC")

        # 4.2 Reasons for Recommendation (TOPSIS)
        add_h2("4.2 Multi-Criteria Evaluation & Selection Rationale (TOPSIS Method)")
        s4_reasons = s4.get("reasons_for_recommendation", {})
        add_body_p(s4_reasons.get("topsis_rationale", ""))
        add_body_p(s4_reasons.get("alignment_summary", ""))

        # 4.3 Practical Actions Tailored to the Business
        add_h2("4.3 Tailored Implementation Actions")
        for act in s4.get("practical_actions", []):
            add_bullet_p(act)

        # 4.4 Alternative Strategies Considered
        add_h2("4.4 Alternative Strategies Evaluated (TOPSIS Ranking Table)")
        add_body_p("The system evaluated four distinct strategic pathways against the five multi-criteria dimensions. Below is the comparative ranking:")

        alt_strats = s4.get("alternative_strategies", [])
        if alt_strats:
            topsis_headers = ["Rank", "Strategy Alternative", "Strategic Focus", "Target Capital", "TOPSIS Score"]
            topsis_rows = []
            for s in alt_strats[:4]:
                s_rank = s.get("rank", "-")
                s_n = s.get("strategy_name", "")
                s_f = s.get("strategic_focus", "")
                s_c = f"LKR {s.get('estimated_capital_required_lkr', 0):,.0f}"
                s_sc = str(s.get("topsis_score", "N/A"))
                topsis_rows.append([f"#{s_rank}", s_n, s_f, s_c, s_sc])
            add_styled_table(topsis_headers, topsis_rows, col_widths=[0.6, 2.2, 1.9, 1.2, 0.9])

        # =====================================================================
        # SECTION 05 — MARKETING AND SALES PLAN (Starts on New Page)
        # =====================================================================
        doc.add_page_break()
        s5 = sec_dict.get("section_5_marketing_sales", {})
        add_h1("SECTION 05 — MARKETING AND SALES PLAN")

        # 5.1 Customer Acquisition Methods
        add_h2("5.1 Customer Acquisition Methods")
        add_body_p(f"Customer acquisition activities focus on establishing immediate awareness and localized trial in {district}:")
        for m in s5.get("customer_acquisition_methods", []):
            add_bullet_p(m)

        # 5.2 Suitable Promotional Activities
        add_h2("5.2 Promotional Activities & Launch Campaign")
        for p in s5.get("suitable_promotional_activities", []):
            add_bullet_p(p)

        # 5.3 Pricing Approach
        add_h2("5.3 Pricing Approach & Commercial Rationale")
        s5_price = s5.get("pricing_approach", {})
        exp_u_price = s5_price.get("expected_unit_price_lkr", 0.0)
        p_strat = s5_price.get("pricing_strategy", "Competitive Value-Based Pricing")
        p_rat = s5_price.get("rationale", "")
        add_body_p(f"The business adopts a {p_strat} methodology with a target average spend of LKR {exp_u_price:,.2f} per customer. {p_rat}")

        # 5.4 Sales and Distribution Channels
        add_h2("5.4 Sales & Distribution Channels")
        for ch in s5.get("sales_distribution_channels", []):
            add_bullet_p(ch)

        # 5.5 Initial Sales Targets and Milestones
        add_h2("5.5 Initial Sales Targets & Gross Sales Calculation")
        s5_sales = s5.get("initial_sales_targets", {})
        cust_d = s5_sales.get("target_customers_per_day", 0)
        op_d = s5_sales.get("operating_days_per_month", 26)
        tot_interactions = s5_sales.get("monthly_customer_interactions", cust_d * op_d)
        est_m_sales = s5_sales.get("estimated_monthly_gross_sales_lkr", 0.0)
        formula_str = s5_sales.get("calculation_formula", "")
        disc_str = s5_sales.get("assumption_disclosure", "")

        sales_lines = [
            f"Estimated Monthly Gross Sales Target: LKR {est_m_sales:,.2f}",
            f"Operating Parameters: {cust_d} Customers/Day × {op_d} Days/Month = {tot_interactions:,} Interactions/Month",
            f"Calculation Formula: {formula_str}",
            f"Disclosure: {disc_str}"
        ]
        add_callout_box("INITIAL SALES TARGET CALCULATION", sales_lines, bg_hex="F8FAFC")

        # =====================================================================
        # SECTION 06 — FINANCIAL AND RESOURCE PLAN (Starts on New Page)
        # =====================================================================
        doc.add_page_break()
        s6 = sec_dict.get("section_6_financial_resource", {})
        add_h1("SECTION 06 — FINANCIAL AND RESOURCE PLAN")

        # 6.1 Estimated Startup Costs
        add_h2("6.1 Estimated Startup Costs Breakdown")
        s6_costs = s6.get("estimated_startup_costs", {})
        inv_c = s6_costs.get("initial_inventory_cost_lkr", 0.0)
        eq_c = s6_costs.get("equipment_and_setup_lkr", 0.0)
        res_c = s6_costs.get("working_capital_reserve_lkr", 0.0)
        tot_c = s6_costs.get("total_initial_startup_cost_lkr", 0.0)

        cost_headers = ["Cost Category", "Estimated Amount (LKR)", "Budget Allocation Notes"]
        cost_rows = [
            ["Initial Opening Inventory Stock", f"LKR {inv_c:,.2f}", "Opening wholesale inventory procured prior to launch"],
            ["Equipment, Fixtures & Premise Setup", f"LKR {eq_c:,.2f}", "Essential counter, shelving, and operational tools"],
            ["Working Capital Reserve Buffer", f"LKR {res_c:,.2f}", "Liquidity buffer covering baseline operational ramp-up"],
            ["Total Initial Startup Cost", f"LKR {tot_c:,.2f}", "Calibrated baseline startup requirement"],
        ]
        add_styled_table(cost_headers, cost_rows, col_widths=[2.4, 1.8, 2.6])

        # 6.2 Available Capital and Funding Requirements
        add_h2("6.2 Available Capital & Funding Requirements")
        s6_fund = s6.get("available_capital_and_funding", {})
        add_body_p(
            f"The venture is supported by LKR {s6_fund.get('available_capital_lkr', 0):,.2f} in recorded available equity capital and "
            f"LKR {s6_fund.get('loan_amount_lkr', 0):,.2f} in external loan financing, providing total available funding of "
            f"LKR {s6_fund.get('total_available_funds_lkr', 0):,.2f} against a target capital requirement of "
            f"LKR {s6_fund.get('strategy_target_capital_lkr', 0):,.2f} ({s6_fund.get('funding_gap_status', 'Fully funded')})."
        )

        # 6.3 Equipment and Resource Requirements
        add_h2("6.3 Equipment & Resource Requirements")
        s6_eq = s6.get("equipment_and_resource_requirements", {})
        add_body_p(
            f"Equipment readiness is scored at {s6_eq.get('available_equipment_score', '3/5')} against a required baseline of "
            f"{s6_eq.get('required_equipment_score', '3/5')} ({s6_eq.get('readiness_status', '')}). Regional supplier availability score is "
            f"{s6_eq.get('supplier_availability_score', '')}."
        )

        # 6.4 Staffing Requirements
        add_h2("6.4 Staffing Requirements & Roles")
        s6_st = s6.get("staffing_requirements", {})
        add_body_p(
            f"Current available workforce stands at {s6_st.get('available_staff_count', 1)} staff member(s) against an estimated requirement of "
            f"{s6_st.get('required_staff_count', 1)} ({s6_st.get('capacity_status', '')})."
        )
        for r in s6_st.get("key_roles", []):
            add_bullet_p(r)

        # 6.5 Operating Expenses
        add_h2("6.5 Operating Expenses & Working Capital Runway")
        s6_exp = s6.get("operating_expenses", {})
        add_body_p(
            f"Monthly operating budget is established at LKR {s6_exp.get('monthly_operating_budget_lkr', 0):,.2f}. "
            f"This provides approximately {s6_exp.get('strategy_capital_runway_months', 0)} months of strategy budget coverage and "
            f"{s6_exp.get('total_funds_runway_months', 0)} months of total funds liquidity runway. "
            f"{s6_exp.get('expense_guidance', '')}"
        )

        # 6.6 Financial Projections Table
        add_h2("6.6 Financial Projections Summary")
        s6_proj = s6.get("financial_projections", [])
        if s6_proj:
            proj_headers = ["Financial Metric", "Projected Target", "Basis of Projection"]
            proj_rows = [[p.get("metric", ""), p.get("value", ""), p.get("basis", "")] for p in s6_proj]
            add_styled_table(proj_headers, proj_rows, col_widths=[2.2, 1.8, 2.8])

        # =====================================================================
        # SECTION 07 — IMPLEMENTATION ROADMAP (Starts on New Page)
        # =====================================================================
        doc.add_page_break()
        s7 = sec_dict.get("section_7_implementation_roadmap", {})
        add_h1("SECTION 07 — IMPLEMENTATION ROADMAP")

        # 7.1 Prioritized Actions
        add_h2("7.1 Prioritized Pre-Launch Actions")
        for act in s7.get("prioritized_actions", []):
            add_bullet_p(act)

        # 7.2 Implementation Timeline (4 Phases)
        add_h2("7.2 Implementation Timeline (Four Operational Horizons)")
        for ph in s7.get("implementation_timeline", []):
            add_h3(f"{ph.get('phase_name', '')} ({ph.get('timeframe', '')}):")
            add_body_p(ph.get("focus_actions", ""))

        # 7.3 Launch Milestones Table
        add_h2("7.3 Launch Milestones & Success Criteria")
        s7_ms = s7.get("launch_milestones", [])
        if s7_ms:
            ms_headers = ["Milestone Name", "Target Timeline", "Measurable Success Criteria"]
            ms_rows = [[m.get("milestone", ""), m.get("target_timeframe", ""), m.get("success_criteria", "")] for m in s7_ms]
            add_styled_table(ms_headers, ms_rows, col_widths=[2.0, 1.2, 3.6])

        # 7.4 Operational Responsibilities
        add_h2("7.4 Operational Responsibilities Matrix")
        s7_resp = s7.get("responsibilities", [])
        if s7_resp:
            resp_headers = ["Operating Role", "Core Accountabilities & Responsibilities"]
            resp_rows = [[r.get("role", ""), r.get("accountabilities", "")] for r in s7_resp]
            add_styled_table(resp_headers, resp_rows, col_widths=[2.2, 4.6])

        # =====================================================================
        # SECTION 08 — EXPECTED OUTCOMES AND KEY ASSUMPTIONS (Starts on New Page)
        # =====================================================================
        doc.add_page_break()
        s8 = sec_dict.get("section_8_outcomes_assumptions", {})
        add_h1("SECTION 08 — EXPECTED OUTCOMES AND KEY ASSUMPTIONS")

        # 8.1 Expected Business Outcomes
        add_h2("8.1 Expected Business Outcomes")
        for eo in s8.get("expected_business_outcomes", []):
            add_bullet_p(eo)

        # 8.2 Measurable Targets and Monitoring KPIs
        add_h2("8.2 Measurable Targets & Key Performance Indicators (KPIs)")
        add_body_p("Management should monitor the following operational indicators regularly (Note: These represent monitoring metrics, not model predictions):")
        s8_kpis = s8.get("measurable_targets", [])
        if s8_kpis:
            kpi_headers = ["KPI / Monitoring Metric", "Target Metric", "Frequency", "Focus Area"]
            kpi_rows = [[k.get("kpi_name", ""), str(k.get("target_value", "")), k.get("monitoring_frequency", "Monthly"), k.get("focus_area", "Operations")] for k in s8_kpis]
            add_styled_table(kpi_headers, kpi_rows, col_widths=[1.8, 1.8, 1.2, 2.0])

        # 8.3 Important Business Assumptions
        add_h2("8.3 Important Business Assumptions")
        for asm in s8.get("important_business_assumptions", []):
            add_bullet_p(asm)

        # 8.4 Data Limitations and Validation Disclosures
        add_h2("8.4 Data Limitations & Methodological Disclosures")
        for lim in s8.get("data_limitations_and_validation", []):
            add_bullet_p(lim)

    @staticmethod
    def _render_unified_growth_sections(report_data: dict, ctx: dict):
        doc = ctx["doc"]
        add_h1 = ctx["add_h1"]
        add_h2 = ctx["add_h2"]
        add_h3 = ctx["add_h3"]
        add_body_p = ctx["add_body_p"]
        add_bullet_p = ctx["add_bullet_p"]
        add_callout_box = ctx["add_callout_box"]
        add_metric_strip = ctx["add_metric_strip"]
        add_styled_table = ctx["add_styled_table"]
        COLOR_PRIMARY = ctx["COLOR_PRIMARY"]
        COLOR_ACCENT = ctx["COLOR_ACCENT"]
        COLOR_DARK = ctx["COLOR_DARK"]
        COLOR_MUTED = ctx["COLOR_MUTED"]

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
        add_h1("EXECUTIVE SUMMARY")

        # Business & Growth Purpose
        add_h2("Existing Enterprise Overview & Growth Purpose")
        add_body_p(s_exec.get("business_summary", f"{biz_name} is an established enterprise operating in {district}."))
        add_body_p(s_exec.get("growth_objectives", ""), bold_prefix="Core Growth Objectives: ")

        # AI Feasibility Finding
        add_h2("AI Feasibility Assessment & Model Confidence")
        feas = s_exec.get("ai_feasibility_result", {})
        pred_label = feas.get("predicted_label", "Conditionally Feasible")
        conf_pct = feas.get("confidence_percentage", "65.0%")
        probs = feas.get("probabilities", {})
        prob_feas = probs.get("Feasible", 0.0)
        prob_cond = probs.get("Conditionally Feasible", 0.0)
        prob_infeas = probs.get("Infeasible", 0.0)

        feas_lines = [
            f"Multi-Class Model Distribution: Feasible: {prob_feas:.1%} | Conditionally Feasible: {prob_cond:.1%} | Infeasible: {prob_infeas:.1%}",
            feas.get("interpretation", "")
        ]
        add_callout_box(f"ASSESSMENT VERDICT: {pred_label.upper()} (Predicted Class Probability: {conf_pct})", feas_lines, bg_hex="F8FAFC")

        # Chart
        try:
            chart_bytes = BusinessPlanChartGenerator.generate_probability_chart(probs)
            p_chart = doc.add_paragraph()
            p_chart.add_run().add_picture(io.BytesIO(chart_bytes), width=Inches(5.5))
            p_chart.paragraph_format.space_after = Pt(6)
        except Exception:
            pass

        # Recommended Growth Strategy & Investment Summary
        add_h2("Recommended Growth Strategy & Capital Plan")
        s_strat = s_exec.get("recommended_strategy", {})
        strat_name = s_strat.get("strategy_name", "Capital-Protected Phased Growth")
        strat_focus = s_strat.get("strategic_focus", "Operational Efficiency")
        topsis_score = s_strat.get("topsis_score", "N/A")
        align_note = s_strat.get("alignment_note", "")
        add_body_p(
            f"Based on multi-criteria TOPSIS evaluation and algorithmic decision support, the system identifies {strat_name} "
            f"(TOPSIS Closeness Score: {topsis_score}) as the optimal growth pathway. "
            f"Strategic Focus: {strat_focus}. {align_note}"
        )

        s_fund = s_exec.get("investment_funding_summary", {})
        target_cap = s_fund.get("estimated_growth_capital_lkr", 0.0)
        avail_cap = s_fund.get("available_capital_lkr", 0.0)
        loan_amt = s_fund.get("loan_amount_lkr", 0.0)
        total_funds = s_fund.get("total_available_funds_lkr", avail_cap + loan_amt)
        monthly_exp = s_fund.get("monthly_operating_budget_lkr", 0.0)
        gap_status = s_fund.get("funding_gap_status", "Fully funded")

        exec_metrics = [
            ("Target Capital", f"LKR {target_cap:,.0f}", "Baseline Requirement"),
            ("Available Capital", f"LKR {avail_cap:,.0f}", f"+ LKR {loan_amt:,.0f} Loan"),
            ("Monthly Budget", f"LKR {monthly_exp:,.0f}", "Operating Ceiling"),
            ("Funding Status", gap_status, f"Total Funds: LKR {total_funds:,.0f}")
        ]
        add_metric_strip(exec_metrics)

        # Expected Outcomes Summary
        add_h2("Expected Key Outcomes")
        for out in s_exec.get("expected_outcomes", []):
            add_bullet_p(out)

        # Every section starts on a new page!
        doc.add_page_break()

        # =====================================================================
        # 1. EXISTING BUSINESS OVERVIEW AND GROWTH OBJECTIVES
        # =====================================================================
        s1 = sec_dict.get("section_1_overview_objectives", {})
        add_h1("1. EXISTING BUSINESS OVERVIEW AND GROWTH OBJECTIVES")

        # 1.1 Business Profile & Operating Background
        add_h2("1.1 Business Profile & Operating Background")
        b_id = s1.get("business_identity", {})
        add_body_p(
            f"{biz_name} is an established enterprise operating within the {category} industry, "
            f"located in {district}, {province} Province, Sri Lanka (Location: {b_id.get('location_address', district)}). "
            f"The business operates in a {b_id.get('location_type', 'Commercial Hub')} setting with a location suitability score of "
            f"{b_id.get('location_suitability_score', '3/5')}. Unlike a startup venture, {biz_name} possesses active operational history, "
            f"an existing customer base, and established supplier linkages."
        )

        # 1.2 Existing Products & Services
        add_h2("1.2 Existing Products & Services")
        add_body_p(s1.get("existing_products_and_services", ""))

        # 1.3 Current Operating Situation & Available Resources
        add_h2("1.3 Current Operating Situation & Available Resources")
        res = s1.get("current_business_situation_and_resources", {})
        add_body_p(
            f"The business currently operates with {res.get('current_staff_count', 1)} active staff member(s) against an estimated requirement of "
            f"{res.get('required_staff_count', 1)}. Equipment readiness is scored at {res.get('equipment_readiness_score', '3/5')} (target requirement: {res.get('required_equipment_score', '3/5')}), "
            f"while local supplier availability is rated at {res.get('supplier_availability_score', '3/5')}. "
            f"The business owner brings {res.get('entrepreneur_experience_years', '3 Years')} of commercial experience, supporting operational resilience."
        )
        res_metrics = [
            ("Available Capital", f"LKR {res.get('available_capital_lkr', 0):,.0f}", "Owner Equity"),
            ("Monthly Budget", f"LKR {res.get('monthly_operating_budget_lkr', 0):,.0f}", "Current Working Cap"),
            ("Active Workforce", f"{res.get('current_staff_count', 1)} Staff", f"Req: {res.get('required_staff_count', 1)}"),
            ("Equipment Score", res.get('equipment_readiness_score', '3/5'), f"Target: {res.get('required_equipment_score', '3/5')}")
        ]
        add_metric_strip(res_metrics)

        # 1.4 Business Owner's Growth Objectives & Intended Outcomes
        add_h2("1.4 Business Owner's Growth Objectives & Intended Outcomes")
        add_body_p(s1.get("growth_objectives", ""))
        add_h3("Intended Outcomes of Proposed Growth:")
        for io_item in s1.get("intended_outcomes", []):
            add_bullet_p(io_item)

        # 1.5 Important Business Constraints & Improvement Needs
        add_h2("1.5 Important Business Constraints & Improvement Needs")
        for cn in s1.get("constraints_and_improvement_needs", []):
            add_bullet_p(cn)

        # Every section starts on a new page!
        doc.add_page_break()

        # =====================================================================
        # 2. MARKET AND GROWTH OPPORTUNITY ANALYSIS
        # =====================================================================
        s2 = sec_dict.get("section_2_market_opportunities", {})
        add_h1("2. MARKET AND GROWTH OPPORTUNITY ANALYSIS")

        # 2.1 Market Catchment & Baseline Demand Dynamics
        add_h2("2.1 Market Catchment & Baseline Demand Dynamics")
        mkt = s2.get("market_catchment", {})
        cust_per_day = mkt.get("expected_customers_per_day", 0)
        unit_price = mkt.get("expected_selling_price_lkr", 0.0)
        op_days = mkt.get("operating_days_per_month", 26)
        monthly_vol = cust_per_day * op_days
        demand_score = mkt.get("customer_demand_score", "50/100")
        gross_sales = mkt.get("monthly_gross_sales_estimate", 0.0)

        add_body_p(
            f"The business serves the {mkt.get('target_market', district)} commercial catchment area, targeting {mkt.get('customer_profile', 'local patrons')}. "
            f"Baseline operations capture approximately {cust_per_day} customer transactions per day at an average unit price of "
            f"LKR {unit_price:,.2f} across {op_days} operating days per month. This generates an estimated monthly throughput of "
            f"{monthly_vol:,} customer interactions and an estimated monthly gross sales volume of LKR {gross_sales:,.2f}. "
            f"The evaluated customer demand index stands at {demand_score}."
        )

        # 2.2 Relevant Growth Opportunities
        add_h2("2.2 Identification of Relevant Growth Opportunities")
        add_body_p(
            "Rather than assuming a mandatory expansion pathway or enforcing a branch/product dichotomy, SME360 AI evaluated seven "
            "potential growth avenues against the business's actual capital runway, equipment readiness, staffing, and local demand score. "
            "The opportunities below are prioritized based on verified data suitability:"
        )

        for opp in s2.get("identified_growth_opportunities", []):
            opp_name = opp.get("opportunity_area", "Growth Avenue")
            opp_app = opp.get("applicability", "Relevant")
            opp_act = opp.get("strategic_action", "")
            add_callout_box(f"Opportunity: {opp_name} [{opp_app.upper()}]", [opp_act], bg_hex="F8FAFC")

        # 2.3 Competitive Dynamics & Local Market Positioning
        add_h2("2.3 Competitive Dynamics & Local Market Positioning")
        comp = s2.get("competitive_environment", {})
        add_body_p(
            f"The local competitive environment is recorded at a {comp.get('competition_level', 'Moderate')} competition level "
            f"({comp.get('competitor_count_nearby', 'Nearby competitor count')} | {comp.get('competitor_information', '')}). "
            f"To secure patron retention and defend gross margins, the enterprise's recommended market positioning is: "
            f"{comp.get('positioning_strategy', 'Consistent operational execution and service differentiation.')}"
        )

        # Every section starts on a new page!
        doc.add_page_break()

        # =====================================================================
        # 3. FEASIBILITY ASSESSMENT AND KEY FINDINGS
        # =====================================================================
        s3 = sec_dict.get("section_3_feasibility_findings", {})
        add_h1("3. FEASIBILITY ASSESSMENT AND KEY FINDINGS")

        # 3.1 AI Feasibility Classification & Model Prediction
        add_h2("3.1 AI Feasibility Classification & Model Prediction")
        ml_feas = s3.get("ml_feasibility_classification", {})
        f_pred = ml_feas.get("predicted_label", "Conditionally Feasible")
        f_conf = ml_feas.get("confidence_percentage", "65.0%")
        f_probs = ml_feas.get("probabilities", {})

        f_lines = [
            f"Probability Distribution: Feasible: {f_probs.get('Feasible', 0.0):.1%} | Conditionally Feasible: {f_probs.get('Conditionally Feasible', 0.0):.1%} | Infeasible: {f_probs.get('Infeasible', 0.0):.1%}",
            ml_feas.get("interpretation", "")
        ]
        add_callout_box(f"ASSESSMENT VERDICT: {f_pred.upper()} (Model Confidence: {f_conf})", f_lines, bg_hex="F8FAFC")

        # Chart
        try:
            chart_bytes = BusinessPlanChartGenerator.generate_probability_chart(f_probs)
            p_chart = doc.add_paragraph()
            p_chart.add_run().add_picture(io.BytesIO(chart_bytes), width=Inches(5.5))
            p_chart.paragraph_format.space_after = Pt(6)
        except Exception:
            pass

        # 3.2 Key Factors Influencing the Prediction (SHAP Explainability)
        add_h2("3.2 Key Factors Influencing the Prediction (SHAP Explainability)")
        add_body_p(
            "To ensure transparent decision support, SHAP (SHapley Additive exPlanations) values decompose the model's prediction into "
            "individual feature contributions, highlighting positive business strengths versus operational friction points:"
        )

        add_h3("Primary Positive Supporting Factors:")
        pos_drivers = s3.get("key_positive_drivers", [])
        if pos_drivers:
            for p_drv in pos_drivers:
                add_bullet_p(p_drv.get("business_interpretation", ""), bold_prefix=f"{p_drv.get('feature', '')} ({p_drv.get('feature_value', '')}): ")
        else:
            add_bullet_p("Available capital and customer demand score align positively with baseline operational requirements.")

        add_h3("Operational Hurdles Requiring Management Attention:")
        neg_hurdles = s3.get("key_negative_hurdles", [])
        if neg_hurdles:
            for n_hrd in neg_hurdles:
                add_bullet_p(n_hrd.get("business_interpretation", ""), bold_prefix=f"{n_hrd.get('feature', '')} ({n_hrd.get('feature_value', '')}): ")
        else:
            add_bullet_p("Working capital buffer and peak customer throughput should be monitored to avoid cash strain.")

        # 3.3 Resource Availability & Operational Readiness
        add_h2("3.3 Resource Availability & Operational Readiness")
        res_avail = s3.get("resource_availability_assessment", {})
        add_bullet_p(res_avail.get("staffing_balance", ""), bold_prefix="Staffing Balance: ")
        add_bullet_p(res_avail.get("equipment_readiness", ""), bold_prefix="Equipment Readiness: ")
        add_bullet_p(res_avail.get("supplier_access", ""), bold_prefix="Supplier Access: ")
        add_bullet_p(res_avail.get("location_suitability", ""), bold_prefix="Location Suitability: ")

        # 3.4 Identified Affordability Gaps & Strategic Findings
        add_h2("3.4 Identified Affordability Gaps & Key Findings")
        aff_gaps = s3.get("affordability_gaps_and_findings", {})
        add_body_p(
            f"The business growth strategy targets a capital requirement of LKR {aff_gaps.get('strategy_target_capital_lkr', 0):,.2f}. "
            f"Recorded available funding equals LKR {aff_gaps.get('total_available_funds_lkr', 0):,.2f} (Available Equity: LKR {aff_gaps.get('available_capital_lkr', 0):,.2f} + Loan: LKR {aff_gaps.get('loan_amount_lkr', 0):,.2f}), "
            f"placing the enterprise in a {aff_gaps.get('funding_gap_status', 'Fully funded')} position. "
            f"Liquidity runway provides approximately {aff_gaps.get('capital_runway_months', 0)} months of strategy budget coverage. "
            f"{aff_gaps.get('key_findings_summary', '')}"
        )

        # Every section starts on a new page!
        doc.add_page_break()

        # =====================================================================
        # 4. PERSONALIZED GROWTH STRATEGY
        # =====================================================================
        s4 = sec_dict.get("section_4_growth_strategy", {})
        add_h1("4. PERSONALIZED GROWTH STRATEGY")

        # 4.1 Recommended Growth Approach
        add_h2("4.1 Recommended Strategic Growth Approach")
        rec_app = s4.get("recommended_growth_approach", {})
        add_body_p(
            f"SME360 AI recommends {rec_app.get('strategy_name', 'Capital-Protected Phased Growth')} "
            f"(Strategic Focus: {rec_app.get('strategic_focus', 'Controlled Phased Growth')}, "
            f"TOPSIS Closeness Score: {rec_app.get('topsis_score', 'N/A')}) as the primary growth vehicle for {biz_name}. "
            f"{rec_app.get('selection_status', '')}"
        )
        add_body_p(rec_app.get("operational_approach", ""))

        # Strategy Suitability Rationale
        add_h3("Strategic Suitability Rationale:")
        add_body_p(s4.get("strategy_suitability_rationale", ""))

        # 4.2 Multi-Criteria Comparison of Strategic Alternatives (TOPSIS Ranking)
        add_h2("4.2 Multi-Criteria Comparison of Strategic Alternatives (TOPSIS Ranking)")
        add_body_p(
            "To avoid subjective bias, four strategic pathways were evaluated using the Technique for Order of Preference by "
            "Similarity to Ideal Solution (TOPSIS). The evaluation balanced five validated dimensions: "
            "Financial Viability (25%), Market Demand Alignment (25%), Implementation Feasibility (20%), "
            "Operational Risk (15%), and Resource Efficiency (15%):"
        )

        topsis_headers = ["Rank", "Strategy Pathway", "Strategic Focus", "Target Capital", "TOPSIS Score"]
        topsis_rows = []
        alt_comp = s4.get("alternatives_comparison", {})
        for r_strat in alt_comp.get("ranked_strategies", []):
            topsis_rows.append([
                f"#{r_strat.get('rank', '-')}",
                r_strat.get("strategy_name", ""),
                r_strat.get("strategic_focus", "Growth"),
                f"LKR {r_strat.get('estimated_capital_required_lkr', 0):,.0f}",
                str(r_strat.get("topsis_score", "N/A"))
            ])
        add_styled_table(topsis_headers, topsis_rows, col_widths=[0.6, 2.0, 1.8, 1.4, 0.9])

        # 4.3 Practical & Prioritized Actions
        add_h2("4.3 Practical & Prioritized Growth Actions")
        for act in s4.get("prioritized_practical_actions", []):
            add_bullet_p(act)

        # 4.4 Addressing Identified Resource & Operational Gaps
        add_h2("4.4 Addressing Resource & Operational Gaps")
        for gap in s4.get("gap_mitigation_plan", []):
            add_bullet_p(gap)

        # Every section starts on a new page!
        doc.add_page_break()

        # =====================================================================
        # 5. FINANCIAL AND RESOURCE PLAN
        # =====================================================================
        s5 = sec_dict.get("section_5_financial_resource", {})
        add_h1("5. FINANCIAL AND RESOURCE PLAN")

        # 5.1 Estimated Cost of Recommended Growth Actions
        add_h2("5.1 Estimated Cost of Recommended Growth Actions")
        costs = s5.get("estimated_growth_costs", {})
        capex_val = costs.get("capex_and_tooling_upgrades_lkr", 0.0)
        inv_val = costs.get("inventory_replenishment_cost_lkr", 0.0)
        buf_val = costs.get("working_capital_reserve_lkr", 0.0)
        tot_val = costs.get("total_estimated_growth_capital_lkr", 0.0)

        cost_headers = ["Growth Investment Component", "Estimated Capital (LKR)", "Strategic Purpose & Description"]
        cost_rows = [
            ["CapEx & Fixture/Tooling Upgrades", f"LKR {capex_val:,.2f}", "Physical workspace optimization and equipment upgrades"],
            ["Initial Inventory & Wholesale Stock", f"LKR {inv_val:,.2f}", "Stock replenishment to support anticipated customer footfall"],
            ["Working Capital Reserve Buffer", f"LKR {buf_val:,.2f}", "Liquidity buffer covering baseline operational ramp-up"],
            ["Total Estimated Growth Capital", f"LKR {tot_val:,.2f}", "Calibrated baseline target growth allocation"]
        ]
        add_styled_table(cost_headers, cost_rows, col_widths=[2.2, 1.6, 2.9])

        # 5.2 Capital Structure & Funding Requirements
        add_h2("5.2 Capital Structure, Funding Requirements & Liquidity Runway")
        fund_data = s5.get("available_capital_and_funding", {})
        add_body_p(
            f"The business is supported by LKR {fund_data.get('available_capital_lkr', 0):,.2f} in recorded available capital and "
            f"LKR {fund_data.get('loan_amount_lkr', 0):,.2f} in external debt financing, delivering total available funds of "
            f"LKR {fund_data.get('total_available_funds_lkr', 0):,.2f} against a target growth capital requirement of "
            f"LKR {fund_data.get('strategy_target_capital_lkr', 0):,.2f} ({fund_data.get('funding_gap_status', 'Fully funded')})."
        )

        # 5.3 Resource & Staffing Requirements
        add_h2("5.3 Staffing & Equipment Resource Plan")
        st_data = s5.get("resource_and_staffing_requirements", {})
        add_body_p(
            f"Current staff allocation stands at {st_data.get('available_staff_count', 1)} staff member(s) against an estimated requirement of "
            f"{st_data.get('required_staff_count', 1)} ({st_data.get('capacity_status', '')}). "
            f"Equipment readiness status: {st_data.get('equipment_status', '3/5')}. Local supplier access: {st_data.get('supplier_access', '')}."
        )

        # 5.4 Operating Expenses & Revenue Projections
        add_h2("5.4 Operating Expenses & Financial Projections")
        op_data = s5.get("operating_expenses", {})
        add_body_p(
            f"Monthly operating budget is established at LKR {op_data.get('monthly_operating_budget_lkr', 0):,.2f}, providing approximately "
            f"{op_data.get('strategy_capital_runway_months', 0)} months of strategy budget coverage and "
            f"{op_data.get('total_funds_runway_months', 0)} months of total funds liquidity runway. "
            f"{op_data.get('expense_guidance', '')}"
        )

        # Financial Projections Table
        f_proj = s5.get("financial_projections", [])
        if f_proj:
            proj_headers = ["Financial Metric", "Projected Target", "Basis of Projection"]
            proj_rows = [[p.get("metric", ""), p.get("value", ""), p.get("basis", "")] for p in f_proj]
            add_styled_table(proj_headers, proj_rows, col_widths=[2.0, 1.8, 2.9])

        # 5.5 Investment Recovery & Payback Analysis
        add_h2("5.5 Investment Recovery & Payback Safeguards")
        pb = s5.get("payback_and_affordability_analysis", {})
        if pb.get("is_calculated"):
            add_body_p(
                f"Based on stated one-time growth CapEx and operating net cash flow baseline, the target investment "
                f"payback period is estimated at approximately ~{pb.get('estimated_payback_months')} months. "
                f"(Note: Assumes sustained monthly net profit without unexpected commodity cost inflation.)"
            )
        else:
            add_body_p(
                f"To maintain professional accounting integrity, payback period and ROI are not fabricated or derived from gross sales turnover alone. "
                f"{pb.get('affordability_note', '')}",
                bold_prefix="Payback Calculation Status: Baseline Net Profit Input Pending. "
            )

        # Every section starts on a new page!
        doc.add_page_break()

        # =====================================================================
        # 6. IMPLEMENTATION ROADMAP
        # =====================================================================
        s6 = sec_dict.get("section_6_implementation_roadmap", {})
        add_h1("6. IMPLEMENTATION ROADMAP")

        # 6.1 Prioritized Growth Implementation Actions
        add_h2("6.1 Prioritized Growth Implementation Actions")
        for p_act in s6.get("prioritized_actions", []):
            add_bullet_p(p_act)

        # 6.2 Recommended Implementation Stages (Four Horizons)
        add_h2("6.2 Recommended Implementation Stages (Four Operational Horizons)")
        for stg in s6.get("implementation_stages", []):
            add_h3(f"{stg.get('stage_name', '')} ({stg.get('timeframe', '')}):")
            add_body_p(stg.get("focus_actions", ""))

        # 6.3 Key Growth Milestones & Success Criteria
        add_h2("6.3 Key Growth Milestones & Success Criteria")
        ms_list = s6.get("launch_milestones", [])
        if ms_list:
            ms_headers = ["Milestone Name", "Target Timeline", "Measurable Success Criteria"]
            ms_rows = [[m.get("milestone", ""), m.get("target_timeframe", ""), m.get("success_criteria", "")] for m in ms_list]
            add_styled_table(ms_headers, ms_rows, col_widths=[1.8, 1.2, 3.7])

        # 6.4 Operational Responsibilities Matrix
        add_h2("6.4 Operational Responsibilities Matrix")
        resp_list = s6.get("responsibilities", [])
        if resp_list:
            resp_headers = ["Operating Role", "Core Accountabilities & Responsibilities"]
            resp_rows = [[r.get("role", ""), r.get("accountabilities", "")] for r in resp_list]
            add_styled_table(resp_headers, resp_rows, col_widths=[2.0, 4.7])

        # 6.5 Progress Monitoring & Governance
        add_h2("6.5 Progress Monitoring & Governance Cadence")
        add_body_p(s6.get("progress_monitoring", "Management should conduct regular cash reconciliations and strategy reviews."))

        # Every section starts on a new page!
        doc.add_page_break()

        # =====================================================================
        # 7. EXPECTED OUTCOMES AND SUCCESS INDICATORS
        # =====================================================================
        s7 = sec_dict.get("section_7_outcomes_indicators", {})
        add_h1("7. EXPECTED OUTCOMES AND SUCCESS INDICATORS")

        # 7.1 Expected Business Improvements & Outcomes
        add_h2("7.1 Expected Business Improvements & Outcomes")
        for outcome in s7.get("expected_business_outcomes", []):
            add_bullet_p(outcome)

        # 7.2 Measurable Business Targets & KPIs
        add_h2("7.2 Measurable Business Targets & Key Performance Indicators")
        kpi_list = s7.get("measurable_targets_kpis", [])
        if kpi_list:
            kpi_headers = ["Performance Indicator", "Target Objective", "Tracking Frequency", "Focus Area"]
            kpi_rows = [[k.get("kpi_name", ""), str(k.get("target_value", "")), k.get("monitoring_frequency", "Monthly"), k.get("focus_area", "Operational")] for k in kpi_list]
            add_styled_table(kpi_headers, kpi_rows, col_widths=[1.8, 2.0, 1.4, 1.5])

        # 7.3 Suggested Methods for Tracking Progress
        add_h2("7.3 Suggested Methods for Tracking Progress")
        for mth in s7.get("suggested_methods_for_tracking_progress", []):
            add_bullet_p(mth)

        # 7.4 Important Business Assumptions & Methodological Disclosures
        add_h2("7.4 Important Business Assumptions & Planning Limitations")
        add_h3("Planning Assumptions:")
        for asm in s7.get("important_business_assumptions", []):
            add_bullet_p(asm)

        add_h3("Data Limitations & Methodological Disclosures:")
        for lim in s7.get("data_limitations_and_validation", []):
            add_bullet_p(lim)

    _render_existing_business_sections = _render_unified_growth_sections
