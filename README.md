# 🎯 Component 1: AI-Based Business Feasibility Analysis & Personalized Business Plan Recommendation

### 📌 Student ID: `IT23331136` | **Kumodya Thamadi** | Research Group: `J26-IT-362`

---

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.1-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> 🎓 **SLIIT 4th Year Research Project (2026)**  
> **Research Component 1:** *AI-Based Business Feasibility Analysis & Personalized Business/Growth Plan Recommendation for Sri Lankan SMEs*  
> **Project Repository:** [`https://github.com/kumodyathamadi/J26-IT-362.git`](https://github.com/kumodyathamadi/J26-IT-362)  
> **Research Branch:** [`Component_1_Kumodya`](https://github.com/kumodyathamadi/J26-IT-362/tree/Component_1_Kumodya)

---

## 📋 Table of Contents
- [📖 About the Project](#-about-the-project)
- [🏢 Target SME Sectors & Localization](#-target-sme-sectors--localization)
- [🏗️ End-to-End System Architecture](#️-end-to-end-system-architecture)
- [✨ Key Features](#-key-features)
- [🛠️ Technologies Used](#️-technologies-used)
- [📁 Directory Structure](#-directory-structure)
- [⚙️ Installation & Setup Guide](#️-installation--setup-guide)
  - [1️⃣ Clone the Repository](#1️⃣-clone-the-repository)
  - [2️⃣ Navigate to Project Directory](#2️⃣-navigate-to-project-directory)
  - [3️⃣ Switch to Component 1 Branch](#3️⃣-switch-to-component-1-branch)
  - [4️⃣ Setup Python Backend](#4️⃣-setup-python-backend)
  - [5️⃣ Setup React Frontend](#5️⃣-setup-react-frontend)
  - [6️⃣ Launch Application](#6️⃣-launch-application)
- [🚀 Step-by-Step User Walkthrough](#-step-by-step-user-walkthrough)
- [🧪 Automated Testing & Verification](#-automated-testing--verification)
- [📊 Research Evaluation & Model Performance](#-research-evaluation--model-performance)
- [👤 Research Author & Credentials](#-research-author--credentials)
- [📄 License](#-license)

---

## 📖 About the Project

**SME360 AI (Component 1)** is an intelligent, full-stack decision-support system engineered specifically for Sri Lankan Small and Medium Enterprises (SMEs), aspiring entrepreneurs, and financial advisors. Developed as part of a final-year research initiative at the **Sri Lanka Institute of Information Technology (SLIIT)**, this system addresses the high failure rate of developing-economy SMEs by providing **data-driven viability assessments, explainable risk diagnostics, and customized strategic roadmaps**.

### 💡 The Problem
In Sri Lanka, over **50% of new SME ventures cease operations within their first three years** due to:
- ❌ Inadequate financial planning and inaccurate capital allocation.
- ❌ Failure to assess local competition and district-level operational hurdles.
- ❌ Inability to identify specific operational weaknesses before capital deployment.
- ❌ Lack of access to high-cost financial and management consultancy services.

### 🌟 The Solution
**SME360 AI** democratizes enterprise-grade business consultancy through machine learning:
- 🔮 **Predicts Business Viability** into 3 classes: `Feasible`, `Conditionally Feasible`, or `Infeasible` with **88.33% accuracy**.
- 🔍 **Explains Decisions Transparently** using Game-Theoretic Explainable AI (**SHAP**), highlighting precise feature enablers (+) and risk hurdles (-).
- 🎯 **Ranks Strategic Interventions** using Multi-Criteria Decision Making (**TOPSIS**) according to cost, timeline, and impact.
- 🎛️ **Simulates What-If Scenarios** in real time, calculating minimum required capital or revenue adjustments to achieve viability.
- 📄 **Generates Complete Business Plans** instantly exported as executive **PDF** and editable **Microsoft Word (.docx)** files.

---

## 🏢 Target SME Sectors & Localization

The platform operates with native currency handling in **Sri Lankan Rupees (LKR)** and provides calibrated models across Sri Lankan administrative districts with a strong Colombo District benchmark.

| Icon | Sector | Example Ventures |
| :---: | :--- | :--- |
| 🛒 | **Grocery & Mini-Marts** | Neighborhood retail shops, convenience stores, provision stores |
| 👗 | **Clothing & Garment Retail** | Apparel boutiques, fabric shops, ready-made garment stores |
| 💇 | **Beauty Salons & Personal Care** | Hair styling, beauty parlors, skincare and grooming studios |
| 🥖 | **Bakeries & Food Outlets** | Artisan bakeries, tea shops, pastry outlets, takeaway eateries |

---

## 🏗️ End-to-End System Architecture

The core pipeline processes business parameters through an interconnected 9-stage research architecture:

```
┌─────────────────────────────────┐
│     Structured Web Form OR      │
│   Singlish NLP Intake Parser    │
└────────────────┬────────────────┘
                 │ (Raw Parameters)
                 ▼
┌─────────────────────────────────┐
│   FastAPI REST Backend Service  │
│   (Validation & CORS Handlers)  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ 01. Preprocessing & Scaling     │ ───► Standardized Feature Vectors (preprocessor.joblib)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ 02. Random Forest Model (88.3%) │ ───► Feasible / Conditionally Feasible / Infeasible
└────────────────┬────────────────┘
                 │
     ┌───────────┴──────────────────────────────┬─────────────────────────────┐
     ▼                                          ▼                             ▼
┌─────────────────────────┐        ┌─────────────────────────┐   ┌─────────────────────────┐
│ 03. SHAP TreeExplainer  │        │ 04. TOPSIS MCDM Ranker  │   │ 05. What-If Simulator   │
│ Local Attributions      │        │ Multi-Objective Strategy│   │ Real-time Adjustments & │
│ Enablers (+) / Risks (-)│        │ Closeness Score (C_i*)  │   │ Counterfactual Search   │
└────────────┬────────────┘        └────────────┬────────────┘   └────────────┬────────────┘
             │                                  │                             │
             └──────────────────────────────────┼─────────────────────────────┘
                                                ▼
                               ┌─────────────────────────────────┐
                               │ 06. Business Plan Generator     │
                               │ Executive PDF & DOCX Compilers  │
                               └────────────────┬────────────────┘
                                                │
                     ┌──────────────────────────┴──────────────────────────┐
                     ▼                                                     ▼
       ┌───────────────────────────┐                         ┌───────────────────────────┐
       │ SQLite / PostgreSQL DB    │                         │ React 18 + Vite Frontend  │
       │ (Audits, Profiles, Logs)  │                         │ (Dark Glassmorphism UI)   │
       └───────────────────────────┘                         └───────────────────────────┘
```

---

## ✨ Key Features

- 🤖 **Multi-Class AI Feasibility Prediction**: Evaluates business viability into `Feasible`, `Conditionally Feasible`, or `Infeasible` using an ensemble Random Forest model (**88.33% accuracy**, **0.9599 ROC-AUC**).
- 🔍 **Explainable AI (XAI) via SHAP**: Integrates `SHAP TreeExplainer` to demystify black-box predictions, isolating exact numerical drivers that increase success (+) and risk factors that decrease viability (-).
- 🎯 **Multi-Criteria Strategy Prioritization (TOPSIS)**: Evaluates and ranks tailored SME operational, marketing, financial, and digital transformation strategies based on multi-criteria closeness coefficients ($C_i^*$).
- 🎛️ **Dynamic What-If & Counterfactual Simulation**: Interactive sliders for startup capital, projected monthly revenue, operating expenses, and pricing tier to model viability trajectories dynamically without altering baseline records.
- 💬 **Dual Intake Engine (Forms & Singlish NLP)**: Accepts standard structured form inputs or natural language text in English and Singlish (Sinhala-English colloquial mix), extracting parameters automatically with confidence scores.
- 📄 **Instant Business Plan Generation (PDF & Word)**: One-click export of complete 5-section executive business roadmaps in high-fidelity PDF (ReportLab) and fully editable Word format (`.docx`).
- 📊 **Executive Glassmorphism Dashboard**: Real-time KPI summaries, Recharts-powered probability donuts, activity logs, and a "Continue Where You Left Off" quick-resume module.
- 🌐 **Multilingual Localization & Compliance**: Seamless instant client-side switching between **English**, **Sinhala (සිංහල)**, and **Tamil (தமிழ்)** with regulatory audit trails.

---

## 🛠️ Technologies Used

### 💻 Frontend
- ⚛️ **React 18** — Component-driven Single Page Application (SPA) architecture.
- ⚡ **Vite 5** — Lightning-fast development tooling and optimized production bundler.
- 🎨 **Tailwind CSS 3.4** — Utility-first styling for dark glassmorphism aesthetics.
- 🧭 **React Router v6** — Client-side SPA navigation and layout handling.
- 📈 **Recharts** — Responsive SVG charting for probability distributions and trajectory curves.
- 🔣 **Lucide React** — Crisp modern iconography across all dashboard views.
- 📡 **Axios** — Robust HTTP client for communication with the FastAPI backend.

### ⚙️ Backend & APIs
- 🐍 **Python 3.10+** — Core language for scientific computing and service APIs.
- 🚀 **FastAPI** — Asynchronous, high-throughput REST API framework with auto-generated OpenAPI/Swagger docs.
- 🦄 **Uvicorn** — Production-grade ASGI server implementation.
- 🛡️ **Pydantic v2** — Data schema validation, type checking, and serialization.
- 🗄️ **SQLAlchemy 2.0 & Alembic** — Object-Relational Mapping (ORM) and schema migration management.
- 💾 **SQLite & PostgreSQL** — Relational storage for business profiles, scenario snapshots, and audit trails.

### 🧠 Machine Learning & Data Science
- 🌲 **Scikit-Learn** — Feature extraction, preprocessing pipelines, and Random Forest ensemble classifier.
- 🔮 **SHAP (SHapley Additive exPlanations)** — Game-theoretic local and global feature attribution.
- 🔢 **NumPy & Pandas** — Matrix operations, feature engineering, and tabular data manipulation.
- 📐 **SciPy** — Mathematical vector calculations for TOPSIS normalization and Euclidean distances.
- 📦 **Joblib** — Model and preprocessor artifact serialization.

### 📑 Document Generation
- 🖨️ **ReportLab** — High-fidelity programmatic PDF compilation with custom styles, headers, and tables.
- 📝 **python-docx** — Microsoft Word document compiler for editable business plan roadmaps.

---

## 📁 Directory Structure

```text
campus-project/
├── 📁 backend/                       # FastAPI REST API Service
│   ├── main.py                       # Application entry point & router definitions
│   ├── database.py                   # SQLAlchemy engine & SQLite/PostgreSQL connection
│   ├── models.py                     # Relational database models (Assessments, Snapshots)
│   ├── schemas.py                    # Pydantic input/output schemas
│   └── routes/                       # Modular API route controllers
│       ├── analysis.py               # Feasibility analysis endpoints
│       ├── intake.py                 # Singlish/English NLP intake endpoints
│       └── business_plan.py          # PDF & DOCX export endpoints
├── 📁 frontend/                      # React 18 + Vite User Interface
│   ├── index.html                    # Single page HTML entry
│   ├── vite.config.js                # Vite configuration with API proxy (port 3000 -> 8000)
│   ├── package.json                  # Node dependencies and scripts
│   └── src/
│       ├── App.jsx                   # Main React dashboard controller
│       ├── components/               # Glassmorphism UI components
│       │   ├── Navbar.jsx            # Top navigation bar & language switcher
│       │   ├── Sidebar.jsx           # App navigation sidebar
│       │   ├── BusinessForm.jsx      # Assessment intake form
│       │   ├── FeasibilityCard.jsx   # Prediction outcome & probability badges
│       │   ├── ProbabilityChart.jsx  # Recharts feasibility distribution donut
│       │   ├── ShapExplanation.jsx   # SHAP feature attributions (+/- drivers)
│       │   ├── StrategyCard.jsx      # Strategy card display
│       │   ├── TopsisTable.jsx       # TOPSIS ranked strategy comparison table
│       │   ├── WhatIfSimulator.jsx   # Dynamic interactive scenario sliders
│       │   └── BusinessPlan.jsx      # PDF & DOCX export interface
│       └── utils/                    # Frontend helpers and API clients
├── 📁 src/                           # Core Modular Python Research Pipeline
│   ├── orchestrator.py               # Central end-to-end pipeline coordinator
│   ├── preprocessing/                # Input validation & scaling transformers
│   ├── prediction/                   # Random Forest feasibility inference engine
│   ├── explainability/               # SHAP TreeExplainer attribution service
│   ├── strategies/                   # Multi-objective SME strategy generator
│   ├── topsis/                       # TOPSIS MCDM strategy ranker
│   ├── what_if/                      # Dynamic counterfactual simulation engine
│   ├── planning/                     # 5-section personalized business plan builder
│   └── profile/                      # Schema v1.0.0 structured profile assembler
├── 📁 models/                        # Serialized ML Artifacts
│   └── feasibility_model/            # Trained random_forest.joblib & preprocessor.joblib
├── 📁 reports/                       # Research Evaluation Figures & Charts
│   ├── figures/                      # SHAP beeswarms, TOPSIS rankings, What-If plots
│   └── research_evaluation/          # ROC curves and validation logs
├── 📁 tests/                         # Automated Test Suites
│   ├── test_api.py                   # FastAPI REST endpoints integration tests
│   └── test_orchestrator.py          # End-to-end ML pipeline tests
├── requirements.txt                  # Python dependencies
└── IT23331136 Readme.md              # Research Component 1 Documentation (This file)
```

---

## ⚙️ Installation & Setup Guide

Follow these exact steps to set up and run Component 1 locally on your system:

### 📋 Prerequisites
- 🐍 **Python 3.10 or higher** installed (`python --version`)
- 🟢 **Node.js 18 or higher** & **npm** installed (`node --version` / `npm --version`)
- 🐙 **Git** installed (`git --version`)

---

### 1️⃣ Clone the Repository

Clone the official research project repository from GitHub:

```bash
git clone https://github.com/kumodyathamadi/J26-IT-362.git
```

> 💡 *Alternatively, to clone directly into the Component 1 research branch:*
> ```bash
> git clone -b Component_1_Kumodya https://github.com/kumodyathamadi/J26-IT-362.git
> ```

---

### 2️⃣ Navigate to Project Directory

```bash
cd J26-IT-362
```

---

### 3️⃣ Switch to Component 1 Branch

Ensure you are working on the dedicated research branch for Component 1:

```bash
git checkout Component_1_Kumodya
```

---

### 4️⃣ Setup Python Backend

#### A. Create a Python Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### B. Install Required Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> ℹ️ *Database Notice: The backend automatically defaults to a zero-configuration SQLite database (`data/component_1.db`) if local PostgreSQL is not configured.*

---

### 5️⃣ Setup React Frontend

Open a new terminal window or navigate into the `frontend` folder:

```powershell
cd frontend
npm install
cd ..
```

---

### 6️⃣ Launch Application

Run the backend and frontend services simultaneously:

#### 🖥️ Terminal 1 — Start the FastAPI Backend Server
```powershell
# From repository root with virtual environment activated:
python backend/main.py
```
- 🌐 **API Base URL:** `http://127.0.0.1:8000`
- 📑 **Swagger Interactive API Docs:** `http://127.0.0.1:8000/docs`
- 🩺 **Health Check:** `http://127.0.0.1:8000/api/health`

#### 💻 Terminal 2 — Start the React + Vite Frontend
```powershell
# From repository root:
cd frontend
npm run dev
```
- 🚀 **Web Application:** `http://localhost:3000`

---

## 🚀 Step-by-Step User Walkthrough

```
[1. Open Dashboard] ──► [2. Input Business] ──► [3. AI Feasibility] ──► [4. TOPSIS Ranking] ──► [5. What-If Tuning] ──► [6. Export Plan]
```

### 1️⃣ Access the Executive Dashboard
Open your browser and navigate to `http://localhost:3000`. The main dashboard displays portfolio summaries, feasibility metrics, and historical business records.

### 2️⃣ Submit Business Parameters
Click **"New Assessment"** (`/analysis/new`) and select your preferred intake mode:
- 📝 **Structured Form**: Input business name, industry sector (Grocery, Clothing, Salon, Bakery), district location, startup capital (LKR), expected monthly revenue (LKR), operating expenses, headcount, owner experience, and pricing tier.
- 💬 **Singlish/English NLP Intake**: Type or paste a natural language description (e.g., *"I want to open a small bakery in Colombo with 1,500,000 LKR capital and 3 employees..."*). Click **Extract** to automatically populate the parameters.

### 3️⃣ Review AI Feasibility Assessment & SHAP Insights
Click **"Analyze Feasibility"**:
- 📊 **Probability Breakdown**: View exact probabilities across `Feasible`, `Conditionally Feasible`, and `Infeasible`.
- 🔍 **SHAP Diagnostic Cards**: Inspect what factors positively drove viability (e.g., low operating cost, sufficient working capital) and what factors represent critical risk hurdles.

### 4️⃣ Prioritize Strategic Pathways (TOPSIS)
Navigate to the **Recommendations** view:
- 📈 View multi-objective strategies evaluated by the TOPSIS MCDM algorithm.
- 🎯 Inspect strategy rankings based on operational cost, implementation timeframe, and expected impact.

### 5️⃣ Run Dynamic What-If Simulations
Navigate to the **Scenario Explorer**:
- 🎛️ Adjust interactive sliders for capital, monthly revenue, pricing, or expenses.
- ⚡ Observe real-time shifts in feasibility probability trajectories to discover the exact minimum adjustments required for success.

### 6️⃣ Export Formal Business Plans
Switch to the **Business Plan** view:
- 📕 **Download PDF**: Generates a formal, investor-ready executive PDF report with tables and milestone roadmaps.
- 📘 **Download Word (.docx)**: Exports a fully editable document containing executive summary, market analysis, financial model, and 3-phase strategic roadmap.

---

## 🧪 Automated Testing & Verification

Ensure system reliability by running the built-in test suites:

```powershell
# 1. Run Core Modular Pipeline Orchestrator Tests:
python tests/test_orchestrator.py

# 2. Run Backend API Integration Tests:
python tests/test_api.py

# 3. Verify Frontend Production Build:
cd frontend
npm run build
cd ..
```

---

## 📊 Research Evaluation & Model Performance

### 📈 Machine Learning Benchmarks
- **Dataset**: 1,200+ validated Sri Lankan SME records with district weighting.
- **Target Classes**: `Feasible`, `Conditionally Feasible`, `Infeasible`.

| Metric | Result | Target Benchmark | Status |
| :--- | :---: | :---: | :---: |
| 🎯 **Classification Accuracy** | **88.33%** | > 85.0% | ✅ Exceeded |
| ⚖️ **Weighted F1-Score** | **0.8800** | > 0.85.0 | ✅ Exceeded |
| 📈 **ROC-AUC Score** | **0.9599** | > 0.90.0 | ✅ Exceeded |
| 📊 **Precision-Recall AUC** | **0.9494** | > 0.90.0 | ✅ Exceeded |

---

### 🖼️ Research Figures & Empirical Validations

| 📈 Model ROC Curve | 🔍 SHAP Class Comparison |
| :---: | :---: |
| ![ROC Curve](reports/research_evaluation/experiment_01_ml_validation/roc_curve.png) | ![SHAP Beeswarm](reports/figures/05_shap_class_comparison.png) |

| 🎯 TOPSIS Strategy Closeness Scores | 🎛️ Dynamic What-If Trajectories |
| :---: | :---: |
| ![TOPSIS Scores](reports/figures/07_topsis_scores.png) | ![What-If Trajectories](reports/figures/08_what_if_trajectories.png) |

---

## 👤 Research Author & Credentials

| Field | Details |
| :--- | :--- |
| 👤 **Author Name** | **Kumodya Thamadi** |
| 🆔 **Student ID** | **IT23331136** |
| 👥 **Research Group** | **J26-IT-362** |
| 🎓 **Institution** | **Sri Lanka Institute of Information Technology (SLIIT)** |
| 🏛️ **Faculty** | **Faculty of Computing** |
| 🔬 **Department / Specialization** | **Information Technology / Software Engineering** |
| 📧 **Email** | [kumodyathamadi@gmail.com](mailto:kumodyathamadi@gmail.com) |
| 🐙 **GitHub Profile** | [@kumodyathamadi](https://github.com/kumodyathamadi) |
| 📦 **Project Repository** | [https://github.com/kumodyathamadi/J26-IT-362](https://github.com/kumodyathamadi/J26-IT-362) |
| 🌿 **Component Branch** | [Component_1_Kumodya](https://github.com/kumodyathamadi/J26-IT-362/tree/Component_1_Kumodya) |

---

## 📄 License

This research software component is open-source and licensed under the **MIT License**:

```text
MIT License

Copyright (c) 2026 Kumodya Thamadi (IT23331136)
Sri Lanka Institute of Information Technology (SLIIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
