"""
Generate sample business plan PDFs matching the user's FreshMart Grocery and
Trendy Style Clothing Shop reports and save to data/sample_plans/
"""

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.services.business_plan_generator.report_builder import BusinessPlanReportBuilder
from backend.services.business_plan_generator.pdf_generator import BusinessPlanPDFGenerator

OUTPUT_DIR = _REPO_ROOT / "data" / "sample_plans"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

freshmart_profile = {
    "metadata": {
        "record_id": "011bbccd-b633-401c-8b3b-b89397b02520",
        "created_at": "2026-10-15T10:00:00Z"
    },
    "business_input": {
        "business_name": "FreshMart Grocery",
        "business_category": "Grocery / Mini-Mart",
        "business_stage": "Existing Business",
        "district": "Colombo",
        "available_capital_lkr": 2500000.0,
        "monthly_budget_lkr": 21250.0,
        "expected_customers_per_day": 60,
        "expected_price_lkr": 300.0,
        "entrepreneur_experience_years": 4,
        "available_staff_count": 1,
        "competition_level": "High",
        "has_existing_loans": True,
        "has_equipment": True,
        "has_supplier_contacts": True
    },
    "feasibility_analysis": {
        "predicted_label": "Conditionally Feasible",
        "confidence_score": 0.48,
        "probabilities": {
            "Feasible": 0.225,
            "Conditionally Feasible": 0.48,
            "Infeasible": 0.295
        }
    },
    "explainability": {
        "positive_drivers": [
            "Customer Demand Score (1-100) (54 / 100)",
            "Available Capital (Lkr) (LKR 2,500,000)",
            "Expected Product Price (Lkr) (LKR 300)"
        ],
        "negative_drivers": [
            "Business Stage (Existing Business)",
            "Available Equipment Score (1-5) (3 / 5)",
            "Requested Loan Amount (Lkr) (LKR 1,000,000)"
        ]
    },
    "strategic_recommendations": {
        "candidate_strategies": [
            {
                "strategy_name": "Online Ordering & Delivery Expansion",
                "focus": "Multi-Channel Orders & Shared Hub Efficiency",
                "impact": "Asset-Light Revenue Growth",
                "target_capital": 1875000,
                "monthly_budget": 21250,
                "target_footfall": 69,
                "topsis_score": 0.8575
            },
            {
                "strategy_name": "Step-by-Step Staged Expansion",
                "focus": "Capital Protection & Phased Scale",
                "impact": "Guarded Capital Outlay",
                "target_capital": 1500000,
                "monthly_budget": 18750,
                "target_footfall": 51,
                "topsis_score": 0.6413
            }
        ],
        "topsis_ranking": {
            "top_recommended_strategy": "Online Ordering & Delivery Expansion",
            "top_topsis_score": "0.8575",
            "ranked_strategies": [
                {
                    "strategy_name": "Online Ordering & Delivery Expansion",
                    "focus": "Multi-Channel Orders & Shared Hub Efficiency",
                    "topsis_score": 0.8575
                }
            ],
            "evaluation_criteria": [
                {"criterion": "Financial Viability", "weight": "25%"},
                {"criterion": "Implementation Feasibility", "weight": "20%"},
                {"criterion": "Market Demand Alignment", "weight": "25%"}
            ]
        }
    },
    "scenario_analysis": {
        "what_if_simulations": [
            {"scenario": "+50% Capital Injection", "shift": "+0.0% Feasible"},
            {"scenario": "+30% Customer Footfall Boost", "shift": "+15.5% Feasible"}
        ]
    },
    "personalized_business_plan": {
        "executive_overview": {
            "business_summary": (
                "FreshMart Grocery is an established enterprise operating within the Grocery / Mini-Mart sector, "
                "located in Colombo, Western Province, Sri Lanka. Operating under a Direct Retail / Service business model, "
                "the enterprise aims to execute strategic growth and operational refinement. Based on the operational details provided: "
                "The main objective of this expansion is to increase sales, extend the business's geographical coverage, "
                "strengthen its market presence, and establish a foundation for future growth. The new branch will operate under "
                "the existing FreshMart Grocery brand and follow similar service standards, product-quality requirements, and "
                "pricing strategies as the original store. The owner also intends to improve customer convenience by offering a wider "
                "selection of essential products, maintaining reliable stock availability, and introducing WhatsApp-based ordering "
                "and local delivery services where practical."
            )
        },
        "operational_plan": {
            "staffing_requirements": "The enterprise currently deploys 1 active staff member(s) against an estimated requirement of 1, representing a Balanced staffing.",
            "equipment_readiness": "Available equipment readiness is rated at 3/5, currently satisfying operational requirements."
        },
        "marketing_plan": {
            "demand_score": "Customer demand score recorded at 54/100 within Colombo expansion catchment.",
            "target_daily_customers": "60 customers per day"
        },
        "financial_plan": {
            "counterfactual_guidance": "Funding structure comprises LKR 2,500,000 recorded available capital and LKR 1,000,000 in external loan financing."
        },
        "action_roadmap": {
            "phase_1_immediate_0_to_3_months": [
                "Finalize expansion site agreements, space layout, and legal compliance for FreshMart Grocery.",
                "Configure online ordering and delivery expansion for FreshMart Grocery in Colombo.",
                "Reallocate core senior staff to oversee expansion preparation."
            ],
            "phase_2_stabilization_3_to_12_months": [
                "Complete interior fit-out and equipment installation in Colombo.",
                "Conduct pilot test runs and soft-launch to existing loyal customer database.",
                "Monitor additional monthly operating burn strictly against LKR 21,250.00."
            ],
            "phase_3_growth_1_year_plus": [
                "Execute full commercial expansion launch targeted at 69 additional daily patrons.",
                "Conduct comprehensive payback review against initial investment."
            ]
        }
    }
}

trendy_profile = {
    "metadata": {
        "record_id": "b6be5bde-cf2b-433c-bf98-6eba350d261e",
        "created_at": "2026-10-14T10:00:00Z"
    },
    "business_input": {
        "business_name": "Trendy Style Clothing Shop",
        "business_category": "Clothing / Garment",
        "business_stage": "New Startup",
        "district": "Colombo",
        "available_capital_lkr": 600000.0,
        "monthly_budget_lkr": 38250.0,
        "expected_customers_per_day": 10,
        "expected_price_lkr": 500.0,
        "entrepreneur_experience_years": 2,
        "available_staff_count": 2,
        "competition_level": "Moderate",
        "has_existing_loans": True,
        "has_equipment": True,
        "has_supplier_contacts": True
    },
    "feasibility_analysis": {
        "predicted_label": "Conditionally Feasible",
        "confidence_score": 0.47,
        "probabilities": {
            "Feasible": 0.315,
            "Conditionally Feasible": 0.47,
            "Infeasible": 0.215
        }
    },
    "explainability": {
        "positive_drivers": [
            "Available Capital (Lkr) (LKR 600,000)",
            "Business Stage (New Startup)",
            "Expected Product Price (Lkr) (LKR 500)"
        ],
        "negative_drivers": [
            "Available Equipment Score (1-5) (4 / 5)",
            "Available Staff Count (2 Staff)",
            "Business Category (Clothing/ Garment)"
        ]
    },
    "strategic_recommendations": {
        "candidate_strategies": [
            {
                "strategy_name": "Storefront + Home Delivery Model",
                "focus": "In-Store Sales with Phone & WhatsApp Orders",
                "impact": "Broader Reach via Storefront & Home Delivery",
                "target_capital": 450000,
                "monthly_budget": 38250,
                "target_footfall": 11,
                "topsis_score": 0.6357
            }
        ],
        "topsis_ranking": {
            "top_recommended_strategy": "Storefront + Home Delivery Model",
            "top_topsis_score": "0.6357",
            "ranked_strategies": [
                {
                    "strategy_name": "Storefront + Home Delivery Model",
                    "focus": "In-Store Sales with Phone & WhatsApp Orders",
                    "topsis_score": 0.6357
                }
            ],
            "evaluation_criteria": [
                {"criterion": "Financial Viability", "weight": "25%"},
                {"criterion": "Implementation Feasibility", "weight": "20%"}
            ]
        }
    },
    "scenario_analysis": {
        "what_if_simulations": [
            {"scenario": "+30% Customer Footfall Boost", "shift": "+1.0% Feasible"}
        ]
    },
    "personalized_business_plan": {
        "executive_overview": {
            "business_summary": (
                "Trendy Style Clothing Shop is a proposed new startup venture within the Clothing / Garment sector, "
                "planned for launch in Colombo, Western Province, Sri Lanka. The enterprise is structured under a Direct Retail / Service model, "
                "providing commercial offerings tailored to the local market catchment. As a new venture in its initial setup phase, "
                "commercial priorities center on establishing initial operations, building customer awareness, and maintaining disciplined "
                "operating expenditure. Based on the operational details provided: I plan to establish a small clothing shop offering "
                "fashionable and affordable clothing for men, women, and children. The shop will sell T-shirts, trousers, dresses, "
                "casual wear, office wear, and seasonal clothing. My target customers include students, working professionals, families, "
                "and budget-conscious shoppers in the surrounding residential area. I plan to purchase clothing from reliable local "
                "wholesalers and suppliers to provide different designs, sizes, and price ranges. I will attract customers through competitive "
                "pricing, seasonal discounts, social media promotions, and friendly customer service. My main competitive advantage will be "
                "offering trendy clothing at affordable prices in a convenient location. Initially, I expect to invest approximately LKR 600,000 "
                "in inventory, shop setup, display racks, and other startup expenses. My goal is to build a loyal customer base, manage stock "
                "efficiently, and gradually expand the business according to customer demand."
            )
        },
        "operational_plan": {
            "staffing_requirements": "The enterprise currently deploys 2 active staff member(s) against an estimated requirement of 2, representing a Balanced staffing allocation.",
            "equipment_readiness": "Available equipment readiness is rated at 4/5, currently satisfying operational requirements."
        },
        "marketing_plan": {
            "demand_score": "Recorded customer demand score is 56/100.",
            "target_daily_customers": "10 customers per day"
        },
        "financial_plan": {
            "counterfactual_guidance": "The business financing structure comprises LKR 600,000 in recorded available capital and LKR 500,000 in external loan financing."
        },
        "action_roadmap": {
            "phase_1_immediate_0_to_3_months": [
                "Establish initial operational workspace and layout for Trendy Style Clothing Shop.",
                "Configure storefront and home delivery coordination for Trendy Style Clothing Shop in Colombo.",
                "Confirm commercial supplier agreements and inventory delivery terms."
            ],
            "phase_2_stabilization_3_to_12_months": [
                "Launch targeted customer outreach to attain 11 daily patrons.",
                "Monitor monthly operating burn closely against LKR 38,250.00 budget."
            ],
            "phase_3_growth_1_year_plus": [
                "Conduct quarterly financial review and audit simplified budget coverage.",
                "Evaluate whether commercial expansion or channel extension is justified."
            ]
        }
    }
}

def generate_sample_pdf(profile_dict, filename):
    report_data = BusinessPlanReportBuilder.build_report_data(profile_dict)
    pdf_bytes = BusinessPlanPDFGenerator.generate_pdf(report_data)
    file_path = OUTPUT_DIR / filename
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Generated {file_path} ({len(pdf_bytes)} bytes)")

if __name__ == "__main__":
    generate_sample_pdf(freshmart_profile, "FreshMart_Grocery_Business_Plan.pdf")
    generate_sample_pdf(trendy_profile, "Trendy_Style_Clothing_Shop_Business_Plan.pdf")
    print("Sample PDFs successfully created!")
