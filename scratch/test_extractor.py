import sys
from pathlib import Path

# Add project root to path
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.app.compliance.plan_pdf_extractor import extract_business_profile_from_text

sample_freshmart_text = """
SME360 AI
STRATEGIC BUSINESS GROWTH &
EXPANSION PLAN
AI-Driven Business Growth, Expansion Feasibility & Investment Planning
Prepared For: FreshMart Grocery
Industry Category: Grocery / Mini-Mart | Business Stage: Existing Business
Operating Location: Colombo, Western Province, Sri Lanka
Prepared Date: October 15, 2026
Decision System Reference: 011bbccd-b633-401c-8b3b-b89397b02520

SECTION 01 — ENTERPRISE BASELINE & EXPANSION SCOPE
1.1 Business Overview
FreshMart Grocery is an established enterprise operating within the Grocery / Mini-Mart sector, located in Colombo, Western Province, Sri
Lanka. Operating under a Direct Retail / Service business model, the enterprise aims to execute strategic growth and operational
refinement.
Based on the operational details provided: The main objective of this expansion is to increase sales, extend the business's geographical
coverage, strengthen its market presence, and establish a foundation for future growth. The new branch will operate under the existing
FreshMart Grocery brand and follow similar service standards, product-quality requirements, and pricing strategies as the original store. The
owner also intends to improve customer convenience by offering a wider selection of essential products, maintaining reliable stock
availability, and introducing WhatsApp-based ordering and local delivery services where practical.

1.2 Business Concept & Objectives
Strategic plan for a proposed grocery / mini-mart in Colombo.
• Primary Commercial Offerings: Commercial offerings within Grocery / Mini-Mart
• Target Customer Profile: Consumers and households in Colombo
• Foundational Objectives: Establish a sustainable Grocery / Mini-Mart enterprise in Colombo.

SECTION 02 — AI FEASIBILITY & KEY INSIGHTS
Available Capital (Lkr) (LKR 2,500,000)
Available Staff Count (1 Staff)
Requested Loan Amount (Lkr) (LKR 1,000,000)

SECTION 03 — STRATEGIC RECOMMENDATIONS & TOPSIS RANKING
ACTIVE OPERATING STRATEGY: Online Ordering & Delivery Expansion (Matches AI Rank #1)
"""

sample_trendy_text = """
SME360 AI
STRATEGIC BUSINESS PLAN
A Comprehensive Feasibility, Strategic Direction & Implementation Blueprint
Prepared For: Trendy Style Clothing Shop
Industry Category: Clothing / Garment | Business Stage: New Startup
Operating Location: Colombo, Western Province, Sri Lanka
Prepared Date: October 14, 2026
Decision System Reference: b6be5bde-cf2b-433c-bf98-6eba350d261e

SECTION 01 — BUSINESS & MARKET OVERVIEW
1.1 Business Overview
Trendy Style Clothing Shop is a proposed new startup venture within the Clothing / Garment sector, planned for launch in Colombo,
Western Province, Sri Lanka. The enterprise is structured under a Direct Retail / Service model, providing commercial offerings tailored to
the local market catchment.
Based on the operational details provided: I plan to establish a small clothing shop offering fashionable and affordable clothing for men,
women, and children. The shop will sell T-shirts, trousers, dresses, casual wear, office wear, and seasonal clothing. My target customers
include students, working professionals, families, and budget-conscious shoppers in the surrounding residential area.

SECTION 02 — AI FEASIBILITY & KEY INSIGHTS
Available Capital (Lkr) (LKR 600,000)
Available Staff Count (2 Staff)

SECTION 03 — STRATEGIC RECOMMENDATIONS & TOPSIS RANKING
ACTIVE OPERATING STRATEGY: Storefront + Home Delivery Model (Matches AI Rank #1)
"""

res1 = extract_business_profile_from_text(sample_freshmart_text, "FreshMart_Grocery_Business_Plan.pdf")
print("=== FRESHMART RESULT ===")
for k, v in res1["profile"].items():
    print(f"  {k}: {v}")

res2 = extract_business_profile_from_text(sample_trendy_text, "Trendy_Style_Clothing_Shop_Business_Plan.pdf")
print("\n=== TRENDY STYLE RESULT ===")
for k, v in res2["profile"].items():
    print(f"  {k}: {v}")
