import os
from datetime import datetime
from typing import Dict, Any


class BusinessPlanReportBuilder:
    """
    Normalizes structured profile analysis results into a clean, comprehensive 
    BusinessPlanReport data dictionary for PDF and DOCX document generators.
    
    Structure adheres strictly to the Research-Grounded Report Sections:
    - Section 01: Business & Market Overview
    - Section 02: AI Feasibility & Key Insights (Probabilities & SHAP)
    - Section 03: Strategic Recommendations & TOPSIS Ranking
    - Section 04: Financial & Operational Plan (Aligned with Selected Strategy)
    - Section 05: Scenario Analysis & Action Roadmap
    - Final AI Recommendation & Decision Summary
    """

    @staticmethod
    def build_report_data(profile: dict) -> dict:
        metadata = profile.get("metadata", {})
        business_input = profile.get("business_input", {})
        feasibility_analysis = profile.get("feasibility_analysis", {})
        explainability = profile.get("explainability", {})
        strategic_recommendations = profile.get("strategic_recommendations", {})
        scenario_analysis = profile.get("scenario_analysis", {})
        personalized_business_plan = profile.get("personalized_business_plan", {})

        # Date
        created_at_raw = metadata.get("created_at") or metadata.get("generated_at") or datetime.now().isoformat()
        try:
            date_str = datetime.fromisoformat(str(created_at_raw).replace("Z", "+00:00")).strftime("%B %d, %Y")
        except Exception:
            date_str = datetime.now().strftime("%B %d, %Y")

        # Identity
        category = business_input.get("business_category", "SME Enterprise")
        stage = business_input.get("business_stage", "New Startup")
        district = business_input.get("district", "Colombo")
        province = business_input.get("province", "Western")
        raw_name = business_input.get("business_name") or profile.get("business_name") or f"{district} {category}"
        business_name = str(raw_name).strip()

        # Check for pre-built structured sections in personalized_business_plan
        sec_01 = personalized_business_plan.get("section_01_business_market_overview")
        sec_02 = personalized_business_plan.get("section_02_ai_feasibility_insights")
        sec_03 = personalized_business_plan.get("section_03_strategic_recommendations")
        sec_04 = personalized_business_plan.get("section_04_financial_operational_plan")
        sec_05 = personalized_business_plan.get("section_05_scenario_action_roadmap")
        final_rec = personalized_business_plan.get("final_recommendation")

        # Fallback / extraction if older profile record without section_01
        predicted_label = feasibility_analysis.get("predicted_label") or feasibility_analysis.get("prediction", "Conditionally Feasible")
        confidence_score = float(feasibility_analysis.get("confidence_score", feasibility_analysis.get("probability_score", 0.65)))
        probabilities = feasibility_analysis.get("probabilities", {
            "Feasible": 0.25,
            "Conditionally Feasible": 0.65,
            "Infeasible": 0.10
        })

        executive_overview = personalized_business_plan.get("executive_overview", {})
        operational_plan = personalized_business_plan.get("operational_plan", {})
        marketing_plan = personalized_business_plan.get("marketing_plan", {})
        financial_plan = personalized_business_plan.get("financial_plan", {})
        action_roadmap = personalized_business_plan.get("action_roadmap", {})

        # TOPSIS & Strategies handling
        topsis_ranking = strategic_recommendations.get("topsis_ranking", {})
        ranked_strategies = topsis_ranking.get("ranked_strategies", [])
        candidate_strategies = ranked_strategies or strategic_recommendations.get("candidate_strategies", [])
        
        # Ensure every candidate strategy has rank and topsis_score
        for rank_idx, s in enumerate(candidate_strategies, start=1):
            if "rank" not in s or s["rank"] in ["-", None]:
                s["rank"] = rank_idx
            if "topsis_score" not in s or s["topsis_score"] in ["N/A", None]:
                s["topsis_score"] = topsis_ranking.get("top_topsis_score", 0.7500) if rank_idx == 1 else round(0.75 - rank_idx * 0.05, 4)

        ai_top_strategy = topsis_ranking.get("top_recommended_strategy", "Lean Operational Bootstrapping Strategy")
        ai_top_score = str(topsis_ranking.get("top_topsis_score", "0.7850"))
        
        selected_strategy_id = strategic_recommendations.get("selected_strategy_id") or executive_overview.get("strategy_id")
        selected_strategy_name = strategic_recommendations.get("selected_strategy_name") or executive_overview.get("recommended_primary_strategy")
        is_user_selected = bool(
            executive_overview.get("is_user_selected") or
            (selected_strategy_id and selected_strategy_id != topsis_ranking.get("top_recommended_id"))
        )

        active_strategy_name = selected_strategy_name if is_user_selected else ai_top_strategy
        active_strategy_id = selected_strategy_id if is_user_selected else topsis_ranking.get("top_recommended_id", "STRAT_01")
        active_strategy = next(
            (s for s in candidate_strategies if s.get("strategy_id") == active_strategy_id or s.get("strategy_name") == active_strategy_name),
            candidate_strategies[0] if candidate_strategies else {}
        )

        # Capital and Coverage
        effective_capital = float(business_input.get("available_capital_lkr") if business_input.get("available_capital_lkr") is not None else financial_plan.get("available_capital_lkr", 0.0))
        effective_budget = float(business_input.get("monthly_budget_lkr") if business_input.get("monthly_budget_lkr") is not None else financial_plan.get("monthly_operating_budget_lkr", 0.0))
        strategy_target_capital = float(active_strategy.get("estimated_capital_required_lkr") or financial_plan.get("strategy_target_capital_lkr") or effective_capital)
        loan_amount = float(business_input.get("loan_amount_lkr", 0.0))
        total_available_funds = effective_capital + loan_amount
        monthly_budget_val = max(effective_budget, 1.0)
        
        strategy_budget_coverage = round(strategy_target_capital / monthly_budget_val, 1)
        available_funds_coverage = round(total_available_funds / monthly_budget_val, 1)
        
        customers_per_day = int(business_input.get("expected_customers_per_day") if business_input.get("expected_customers_per_day") is not None else marketing_plan.get("target_daily_customers", 0))
        expected_price = float(business_input.get("expected_price_lkr", 0.0))
        operating_days = int(business_input.get("expected_operating_days_per_month", 26))

        # Competitor count logic
        raw_comp_count = business_input.get("competitor_count_nearby")
        if raw_comp_count is None or raw_comp_count == 0 or raw_comp_count == "0":
            competitor_count_display = "Not provided in current business input"
            competitor_info_display = business_input.get("competitor_information") or "Specific nearby direct competitor counts were not provided in current business inputs."
        else:
            competitor_count_display = int(raw_comp_count)
            competitor_info_display = business_input.get("competitor_information") or f"{raw_comp_count} direct competitor(s) recorded in initial business intake."

        cover_image = profile.get("cover_image") or metadata.get("cover_image") or business_input.get("cover_image")

        is_new_startup = "new" in str(stage).lower() or "start" in str(stage).lower()
        doc_title = "STRATEGIC BUSINESS PLAN" if is_new_startup else "PERSONALIZED BUSINESS GROWTH PLAN"
        doc_subtitle = (
            "A Comprehensive Feasibility, Strategic Direction & Implementation Blueprint"
            if is_new_startup else
            "A Tailored Strategic Growth & Decision Support Blueprint"
        )

        funding_gap = max(0.0, strategy_target_capital - total_available_funds)
        funding_status = "Fully funded from baseline capital" if total_available_funds >= strategy_target_capital else f"Capital gap of LKR {funding_gap:,.2f} identified"
        monthly_gross_sales = customers_per_day * expected_price * operating_days
        inv_cost = float(business_input.get("initial_inventory_cost_lkr", 0.0))
        setup_cost = max(0.0, strategy_target_capital - inv_cost - (effective_budget * 2))
        buffer_cost = effective_budget * 2
        demand_score_val = business_input.get("customer_demand_score", 50)

        # Build Section Structures
        new_startup_sections = None
        unified_growth_sections = None

        if is_new_startup:

            # 1. Executive Summary
            s1_exec = {
                "section_number": "01",
                "section_title": "01 — Executive Summary",
                "business_idea_overview": {
                    "business_name": business_name,
                    "business_category": category,
                    "business_stage": "New Startup",
                    "location": f"{district}, {province} Province, Sri Lanka",
                    "summary_text": executive_overview.get("business_summary") or f"A proposed new startup within the {category} sector, planned for commercial launch in {district}, {province} Province."
                },
                "ai_feasibility_result": {
                    "predicted_label": predicted_label,
                    "confidence_score": confidence_score,
                    "confidence_percentage": f"{(confidence_score * 100):.1f}%",
                    "probabilities": probabilities,
                    "interpretation": (
                        f"The proposed enterprise is classified as '{predicted_label}' with a predicted class probability of {confidence_score:.1%}. "
                        f"While baseline market and location conditions offer positive commercial potential, disciplined cash-flow management is essential during the startup launch phase."
                    )
                },
                "recommended_strategy": {
                    "strategy_name": active_strategy_name,
                    "strategy_id": active_strategy_id,
                    "strategic_focus": active_strategy.get("strategic_focus", "Capital Protection & Phased Scale"),
                    "topsis_score": ai_top_score,
                    "is_user_selected": is_user_selected,
                    "alignment_note": "Selected strategy matches the AI recommendation engine's highest-ranked alternative." if not is_user_selected else f"Adopted entrepreneur preference: {active_strategy_name}."
                },
                "investment_funding_summary": {
                    "available_capital_lkr": effective_capital,
                    "loan_amount_lkr": loan_amount,
                    "total_available_funds_lkr": total_available_funds,
                    "strategy_target_capital_lkr": strategy_target_capital,
                    "funding_status": funding_status,
                    "monthly_operating_budget_lkr": effective_budget,
                    "capital_runway_months": strategy_budget_coverage
                }
            }

            # 2. Business Overview
            s2_overview = {
                "section_number": "02",
                "section_title": "02 — Business Overview",
                "concept_and_objectives": {
                    "business_concept": executive_overview.get("business_summary") or f"Establish a professional, customer-focused {category} enterprise in {district}.",
                    "business_model": business_input.get("business_model") or "Direct Retail / Service",
                    "primary_objectives": [
                        f"Establish a viable physical commercial presence in {district}.",
                        f"Capture an initial steady footfall baseline of approximately {customers_per_day} daily patrons.",
                        "Achieve disciplined operational cost control within the stated monthly operating budget.",
                        "Build sustainable local customer relationships and repeat patronage."
                    ]
                },
                "business_location": {
                    "district": district,
                    "province": province,
                    "location_type": business_input.get("location_type", "Suburban Commercial Hub"),
                    "address": business_input.get("address") or "Information not provided in initial business intake",
                    "location_suitability_score": f"{business_input.get('location_suitability_score', 3)}/5",
                    "location_context": f"Operating within a {business_input.get('location_type', 'commercial')} catchment in {district}, providing accessible customer footfall."
                },
                "products_or_services": {
                    "offerings_summary": f"Commercial products and services within the {category} category.",
                    "operational_details": business_input.get("additional_description") or "Standard retail and counter service tailored to local consumer preferences.",
                    "expected_price_lkr": expected_price
                },
                "target_customers": {
                    "target_profile": business_input.get("target_age_group") or f"Residents, working professionals, and walk-in shoppers across {district}.",
                    "customer_demand_score": f"{business_input.get('customer_demand_score', 50)}/100",
                    "demand_assessment": f"The recorded customer demand score of {business_input.get('customer_demand_score', 50)}/100 reflects viable local consumer interest, requiring targeted opening awareness campaigns."
                },
                "relevant_market_context": {
                    "competition_level": business_input.get("competition_level", "Moderate"),
                    "competitor_count_nearby": competitor_count_display,
                    "competitor_information": competitor_info_display,
                    "positioning_strategy": f"Differentiation through consistent service quality, fair pricing (approx LKR {expected_price:,.2f}/visit), and disciplined execution of the {active_strategy_name}."
                }
            }

            # 3. Feasibility Assessment and Key Findings
            s3_feasibility = {
                "section_number": "03",
                "section_title": "03 — Feasibility Assessment and Key Findings",
                "ml_feasibility_prediction": {
                    "predicted_label": predicted_label,
                    "confidence_score": confidence_score,
                    "confidence_percentage": f"{(confidence_score * 100):.1f}%",
                    "probabilities": probabilities,
                    "methodology_disclosure": "Prediction produced by the trained Random Forest Feasibility Classifier evaluating 22 standardized SME financial, operational, and location variables against historical Sri Lankan enterprise outcomes."
                },
                "factors_influencing_prediction": {
                    "positive_enablers": [
                        {
                            "feature": d.get("feature", "").replace("_", " ").title(),
                            "importance": round(abs(float(d.get("importance", d.get("impact_score", 0.0)))), 4),
                            "feature_value": str(d.get("feature_value", "N/A")),
                            "impact_explanation": f"Recorded condition for {d.get('feature', '').replace('_', ' ').title()} ({d.get('feature_value', 'N/A')}) provided positive algorithmic support toward operational feasibility."
                        }
                        for d in explainability.get("positive_drivers", [])[:4]
                    ],
                    "operational_hurdles": [
                        {
                            "feature": d.get("feature", "").replace("_", " ").title(),
                            "importance": round(abs(float(d.get("importance", d.get("impact_score", 0.0)))), 4),
                            "feature_value": str(d.get("feature_value", "N/A")),
                            "impact_explanation": f"Constraint in {d.get('feature', '').replace('_', ' ').title()} ({d.get('feature_value', 'N/A')}) exerted downward pressure, representing an operational risk to actively mitigate."
                        }
                        for d in explainability.get("negative_drivers", [])[:4]
                    ]
                },
                "resource_and_affordability_gaps": {
                    "available_capital_lkr": effective_capital,
                    "monthly_budget_lkr": effective_budget,
                    "capital_to_budget_ratio": strategy_budget_coverage,
                    "counterfactual_boundary": scenario_analysis.get("counterfactual_boundary", {}),
                    "affordability_assessment": (
                        f"Current available equity of LKR {effective_capital:,.2f} provides approximately {strategy_budget_coverage} months of monthly operating budget coverage. "
                        + (scenario_analysis.get("counterfactual_boundary", {}).get("recommendation") or "Maintaining a 3 to 6-month liquidity reserve is strongly recommended to protect against early revenue volatility.")
                    )
                },
                "key_findings": [
                    f"Feasibility classification stands at '{predicted_label}' with {confidence_score:.1%} model confidence.",
                    f"Location and customer demand ratings provide an encouraging operational baseline in {district}.",
                    f"Managing initial overhead and keeping monthly expenses below LKR {effective_budget:,.2f} represents the critical success determinant.",
                    f"Procurement arrangements and initial inventory stocking (LKR {inv_cost:,.2f}) should be finalized prior to public launch."
                ]
            }

            # 4. Personalized Business Strategy
            s4_strategy = {
                "section_number": "04",
                "section_title": "04 — Personalized Business Strategy",
                "recommended_strategy": {
                    "strategy_name": active_strategy_name,
                    "strategy_id": active_strategy_id,
                    "strategic_focus": active_strategy.get("strategic_focus", "Capital Protection & Phased Scale"),
                    "target_daily_customers": int(active_strategy.get("target_daily_customers", customers_per_day)),
                    "estimated_capital_required_lkr": float(active_strategy.get("estimated_capital_required_lkr", effective_capital)),
                    "estimated_monthly_budget_lkr": float(active_strategy.get("estimated_monthly_budget_lkr", effective_budget)),
                    "operational_approach": active_strategy.get("operational_approach") or f"Deploy a disciplined operational model for {business_name} focused on capital preservation and steady local customer acquisition."
                },
                "reasons_for_recommendation": {
                    "topsis_rationale": "Ranked #1 using Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) across 5 multi-criteria dimensions: Financial Viability (25%), Implementation Feasibility (20%), Market Demand Alignment (25%), Operational Friction (15%), and Resource Efficiency (15%).",
                    "alignment_summary": f"This strategy balances lean startup risk against local market demand, minimizing fixed cost exposure while establishing reliable operations."
                },
                "practical_actions": active_strategy.get("tactics", [
                    "Maintain lean operating overhead and avoid non-essential upfront administrative costs.",
                    "Preserve a dedicated working capital reserve buffer to cover initial ramp-up weeks.",
                    "Implement direct customer engagement to build word-of-mouth reputation in the neighborhood.",
                    "Establish clear inventory replenishment cycles with reliable local wholesalers."
                ]),
                "alternative_strategies": candidate_strategies
            }

            # 5. Marketing and Sales Plan
            s5_marketing = {
                "section_number": "05",
                "section_title": "05 — Marketing and Sales Plan",
                "customer_acquisition_methods": [
                    f"High-visibility exterior signage and entrance display in {district} commercial area.",
                    "Opening week neighborhood flyer distribution and personal community invitations.",
                    "Active WhatsApp and social media presence for local community announcements and product availability.",
                    "Word-of-mouth referral incentives for satisfied first-month customers."
                ],
                "suitable_promotional_activities": [
                    "Introductory launch pricing discounts and bundle packages during Weeks 1–2.",
                    "Customer loyalty perks (e.g. repeat-visit stamp cards or value bundles).",
                    "Seasonal promotions aligned with local holidays and community gatherings."
                ],
                "pricing_approach": {
                    "expected_unit_price_lkr": expected_price,
                    "pricing_strategy": "Competitive Value-Based Pricing",
                    "rationale": f"An average transaction value of LKR {expected_price:,.2f} is positioned to be competitive within {district} while covering basic unit costs and supporting commercial viability."
                },
                "sales_distribution_channels": [
                    "Primary Channel: Physical over-the-counter walk-in sales at commercial premises.",
                    "Secondary Channel: Direct phone / WhatsApp orders for local pickup and nearby doorstep delivery."
                ],
                "initial_sales_targets": {
                    "target_customers_per_day": customers_per_day,
                    "operating_days_per_month": operating_days,
                    "monthly_customer_interactions": customers_per_day * operating_days,
                    "estimated_monthly_gross_sales_lkr": monthly_gross_sales,
                    "calculation_formula": f"Estimated Monthly Gross Sales = Daily Customers ({customers_per_day}) × Average Spend (LKR {expected_price:,.2f}) × Operating Days/Month ({operating_days})",
                    "assumption_disclosure": "Estimated gross sales figures are illustrative targets based on stated customer volume and spend assumptions. They reflect gross turnover, not net profit, and do not model variable cost of goods sold."
                }
            }

            # 6. Financial and Resource Plan
            s6_financial = {
                "section_number": "06",
                "section_title": "06 — Financial and Resource Plan",
                "estimated_startup_costs": {
                    "initial_inventory_cost_lkr": inv_cost,
                    "equipment_and_setup_lkr": setup_cost if setup_cost > 0 else (effective_capital * 0.4),
                    "working_capital_reserve_lkr": buffer_cost,
                    "total_initial_startup_cost_lkr": strategy_target_capital
                },
                "available_capital_and_funding": {
                    "available_capital_lkr": effective_capital,
                    "loan_amount_lkr": loan_amount,
                    "total_available_funds_lkr": total_available_funds,
                    "strategy_target_capital_lkr": strategy_target_capital,
                    "funding_gap_status": funding_status,
                    "funding_gap_lkr": funding_gap
                },
                "equipment_and_resource_requirements": {
                    "available_equipment_score": f"{business_input.get('available_equipment_score', 3)}/5",
                    "required_equipment_score": f"{business_input.get('required_equipment_score', 3)}/5",
                    "readiness_status": "Equipment meets operating baseline" if int(business_input.get('available_equipment_score', 3)) >= int(business_input.get('required_equipment_score', 3)) else "Additional tooling/fixtures required before opening",
                    "supplier_availability_score": f"{business_input.get('supplier_availability_score', 3)}/5 in {district}"
                },
                "staffing_requirements": {
                    "available_staff_count": business_input.get("available_staff_count", 1),
                    "required_staff_count": business_input.get("required_staff_count", 1),
                    "capacity_status": "Balanced staffing allocation" if int(business_input.get("available_staff_count", 1)) >= int(business_input.get("required_staff_count", 1)) else "Additional staffing required prior to launch",
                    "key_roles": [
                        "Managing Founder: Financial control, supplier ordering, overall management.",
                        "Frontline Service Assistant: Customer handling, order preparation, sales register."
                    ]
                },
                "operating_expenses": {
                    "monthly_operating_budget_lkr": effective_budget,
                    "strategy_capital_runway_months": strategy_budget_coverage,
                    "total_funds_runway_months": available_funds_coverage,
                    "expense_guidance": "Recommended expense distribution: Premises & Utilities (30-35%), Stock Replenishment (40-45%), Wages & Supplies (15-20%), Contingency (5-10%)."
                },
                "financial_projections": [
                    {"metric": "Estimated Monthly Gross Sales", "value": f"LKR {monthly_gross_sales:,.2f}", "basis": f"{customers_per_day} customers/day × LKR {expected_price:,.2f} × {operating_days} days"},
                    {"metric": "Monthly Operating Budget", "value": f"LKR {effective_budget:,.2f}", "basis": "Stated monthly working expense ceiling"},
                    {"metric": "Strategy Capital Coverage", "value": f"Approx {strategy_budget_coverage} Months", "basis": "Available capital divided by monthly operating budget"},
                    {"metric": "Total Funds Liquidity Buffer", "value": f"Approx {available_funds_coverage} Months", "basis": "Combined capital + loan divided by monthly budget"}
                ]
            }

            # 7. Implementation Roadmap
            s7_roadmap = {
                "section_number": "07",
                "section_title": "07 — Implementation Roadmap",
                "prioritized_actions": [
                    "Finalize commercial premises lease agreement and verify utility connections.",
                    "Complete basic interior setup, essential fixtures, and equipment installation.",
                    "Establish trade accounts and initial delivery terms with primary local suppliers in district.",
                    "Procure initial opening inventory stock and establish storage controls.",
                    "Execute pre-opening neighborhood marketing and launch storefront signage."
                ],
                "implementation_timeline": [
                    {
                        "phase_name": "Phase 1: Pre-Launch Setup & Compliance",
                        "timeframe": "Days 0 – 30",
                        "focus_actions": "Secure lease, install fixtures, establish wholesale supplier accounts, register business."
                    },
                    {
                        "phase_name": "Phase 2: Commercial Launch & Market Entry",
                        "timeframe": "Months 1 – 3",
                        "focus_actions": "Open storefront doors, launch introductory promotions, manage daily customer service, track daily cash flow."
                    },
                    {
                        "phase_name": "Phase 3: Operational Stabilization",
                        "timeframe": "Months 3 – 6",
                        "focus_actions": f"Review actual monthly expenditure against LKR {effective_budget:,.2f} budget, adjust inventory reorder points, foster repeat customer loyalty."
                    },
                    {
                        "phase_name": "Phase 4: Growth & Service Optimization",
                        "timeframe": "Months 6 – 12",
                        "focus_actions": "Evaluate service expansion or complementary product additions, optimize supplier discounts, stabilize monthly surplus."
                    }
                ],
                "launch_milestones": [
                    {"milestone": "Premises & Fixture Readiness", "target_timeframe": "Day 20", "success_criteria": "Commercial workspace clean, fitted, and functional."},
                    {"milestone": "Supplier Line Established", "target_timeframe": "Day 25", "success_criteria": "Initial stock delivered and quality-checked."},
                    {"milestone": "Storefront Official Opening", "target_timeframe": "Day 30", "success_criteria": "Doors open, signage active, initial customers served."},
                    {"milestone": "Footfall Volume Baseline", "target_timeframe": "Month 2", "success_criteria": f"Attaining approximately {customers_per_day} daily patrons."},
                    {"milestone": "Budget Compliance Audit", "target_timeframe": "Month 3", "success_criteria": f"Monthly spending within LKR {effective_budget:,.2f}."}
                ],
                "responsibilities": [
                    {"role": "Managing Entrepreneur / Founder", "accountabilities": "Overall operational oversight, financial governance, supplier negotiations, compliance."},
                    {"role": "Operations & Inventory Lead", "accountabilities": "Daily premise readiness, stock management, reorder alerts, customer service standards."},
                    {"role": "Frontline Service Staff", "accountabilities": "Customer greeting, order processing, cash counter management, premise hygiene."}
                ]
            }

            # 8. Expected Outcomes and Key Assumptions
            s8_outcomes = {
                "section_number": "08",
                "section_title": "08 — Expected Outcomes and Key Assumptions",
                "expected_business_outcomes": [
                    f"Establish a sustainable, recognized {category} business footprint in {district}.",
                    f"Achieve consistent daily footfall averaging {customers_per_day} customers per day.",
                    f"Maintain financial discipline to operate within the LKR {effective_budget:,.2f} monthly budget ceiling.",
                    "Establish a proven baseline for potential future expansion after 12 months of stable operation."
                ],
                "measurable_targets": [
                    {"kpi_name": "Daily Customer Footfall", "target_value": f"{customers_per_day} Customers / Day", "monitoring_frequency": "Daily", "focus_area": "Customer Volume"},
                    {"kpi_name": "Monthly Gross Sales", "target_value": f"LKR {monthly_gross_sales:,.2f}", "monitoring_frequency": "Monthly", "focus_area": "Revenue Generation"},
                    {"kpi_name": "Monthly Budget Compliance", "target_value": f"≤ LKR {effective_budget:,.2f} / Month", "monitoring_frequency": "Monthly", "focus_area": "Cost Control"},
                    {"kpi_name": "Liquidity Runway Buffer", "target_value": "Maintain ≥ 2 Months of Operating Budget", "monitoring_frequency": "Monthly", "focus_area": "Financial Resilience"},
                    {"kpi_name": "Customer Demand Satisfaction", "target_value": f"Maintain ≥ {demand_score_val}/100 Rating", "monitoring_frequency": "Quarterly", "focus_area": "Customer Experience"}
                ],
                "important_business_assumptions": [
                    f"The enterprise operates across an estimated {operating_days} operating days per month.",
                    f"Average transaction value remains stable at approximately LKR {expected_price:,.2f} per customer visit.",
                    f"Local supplier networks in {district} maintain steady wholesale replenishment without disruptive price shocks.",
                    "Customer awareness campaigns succeed in driving planned footfall within the first 60 days of launch."
                ],
                "data_limitations_and_validation": [
                    "The feasibility assessment was evaluated using a machine learning model trained on historical Sri Lankan SME dataset records and represents statistical likelihood rather than a commercial guarantee.",
                    "Financial projections are based on user-provided inputs and stated assumptions; they reflect gross turnover estimates and do not constitute certified accounting audits.",
                    "The entrepreneur must independently verify commercial lease terms, municipal permit requirements, and local supplier price lists before committing irreversible capital outlays."
                ]
            }

            new_startup_sections = {
                "section_1_executive_summary": s1_exec,
                "section_2_business_overview": s2_overview,
                "section_3_feasibility_findings": s3_feasibility,
                "section_4_personalized_strategy": s4_strategy,
                "section_5_marketing_sales": s5_marketing,
                "section_6_financial_resource": s6_financial,
                "section_7_implementation_roadmap": s7_roadmap,
                "section_8_outcomes_assumptions": s8_outcomes
            }
        else:
            # =================================================================
            # UNIFIED PERSONALIZED BUSINESS GROWTH PLAN (7 SECTIONS + EXEC SUMMARY)
            # =================================================================
            new_startup_sections = None

            # Dynamically identify relevant growth opportunities supported by actual data
            growth_opportunities = []
            
            # 1. Attracting new customers and retaining existing customers
            opp_1_action = (
                f"Capitalize on recorded customer demand ({demand_score_val}/100) and established presence in {district} "
                f"by deploying structured customer loyalty incentives, referral programs, and repeat-visit benefits "
                f"to stabilize baseline patron volume and drive lifetime customer value."
            )
            growth_opportunities.append({
                "opportunity_area": "Customer Acquisition & Retention",
                "applicability": "High Operational Priority",
                "strategic_action": opp_1_action
            })

            # 2. Improving sales and marketing
            opp_2_action = (
                f"Upgrade storefront visibility, local community brand presence, and targeted digital marketing within "
                f"{district} to attract commuters, residential shoppers, and business clients while differentiating from local competitors."
            )
            growth_opportunities.append({
                "opportunity_area": "Sales & Targeted Local Marketing",
                "applicability": "High Commercial Priority",
                "strategic_action": opp_2_action
            })

            # 3. Improving existing products or services
            opp_3_action = (
                f"Refine core {category} commercial offerings based on current patron feedback, streamlining service speed, "
                f"improving product presentation, and optimizing inventory availability during high-traffic operating hours."
            )
            growth_opportunities.append({
                "opportunity_area": "Improving Existing Products or Services",
                "applicability": "Core Focus Area",
                "strategic_action": opp_3_action
            })

            # 4. Introducing related products or services
            if "STRAT_04" in str(active_strategy_id) or effective_capital >= 500000:
                opp_4_action = (
                    f"Introduce complementary, higher-margin merchandise or specialized service add-ons within the existing premises, "
                    f"increasing average spend per customer interaction without proportional fixed rental overhead increases."
                )
                opp_4_status = "Primary Strategic Fit" if "STRAT_04" in str(active_strategy_id) else "High Potential"
            else:
                opp_4_action = (
                    f"Selectively trial low-inventory complementary goods, assessing customer uptake and margin contribution "
                    f"prior to committing substantial working capital outlays."
                )
                opp_4_status = "Selective / Phased Potential"
            growth_opportunities.append({
                "opportunity_area": "Introducing Related Products or Services",
                "applicability": opp_4_status,
                "strategic_action": opp_4_action
            })

            # 5. Improving operational capacity or distribution
            if int(business_input.get("available_equipment_score", 3)) < int(business_input.get("required_equipment_score", 3)) or int(business_input.get("available_staff_count", 1)) < int(business_input.get("required_staff_count", 1)):
                opp_5_action = (
                    f"Eliminate service bottlenecks through targeted equipment tooling upgrades and structured employee shift schedules, "
                    f"expanding daily customer processing capacity to match peak localized demand."
                )
                opp_5_status = "Immediate Operational Need"
            else:
                opp_5_action = (
                    f"Leverage current operational readiness to support extended operating hours, telephone/digital pre-ordering, "
                    f"or direct neighborhood delivery fulfillment across {district}."
                )
                opp_5_status = "Operational Efficiency Opportunity"
            growth_opportunities.append({
                "opportunity_area": "Improving Operational Capacity & Distribution",
                "applicability": opp_5_status,
                "strategic_action": opp_5_action
            })

            # 6. Reaching new customer segments or markets
            opp_6_action = (
                f"Expand commercial footprint beyond immediate walk-in neighborhood traffic to nearby institutional clients, "
                f"local offices, schools, and residential clusters in {district} through tailored commercial packages or bulk accounts."
            )
            growth_opportunities.append({
                "opportunity_area": "Reaching New Customer Segments & Markets",
                "applicability": "Moderate to High Potential",
                "strategic_action": opp_6_action
            })

            # 7. Expanding geographical reach / opening another branch
            if total_available_funds >= 1500000 and strategy_budget_coverage >= 4.0:
                opp_7_action = (
                    f"Given a resilient capital runway buffer of approximately {strategy_budget_coverage} months, the business maintains "
                    f"sufficient financial cushion to plan phased physical branch expansion into an adjacent high-density commercial node "
                    f"once primary operational cash flow remains steady for 6 consecutive months."
                )
                opp_7_status = "Medium-Term Scalability"
            else:
                opp_7_action = (
                    f"Physical branch expansion is deferred in the near term to prioritize working liquidity and operational consolidation at the primary location, "
                    f"preserving reserves until total available liquidity exceeds 6 months of operating expenditures."
                )
                opp_7_status = "Deferred / Long-Term Scalability"
            growth_opportunities.append({
                "opportunity_area": "Expanding Geographical Reach & Branch Expansion",
                "applicability": opp_7_status,
                "strategic_action": opp_7_action
            })

            # Executive Summary (Unified Growth)
            eg_exec = {
                "section_number": "00",
                "section_title": "Executive Summary",
                "business_summary": (
                    f"{business_name} is an established enterprise operating within the {category} industry in {district}, "
                    f"{province} Province, Sri Lanka. The enterprise operates under a {business_input.get('business_model', 'Direct Retail / Service')} "
                    f"model, serving the local commercial catchment. This Personalized Business Growth Plan synthesizes machine learning feasibility, "
                    f"explainable SHAP factor attribution, and multi-criteria TOPSIS strategy evaluation to deliver an actionable growth blueprint."
                ),
                "growth_objectives": (
                    business_input.get("proposed_action") or business_input.get("additional_description") or
                    f"Accelerate commercial growth, optimize operating capacity, and improve customer reach for {business_name} in {district}."
                ),
                "ai_feasibility_result": {
                    "predicted_label": predicted_label,
                    "confidence_percentage": f"{(confidence_score * 100):.1f}%",
                    "probabilities": probabilities,
                    "interpretation": (
                        f"The trained AI decision engine classifies the proposed business growth as '{predicted_label}' "
                        f"with {confidence_score:.1%} predicted class probability under the evaluated capital, demand, and operational parameters."
                    )
                },
                "recommended_strategy": {
                    "strategy_name": active_strategy_name,
                    "strategic_focus": active_strategy.get("strategic_focus", "Capital-Protected Phased Growth"),
                    "topsis_score": str(topsis_ranking.get("top_topsis_score", "0.7850")),
                    "alignment_note": (
                        "Matches the algorithmic multi-criteria optimal recommendation."
                        if not is_user_selected else
                        f"Entrepreneur-selected operating path ({active_strategy_name}); strategic plan aligned accordingly."
                    )
                },
                "investment_funding_summary": {
                    "estimated_growth_capital_lkr": strategy_target_capital,
                    "available_capital_lkr": effective_capital,
                    "loan_amount_lkr": loan_amount,
                    "total_available_funds_lkr": total_available_funds,
                    "monthly_operating_budget_lkr": effective_budget,
                    "funding_gap_status": funding_status,
                    "funding_gap_lkr": funding_gap
                },
                "expected_outcomes": [
                    f"Strengthen commercial presence and customer retention for {business_name} in {district}.",
                    f"Target daily customer volume reaching approximately {customers_per_day} customers per day.",
                    f"Maintain financial discipline with monthly working expenses capped at LKR {effective_budget:,.2f}.",
                    f"Maintain liquidity reserves providing approximately {strategy_budget_coverage} months of operating coverage."
                ]
            }

            # 1. Existing Business Overview and Growth Objectives
            eg_s1 = {
                "section_number": "01",
                "section_title": "01 — Existing Business Overview and Growth Objectives",
                "business_identity": {
                    "business_name": business_name,
                    "business_category": category,
                    "business_stage": "Existing Business",
                    "district": district,
                    "province": province,
                    "location_address": business_input.get("address") or "Information not provided in business intake",
                    "location_type": business_input.get("location_type", "Commercial Hub"),
                    "location_suitability_score": f"{business_input.get('location_suitability_score', 3)}/5"
                },
                "existing_products_and_services": (
                    business_input.get("additional_description") or
                    f"Established commercial products and customer services within the {category} sector, operating under a {business_input.get('business_model', 'Direct Retail / Service')} model."
                ),
                "current_business_situation_and_resources": {
                    "available_capital_lkr": effective_capital,
                    "monthly_operating_budget_lkr": effective_budget,
                    "current_staff_count": business_input.get("available_staff_count", 1),
                    "required_staff_count": business_input.get("required_staff_count", 1),
                    "equipment_readiness_score": f"{business_input.get('available_equipment_score', 3)}/5",
                    "required_equipment_score": f"{business_input.get('required_equipment_score', 3)}/5",
                    "supplier_availability_score": f"{business_input.get('supplier_availability_score', 3)}/5 in {district}",
                    "entrepreneur_experience_years": f"{business_input.get('entrepreneur_experience_years', 3)} Years"
                },
                "growth_objectives": (
                    business_input.get("proposed_action") or business_input.get("additional_description") or
                    f"Execute targeted operational and commercial growth for {business_name} to expand customer reach and strengthen enterprise resilience."
                ),
                "constraints_and_improvement_needs": [
                    f"Hurdle in {d.get('feature', '').replace('_', ' ').title()}: Recorded condition ({d.get('feature_value', 'Requires attention')}) creates a downward constraint requiring operational mitigation."
                    for d in explainability.get("negative_drivers", [])[:3]
                ] or [
                    "Working capital buffer requires ongoing preservation against wholesale supplier price volatility.",
                    "Staffing allocation requires structured shift scheduling to maintain consistent service throughput during peak hours.",
                    "Equipment throughput requires periodic preventive maintenance to avoid unplanned commercial downtime."
                ],
                "intended_outcomes": [
                    f"Achieve sustainable revenue growth and expanded footfall averaging {customers_per_day} customers per day.",
                    f"Enhance operating efficiency and service delivery across the {district} commercial catchment.",
                    f"Protect parent enterprise profitability by capping working expenditures within LKR {effective_budget:,.2f} per month.",
                    f"Build a proven operational baseline for potential future multi-channel or branch expansion."
                ]
            }

            # 2. Market and Growth Opportunity Analysis
            eg_s2 = {
                "section_number": "02",
                "section_title": "02 — Market and Growth Opportunity Analysis",
                "market_catchment": {
                    "target_market": f"{district} ({business_input.get('location_type', 'Urban Commercial Hub')} Catchment)",
                    "customer_profile": business_input.get("target_age_group") or "Local consumers, commuters, and residential patrons",
                    "expected_customers_per_day": customers_per_day,
                    "expected_selling_price_lkr": expected_price,
                    "operating_days_per_month": operating_days,
                    "customer_demand_score": f"{demand_score_val}/100",
                    "monthly_gross_sales_estimate": monthly_gross_sales
                },
                "identified_growth_opportunities": growth_opportunities,
                "competitive_environment": {
                    "competition_level": business_input.get("competition_level", "Moderate"),
                    "competitor_count_nearby": competitor_count_display,
                    "competitor_information": competitor_info_display,
                    "positioning_strategy": f"Differentiate through consistent service execution, localized relationship building, and {active_strategy_name} rather than margin-eroding price discounting."
                }
            }

            # 3. Feasibility Assessment and Key Findings
            eg_s3 = {
                "section_number": "03",
                "section_title": "03 — Feasibility Assessment and Key Findings",
                "ml_feasibility_classification": {
                    "predicted_label": predicted_label,
                    "confidence_score": confidence_score,
                    "confidence_percentage": f"{(confidence_score * 100):.1f}%",
                    "probabilities": probabilities,
                    "interpretation": (
                        f"The trained Random Forest machine learning model predicts an assessment verdict of '{predicted_label}' "
                        f"with {confidence_score:.1%} predicted class probability under the evaluated operational and financial inputs."
                    )
                },
                "key_positive_drivers": [
                    {
                        "feature": d.get("feature", "").replace("_", " ").title(),
                        "direction": "+",
                        "relative_importance": round(abs(float(d.get("importance", d.get("impact_score", 0.0)))), 4),
                        "feature_value": str(d.get("feature_value", "N/A")),
                        "business_interpretation": f"Favorable recorded condition for {d.get('feature', '').replace('_', ' ').title()} ({d.get('feature_value', '')}) provides strong positive backing to feasibility."
                    }
                    for d in explainability.get("positive_drivers", [])[:4]
                ],
                "key_negative_hurdles": [
                    {
                        "feature": d.get("feature", "").replace("_", " ").title(),
                        "direction": "-",
                        "relative_importance": round(abs(float(d.get("importance", d.get("impact_score", 0.0)))), 4),
                        "feature_value": str(d.get("feature_value", "N/A")),
                        "business_interpretation": f"Recorded level for {d.get('feature', '').replace('_', ' ').title()} ({d.get('feature_value', '')}) represents a downward operational or financial hurdle requiring active management."
                    }
                    for d in explainability.get("negative_drivers", [])[:4]
                ],
                "resource_availability_assessment": {
                    "staffing_balance": f"Available Staff: {business_input.get('available_staff_count', 1)} | Required: {business_input.get('required_staff_count', 1)} ({'Balanced' if int(business_input.get('available_staff_count', 1)) >= int(business_input.get('required_staff_count', 1)) else 'Recruitment needed'})",
                    "equipment_readiness": f"Equipment Score: {business_input.get('available_equipment_score', 3)}/5 vs Required Target: {business_input.get('required_equipment_score', 3)}/5 ({'Ready' if int(business_input.get('available_equipment_score', 3)) >= int(business_input.get('required_equipment_score', 3)) else 'Upgrades required'})",
                    "supplier_access": f"Supplier Availability Rating: {business_input.get('supplier_availability_score', 3)}/5 in {district}",
                    "location_suitability": f"Location Suitability Score: {business_input.get('location_suitability_score', 3)}/5 in {district}"
                },
                "affordability_gaps_and_findings": {
                    "available_capital_lkr": effective_capital,
                    "loan_amount_lkr": loan_amount,
                    "total_available_funds_lkr": total_available_funds,
                    "strategy_target_capital_lkr": strategy_target_capital,
                    "funding_gap_status": funding_status,
                    "funding_gap_lkr": funding_gap,
                    "capital_runway_months": strategy_budget_coverage,
                    "total_funds_runway_months": available_funds_coverage,
                    "key_findings_summary": (
                        f"Feasibility classification confirms viable growth potential supported by founder experience and customer demand ({demand_score_val}/100). "
                        f"However, liquidity runway ({strategy_budget_coverage} months) necessitates strict cost discipline to safeguard parent enterprise stability."
                    )
                }
            }

            # 4. Personalized Growth Strategy
            eg_s4 = {
                "section_number": "04",
                "section_title": "04 — Personalized Growth Strategy",
                "recommended_growth_approach": {
                    "strategy_name": active_strategy_name,
                    "strategy_id": active_strategy_id,
                    "strategic_focus": active_strategy.get("strategic_focus", "Capital-Protected Phased Growth"),
                    "topsis_score": str(topsis_ranking.get("top_topsis_score", "0.7850")),
                    "operational_approach": (
                        active_strategy.get("operational_approach") or
                        f"Execute structured commercial growth for {business_name} focusing on {active_strategy.get('strategic_focus', 'operational scale')} "
                        f"to maximize patron volume and average spend while strictly safeguarding working capital."
                    ),
                    "is_user_selected": is_user_selected,
                    "selection_status": (
                        "Matches algorithmic multi-criteria optimal TOPSIS ranking."
                        if not is_user_selected else
                        f"Entrepreneur actively selected alternative strategy ({active_strategy_name}); business plan re-aligned accordingly."
                    )
                },
                "strategy_suitability_rationale": (
                    f"The selection of '{active_strategy_name}' is grounded in the enterprise's current operational footprint. "
                    f"With available capital of LKR {effective_capital:,.2f} and a monthly operating budget of LKR {effective_budget:,.2f}, "
                    f"this approach balances demand capture ({demand_score_val}/100 demand index) against resource constraints. "
                    f"Rather than committing to irreversible physical lease commitments prematurely, it prioritizes throughput optimization, "
                    f"customer retention, and margin enhancement within the established {district} facility."
                ),
                "alternatives_comparison": {
                    "criteria_weights": [
                        {"criterion": "Financial Viability", "weight": 0.25, "description": "Cash flow sustainability, runway adequacy, and capital discipline."},
                        {"criterion": "Implementation Feasibility", "weight": 0.20, "description": "Operational ease given available staff and entrepreneur experience."},
                        {"criterion": "Market Demand Alignment", "weight": 0.25, "description": "Alignment with local customer footfall and demand score."},
                        {"criterion": "Operational Risk", "weight": 0.15, "description": "Mitigation of fixed cost exposure and supply chain disruptions."},
                        {"criterion": "Resource Efficiency", "weight": 0.15, "description": "Output generation relative to equipment and labor deployed."}
                    ],
                    "ranked_strategies": candidate_strategies
                },
                "prioritized_practical_actions": [
                    f"Reconfigure existing layout and service counter workflows to accommodate peak customer volume ({customers_per_day} patrons/day).",
                    f"Establish structured trade credit and volume replenishment agreements with primary local suppliers in {district}.",
                    "Implement a customer retention loyalty tracking system to encourage repeat visits and word-of-mouth recommendations.",
                    "Execute targeted promotional campaigns and storefront visual signage across the immediate commercial area.",
                    "Review weekly sales figures and operating expenditures against stated budget ceilings to maintain liquidity runway."
                ],
                "gap_mitigation_plan": [
                    "Address staffing capacity by cross-training existing team members across customer service and inventory replenishment.",
                    "Address equipment readiness gaps by scheduling preventive servicing and procuring essential fixtures prior to launch of expansion activities.",
                    "Maintain strict financial ring-fencing to ensure expansion capital does not cannibalize core operating working cash reserves."
                ]
            }

            # 5. Financial and Resource Plan
            eg_s5 = {
                "section_number": "05",
                "section_title": "05 — Financial and Resource Plan",
                "estimated_growth_costs": {
                    "capex_and_tooling_upgrades_lkr": setup_cost,
                    "inventory_replenishment_cost_lkr": inv_cost,
                    "working_capital_reserve_lkr": buffer_cost,
                    "total_estimated_growth_capital_lkr": strategy_target_capital
                },
                "available_capital_and_funding": {
                    "available_capital_lkr": effective_capital,
                    "loan_amount_lkr": loan_amount,
                    "total_available_funds_lkr": total_available_funds,
                    "strategy_target_capital_lkr": strategy_target_capital,
                    "funding_gap_status": funding_status,
                    "funding_gap_lkr": funding_gap
                },
                "resource_and_staffing_requirements": {
                    "available_staff_count": business_input.get("available_staff_count", 1),
                    "required_staff_count": business_input.get("required_staff_count", 1),
                    "capacity_status": "Balanced staffing allocation" if int(business_input.get("available_staff_count", 1)) >= int(business_input.get("required_staff_count", 1)) else "Additional staffing required prior to expansion launch",
                    "equipment_status": f"Available: {business_input.get('available_equipment_score', 3)}/5 vs Target: {business_input.get('required_equipment_score', 3)}/5",
                    "supplier_access": f"Supplier score: {business_input.get('supplier_availability_score', 3)}/5 in {district}"
                },
                "operating_expenses": {
                    "monthly_operating_budget_lkr": effective_budget,
                    "strategy_capital_runway_months": strategy_budget_coverage,
                    "total_funds_runway_months": available_funds_coverage,
                    "expense_guidance": "Recommended expenditure breakdown: Premises & Utilities (25-30%), Stock Replenishment (45-50%), Wages & Supplies (15-20%), Contingency (5-10%)."
                },
                "financial_projections": [
                    {"metric": "Estimated Monthly Gross Sales", "value": f"LKR {monthly_gross_sales:,.2f}", "basis": f"{customers_per_day} customers/day × LKR {expected_price:,.2f} × {operating_days} operating days"},
                    {"metric": "Monthly Operating Budget Ceiling", "value": f"LKR {effective_budget:,.2f}", "basis": "Stated monthly working expense cap"},
                    {"metric": "Strategy Capital Coverage", "value": f"Approx {strategy_budget_coverage} Months", "basis": "Available capital divided by monthly budget"},
                    {"metric": "Total Funds Liquidity Runway", "value": f"Approx {available_funds_coverage} Months", "basis": "Combined capital + loan divided by monthly budget"}
                ],
                "payback_and_affordability_analysis": {
                    "is_calculated": bool(business_input.get("expansion_capex_lkr") and business_input.get("current_monthly_net_profit_lkr")),
                    "estimated_payback_months": round(float(business_input.get("expansion_capex_lkr", 0.0)) / max(float(business_input.get("current_monthly_net_profit_lkr", 1.0)), 1.0), 1) if business_input.get("expansion_capex_lkr") and business_input.get("current_monthly_net_profit_lkr") else None,
                    "affordability_note": "Financial projections reflect gross turnover assumptions based on user-stated footfall and unit prices. Net margin and payback depend on operating discipline and variable cost control."
                }
            }

            # 6. Implementation Roadmap
            eg_s6 = {
                "section_number": "06",
                "section_title": "06 — Implementation Roadmap",
                "prioritized_actions": [
                    "Conduct operational baseline audit and reconfigure customer service layout.",
                    "Procure necessary equipment tooling and finalize supplier wholesale delivery terms in district.",
                    "Execute pre-launch marketing campaign and roll out customer loyalty rewards.",
                    "Onboard and train staff on service standards, inventory handling, and daily sales logging.",
                    "Establish monthly financial audit cadence to review operating budget compliance."
                ],
                "implementation_stages": [
                    {
                        "stage_name": "Stage 1: Resource Staging & Alignment",
                        "timeframe": "Days 0 – 30",
                        "focus_actions": "Verify equipment readiness, finalize supplier trade credit terms, and confirm operating budget allocations."
                    },
                    {
                        "stage_name": "Stage 2: Operational Rollout & Capacity Setup",
                        "timeframe": "Months 1 – 3",
                        "focus_actions": "Reconfigure service counters, install equipment tooling, and train staff on throughput efficiency."
                    },
                    {
                        "stage_name": "Stage 3: Market Expansion & Customer Acquisition",
                        "timeframe": "Months 3 – 6",
                        "focus_actions": "Launch targeted local promotions, roll out customer loyalty tracking, and engage nearby commercial clusters."
                    },
                    {
                        "stage_name": "Stage 4: Optimization, Review & Sustained Scale",
                        "timeframe": "Months 6 – 12",
                        "focus_actions": "Review monthly revenue against targets, audit working capital runway, and assess multi-channel or branch expansion viability."
                    }
                ],
                "launch_milestones": [
                    {"milestone": "Operational Capacity Readiness", "target_timeframe": "Day 30", "success_criteria": "Fixtures installed and equipment score verified at target level."},
                    {"milestone": "Supplier Trade Terms Finalized", "target_timeframe": "Day 45", "success_criteria": "Direct replenishment schedules confirmed with primary suppliers."},
                    {"milestone": "Customer Footfall Target Achieved", "target_timeframe": "Month 3", "success_criteria": f"Sustained average of {customers_per_day} customer transactions daily."},
                    {"milestone": "Financial Budget Discipline Verified", "target_timeframe": "Month 6", "success_criteria": f"Operating expenses stay within LKR {effective_budget:,.2f} monthly ceiling."},
                    {"milestone": "Expansion Review & Milestone Audit", "target_timeframe": "Month 12", "success_criteria": "Full year review completed with sustained positive cash flow reserves."}
                ],
                "responsibilities": [
                    {"role": "Managing Director / Owner", "accountabilities": "Overall strategic direction, financial approvals, lease terms, and banking relationships."},
                    {"role": "Operations & Inventory Lead", "accountabilities": "Equipment maintenance, supplier ordering, quality control, and shift management."},
                    {"role": "Customer Service / Frontline Staff", "accountabilities": "Order taking, customer engagement, POS sales recording, and storefront upkeep."}
                ],
                "progress_monitoring": "Management should conduct weekly cash flow reconciliations and monthly strategy audits to track milestone compliance."
            }

            # 7. Expected Outcomes and Success Indicators
            eg_s7 = {
                "section_number": "07",
                "section_title": "07 — Expected Outcomes and Success Indicators",
                "expected_business_outcomes": [
                    f"Strengthen commercial presence, brand recognition, and customer loyalty for {business_name} in {district}.",
                    f"Attain consistent customer throughput reaching approximately {customers_per_day} patrons per operating day.",
                    f"Maintain financial discipline with monthly operating costs kept within the LKR {effective_budget:,.2f} budget ceiling.",
                    f"Maintain liquidity reserves providing approximately {strategy_budget_coverage} months of operating buffer.",
                    "Establish a proven, robust operational foundation for potential future branch or channel expansion."
                ],
                "measurable_targets_kpis": [
                    {"kpi_name": "Daily Customer Footfall", "target_value": f"{customers_per_day} Customers / Day", "monitoring_frequency": "Daily", "focus_area": "Customer Volume"},
                    {"kpi_name": "Monthly Gross Sales", "target_value": f"LKR {monthly_gross_sales:,.2f}", "monitoring_frequency": "Monthly", "focus_area": "Revenue Generation"},
                    {"kpi_name": "Monthly Budget Compliance", "target_value": f"≤ LKR {effective_budget:,.2f} / Month", "monitoring_frequency": "Monthly", "focus_area": "Cost Control"},
                    {"kpi_name": "Liquidity Runway Buffer", "target_value": f"Maintain ≥ 2 Months of Operating Budget", "monitoring_frequency": "Monthly", "focus_area": "Financial Resilience"},
                    {"kpi_name": "Customer Demand Satisfaction", "target_value": f"Maintain ≥ {demand_score_val}/100 Rating", "monitoring_frequency": "Quarterly", "focus_area": "Customer Experience"}
                ],
                "suggested_methods_for_tracking_progress": [
                    "Daily Sales Log & Cash Drawer Reconciliation: Record daily customer count, transaction values, and daily gross turnover.",
                    "Monthly Expense Audit: Reconcile actual supplier invoices, utilities, and wages against the monthly budget ceiling.",
                    "Customer Feedback Surveys: Conduct informal quarterly customer inquiries on service quality and product availability.",
                    "Supplier Cost Monitoring: Review quarterly wholesale price lists to safeguard gross margins against inflationary spikes."
                ],
                "important_business_assumptions": [
                    f"The enterprise operates across an estimated {operating_days} operating days per month.",
                    f"Average unit spend remains stable at approximately LKR {expected_price:,.2f} per customer transaction.",
                    f"Local supplier networks in {district} maintain steady delivery schedules without disruptive commodity price shocks.",
                    "Customer awareness activities succeed in driving planned footfall within the first 60 days of expansion."
                ],
                "data_limitations_and_validation": [
                    "The feasibility classification was generated using a machine learning model trained on historical Sri Lankan SME dataset records and represents statistical likelihood rather than a commercial guarantee.",
                    "Financial projections are based on user-provided inputs and stated assumptions; they reflect gross turnover estimates and do not constitute certified accounting audits.",
                    "The business owner must independently verify commercial premises lease terms, municipal permits, and local wholesale distributor agreements before committing capital outlays."
                ]
            }

            unified_growth_sections = {
                "executive_summary": eg_exec,
                "section_1_overview_objectives": eg_s1,
                "section_2_market_opportunities": eg_s2,
                "section_3_feasibility_findings": eg_s3,
                "section_4_growth_strategy": eg_s4,
                "section_5_financial_resource": eg_s5,
                "section_6_implementation_roadmap": eg_s6,
                "section_7_outcomes_indicators": eg_s7
            }

        # Build Normalized Report Dictionary
        report_data = {
            "cover_image": cover_image,
            "new_startup_sections": new_startup_sections,
            "unified_growth_sections": unified_growth_sections,
            "existing_growth_sections": unified_growth_sections,
            "metadata": {
                "record_id": metadata.get("record_id", "N/A"),
                "schema_version": metadata.get("schema_version", "2.0.0"),
                "generated_date": date_str,
                "system_brand": "SME360 AI",
                "document_title": doc_title,
                "document_subtitle": doc_subtitle,
                "is_new_startup": is_new_startup,
                "is_existing_growth": not is_new_startup
            },
            "business_identity": {
                "business_name": business_name,
                "business_category": category,
                "business_stage": stage,
                "district": district,
                "province": province,
                "prepared_for": f"{business_name} Ownership / Management",
            },

            # -----------------------------------------------------------------
            # 5 Major Research Sections
            # -----------------------------------------------------------------
            "section_01": sec_01 or {
                "section_number": "01",
                "section_title": "01 — Business & Market Overview",
                "business_summary": {
                    "business_name": business_name,
                    "business_category": category,
                    "business_stage": stage,
                    "business_model": business_input.get("business_model") or "Direct Retail / Service",
                    "district": district,
                    "province": province,
                    "location_address": business_input.get("address") or "Information not provided",
                    "proposed_action": business_input.get("proposed_action") or "Launch Operations",
                    "business_description": business_input.get("additional_description") or "Information not provided"
                },
                "business_concept": {
                    "concept_overview": executive_overview.get("business_summary", f"Strategic plan for a proposed {stage.lower()} {category.lower()} in {district}."),
                    "products_services": f"Products and commercial offerings in {category}",
                    "target_customers": business_input.get("target_age_group") or f"Local consumers in {district}",
                    "business_objectives": business_input.get("additional_description") or f"Establish a sustainable {category} in {district}."
                },
                "market_overview": {
                    "target_market": f"{district} ({business_input.get('location_type', 'Urban')} Catchment)",
                    "customer_profile": business_input.get("target_age_group") or "Information not provided",
                    "expected_customers_per_day": customers_per_day,
                    "expected_selling_price_lkr": expected_price,
                    "operating_days_per_month": operating_days,
                    "customer_demand_score": f"{business_input.get('customer_demand_score', 50)}/100"
                },
                "competition": {
                    "competition_level": business_input.get("competition_level", "Moderate"),
                    "competitor_count_nearby": competitor_count_display,
                    "competitor_information": competitor_info_display,
                    "competitive_positioning": f"Differentiation via customer service and {active_strategy_name}."
                },
                "location": {
                    "district": district,
                    "province": province,
                    "location_type": business_input.get("location_type", "Commercial Hub"),
                    "location_suitability_score": f"{business_input.get('location_suitability_score', 3)}/5",
                    "location_considerations": f"Commercial density and customer foot traffic in {district}."
                }
            },

            "section_02": sec_02 or {
                "section_number": "02",
                "section_title": "02 — AI Feasibility & Key Insights",
                "feasibility_assessment": {
                    "final_predicted_label": predicted_label,
                    "confidence_score": confidence_score,
                    "confidence_percentage": f"{(confidence_score * 100):.1f}%",
                    "predicted_class_probability": confidence_score,
                    "predicted_probability_percentage": f"{(confidence_score * 100):.1f}%",
                    "probabilities": probabilities
                },
                "feasibility_interpretation": (
                    f"The proposed business is assessed as '{predicted_label}' with {confidence_score:.1%} predicted class probability "
                    f"under the evaluated financial, operational, and market parameters."
                ),
                "shap_explainability": {
                    "methodology_note": "SHAP feature attribution indicates factors that contributed to the model prediction without asserting causal proof.",
                    "positive_enablers": [
                        {
                            "feature": d.get("feature", "").replace("_", " ").title(),
                            "direction": "+",
                            "relative_importance": round(abs(float(d.get("importance", d.get("impact_score", 0.0)))), 4),
                            "feature_value": str(d.get("feature_value", "N/A")),
                            "business_interpretation": f"Favorable recorded condition for {d.get('feature', '')} contributed positive support to feasibility."
                        }
                        for d in explainability.get("positive_drivers", [])[:4]
                    ],
                    "negative_hurdles": [
                        {
                            "feature": d.get("feature", "").replace("_", " ").title(),
                            "direction": "-",
                            "relative_importance": round(abs(float(d.get("importance", d.get("impact_score", 0.0)))), 4),
                            "feature_value": str(d.get("feature_value", "N/A")),
                            "business_interpretation": f"Constraint in {d.get('feature', '')} contributed downward pressure, highlighting an operational hurdle."
                        }
                        for d in explainability.get("negative_drivers", [])[:4]
                    ]
                },
                "key_insights": {
                    "strengths": [f"Favorable {d.get('feature', '')}: {d.get('feature_value', 'Adequate')}" for d in explainability.get("positive_drivers", [])[:3]] or ["Baseline readiness supports initial launch."],
                    "constraints": [f"Constraint in {d.get('feature', '')}: {d.get('feature_value', 'Requires attention')}" for d in explainability.get("negative_drivers", [])[:3]] or ["Working capital buffer requires ongoing monitoring."]
                }
            },

            "section_03": sec_03 or {
                "section_number": "03",
                "section_title": "03 — Strategic Recommendations & TOPSIS Ranking",
                "available_strategic_alternatives": candidate_strategies,
                "topsis_evaluation": {
                    "criteria_weights": [
                        {"criterion": "Financial Viability", "weight": 0.25, "description": "Assessment of cash flow adequacy, capital runway, and budgetary resilience."},
                        {"criterion": "Implementation Feasibility", "weight": 0.20, "description": "Ease of operational execution given available experience and team size."},
                        {"criterion": "Market Demand Alignment", "weight": 0.25, "description": "Alignment with local consumer demand score and footfall potential."},
                        {"criterion": "Resource & Operational Friction", "weight": 0.15, "description": "Exposure to fixed-cost burn, supply dependencies, and resource hurdles."},
                        {"criterion": "Resource Efficiency", "weight": 0.15, "description": "Ratio of output generation to invested equipment and human capital."}
                    ]
                },
                "strategy_ranking": topsis_ranking.get("ranked_strategies", candidate_strategies),
                "ai_recommended_strategy": {
                    "strategy_name": ai_top_strategy,
                    "strategy_id": topsis_ranking.get("top_recommended_id", "STRAT_01"),
                    "topsis_score": ai_top_score
                },
                "human_in_the_loop_selection": {
                    "is_user_selected": is_user_selected,
                    "selected_strategy_id": active_strategy_id,
                    "selected_strategy_name": active_strategy_name,
                    "alignment_status": (
                        "Selected strategy matches the AI's highest-ranked recommendation."
                        if not is_user_selected else
                        f"The entrepreneur selected an alternative strategy ({active_strategy_name}) that was ranked differently by the AI. The business plan has been re-aligned with the entrepreneur's selected strategy."
                    )
                }
            },

            "section_04": sec_04 or {
                "section_number": "04",
                "section_title": "04 — Financial & Operational Plan",
                "active_strategy_alignment": {
                    "strategy_name": active_strategy_name,
                    "is_user_selected": is_user_selected
                },
                "startup_investment": {
                    "available_capital_lkr": effective_capital,
                    "strategy_target_capital_lkr": strategy_target_capital,
                    "loan_amount_lkr": loan_amount,
                    "initial_inventory_cost_lkr": float(business_input.get("initial_inventory_cost_lkr", 0.0)),
                    "funding_gap_lkr": max(0.0, strategy_target_capital - total_available_funds),
                    "funding_gap_status": "Fully funded from baseline capital" if total_available_funds >= strategy_target_capital else "Capital gap identified"
                },
                "monthly_financial_plan": {
                    "monthly_operating_budget_lkr": effective_budget,
                    "expected_price_lkr": expected_price,
                    "expected_customers_per_day": customers_per_day,
                    "operating_days_per_month": operating_days,
                    "estimated_monthly_gross_sales_lkr": customers_per_day * expected_price * operating_days,
                    "estimated_monthly_revenue_lkr": customers_per_day * expected_price * operating_days,
                    "revenue_calculation_formula": "Estimated Monthly Gross Sales = Target Customers/Day × Expected Unit Price × Operating Days/Month",
                    "calculation_note": "Gross sales estimate based on stated customer volume, unit price, and operating days. Does not model variable costs or net profit."
                },
                "funding_structure": {
                    "available_capital_lkr": effective_capital,
                    "initial_available_capital_lkr": effective_capital,
                    "debt_financing_lkr": loan_amount,
                    "total_available_funds_lkr": total_available_funds,
                    "target_required_capital_lkr": strategy_target_capital,
                    "strategy_budget_coverage_months": strategy_budget_coverage,
                    "available_funds_coverage_months": available_funds_coverage,
                    "capital_runway_months": strategy_budget_coverage
                },
                "operational_plan": {
                    "staffing": {
                        "available_staff_count": business_input.get("available_staff_count", 1),
                        "required_staff_count": business_input.get("required_staff_count", 1),
                        "capacity_status": "Balanced staffing allocation"
                    },
                    "equipment": {
                        "available_equipment_score": f"{business_input.get('available_equipment_score', 3)}/5",
                        "required_equipment_score": f"{business_input.get('required_equipment_score', 3)}/5",
                        "readiness_status": "Equipment meets operating baseline"
                    },
                    "suppliers": {
                        "supplier_availability_score": f"{business_input.get('supplier_availability_score', 3)}/5",
                        "network_region": f"Local supplier channels in {district}"
                    }
                },
                "marketing_plan": {
                    "marketing_channel": business_input.get("marketing_channel", "Word of Mouth"),
                    "promotional_tactics": marketing_plan.get("promotional_tactics", [])
                }
            },

            "section_05": sec_05 or {
                "section_number": "05",
                "section_title": "05 — Scenario Analysis & Action Roadmap",
                "what_if_analysis": {
                    "scenarios": scenario_analysis.get("what_if_simulations", [])
                },
                "counterfactual_analysis": scenario_analysis.get("counterfactual_boundary", {}),
                "personalized_action_roadmap": {
                    "phase_0_to_30_days": action_roadmap.get("phase_1", []),
                    "phase_30_to_90_days": action_roadmap.get("phase_2", [])[:2],
                    "phase_3_to_6_months": action_roadmap.get("phase_2", [])[2:],
                    "phase_6_to_12_months": action_roadmap.get("phase_3", [])
                },
                "management_monitoring_measures": [
                    {"measure_name": "Monthly Gross Sales", "target": f"LKR {customers_per_day * expected_price * operating_days:,.2f}", "frequency": "Monthly", "category": "Sales Tracking"},
                    {"measure_name": "Daily Customer Count", "target": f"{customers_per_day} / Day", "frequency": "Daily", "category": "Volume"},
                    {"measure_name": "Operating Budget Compliance", "target": f"≤ LKR {effective_budget:,.2f} / Month", "frequency": "Monthly", "category": "Cost Control"},
                    {"measure_name": "Simplified Budget Coverage", "target": f"Monitor reserve buffer (approx {strategy_budget_coverage} mo)", "frequency": "Monthly", "category": "Liquidity"}
                ],
                "measurable_kpis": [
                    {"kpi_name": "Monthly Gross Sales", "target": f"LKR {customers_per_day * expected_price * operating_days:,.2f}", "frequency": "Monthly"},
                    {"kpi_name": "Daily Customer Count", "target": f"{customers_per_day} / Day", "frequency": "Daily"},
                    {"kpi_name": "Operating Budget Compliance", "target": f"≤ LKR {effective_budget:,.2f} / Month", "frequency": "Monthly"},
                    {"kpi_name": "Simplified Budget Coverage", "target": f"Approx {strategy_budget_coverage} Months", "frequency": "Monthly"}
                ],
                "operational_constraints_and_management_considerations": [
                    {"constraint": "Capital Allocation", "management_action": "Enforce strict working capital controls and prioritize lean setup investments."},
                    {"constraint": "Staff Capacity", "management_action": "Establish standardized operating checklists and cross-train staff."},
                    {"constraint": "Equipment Readiness", "management_action": "Prioritize vital operating fixtures and arrange supplier warranties."}
                ],
                "business_constraints_and_mitigation": [
                    {"constraint": "Capital Allocation", "mitigation": "Enforce strict working capital controls and prioritize lean setup investments."},
                    {"constraint": "Staff Capacity", "mitigation": "Establish standardized operating checklists and cross-train staff."},
                    {"constraint": "Equipment Readiness", "mitigation": "Prioritize vital operating fixtures and arrange supplier warranties."}
                ],
                "final_ai_recommendation": {
                    "ai_feasibility_verdict": predicted_label,
                    "ai_recommended_strategy": ai_top_strategy,
                    "entrepreneur_selected_strategy": active_strategy_name,
                    "is_user_selected": is_user_selected,
                    "recommended_immediate_next_step": "Confirm initial supplier arrangements, configure ordering channels, and prepare operating workspace."
                }
            },

            "final_recommendation": final_rec or {
                "ai_feasibility_verdict": predicted_label,
                "ai_confidence_score": confidence_score,
                "predicted_class_probability": confidence_score,
                "ai_recommended_strategy": ai_top_strategy,
                "entrepreneur_selected_strategy": active_strategy_name,
                "is_user_selected": is_user_selected,
                "recommended_immediate_next_step": "Confirm initial supplier arrangements, configure ordering channels, and prepare operating workspace."
            },

            # -----------------------------------------------------------------
            # Backward-Compatibility Keys
            # -----------------------------------------------------------------
            "executive_summary": {
                "business_summary": executive_overview.get("business_summary", f"Strategic plan for a proposed {stage.lower()} {category.lower()} in {district}."),
                "predicted_label": predicted_label,
                "confidence_score": confidence_score,
                "confidence_percent": f"{(confidence_score * 100):.1f}%",
                "probabilities": probabilities,
                "active_strategy": active_strategy_name,
                "is_user_selected": is_user_selected,
            },
            "business_overview": {
                "category": category,
                "stage": stage,
                "district": district,
                "experience_years": int(business_input.get("entrepreneur_experience_years", 0)),
                "staff_count": int(business_input.get("available_staff_count", 1)),
                "competition_level": business_input.get("competition_level", "Moderate")
            },
            "financial_overview": {
                "available_capital_lkr": effective_capital,
                "monthly_budget_lkr": effective_budget,
                "expected_price_lkr": expected_price,
                "estimated_monthly_gross_sales_lkr": customers_per_day * expected_price * operating_days,
                "estimated_monthly_revenue_lkr": customers_per_day * expected_price * operating_days,
                "loan_required": effective_capital < (effective_budget * 6),
                "strategy_budget_coverage_months": strategy_budget_coverage,
                "available_funds_coverage_months": available_funds_coverage,
                "capital_runway_months": strategy_budget_coverage,
                "guidance_summary": financial_plan.get("counterfactual_guidance", "Maintain a conservative operating buffer.")
            },
            "market_analysis": {
                "expected_customers_per_day": customers_per_day,
                "target_monthly_customers": customers_per_day * operating_days,
                "competition_level": business_input.get("competition_level", "Moderate"),
                "demand_score": marketing_plan.get("demand_score", "Moderate Market Demand"),
                "target_customer_desc": marketing_plan.get("target_daily_customers", f"{customers_per_day} target daily customers in {district}.")
            },
            "operational_plan": {
                "staffing_requirements": operational_plan.get("staffing_requirements", f"Current staff allocation: {business_input.get('available_staff_count', 1)}."),
                "equipment_readiness": operational_plan.get("equipment_readiness", "Essential operating equipment requirements identified.")
            },
            "key_business_factors": {
                "positive_enablers": explainability.get("positive_drivers", []),
                "operational_hurdles": explainability.get("negative_drivers", []),
                "risk_hurdles": explainability.get("negative_drivers", [])
            },
            "strategies": candidate_strategies,
            "strategy_priorities": {
                "top_recommended_strategy": active_strategy_name,
                "top_topsis_score": ai_top_score,
                "ai_top_strategy": ai_top_strategy,
                "ai_top_score": ai_top_score,
                "is_user_selected": is_user_selected,
                "selected_strategy_id": active_strategy_id,
                "selected_strategy_name": active_strategy_name,
                "ranked_strategies": topsis_ranking.get("ranked_strategies", candidate_strategies)
            },
            "scenarios": scenario_analysis.get("what_if_simulations", []),
            "action_roadmap": {
                "phase_1": action_roadmap.get("phase_1", []),
                "phase_2": action_roadmap.get("phase_2", []),
                "phase_3": action_roadmap.get("phase_3", [])
            },
            "assumptions_and_considerations": [
                "Feasibility assessments are based on multi-dimensional analysis of capital, market, and operational indicators.",
                "Financial projections assume operating days and steady unit pricing based on provided business inputs.",
                "Simplified budget coverage represents a capital-to-budget ratio and does not constitute a guaranteed survival period.",
                "The entrepreneur should perform on-the-ground market and supplier validation before committing heavy capital investments."
            ],
            "raw_profile": profile
        }

        return report_data
