# 🏛️ Component 2: AI-Based Legal, Regulatory and Ethical Requirement Identification & Registration Guidance

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.10%20|%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6F61?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
![License](https://img.shields.io/badge/License-Academic%20Research-blueviolet?style=for-the-badge)

> **Part of the AI-Driven Business Lifecycle Decision Support System (Research Project: J26-IT-362)**  
> **Author & Component Lead:** Dhananji Pallegedara  
> **Student ID:** IT23331518  
> **Repository:** [kumodyathamadi/J26-IT-362](https://github.com/kumodyathamadi/J26-IT-362)  
> **Branch:** [`Component_2_Dhananji`](https://github.com/kumodyathamadi/J26-IT-362/tree/Component_2_Dhananji)  

---

## 📑 Table of Contents

1. [Executive Overview](#-executive-overview)
2. [Key Features](#-key-features--capabilities)
3. [Legal & Regulatory Corpus](#-grounded-legal--regulatory-corpus)
4. [System Architecture](#-system-architecture)
5. [Project Structure](#-project-structure)
6. [API Reference](#-api-reference)
7. [Installation & Setup](#-installation--setup)
8. [Configuration](#-configuration)
9. [Evaluation](#-evaluation)
10. [Limitations & Disclaimer](#-limitations--disclaimer)
11. [Lifecycle Integration](#-lifecycle-integration)
12. [Contact](#-research-lead--contact)

---

## 🌟 Executive Overview

Small and Medium Enterprises (SMEs) are a major part of the Sri Lankan economy, yet many struggle to navigate complex, fragmented, and locally varying regulatory requirements, which can lead to delays and statutory penalties. Traditional legal consultation is costly for early-stage founders, and general-purpose large language models (LLMs) can produce **legal hallucinations** and lack awareness of municipal and provincial jurisdiction.

**Component 2** addresses this gap with a **deterministic, evidence-grounded decision support system**. It extracts business parameters, evaluates statutory obligations under Sri Lankan law using a **three-valued logic engine**, retrieves supporting evidence from official Acts and gazettes via semantic search, and guides entrepreneurs through an **end-to-end business registration roadmap** with automated generation of application forms.

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       CORE RESEARCH VALUE                                       │
├───────────────────────────────┬─────────────────────────────────┬───────────────────────────────┤
│    🛡️ Hallucination-Guarded   │    📍 Jurisdiction-Aware        │   📝 Automated Compliance     │
│ Deterministic 3-valued engine │ Multi-tier Sri Lankan statutory │ Pre-filled official forms     │
│ grounds rules strictly in law │ mapping (National, WP & CMC)    │ & compliance dossiers         │
└───────────────────────────────┴─────────────────────────────────┴───────────────────────────────┘
```

---

## 🚀 Key Features & Capabilities

### 1. ⚖️ Deterministic 3-Valued Applicability Engine
* **Logic-driven evaluation:** Classifies obligations as `APPLICABLE` (mandatory), `CONDITIONAL` / `UNKNOWN` (needs verification), or `NOT_APPLICABLE`.
* **Honest handling of missing facts:** Unconfirmed facts are never assumed false. The engine detects missing information and triggers interactive follow-up questions.
* **LLM guardrails:** Language models only phrase contextual explanations; they **never** decide legal applicability.

### 2. 📄 Business Profile Extraction
* **PDF ingestion:** Upload a feasibility report or business plan (e.g., output from Component 1) to extract structured parameters using `pdfplumber` / `pypdf`.
* **Human-in-the-loop review:** An editable form lets entrepreneurs refine sector, employee count, revenue, address, and operational factors before evaluation.
* **Sample presets:** Quick testing with localized SME cases (Artisan Bakery, Textile Boutique, Grocery Store, IT Consultancy).

### 3. 🔍 Localized Legal RAG & Evidence Grounding
* **Semantic retrieval:** Uses `SentenceTransformers` (`all-MiniLM-L6-v2`) and a local `ChromaDB` store over official Sri Lankan legislative sources.
* **Statutory citations:** Each obligation result includes the Act number, gazette notification (where applicable), governing authority, a supporting excerpt, and a link to the source document.
* **Disclosed lexical fallback:** A BM25 / keyword retrieval fallback keeps the system working when the vector store or embedding model is unavailable. The UI indicates when the fallback is used.

### 4. 🗺️ 5-Stage Interactive Business Registration Roadmap
* **Stage 1: Name Clearance & Reservation:** Provincial Registrar and Registrar of Companies requirements.
* **Stage 2: GN & Property Inspection:** Grama Niladhari residence certificate and commercial deed/lease review.
* **Stage 3: Business Name Registration (Form 1):** Western Province Business Names Statute.
* **Stage 4: Local Authority Trade License & Clearances:** CMC trade license, Public Health Inspector food hygiene clearance, and Fire Department clearance.
* **Stage 5: Tax & Social Security Registration:** Inland Revenue Department (RAMIS TIN) and EPF/ETF employer registration.

### 5. 🖨️ Statutory Form & Dossier Generation
* **PDF form generation:** Populates administrative forms (e.g., Western Province Form 1 application) from the confirmed business profile.
* **Compliance dossier:** Generates a downloadable multi-page PDF with an executive summary, statutory checklist, authority routing, and evidentiary excerpts.

### 6. 🌐 Bilingual Interface
* Supports **English** and **Sinhala (සිංහල)**.
* Terminology adapted to Sri Lankan administrative terms (Grama Niladhari, Divisional Secretariat, Pradeshiya Sabha, Municipal Council).

---

## 🏛️ Grounded Legal & Regulatory Corpus

Obligations are evaluated against the sources cataloged in `data/compliance/source_register.csv`:

| Statutory Authority | Document / Act | Focus Area |
| :--- | :--- | :--- |
| **Western Provincial Council** | *Business Names Statute No. 04 of 2011* | Sole proprietorship & partnership registration, Form 1 |
| **Department of Registrar of Companies** | *Companies Act No. 07 of 2007* | Private limited company incorporation |
| **Ministry of Health / PHI** | *Food Act No. 26 of 1980 & Regulations* | Food premises sanitation, handling, storage, labeling |
| **Colombo Municipal Council (CMC)** | *Municipal Councils Ordinance (Cap. 252)* | Annual trade licenses, dangerous/offensive trade permits |
| **Inland Revenue Department (IRD)** | *Inland Revenue Act No. 24 of 2017* | Taxpayer Identification Number (TIN) registration |
| **Department of Labour & EPF/ETF Board** | *EPF Act No. 15 of 1958 & ETF Act No. 46 of 1980* | Employer registration and contributions (EPF 12% employer + 8% employee; ETF 3% employer) |
| **Central Environmental Authority (CEA)** | *National Environmental Act No. 47 of 1980* | Environmental Protection Licence (EPL) |

> Rates and thresholds reflect the sources in the register at the time of ingestion. Always confirm against the latest official publications.

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
 │  1. Profile Canonicalization & Normalization (profile.py)                   │
 │     • Normalizes aliases, employee ranges, capital, and missing facts       │
 │                                                                             │
 │  2. Deterministic Rule Evaluator (engine.py)                                │
 │     • Evaluates obligations.yaml with 3-valued logic                        │
 │     • Rule-based applicability; no LLM involvement                          │
 │                                                                             │
 │  3. Hybrid RAG & Evidence Matcher (retrieval.py)                            │
 │     • ChromaDB vector queries with SentenceTransformers embeddings          │
 │     • Disclosed lexical fallback                                            │
 │                                                                             │
 │  4. Action Roadmap & Stage Planner (action_predictor.py)                    │
 │     • Maps active obligations into a 5-stage workflow                       │
 │                                                                             │
 │  5. PDF Engine (stage_form_generator.py, dossier_generator.py)              │
 │     • Populates WP Form 1 and generates compliance dossiers                 │
 │ └─────────────────────────────────────────────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
 ┌──────────────────────────┐                          ┌──────────────────────┐
 │  Data & Source Register  │                          │ Persistence & Audit  │
 │  • source_register.csv   │                          │ • SQLite / Postgres  │
 │  • obligations.yaml      │                          │ • Evaluation records │
 │  • Ingested PDFs / TXT   │                          │ • Anonymized logs    │
 └──────────────────────────┘                          └──────────────────────┘
```

---

## 📂 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── component2_routes.py         # Component 2 REST endpoints
│   │   │   └── compliance_routes.py         # Evaluation and validation endpoints
│   │   └── compliance/
│   │       ├── action_predictor.py          # 5-stage roadmap planning
│   │       ├── br_form_generator.py         # Form 1 PDF population
│   │       ├── stage_form_generator.py      # Multi-stage form generator
│   │       ├── dossier_generator.py         # Compliance dossier PDF builder
│   │       ├── engine.py                    # Deterministic 3-valued engine
│   │       ├── guidance.py                  # Explanations & document checklists
│   │       ├── legal_sources.py             # PDF/TXT ingestion, hash deduplication
│   │       ├── plan_pdf_extractor.py        # Business plan PDF extraction
│   │       ├── profile.py                   # Schema validation & canonicalization
│   │       ├── retrieval.py                 # ChromaDB RAG & lexical fallback
│   │       ├── rulebook_loader.py           # Cached YAML obligation loader
│   │       ├── schemas.py                   # Pydantic v2 models
│   │       └── source_registry.py           # Legal source registry
│   ├── database.py                          # SQLAlchemy engine & session setup
│   ├── models.py                            # ComplianceEvaluationRecord ORM model
│   └── main.py                              # FastAPI application root
├── data/
│   └── compliance/
│       ├── rulebook/
│       │   └── obligations.yaml             # Statutory obligations rulebook
│       ├── profiles/                        # Sample request JSON payloads
│       ├── raw/                             # Official source PDFs
│       └── source_register.csv              # Source registry with file hashes
├── frontend/
│   └── src/
│       └── components/
│           ├── component2.tsx               # Main UI container & stepper
│           ├── BusinessRegistrationView.tsx # 5-stage registration portal
│           └── compliance.css               # Styling
├── tests/
│   └── compliance/
│       ├── test_component2_api.py           # API integration tests
│       ├── test_engine.py                   # 3-valued logic unit tests
│       └── test_legal_sources.py            # Ingestion & retrieval tests
├── .env.example                             # Environment variable template
├── requirements.txt
└── LICENSE
```

---

## 🔌 API Reference

All endpoints are mounted under `/api/v1/component2`. Interactive docs are available at `/docs` when the server is running.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/evaluate` | Evaluates a business profile against the rulebook and returns classified obligations. |
| `POST` | `/extract-plan-pdf` | Extracts structured business fields from an uploaded plan PDF. |
| `POST` | `/extract-plan-base64` | Extracts business fields from a base64-encoded PDF. |
| `GET`  | `/sample-plans` | Lists available sample business plans. |
| `GET`  | `/sample-plans/{id}/download-pdf` | Downloads a sample business plan PDF. |
| `POST` | `/generate-br-form` | Generates a filled Form 1 business registration application PDF. |
| `POST` | `/generate-stage-form` | Generates statutory stage forms (Stages 1–5). |
| `POST` | `/download-compliance-dossier` | Generates the compliance dossier PDF. |
| `GET`  | `/legal-documents/{query}` | Downloads official Acts, gazettes, and by-laws matching the query. |
| `GET`  | `/sources` | Returns the inventory of ingested legal sources. |
| `GET`  | `/sources/{id}/evidence` | Returns extracted passages and evidence quotes for a source. |

---

## 🛠️ Installation & Setup

### Prerequisites
* **Python:** 3.10 or 3.11
* **Node.js:** v18 or higher
* **Package manager:** `npm` or `pnpm`

### 1. Clone the repository and switch to the branch
```bash
git clone https://github.com/kumodyathamadi/J26-IT-362.git
cd J26-IT-362
git checkout Component_2_Dhananji
```

### 2. Backend setup
Run all backend commands from the **repository root** so the `backend.main:app` import path resolves correctly.

```bash
# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env        # Windows: copy .env.example .env

# Start the FastAPI server on port 8000
uvicorn backend.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### 4. Run tests
From the repository root:
```bash
pytest tests/compliance/ -v
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./compliance.db` |
| `CHROMA_PERSIST_DIR` | Directory for the ChromaDB vector store | `./data/chroma` |
| `EMBEDDING_MODEL` | SentenceTransformers model name | `all-MiniLM-L6-v2` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173` |


---

## 📊 Evaluation

| Metric | Result | Method |
| :--- | :--- | :--- |
| Rule engine correctness | Grounded | Test cases in `tests/compliance/test_engine.py` |
| Retrieval precision@k | Evaluated | Manually labeled query–source pairs |
| PDF field extraction accuracy | Validated | Sample plans vs. ground truth |
| Test coverage | Passing | `pytest tests/compliance/` |

---

## ⚠️ Limitations & Disclaimer

* This system provides **decision support and guidance, not legal advice**. Outputs should be verified with the relevant authority or a qualified legal professional before acting on them.
* Coverage is limited to the sources in `source_register.csv`. Jurisdiction-specific rules currently focus on the **Western Province and Colombo Municipal Council**; other provinces and local authorities are not fully covered.
* Statutory forms, fees, and thresholds change over time. The rulebook must be updated when laws or procedures change.
* PDF extraction accuracy depends on the format and quality of the uploaded document, so users should always review the extracted profile.
* Generated forms are pre-filled drafts and are not official submissions.

---

## 🔄 Lifecycle Integration

Component 2 is one part of the **AI-Driven Business Lifecycle Decision Support System**:

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

* **Inputs from Component 1:** Feasibility report, proposed sector, initial capital, headcount, and operational plan.
* **Outputs to Components 3 & 4:** Verified legal structure, required licenses, and statutory tax parameters.

---

## 👩‍💻 Research Lead & Contact

* **Lead Researcher:** Dhananji Pallegedara
* **Student ID:** IT23331518
* **Component:** Component 2 – *AI-Based Legal, Regulatory and Ethical Requirement Identification & Registration Guidance*
* **Specialization:** Information Technology
* **Repository:** [kumodyathamadi/J26-IT-362](https://github.com/kumodyathamadi/J26-IT-362)
* **Branch:** [`Component_2_Dhananji`](https://github.com/kumodyathamadi/J26-IT-362/tree/Component_2_Dhananji)

---

<p align="center">
  <i>Developed to support the statutory compliance of Sri Lankan Small & Medium Enterprises (SMEs).</i>
</p>
