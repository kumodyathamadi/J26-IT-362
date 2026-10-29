import requests
import json

url = "http://127.0.0.1:8000/api/v1/component2/evaluate"
payload = {
    "business_plan_text": "Organic food manufacturing factory in Gampaha with 15 employees and wastewater discharge.",
    "district": "Gampaha",
    "employee_count": 15,
    "revenue": 3500000.0,
    "sector": "Food Manufacturing & Agriculture"
}

try:
    print("Sending POST request to:", url)
    res = requests.post(url, json=payload, timeout=60)
    print("Status code:", res.status_code)
    data = res.json()
    out_file = "test_evaluate_output.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Saved output to", out_file)
    for idx, s in enumerate(data.get("source_discovery", [])):
        ag = s.get("action_guidance") or {}
        print(f"Rule {idx+1}: {s.get('title')}")
        print(f"   -> Purpose: {ag.get('rule_purpose')}")
        print(f"   -> Where to Go: {ag.get('where_to_go')}")
        print(f"   -> Office: {ag.get('office_location')}")
        print(f"   -> Action: {ag.get('action_needed')}")
        print(f"   -> Docs count: {len(ag.get('required_documents', []))}")
        print(f"   -> Steps count: {len(ag.get('procedural_steps', []))}")



except Exception as e:
    print("Error:", e)
