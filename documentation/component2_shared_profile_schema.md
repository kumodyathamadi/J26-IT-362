# Component 2: Fixed Business Profile Schema Documentation
**AI-Driven Business Lifecycle Decision Support System**  
**Sub-system:** Legal & Regulatory Requirement Identification (Component 2)  
**Integration Boundary:** Component 1 (Business Idea Intake & Feasibility Analysis) $\to$ Component 2 (Legal & Regulatory Requirement Engine)

---

## 1. Overview & Architectural Contract

The system enforces a **strict deterministic boundary**:
- **Profile In:** Component 1 outputs a business profile (or a user inputs a profile directly via the registration form).
- **Obligations Out:** The deterministic Three-Valued Kleene Logic Rule Engine evaluates the profile against statutory rules in `data/obligations.json`.
- **No LLM in the Loop:** LLMs are strictly forbidden from deciding legal applicability. Applicability decisions are 100% deterministic, transparent, and auditable. An LLM may only rephrase human-readable explanations post-evaluation.

---

## 2. Shared Profile Data Contract (`SharedBusinessProfile`)

Every attribute in the profile is optional and defaults to `None` (representing an **Unknown** fact in three-valued Kleene logic).

### Core Fields

| Field Name | Type | Allowed Values / Examples | Description |
| :--- | :--- | :--- | :--- |
| `province` | `str` | `"Western Province"` (Primary scope) | Administrative province of operation. |
| `business_type` | `str` | `"food"`, `"clothing"`, `"salon"`, `"vehicle_parts"` | The primary commercial sector. |
| `local_authority` | `str` | `"Colombo Municipal Council"`, `"Dehiwala-Mount Lavinia Municipal Council"`, `"Sri Jayawardenepura Kotte Municipal Council"`, etc. | Governing municipal council or local government body. |
| `legal_form` | `str` | `"sole_proprietorship"`, `"partnership"`, `"private_limited"`, `"other"` | Registered corporate structure. |
| `number_of_employees` | `int` | $\ge 0$ (e.g. `0`, `5`, `25`) | Count of paid staff members hired. |
| `has_physical_premises` | `bool` | `true`, `false`, `null` | Whether business occupies a physical commercial space or premises. |
| `handles_food` | `bool` | `true`, `false`, `null` | Whether business prepares, handles, stores, or sells food items. |
| `is_manufacturing` | `bool` | `true`, `false`, `null` | Whether the enterprise manufactures or fabricates goods. |
| `is_importing` | `bool` | `true`, `false`, `null` | Whether the business directly imports products from overseas. |

### Sector-Specific Conditional Fields

| Field Name | Target Sector | Type | Allowed Values | Description |
| :--- | :--- | :--- | :--- | :--- |
| `serves_cooked_food` | `food` | `bool` | `true`, `false`, `null` | Prepares and serves hot cooked meals for direct on-premise consumption. |
| `sells_alcohol` | `food` | `bool` | `true`, `false`, `null` | Sells or serves alcoholic drinks / liquor. |
| `uses_chemicals_or_cosmetics`| `salon` | `bool` | `true`, `false`, `null` | Applies chemical dyes, cosmetics, skin/hair treatments. |
| `handles_waste_oil_or_batteries` | `vehicle_parts` | `bool` | `true`, `false`, `null` | Stores or disposes of spent batteries or engine mineral oils. |
| `turnover_band` | All | `str` | `"under_1m"`, `"1m_10m"`, `"10m_50m"`, `"over_50m"` | Projected annual gross turnover in LKR. |

---

## 3. Three-Valued Kleene Logic Mapping

In Component 2, profile values map to Kleene truth values:
- `True`: Fact is affirmatively verified.
- `False`: Fact is affirmatively absent.
- `None` (`null`): Fact is **Unknown**.

### Truth Tables

#### Conjunction (`all_of` / Kleene AND)
- If **any** operand is `False` $\to$ Result is `False` (`NOT_APPLICABLE`).
- Else if **any** operand is `None` $\to$ Result is `None` (`UNKNOWN`).
- Else (all operands are `True`) $\to$ Result is `True` (`APPLICABLE`).

#### Disjunction (`any_of` / Kleene OR)
- If **any** operand is `True` $\to$ Result is `True` (`APPLICABLE`).
- Else if **any** operand is `None` $\to$ Result is `None` (`UNKNOWN`).
- Else (all operands are `False`) $\to$ Result is `False` (`NOT_APPLICABLE`).

---

## 4. API Endpoints (`POST /api/analyse`)

### Request Example
```json
{
  "province": "Western Province",
  "business_type": "food",
  "has_physical_premises": true,
  "handles_food": true,
  "serves_cooked_food": null
}
```

### Response Example
```json
{
  "summary": {
    "total": 5,
    "applicable": 2,
    "not_applicable": 3,
    "unknown": 0
  },
  "obligations": [
    {
      "obligation_id": "OBL-COMMON-001",
      "title": "[PLACEHOLDER] Business Name Registration (Western Province)",
      "status": "APPLICABLE",
      "triggering_facts": {
        "province": "Western Province",
        "has_physical_premises": true
      },
      "missing_facts": [],
      "authority": "Department of Business Names (Western Province)",
      "source_id": "SRC-WP-BN-1990",
      "source_paragraph": "Section 3(1)",
      "source_text": "[PLACEHOLDER LEGAL TEXT] Every individual or firm carrying on business under a business name in the Western Province...",
      "documents_needed": [
        "Business Registration Application Form A",
        "Grama Niladhari Verification Certificate",
        "National Identity Card (NIC) / Passport copy"
      ]
    }
  ],
  "follow_up_questions": [],
  "disclaimer": "Guidance only, not legal advice. Decisions are determined by a deterministic rule engine. Always verify requirements with the official authority."
}
```
