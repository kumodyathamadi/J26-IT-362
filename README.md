# SME360 AI - Business Feasibility & Decision Support System

An AI-driven decision support system tailored for Sri Lankan Small and Medium Enterprises (SMEs) with native currency support in Sri Lankan Rupees (LKR).

**Research Component:** *AI-Based Business Feasibility Analysis & Personalized Business Plan Recommendation*

---

## Architecture Overview plan

```
Form / NLP Intake ──> FastAPI Backend ──> Preprocessor ──> Random Forest Classifier (Feasibility)
                                                                 │
                                                                 ├──> SHAP TreeExplainer (Local Attribution)
                                                                 ├──> TOPSIS Model (Strategy Ranking)
                                                                 └──> Business Plan Generator (PDF & DOCX)
                                                                 │
                                      SQLite / PostgreSQL <──────┘ (Persisted Workspace & Audit Logs)
                                                                 │
                                    React Router (SPA) <─────────┘ (Real-Time Reactive Dashboards)
```

- **Frontend**: React 18, Vite, React Router v6, Recharts, Lucide Icons, Vanilla Dark Glassmorphism CSS.
- **Backend**: FastAPI (Python 3.10+ / 3.14), SQLAlchemy, Pydantic, Scikit-Learn, SHAP, ReportLab, python-docx.
- **Database**: SQLite (default local development: `data/component_1.db`) with graceful fallback and auto-migrations; compatible with PostgreSQL.

---

## Quickstart: How to Run

### 1. Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed

### 2. Backend Setup & Startup
```powershell
# In repository root:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start FastAPI server on port 8000:
python backend/main.py
```
*The backend API will be live at `http://127.0.0.1:8000` (Swagger docs at `/docs`).*

### 3. Frontend Setup & Startup
```powershell
# In another terminal, navigate to the frontend folder:
cd frontend
npm install
npm run dev
```
*The web interface will be accessible at `http://localhost:3000`.*

---

## How to Run Tests

Execute the automated test suites using Python:

```powershell
# 1. Run Data Correctness Test (No NaNs, RF Model Probabilities, Database Migration):
python tests/test_data_correctness.py

# 2. Run API End-to-End Suite (Intake, Analysis, Soft Delete & Restore, Audit Logs, PDF/DOCX):
python tests/test_api.py

# 3. Verify Frontend Production Bundle Build:
cd frontend
npm run build
```

---

## Supported SME Sectors & Locations
The system strictly supports the following 4 core Sri Lankan SME categories across all 25 official administrative districts:
1. `Grocery / Mini-Mart`
2. `Clothing / Garment`
3. `Beauty Salon`
4. `Bakery / Food / Grocery`

---

## Key Modules & Capabilities
1. **Intake Assistant (`/analysis/new`)**: 3-step natural language intake (`Describe -> Review -> Analyze`) supporting English and Singlish prompt extractions with confidence verification.
2. **Executive Dashboard (`/dashboard`)**: Real-time KPI summary cards, Recharts Feasibility Distribution Donut, Activity Timeline, and "Continue Where You Left Off" resume card.
3. **My Businesses (`/businesses`)**: Server-side pagination, multi-dimensional filters, near-duplicate run grouping, and soft delete with instant undo toast.
4. **Workspace Flow (`/businesses/:id/*`)**:
   - **Overview**: Executive summary, key metric KPIs, and complete operational profile.
   - **Feasibility Assessment**: Multiclass probabilities with embedded factor contributions explaining why the score was assigned.
   - **Key Insights**: Positive supporting drivers (+) and negative risk hurdles (-) with SHAP transparency.
   - **Recommendations & Options**: TOPSIS-ranked strategic pathways with proximity-to-ideal metrics.
   - **Scenario Explorer**: Interactive live-debounced sliders for capital, customer demand, and pricing comparing modified outcomes against baseline.
   - **Business Plan**: Complete 5-section roadmap with instant PDF and Word (.docx) downloads and shareable link copy.
5. **System Settings (`/settings`)**: Multilingual interface localization (English, Sinhala, Tamil), full regulatory audit log table, and scoring methodology guide.
