# Component 2 — Test Report
**Project:** AI-Driven Business Lifecycle Decision Support System  
**Component:** Component 2 — AI-Based Business Registration & Regulatory Compliance  
**Branch:** `Component_2_Dhananji`  
**Target Region:** Western Province, Colombo District, Sri Lanka  
**Report Date:** 2026-10-12  
**Prepared By:** Dhanamji (Dhananji)  
**Python Version:** 3.14.4  
**pytest Version:** 9.1.1  

---

## 1. Automated Test Results

**Test Suite:** `tests/compliance/test_engine.py`  
**Run Command:** `python -m pytest tests/compliance/ -v --tb=short`  
**Result:** ✅ **23 / 23 PASSED — 0 FAILED — 0 ERRORS**  
**Duration:** 0.46s  

### Test Coverage Summary

| Test Class / Function | Obligation | Condition Tested | Result |
|---|---|---|---|
| `test_all_blank_profile_gives_zero_applicable` | All | All-blank profile → all UNKNOWN | ✅ PASS |
| `TestOBL001BusinessNames::test_true_condition` | OBL-001 Business Name Registration | All triggers True → CONDITIONAL | ✅ PASS |
| `TestOBL001BusinessNames::test_false_condition` | OBL-001 | has_physical_premises=False → NOT_IDENTIFIED | ✅ PASS |
| `TestOBL001BusinessNames::test_unknown_condition` | OBL-001 | jurisdiction=None → UNKNOWN | ✅ PASS |
| `TestOBL002TradeLicence::test_true_condition` | OBL-002 CMC Trade Licence | All triggers True → CONDITIONAL/APPLICABLE | ✅ PASS |
| `TestOBL002TradeLicence::test_false_condition` | OBL-002 | has_physical_premises=False → NOT_IDENTIFIED | ✅ PASS |
| `TestOBL002TradeLicence::test_unknown_condition` | OBL-002 | local_authority=None → UNKNOWN | ✅ PASS |
| `TestOBL003FoodHygiene::test_true_condition` | OBL-003 Food Hygiene Licence | handles_food=True → CONDITIONAL/APPLICABLE | ✅ PASS |
| `TestOBL003FoodHygiene::test_false_condition` | OBL-003 | clothing_retail + handles_food=False → NOT_IDENTIFIED | ✅ PASS |
| `TestOBL003FoodHygiene::test_unknown_condition` | OBL-003 | handles_food=None → UNKNOWN | ✅ PASS |
| `TestOBL004TINRegistration::test_true_condition` | OBL-004 TIN Registration | bakery + sole_proprietorship → CONDITIONAL/APPLICABLE | ✅ PASS |
| `TestOBL004TINRegistration::test_false_condition` | OBL-004 | clothing_retail + LegalForm.OTHER → NOT_IDENTIFIED | ✅ PASS |
| `TestOBL004TINRegistration::test_unknown_condition` | OBL-004 | legal_form=None → UNKNOWN | ✅ PASS |
| `TestOBL005EPF::test_true_condition` | OBL-005 EPF Registration | employee_band=MICRO (1–9) → CONDITIONAL | ✅ PASS |
| `TestOBL005EPF::test_false_condition` | OBL-005 | employee_band=NONE (0) → NOT_IDENTIFIED with "Employees = 0" | ✅ PASS |
| `TestOBL005EPF::test_unknown_condition` | OBL-005 | employee_band=None → UNKNOWN | ✅ PASS |
| `TestOBL006ETF::test_true_condition` | OBL-006 ETF Registration | employee_band=SMALL (10–49) → CONDITIONAL/APPLICABLE | ✅ PASS |
| `TestOBL006ETF::test_false_condition` | OBL-006 | employee_band=NONE (0) → NOT_IDENTIFIED | ✅ PASS |
| `TestOBL006ETF::test_unknown_condition` | OBL-006 | employee_band=None → UNKNOWN | ✅ PASS |
| `TestOBL007FoodLabelling::test_true_condition` | OBL-007 Food Labelling | is_manufacturing=True → CONDITIONAL | ✅ PASS |
| `TestOBL007FoodLabelling::test_false_condition` | OBL-007 | is_manufacturing=False → NOT_IDENTIFIED | ✅ PASS |
| `TestOBL007FoodLabelling::test_unknown_condition` | OBL-007 | is_manufacturing=None → UNKNOWN | ✅ PASS |
| `test_scope_guard_out_of_scope_authority` | All (Scope Guard) | Kandy MC + Central Province → NOT_COVERED | ✅ PASS |

---

## 2. Manual API Testing (via Swagger UI — `http://127.0.0.1:8000/docs`)

### 2.1 Endpoint Inventory

| Endpoint | Tag | Status |
|---|---|---|
| `GET /` | Root | ✅ Reachable |
| `GET /api/health` | Health | ✅ Reachable |
| `POST /api/v1/component2/evaluate` | Component 2 - Registration & Compliance | ✅ Reachable |
| `POST /compliance/analyze` | Component 2 — Compliance | ✅ Reachable (after router registration fix) |
| `POST /compliance/analyze/from-component1` | Component 2 — Compliance | ✅ Reachable |
| `GET /compliance/obligations` | Component 2 — Compliance | ✅ Reachable |
| `GET /compliance/sources` | Component 2 — Compliance | ✅ Reachable |
| `GET /compliance/sample-profiles/{profile_id}` | Component 2 — Compliance | ✅ Reachable |

---

### 2.2 Manual Test Cases — `POST /compliance/analyze`

#### TC-API-001 — Valid Full Bakery Profile (Clear Case)
| Field | Value |
|---|---|
| **Test ID** | TC-API-001 |
| **Endpoint** | `POST /compliance/analyze` |
| **Input** | `{"business_type":"bakery","local_authority":"Colombo Municipal Council","handles_food":true,"has_physical_premises":true,"employee_band":"1_9","is_manufacturing":true,"legal_form":"sole_proprietorship","jurisdiction":"Western Province"}` |
| **Expected** | HTTP 200; obligations list with 7 items; applicable/conditional statuses for bakery rules |
| **Actual** | NOT TESTED (server not started during session) |
| **Status** | ⬜ NOT TESTED |

#### TC-API-002 — Empty Profile (All Fields Omitted)
| Field | Value |
|---|---|
| **Test ID** | TC-API-002 |
| **Endpoint** | `POST /compliance/analyze` |
| **Input** | `{}` |
| **Expected** | HTTP 200; all 7 obligations return `status: "unknown"`; `summary.applicable = 0` |
| **Actual** | Confirmed by automated test `test_all_blank_profile_gives_zero_applicable` |
| **Status** | ✅ PASS (via automated test) |

#### TC-API-003 — Out-of-Scope Authority (Kandy MC)
| Field | Value |
|---|---|
| **Test ID** | TC-API-003 |
| **Endpoint** | `POST /compliance/analyze` |
| **Input** | `{"business_type":"bakery","local_authority":"Kandy Municipal Council","jurisdiction":"Central Province"}` |
| **Expected** | HTTP 200; non-national obligations return `status: "not_covered"`; reason mentions not covered |
| **Actual** | Confirmed by automated test `test_scope_guard_out_of_scope_authority` |
| **Status** | ✅ PASS (via automated test) |

#### TC-API-004 — Invalid Sector (POST `/api/v1/component2/evaluate`)
| Field | Value |
|---|---|
| **Test ID** | TC-API-004 |
| **Endpoint** | `POST /api/v1/component2/evaluate` |
| **Input** | `{"business_name":"Test","sector":"grocery","entity_type":"Sole proprietorship","municipal_council":"Colombo Municipal Council","employees_count":2,"annual_revenue_lkr":500000,"activities":["retail"]}` |
| **Expected** | HTTP 400 — `"Invalid sector. Supported: food, clothing, saloon, vehicle"` |
| **Actual** | NOT TESTED (server not started during session) |
| **Status** | ⬜ NOT TESTED |

#### TC-API-005 — Missing Required Field (422 Validation)
| Field | Value |
|---|---|
| **Test ID** | TC-API-005 |
| **Endpoint** | `POST /api/v1/component2/evaluate` |
| **Input** | `{"business_name":"Test Bakery"}` (6 fields missing) |
| **Expected** | HTTP 422 Unprocessable Entity with validation errors listing all missing fields |
| **Actual** | NOT TESTED (server not started during session) |
| **Status** | ⬜ NOT TESTED |

#### TC-API-006 — Sample Profile Load (Clear Case)
| Field | Value |
|---|---|
| **Test ID** | TC-API-006 |
| **Endpoint** | `GET /compliance/sample-profiles/clear_case` |
| **Expected** | HTTP 200; returns bakery profile JSON from `data/compliance/profiles/clear_case.json` |
| **Actual** | NOT TESTED (server not started during session) |
| **Status** | ⬜ NOT TESTED |

---

## 3. Frontend UI Testing

| Test ID | Feature | Action | Expected | Status |
|---|---|---|---|---|
| TC-UI-001 | App loads at `http://localhost:5173` | Open browser | Registration & Compliance Dashboard renders | ⬜ NOT TESTED |
| TC-UI-002 | Business Type dropdown | Select "Bakery" | `bakery` sent in request body | ⬜ NOT TESTED |
| TC-UI-003 | Local Authority dropdown | Select "Colombo MC" | `Colombo Municipal Council` sent | ⬜ NOT TESTED |
| TC-UI-004 | Boolean toggles | Click Yes/No on "Handles Food" | `handles_food: true/false` sent | ⬜ NOT TESTED |
| TC-UI-005 | Analyse Compliance button | Click with full profile | Loading spinner → results panel appears | ⬜ NOT TESTED |
| TC-UI-006 | Empty form submit | Click with no fields selected | API called with `{}` → all UNKNOWN results | ⬜ NOT TESTED |
| TC-UI-007 | Sample profile — Clear Case | Click "Clear Case" button | Fetches `/compliance/sample-profiles/clear_case` then auto-analyses | ⬜ NOT TESTED |
| TC-UI-008 | Follow-up question resolves Unknown | Answer inline question after analysis | Re-submits with new field → status changes | ⬜ NOT TESTED |
| TC-UI-009 | Export Checklist | Click "Export Checklist (Print/PDF)" | Browser print dialog opens | ⬜ NOT TESTED |
| TC-UI-010 | Out-of-scope authority | Select "Kandy MC" → Analyse | NOT_COVERED obligations appear | ⬜ NOT TESTED |
| TC-UI-011 | Network tab — API URL | Open DevTools Network tab | Request goes to `http://localhost:8000/compliance/analyze` | ⬜ NOT TESTED |
| TC-UI-012 | Mobile width (≤640px) | Resize browser to 375px | Form stacks vertically; no overflow | ⬜ NOT TESTED |

---

## 4. Defects Identified (from Source Code Inspection)

| Defect ID | Severity | Location | Description | Status |
|---|---|---|---|---|
| DEF-001 | 🔴 High | `frontend/src/components/component2.tsx` L168 | Frontend calls `http://localhost:8000/compliance/analyze` but compliance router was not registered in `main.py`. Fixed in commit `fb78783`. | ✅ Fixed |
| DEF-002 | 🟡 Medium | `data/compliance/profiles/` | `clear_case.json` and `conditional_case.json` are identical files — conditional case does not demonstrate conditional logic | ⬜ Open |
| DEF-003 | 🟡 Medium | `backend/app/api/component2_routes.py` | `/api/v1/component2/evaluate` returns 100% hardcoded mock data. `vector_score` is always `0.984`. No real RAG logic executed. | ⬜ Open |
| DEF-004 | 🟠 Medium | `data/compliance/rulebook/obligations.yaml` | All 7 rules have empty `evidence.quote: ""` — no verified legal quotes present | ⬜ Open |
| DEF-005 | 🟡 Low | `data/compliance/source_register.csv` | Only 3 of 7 legal sources have URLs; 4 have no URL entry | ⬜ Open |
| DEF-006 | 🟡 Low | `.gitignore` / `data/component_1.db` | Binary `.db` file is tracked in Git despite `*.db` in `.gitignore` (was added before rule) | ⬜ Open |
| DEF-007 | 🟡 Low | `data/compliance/rulebook/obligations.yaml` | Rulebook only covers food-sector businesses (5 business types). Clothing, saloon, vehicle sectors have no backend rules — only frontend mock data. | ⬜ Open |

---

## 5. Compliance Source Reference Inventory

| Source ID | Act / Document | Authority | URL | Verified Quote |
|---|---|---|---|---|
| SL-WESTERNPROV-BUSINESSNAMES-1990 | Business Names Statute No. 6 of 1990 (WP) | WP Governor's Office | ❌ Missing | ❌ Empty |
| SL-CMC-TRADELIC-1980 | CMC Trade Licence By-Laws 1980 | Colombo Municipal Council | ❌ Missing | ❌ Empty |
| SL-FOOD-CONTROL-2011 | Food (Labelling and Advertising) Regulations 2011 | SLSI / Ministry of Health | ❌ Missing | ❌ Empty |
| SL-IRD-TIN-2017 | Inland Revenue Act No. 24 of 2017 | Inland Revenue Department | ✅ https://www.ird.gov.lk | ❌ Empty |
| SL-FOODCONTROL-ACT-1980 | Food Control Act No. 26 of 1980 | Ministry of Health | ❌ Missing | ❌ Empty |
| SL-EMPLOYERSVNF-2012 | ETF Act No. 46 of 1980 | ETF Board | ✅ https://www.etfb.lk | ❌ Empty |
| SL-EPF-1958 | EPF Act No. 15 of 1958 | Department of Labour | ✅ https://www.labour.gov.lk | ❌ Empty |

> **Note:** Zero obligations currently have verified verbatim legal quotes. All rules are marked `reviewer_status: draft`.  
> The UI correctly displays a "No verified source quote yet" warning for all obligations.  
> This is an honest research limitation and not a system error.

---

## 6. Security & Repository Hygiene Checks

| Check | Finding | Status |
|---|---|---|
| `.env` file committed to repo | No `.env` file exists on disk; `.gitignore` includes `.env` | ✅ Safe |
| Credentials or API keys in source | None found in any source file | ✅ Safe |
| `node_modules/` tracked | Not tracked — in `.gitignore` | ✅ Safe |
| `__pycache__/` tracked | Not tracked — in `.gitignore` | ✅ Safe |
| `data/component_1.db` tracked | ⚠️ Binary DB file is tracked despite `*.db` in `.gitignore` | ⚠️ Review |
| `venv/` or `.venv/` tracked | Not present; not tracked | ✅ Safe |

---

## 7. Summary

| Category | Total | Passed | Failed | Not Tested |
|---|---|---|---|---|
| Automated Engine Tests | 23 | **23** | 0 | 0 |
| Manual API Tests | 6 | 2 (via automation) | 0 | 4 |
| Frontend UI Tests | 12 | 0 | 0 | 12 |
| **Total** | **41** | **25** | **0** | **16** |

### Overall Verdict: ✅ Automated tests fully pass. Manual and UI tests pending live server session.

---

## 8. Recommended Next Steps (Priority Order)

1. **[5 min]** Fix `data/compliance/profiles/conditional_case.json` — make it a genuinely conditional profile (has physical premises but missing local_authority).
2. **[30 min]** Add clothing/saloon/vehicle sector obligations to `obligations.yaml`.
3. **[60 min]** Run full manual API test session (Steps TC-API-001, TC-API-004, TC-API-005) with server running.
4. **[60 min]** Run full frontend UI test session (TC-UI-001 through TC-UI-012).
5. **[2 hrs]** Add verified legal quotes to obligations.yaml from official Sri Lankan government sources.

---

*Report generated from static code inspection and live automated test run.*  
*Live server tests to be completed and results recorded before PP1 presentation.*
