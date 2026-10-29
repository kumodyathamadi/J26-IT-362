# Component 2 — AI-Based Business Registration & Regulatory Compliance
**Research Topic:** AI-Driven Business Lifecycle Decision Support System  
**Target Region:** Western Province, Colombo District, Sri Lanka  
**Target Sectors:** Food, Clothing, Saloon, Vehicle Parts / Repair / Reselling  

---

## 1. Executive Summary & Objective

Component 2 provides an intelligent, evidence-grounded, context-aware decision support engine designed to navigate the multi-layered legal and regulatory landscape of business registration in Sri Lanka. 

Operating within **Western Province, Colombo District**, the system bridges the gap between raw business characteristics (sector, scale, entity type, activities, municipal jurisdiction) and enforceable legal mandates (Inland Revenue Act, Municipal By-Laws, Public Health Ordinances, Environmental Protection Directives, and Labour Acts).

```
Expected Output Flow:
[Business Characteristics & Location] 
        │
        ▼
[Context-Aware AI Requirement Identification]
        │
        ▼
[Metadata-Enhanced Cross-Source Regulatory Retrieval (RAG)]
        │
        ▼
[Mandatory Registrations Identification]
        │
        ▼
[Licenses & Permits Matrix Generation]
        │
        ▼
[Evidence-Grounded Step-by-Step Compliance Guidance & Risk Warning]
```

---

## 2. Research Novelty

1. **Business-Context-Aware Regulatory Requirement Identification and Explainable Recommendation**
   - Dynamically evaluates business scale (revenue, employee count), legal structure (Sole Proprietorship, Partnership, Pvt Ltd), exact municipal jurisdiction (Colombo Municipal Council, Sri Jayawardenepura Kotte MC, Dehiwala-Mount Lavinia MC, etc.), and operational micro-activities (e.g., grease trap installation for eateries, waste mineral oil handling for auto repair, fabric fire load ratings for apparel).
2. **Cross-Source, Metadata-Enhanced Regulatory Retrieval**
   - Employs a multi-vector Retrieval-Augmented Generation (RAG) framework indexing diverse legal knowledge corpora:
     - National Acts & Parliamentary Gazettes (Inland Revenue Act No. 24 of 2017, Companies Act No. 07 of 2007, Food Act No. 26 of 1980, EPF/ETF Acts).
     - Provincial Council Statutes (Western Province Business Names Statute No. 06 of 1990).
     - Municipal Council Ordinances & Local Bylaws (CMC Cap 252, Ward Place Regulations).
     - Line Ministry / Regulatory Directives (Central Environmental Authority EPL Schedules, NMRA Cosmetics Passes).
3. **Evidence-Grounded and Explainable Compliance Recommendations**
   - Ensures zero hallucination by pairing every recommendation with exact legal excerpts, similarity scores, enforcing authorities, required physical artifacts, and statutory non-compliance penalty warnings.

---

## 3. System Architecture & UI Design Layout

The UI design is crafted to provide a modern, high-density decision support dashboard matching the system layout:

- **Sidebar Navigation**: Lifecycle modules switcher (Component 1 through Component 4), featuring Colombo District fast-switching presets (`Food`, `Clothing`, `Saloon`, `Vehicle Parts`).
- **Context Assessment Banner**: Live display of current business attributes with an interactive modal to modify activities, location, and scale.
- **Metrics Overview Panel**:
  - *Compliance Readiness Gauge*: Dynamic percentage completion, rules evaluated vs. applied count.
  - *Next Best Action*: AI prioritized next step with deadline countdown and legal urgency rationale.
  - *AI Breakdown*: Quick breakdown of registrations, licenses, taxes, and upcoming deadlines.
- **Interactive Multi-Tab Workflow**:
  - Tab 1: *Step-by-Step Roadmap* (Sequential legal execution flow from entity registration to EPF/ETF labour compliance).
  - Tab 2: *Licenses & Permits Matrix* (Fee structures, authority contacts, renewal intervals).
  - Tab 3: *Tax & Regulatory Obligations* (RAMIS TIN, VAT, SSCL threshold tracking).
  - Tab 4: *Interactive Compliance Checklist* (Real-time readiness score recalculation).
- **Evidence-Grounded Citation Drawer**: Real-time right-hand side panel presenting verified legal text clauses, vector confidence match scores, AI rationale, penalty risks, and direct portal links.

---

## 4. Sector-Specific Rule Matrix (Colombo District)

| Business Sector | Key Legal Acts & Statutes | Enforcing Authority | Key Permits / Licenses | Non-Compliance Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Food & Beverage** (e.g. Lanka Spice Kitchen) | Food Act No. 26 of 1980, Western Province Business Names Statute No. 6 of 1990, Inland Revenue Act | CMC Health Dept, Public Health Inspector (PHI), IRD | Form A Business Name, RAMIS TIN, PHI Sanitary Pass, CMC Trade License | Premises closure, confiscation of goods, Magistrate Court summons |
| **Clothing & Apparel** (e.g. Urban Thread Boutique) | Companies Act No. 07 of 2007, CMC Fire Prevention Bylaws, IRD VAT Directives | Registrar of Companies (ROC), Colombo Fire Brigade, IRD | Form 1 ROC Registration, RAMIS VAT File, Fire Safety Certificate | Bank account freeze, 20% VAT default penalties, municipal shutdown |
| **Saloon & Personal Care** (e.g. Glamour & Glow) | WP Health Directorate Guidelines 2022, NMRA Cosmetic Safety Pass | Kotte Municipal Council, PHI Regional Office, NMRA | Business Name Cert, Autoclave Sanitation Pass, Trade License | Revocation of trade permit, chemical safety injunction |
| **Vehicle Parts & Repair** (e.g. Lanka Auto Gear) | National Environmental Act No. 47 of 1980 (EPL Schedule B-12), Labour Act | Central Environmental Authority (CEA), Dehiwala MC, Labour Dept | CEA Environmental Protection License (EPL), Trade License, EPF/ETF Form D | Up to LKR 100,000/day fine, workshop injunction for illegal waste oil discharge |

---

## 5. Folder Structure & Integration

```
AI-Driven-Business-Lifecycle-Decision-Support-System/
├── frontend/
│   └── src/
│       └── components/
│           └── component2/
│               ├── RegistrationComplianceDashboard.tsx   # Primary UI Dashboard
│               ├── mockData.ts                          # Colombo District RAG Legal Database
│               └── types.ts                             # TypeScript Schemas & Context Interfaces
├── documentation/
│   └── Component_2_Design_Architecture.md               # Research Novelty & Architecture Specification
└── artifact/
    └── registration_compliance_ui.html                  # Full Interactive HTML Dashboard Preview
```
