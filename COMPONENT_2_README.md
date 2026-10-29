# 🏛️ Component 2: AI-Based Legal, Regulatory and Ethical Requirement Identification & Registration Guidance

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6F61?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-Academic%20Research-blueviolet?style=for-the-badge)](LICENSE)

> **Part of the AI-Driven Business Lifecycle Decision Support System (Research Project: J26-IT-362)**  
> **Author & Component Lead:** Dhananji Pallegedara  
> **Repository Branch:** [`Component_2_Dhananji`](https://github.com/kumodyathamadi/J26-IT-362/tree/Component_2_Dhananji)

---

## 🌟 Executive Overview

Small and Medium Enterprises (SMEs) represent over 75% of Sri Lankan businesses, yet over 40% fail or incur severe statutory penalties due to navigating complex, fragmented, and localized regulatory frameworks. Traditional legal consultation is prohibitively expensive, and general-purpose large language models (LLMs) suffer from dangerous **legal hallucinations** and a lack of municipal jurisdiction awareness.

**Component 2** addresses this critical research gap by delivering an **intelligent, deterministic, and evidence-grounded decision support ecosystem**. It automatically extracts business parameters, evaluates statutory obligations under Sri Lankan law through a rigorous **three-valued logic engine**, conducts semantic vector retrieval against authentic gazettes and acts, and interactively guides entrepreneurs through an **end-to-end statutory business registration roadmap** with automated government application generation.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       CORE RESEARCH VALUE                                      │
├───────────────────────────────┬─────────────────────────────────┬───────────────────────────────┤
│    🛡️ Zero Hallucinations    │    📍 Jurisdiction-Aware       │   📝 Automated Compliance     │
│ Deterministic 3-valued engine │ Multi-tier Sri Lankan statutory │ Instant filled official PDFs  │
│ grounds rules strictly in law │ mapping (National, WP & CMC)    │ & compliance dossiers         │
└───────────────────────────────┴─────────────────────────────────┴───────────────────────────────┘
```

---

## 🚀 Key Features & Capabilities

### 1. ⚖️ Deterministic 3-Valued Applicability Engine
* **Logic-Driven Evaluation:** Classifies obligations as `APPLICABLE` (Mandatory), `CONDITIONAL` / `UNKNOWN` (Needs Verification), or `NOT_APPLICABLE`.
* **Honest Handling of Missing Facts:** In accordance with legal jurisprudence, unconfirmed facts are never assumed false. The engine detects missing information and dynamically triggers interactive follow-up questions.
* **LLM Guardrails:** Natural language models are restricted to phrasing contextual explanations; they **never** decide legal applicability.

### 2. 📄 Multi-Modal Business Profile Extraction
* **Smart PDF Ingestion:** Upload full feasibility reports or business plans (e.g., outputs from Component 1) to extract structured entity parameters using `pdfplumber` / `pypdf`.
* **Human-in-the-Loop Review:** Interactive editable form view allows entrepreneurs to refine sector, employee counts, revenue, address, and physical operational factors before execution.
* **Pre-Loaded SME Presets:** Rapid testing with localized sample business cases (Artisan Bakery, Textile Boutique, Grocery Store, IT Consultancy).

### 3. 🔍 Localized Legal RAG & Vector Evidence Grounding
* **Semantic Vector Retrieval:** Uses `SentenceTransformers` (`all-MiniLM-L6-v2`) and local `ChromaDB` embeddings across official Sri Lankan legislative sources.
* **Direct Statutory Citations:** Every obligation result includes the official Act number, gazette notification, governing authority, section/paragraph quote, and direct PDF download links.
* **Graceful Lexical Fallback:** Disclosed BM25/keyword retrieval fallback ensures operational continuity in air-gapped or vector-constrained deployments.

### 4. 🗺️ 5-Stage Interactive Business Registration Roadmap
Guides founders step-by-step through Sri Lanka's municipal and provincial registration procedure:
* **Stage 1: Name Clearance & Reservation** – Provincial Registrar & ROC compliance.
* **Stage 2: GN & Property Inspection** – Grama Niladhari residence certificate & commercial deed/lease review.
* **Stage 3: Business Name Registration (Form 1)** – Western Province Business Names Statute No. 04 of 2011.
* **Stage 4: Local Authority Trade License & PHI Clearances** – CMC trade taxes, Public Health Inspector food hygiene certifications, and Fire Department NOC.
* **Stage 5: Tax & Social Security Registrations** – Inland Revenue Department (RAMIS TIN) and mandatory EPF/ETF Form D employer enrollment.

### 5. 🖨️ Automated Statutory Form & Dossier Generation
* **Direct PDF Generation:** Instantly populates and exports authentic Sri Lankan administrative forms (e.g., Western Province Form 1 Application).
* **Comprehensive Audit Dossier:** Generates a downloadable, multi-page **Compliance Dossier PDF** containing executive compliance ratings, statutory checklists, authority routing, and evidentiary statutory excerpts.

### 6. 🌐 Bilingual & Culturally Adaptive Interface
* Fully localized support for **English** and **Sinhala (සිංහල)**.
* Adaptive terminology translation tailored to Sri Lankan administrative terms (Grama Niladhari, Divisional Secretariat, Pradeshiya Sabha, Municipal Council).

---

## 🏛️ Grounded Legal & Regulatory Corpus

Component 2 evaluates compliance against Sri Lankan statutory frameworks cataloged in `data/compliance/source_register.csv`:

| Statutory Authority | Document / Act | Focus Area |
| :--- | :--- | :--- |
| **Western Provincial Council** | *Business Names Statute No. 04 of 2011* | Sole Proprietorship & Partnership Registration, Form 1 |
| **Department of Registrar of Companies** | *Companies Act No. 07 of 2007* | Private Limited Company Incorporation & Articles |
| **Ministry of Health / PHI** | *Food Act No. 26 of 1980 & Regulations* | Food premises sanitation, food handling, storage & labeling |
| **Colombo Municipal Council (CMC)** | *Municipal Councils Ordinance (Cap. 252)* | Annual Trade Licenses, dangerous/offensive trade permits |
| **Inland Revenue Department (IRD)** | *Inland Revenue Act No. 24 of 2017* | RAMIS Taxpayer Identification Number (TIN) mandatory enrollment |
| **Department of Labour & CBSL** | *EPF Act No. 15 of 1958 & ETF Act No. 46 of 1980* | Mandatory retirement fund contributions (12% + 8% & 3%) |
| **Central Environmental Authority (CEA)** | *National Environmental Act No. 47 of 1980* | Environmental Protection Licenses (EPL) & waste discharge |

---

## 🏗️ System Architecture

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                             FRONTEND (React 18)                             │
 │  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
 │  │  PDF Plan Ingestion │  │ Editable Profile UI │  │ 5-Stage Roadmap UI  │  │
 │  └──────────┬──────────┘  └──────────┬──────────┘  └──────────▲──────────┘  │
 └─────────────┼────────────────────────┼────────────────────────┼─────────────┘
               │ Upload                 │ Submit Profile         │ Guidance
 ┌─────────────▼────────────────────────▼────────────────────────┴─────────────┐
 │                        BACKEND API (FastAPI Router)                         │
 │                                                                             │
 │  1. Profile Canonicalization & Normalization (`profile.py`)                 │
 │     • Normalizes aliases, employee ranges, capital, and missing facts       │
 │                                                                             │
 │  2. Deterministic Rule Evaluator (`engine.py`)                              │
 │     • Evaluates `obligations.yaml` with 3-valued boolean logic              │
 │     • Zero-hallucination applicability scoring                              │
 │                                                                             │
 │  3. Hybrid RAG & Vector Evidence Matcher (`retrieval.py`)                   │
 │     • ChromaDB vector queries with SentenceTransformers embeddings          │
 │     • Disclosed lexical fallback for resilient execution                    │
 │                                                                             │
 │  4. Action Roadmap & Stage Planner (`action_predictor.py`)                 │
 │     • Maps active obligations into a 5-stage sequential workflow            │
 │                                                                             │
 │  5. Statutory PDF Engine (`stage_form_generator.py` & `dossier_generator.py`)│
 │     • Populates official WP Form 1 & generates full Audit Dossiers          │
 └─────────────────────────────────────────────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
 ┌──────────────────────────┐                          ┌──────────────────────┐
 │  Data & Source Register  │                          │ Persistence & Audit  │
 │  • `source_register.csv` │                          │ • SQLite / Postgres  │
 │  • `obligations.yaml`    │                          │ • Evaluation Records │
 │  • Ingested PDFs / TXT   │                          │ • Anonymized Logs    │
 └──────────────────────────┘                          └──────────────────────┘
```

---

## 📂 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── component2_routes.py         # Primary Component 2 REST API endpoints
│   │   │   └── compliance_routes.py         # Evaluation and validation endpoints
│   │   └── compliance/
│   │       ├── action_predictor.py          # 5-Stage roadmap planning & prediction
│   │       ├── br_form_generator.py         # Form 1 PDF population engine
│   │       ├── stage_form_generator.py      # Multi-stage statutory form synthesizer
│   │       ├── dossier_generator.py         # Comprehensive audit dossier PDF builder
│   │       ├── engine.py                    # Deterministic 3-valued applicability engine
│   │       ├── guidance.py                  # Statutory explanations & document checklists
│   │       ├── legal_sources.py             # PDF/TXT ingestion, hash deduplication
│   │       ├── plan_pdf_extractor.py        # PDF business plan extraction engine
│   │       ├── profile.py                   # Schema validation & canonicalization
│   │       ├── retrieval.py                 # ChromaDB vector RAG & lexical fallback
│   │       ├── rulebook_loader.py           # Cached YAML obligation loader
│   │       ├── schemas.py                   # Pydantic v2 data models
│   │       └── source_registry.py           # Authoritative legal source registry
│   ├── database.py                          # SQLAlchemy engine & session setup
│   ├── models.py                            # ComplianceEvaluationRecord ORM model
│   └── main.py                              # FastAPI application root
├── data/
│   └── compliance/
│       ├── rulebook/
│       │   └── obligations.yaml             # Complete statutory obligations rulebook
│       ├── profiles/                        # Sample request JSON payloads
│       ├── raw/                             # Official source PDF statutes
│       └── source_register.csv              # Cryptographically indexed source registry
├── frontend/
│   └── src/
│       └── components/
│           ├── component2.tsx               # Main Component 2 UI container & stepper
│           ├── BusinessRegistrationView.tsx # Interactive 5-stage registration portal
│           └── compliance.css               # Modern responsive styling & animations
└── tests/
    └── compliance/
        ├── test_component2_api.py           # API integration tests
        ├── test_engine.py                   # 3-valued logic unit tests
        └── test_legal_sources.py            # Ingestion & retrieval verification
```

---

## 🔌 API Reference

Component 2 provides a clean, self-documenting REST API mounted under `/api/v1/component2`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/evaluate` | Evaluates business profile against statutory rulebook and returns classified obligations. |
| `POST` | `/extract-plan-pdf` | Ingests an uploaded business plan PDF and extracts structured entity fields. |
| `POST` | `/extract-plan-base64` | Extracts business attributes from a base64-encoded PDF document. |
| `GET`  | `/sample-plans` | Lists available pre-built sample business plans. |
| `GET`  | `/sample-plans/{id}/download-pdf` | Downloads authentic sample business plan PDFs. |
| `POST` | `/generate-br-form` | Synthesizes an official filled Form 1 Business Registration Application PDF. |
| `POST` | `/generate-stage-form` | Generates official statutory stage application forms (Stages 1 through 5). |
| `POST` | `/download-compliance-dossier` | Generates a complete executive compliance audit dossier PDF. |
| `GET`  | `/legal-documents/{query}` | Direct statutory download of official Sri Lankan Acts, Gazettes, and By-laws. |
| `GET`  | `/sources` | Returns metadata inventory of all verified legal sources. |
| `GET`  | `/sources/{id}/evidence` | Returns extracted paragraphs and evidence quotes for an individual legal source. |

---

## 🛠️ Installation & Setup

### Prerequisites
* **Python:** 3.10, 3.11, or 3.14
* **Node.js:** v18.0 or higher
* **Package Manager:** `npm` or `pnpm`

### 1. Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server on port 8000
uvicorn backend.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install packages
npm install

# Start the Vite development server
npm run dev
```
Open your browser at: `http://localhost:5173`

### 3. Running Unit & Integration Tests
```bash
# Run the complete compliance test suite
pytest tests/compliance/ -v
```

---

## 🔄 Lifecycle Integration

Component 2 is an essential pillar in the broader **AI-Driven Business Lifecycle Decision Support System**:

```text
 ┌──────────────────────┐      Structured Profile      ┌──────────────────────┐
 │     Component 1      ├─────────────────────────────►│     Component 2      │
 │ Business Feasibility │                              │  Legal, Regulatory   │
 │ & Strategy Selection │◄─────────────────────────────┤ & Ethical Compliance │
 └──────────────────────┘      Approved Structure      └──────────┬───────────┘
                                                                  │
                                                Compliance Status │ & Entity Type
                                                                  ▼
 ┌──────────────────────┐      Risk Signals & Growth   ┌──────────────────────┐
 │     Component 4      │◄─────────────────────────────┤     Component 3      │
 │ Business Scaling &   │                              │ Financial Monitoring │
 │ Operational Risk     │                              │   & Fraud Detection  │
 └──────────────────────┘                              └──────────────────────┘
```

* **Inputs from Component 1:** Consumes the feasibility report, proposed business sector, initial capital, headcount, and operational plan.
* **Outputs to Component 3 & 4:** Supplies the verified legal structure, required trade licenses, and statutory tax parameters needed for accurate financial threshold monitoring and operational risk modeling.

---

## 👩‍💻 Research Lead & Contact

* **Lead Researcher:** Dhananji Pallegedara
* **Component:** Component 2 – *AI-Based Legal, Regulatory and Ethical Requirement Identification & Registration Guidance*
* **Specialization:** Information Technology / Software Engineering
* **Project Repository:** [kumodyathamadi/J26-IT-362](https://github.com/kumodyathamadi/J26-IT-362)
* **Branch:** [`Component_2_Dhananji`](https://github.com/kumodyathamadi/J26-IT-362/tree/Component_2_Dhananji)

---

<p align="center">
  <i>Developed with dedication for the advancement and statutory empowerment of Sri Lankan Small & Medium Enterprises (SMEs).</i>
</p>
