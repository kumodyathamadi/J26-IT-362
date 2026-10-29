import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_endpoints():
    print("Testing GET /api/v1/component2/sample-plans...")
    res = client.get("/api/v1/component2/sample-plans")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    samples = res.json()
    print("Found samples:", [s["id"] for s in samples])

    print("\nTesting GET /api/v1/component2/sample-plans/freshmart_grocery/extract...")
    res_ext = client.get("/api/v1/component2/sample-plans/freshmart_grocery/extract")
    assert res_ext.status_code == 200, f"Extract failed: {res_ext.text}"
    ext_data = res_ext.json()
    print("Extracted Business Name:", ext_data["extracted_profile"]["business_name"])
    print("Extracted Sector:", ext_data["extracted_profile"]["sector"])
    print("Extracted Products:", ext_data["extracted_profile"]["products_services"])
    print("Extracted Confidence:", ext_data["metadata"]["extraction_confidence"])

    print("\nTesting POST /api/v1/component2/extract-plan-pdf via multipart upload...")
    sample_pdf_path = _REPO_ROOT / "data" / "sample_plans" / "Trendy_Style_Clothing_Shop_Business_Plan.pdf"
    with open(sample_pdf_path, "rb") as f:
        files = {"file": ("Trendy_Style_Clothing_Shop_Business_Plan.pdf", f, "application/pdf")}
        res_upload = client.post("/api/v1/component2/extract-plan-pdf", files=files)
    assert res_upload.status_code == 200, f"Upload failed: {res_upload.text}"
    up_data = res_upload.json()
    print("Uploaded & Extracted:", up_data["extracted_profile"]["business_name"])
    print("Sector:", up_data["extracted_profile"]["sector"])
    print("Staff:", up_data["extracted_profile"]["number_of_employees"])

    print("\nAll new endpoints passed successfully!")

if __name__ == "__main__":
    test_endpoints()
