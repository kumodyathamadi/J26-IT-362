# AI-Driven Business Lifecycle Decision Support System

An AI-powered decision support system designed to assist **Small and Medium Enterprises (SMEs)** throughout their business lifecycle — from business initiation and feasibility assessment to regulatory compliance, financial monitoring, risk management, and sustainable growth.

---

## 📌 Project Overview

Small and Medium Enterprises (SMEs) face numerous challenges throughout their business lifecycle, including:

* Business feasibility assessment
* Business strategy selection
* Legal and regulatory compliance
* Financial management
* Fraud and anomaly detection
* Operational risk management
* Business growth and scaling decisions

To address these challenges, this research proposes an **AI-Driven Business Lifecycle Decision Support System** consisting of four interconnected AI-based components.

The system combines **Machine Learning (ML), Artificial Intelligence (AI), Retrieval-Augmented Generation (RAG), Explainable AI (XAI), Multi-Criteria Decision Making (MCDM), Graph Neural Networks (GNNs), and adaptive analysis** to provide personalized, data-driven decision support.

The system supports both **new businesses and existing SMEs**, providing recommendations that evolve as business conditions change.

---

## 🎯 Research Objective

The primary objective of this research is to develop an intelligent decision-support ecosystem that can assist SMEs in making informed decisions across their complete business lifecycle.

The proposed system aims to:

* Evaluate the feasibility of new business proposals.
* Support existing businesses in making growth and expansion decisions.
* Recommend suitable business strategies based on business-specific constraints.
* Identify applicable legal, licensing, and regulatory requirements.
* Monitor financial performance and identify unusual financial activities.
* Predict business and operational risks.
* Support sustainable and data-driven business growth.
* Dynamically update recommendations when business conditions change.

---

# 🏗️ System Architecture

The proposed system consists of four interconnected components:

```text
                    ┌───────────────────────────────┐
                    │        SME Business Data       │
                    │  Profile • Finance • Location  │
                    │  Resources • Operations • etc. │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
          ┌──────────────────────────────────────────────┐
          │ AI-Driven Business Lifecycle Decision System │
          └──────────────────────┬───────────────────────┘
                                 │
       ┌─────────────────────────┼─────────────────────────┐
       │                         │                         │
       ▼                         ▼                         ▼
┌───────────────┐       ┌────────────────┐       ┌────────────────┐
│ Component 1   │       │ Component 2    │       │ Component 3    │
│               │       │                │       │                │
│ Business      │       │ Local          │       │ Financial &    │
│ Feasibility   │       │ Compliance     │       │ Fraud          │
│ & Strategy    │       │                │       │ Monitoring     │
└───────┬───────┘       └───────┬────────┘       └───────┬────────┘
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                                │
                                ▼
                     ┌────────────────────┐
                     │ Component 4        │
                     │                    │
                     │ Risk & Scaling     │
                     │ GNN-Based Analysis │
                     └─────────┬──────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │ Dynamic Recalibration      │
                │                            │
                │ Updated Recommendations    │
                │ Compliance • Risk • Growth │
                └────────────────────────────┘
```

---

# 🧩 System Components

## Component 1 — AI-Based Business Feasibility Analysis & Personalized Business Plan Recommendation

**Objective:**
Evaluate whether a proposed business or business expansion is feasible and recommend suitable strategies based on business-specific conditions.

### Key Functions

* Business feasibility prediction
* New business feasibility assessment
* Existing SME growth/expansion assessment
* Business strategy recommendation
* Personalized business plan recommendation
* Explainable AI-based decision support
* What-If / Counterfactual analysis
* Multi-criteria strategy ranking

### Key Inputs

The component considers factors such as:

* Available capital
* Loan requirements
* Monthly budget
* Initial investment
* Business category
* Business location
* Market demand
* Competition
* Entrepreneur experience
* Available staff
* Required staff
* Available equipment
* Required equipment
* Supplier availability
* Location suitability
* Proposed business action

### AI / Decision-Making Techniques

* Machine Learning
* Explainable AI (XAI)
* SHAP-based explanations
* Multi-Criteria Decision Making (MCDM)
* TOPSIS
* What-If / Counterfactual Analysis
* Rule-based constraint validation

### Output

```text
Business Feasibility
        ↓
Feasibility Explanation
        ↓
Alternative Strategies
        ↓
TOPSIS Strategy Ranking
        ↓
What-If / Scenario Analysis
        ↓
Personalized Business Plan
        ↓
Structured Business Profile
```

---

# Component 2 — AI-Based Business Registration & Regulatory Compliance

**Objective:**
Assist SMEs in identifying applicable legal, registration, licensing, and regulatory requirements based on their business characteristics and location.

### Key Functions

* Business registration guidance
* License identification
* Regulatory requirement identification
* Business-specific compliance recommendations
* Localized regulatory information retrieval
* Registration process guidance
* Compliance requirement updates

### Key Technology

**Retrieval-Augmented Generation (RAG)** and deterministic rule engine logic are used to evaluate and retrieve relevant information from localized regulatory and legal knowledge sources.

### Output

```text
Business Information
        ↓
Requirement Identification
        ↓
Relevant Regulations
        ↓
Required Registrations
        ↓
Licenses & Permits
        ↓
Compliance Guidance
```

---

### Component 2 Implementation & Developer Quickstart

The full implementation guide is available at [documentation/Component_2_Implementation_Guide.md](documentation/Component_2_Implementation_Guide.md).

#### Overview & Core Novelty
Component 2 provides **deterministic, source-grounded regulatory compliance analysis** for Sri Lankan SMEs (initial scope: food businesses in Colombo District — bakeries, cake shops, sweets shops, restaurants).

* **Source register** — every cited law is in `data/compliance/source_register.csv`.
* **Obligation rulebook** — YAML schema in `data/compliance/rulebook/obligations.yaml`.
* **Three-valued applicability engine** — returns `applicable` / `conditional` / `unknown` / `not_applicable`; missing facts are never assumed false.
* **Metadata-aware evidence** — every result is grounded in a registered source + quote.
* **LLM constraint** — the LLM may only phrase results; it never decides applicability.

#### Directory Structure
```text
backend/
  main.py                          # FastAPI entry point
  requirements.txt                 # Python dependencies
  app/
    api/
      compliance_routes.py         # POST /compliance/analyze and GET endpoints
      component2_routes.py         # Legacy mock endpoint (kept for backward compat)
    compliance/
      schemas.py                   # Pydantic models: BusinessProfile, ObligationRule, etc.
      engine.py                    # Deterministic three-valued applicability engine
      rulebook_loader.py           # YAML loader (cached)
      source_registry.py           # CSV reader (cached)
      component1_mapper.py         # Component 1 → Component 2 field mapper

data/compliance/
  source_register.csv              # Authoritative source document registry
  raw/                             # Original PDFs (never edited)
  processed/                       # Extracted text JSON (one file per source_id)
  rulebook/
    obligations.yaml               # Obligation definitions with three-valued applies_if

scripts/compliance/
  register_source.py               # Register a new source document
  validate_rulebook.py             # Validate rulebook ↔ source register consistency

tests/compliance/
  test_engine.py                   # Pytest: applicable / not_applicable / unknown / conditional

frontend/src/components/
  component2.tsx                   # React UI: profile form + grouped results + evidence panel
```

#### How to Run — Backend
```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start the API server (from repo root)
python -m uvicorn backend.main:app --reload --port 8000
```

#### How to Run — Tests
```bash
# From repo root
pytest tests/compliance/ -v
```

#### How to Run — Frontend
```bash
cd frontend
npm install
npm run dev
```

#### How to Register a New Source Document
```bash
python scripts/compliance/register_source.py \
  --source-id SL-NEW-ACT-2024 \
  --authority "Ministry of Trade" \
  --title "New Trade Act 2024" \
  --doc-type act \
  --jurisdiction "Sri Lanka (National)" \
  --effective-date 2024-01-01 \
  --file data/compliance/raw/new_trade_act_2024.pdf
```

#### How to Validate the Rulebook
```bash
python scripts/compliance/validate_rulebook.py
```

#### Design Principles
| Principle | Implementation |
|---|---|
| LLM never decides applicability | All logic in `engine.py` is pure Python; LLM is not called |
| Three-valued logic | `None` → UNKNOWN; never coerced to False |
| Source-grounded output | Every evidence chunk has `source_id`, `page`, `url`, `quote` |
| No personal data | `BusinessProfile` has no NIC, name, or personal identifiers |
| Reviewer workflow | `reviewer_status: draft` marks unverified quotes; validator enforces verbatim match |


# Component 3 — AI-Based Financial Management & Fraud Monitoring

**Objective:**
Assist SMEs in monitoring financial activities, analyzing business performance, and identifying unusual financial patterns.

### Key Functions

* Financial activity monitoring
* Business performance analysis
* Revenue and expense analysis
* Financial trend analysis
* Transaction monitoring
* Anomaly detection
* Potential fraud detection
* Financial alerts

### AI Techniques

* Machine Learning
* Anomaly Detection
* Pattern Recognition
* Financial Data Analysis
* AI-based monitoring

### Output

```text
Financial Data
      ↓
Financial Performance Analysis
      ↓
Transaction Monitoring
      ↓
Anomaly Detection
      ↓
Potential Fraud Identification
      ↓
Financial Insights & Alerts
```

---

# Component 4 — AI-Based Business Monitoring, Growth Prediction & AI Advisory

**Objective:**
Identify business and operational risks while supporting safe and sustainable business growth.

### Key Functions

* Business risk prediction
* Operational risk analysis
* Relationship-based business analysis
* Growth prediction
* Scaling recommendations
* Risk mitigation recommendations
* AI-based business advisory

### Key Technology

The component utilizes **Graph Neural Networks (GNNs)** to model relationships between business entities, resources, suppliers, customers, transactions, operations, and other relevant business factors.

### Output

```text
Business Relationships
        ↓
Graph Representation
        ↓
GNN-Based Analysis
        ↓
Risk Identification
        ↓
Growth Prediction
        ↓
Risk Mitigation
        ↓
Safe Scaling Recommendations
```

---

# 🔄 Dynamic Recalibration

A key feature of the proposed system is **Dynamic Recalibration**.

Business conditions are not static. Changes in one part of a business can affect decisions across the entire business lifecycle.

For example:

```text
Change in Business Condition
            ↓
      Updated Business Data
            ↓
    ┌───────┼────────┐
    ↓       ↓        ↓
Feasibility Compliance Risk
Update      Update    Update
    │       │        │
    └───────┼────────┘
            ↓
    Updated Recommendations
```

Changes such as:

* Increased operating costs
* Reduced available capital
* New business location
* Changes in market demand
* New regulatory requirements
* Changes in supplier availability
* Changes in financial performance
* Changes in business relationships

can trigger updated analysis and recommendations.

This allows the system to continuously adapt to changing SME conditions instead of treating the original business assessment as a static decision.

---

# 🧠 Core AI Technologies

| Technology            | Purpose                                              |
| --------------------- | ---------------------------------------------------- |
| Machine Learning      | Business feasibility and predictive analysis         |
| Explainable AI (XAI)  | Explain why predictions are produced                 |
| SHAP                  | Feature-level explanation of ML predictions          |
| TOPSIS / MCDM         | Rank alternative business strategies                 |
| What-If Analysis      | Evaluate changes in business conditions              |
| RAG                   | Retrieve localized regulatory and business knowledge |
| Anomaly Detection     | Identify unusual financial activities                |
| Graph Neural Networks | Model business relationships and risks               |
| Rule-Based Validation | Validate constraints and requirements                |
| Adaptive Analysis     | Recalculate recommendations as conditions change     |

---

# 🔗 End-to-End Business Lifecycle

The proposed system follows the SME lifecycle from initiation to growth:

```text
┌───────────────────────┐
│ Business Idea / SME   │
│ Existing Business    │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Component 1           │
│ Feasibility &         │
│ Strategy              │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Component 2           │
│ Registration &        │
│ Compliance            │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Business Operation    │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Component 3           │
│ Financial Monitoring  │
│ & Fraud Detection     │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Component 4           │
│ Risk, Growth &        │
│ AI Advisory           │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Dynamic Recalibration │
└───────────┬───────────┘
            │
            └──────────────► Continuous Business Decision Support
```

---

# 🎯 Target Users

The system is primarily designed for:

* New entrepreneurs
* Existing SME owners
* Small business managers
* Business consultants
* SME support organizations
* Business development stakeholders

---

# 🇱🇰 Localized SME Focus

The proposed research is designed with a particular focus on the **Sri Lankan SME context**.

The system can incorporate localized:

* Business conditions
* Market information
* Business locations
* Regulatory requirements
* Licensing requirements
* Financial considerations
* SME-specific constraints
* Business growth conditions

This allows recommendations to be generated according to the context in which Sri Lankan SMEs operate.

---

# 🔬 Research Contribution

The proposed research integrates multiple AI and decision-support techniques into a unified SME lifecycle framework.

The main research contributions include:

### 1. AI-Based Feasibility Decision Support

Predicts business feasibility using multiple business, financial, operational, resource, and market factors.

### 2. Personalized Strategy Recommendation

Instead of only predicting whether a business is feasible, the system evaluates alternative strategies and provides personalized recommendations.

### 3. Explainable Decision Support

Uses explainability techniques to show the factors influencing feasibility predictions and recommendations.

### 4. Assumption-Aware What-If Analysis

Allows users to explore how changes in business conditions may affect feasibility and strategy recommendations.

### 5. Localized Regulatory Intelligence

Uses RAG to identify business-specific regulatory and registration requirements.

### 6. Integrated Financial Monitoring

Supports ongoing financial monitoring and anomaly detection after business initiation.

### 7. Relationship-Based Risk Analysis

Uses GNN-based analysis to model complex relationships affecting business risk and growth.

### 8. Dynamic Lifecycle Recalibration

Enables recommendations and assessments to adapt when business conditions change.

---

# 🏛️ Proposed System Structure

```text
AI-Driven Business Lifecycle Decision Support System
│
├── Component 1
│   ├── Feasibility Prediction
│   ├── Explainable AI
│   ├── Strategy Recommendation
│   ├── TOPSIS
│   ├── What-If Analysis
│   └── Personalized Business Plan
│
├── Component 2
│   ├── Business Registration
│   ├── Regulatory Requirement Identification
│   ├── Licensing Guidance
│   └── Localized RAG
│
├── Component 3
│   ├── Financial Monitoring
│   ├── Performance Analysis
│   ├── Anomaly Detection
│   └── Fraud Detection
│
├── Component 4
│   ├── Business Risk Prediction
│   ├── GNN Analysis
│   ├── Growth Prediction
│   └── AI Advisory
│
└── Dynamic Recalibration
    ├── Updated Business Data
    ├── Updated Recommendations
    ├── Updated Compliance
    └── Updated Risk Assessment
```

---

# 🚀 Expected Outcome

The final system aims to provide SMEs with an integrated AI-based decision-support environment that can assist with:

**Business Idea → Feasibility → Strategy → Registration → Compliance → Financial Monitoring → Risk Management → Growth → Continuous Advisory**

Rather than providing isolated recommendations, the proposed system aims to maintain a connected understanding of the business throughout its lifecycle and dynamically adapt recommendations as business conditions evolve.

---

# 📊 Research Scope

The research focuses on developing and evaluating AI-driven decision-support techniques for SME business lifecycle management.

The system combines:

**Predictive AI + Explainable AI + RAG + MCDM + Anomaly Detection + GNN + Adaptive Decision Support**

to create an integrated business intelligence and advisory framework.

---

# 👥 Research Components

| Component   | Research Area                                | Main Technology             |
| ----------- | -------------------------------------------- | --------------------------- |
| Component 1 | Business Feasibility & Personalized Planning | ML + XAI + TOPSIS + What-If |
| Component 2 | Registration & Regulatory Compliance         | RAG + AI                    |
| Component 3 | Financial & Fraud Monitoring                 | ML + Anomaly Detection      |
| Component 4 | Risk Prediction & Business Scaling           | GNN + AI Advisory           |

---

# 📌 Project Status

The system is being developed as a research project consisting of four interconnected components.

Each component is independently developed and evaluated before integration into the overall **AI-Driven Business Lifecycle Decision Support System**.

---

# 📜 License

This project is developed for **academic and research purposes**.

---

# 👨‍💻 Research Project

**AI-Driven Business Lifecycle Decision Support System**

A research initiative focused on applying Artificial Intelligence and advanced decision-support techniques to improve SME business decision-making throughout the business lifecycle.
