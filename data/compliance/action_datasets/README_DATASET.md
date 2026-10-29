# Western Province SME Action Recommendation Dataset — 360 Records

## Geographic scope
This tailored dataset covers only the three districts of Sri Lanka's Western Province:
- Colombo: 120 records
- Gampaha: 120 records
- Kalutara: 120 records

There are 20 records per district in each of six categories.

## Important provenance and limitations
- Colombo and Kalutara records are filtered from the uploaded 600-record dataset.
- The original dataset had no Gampaha records. To provide coverage across all three Western Province districts, 120 Gampaha scenarios were synthetically adapted from Colombo/Kalutara examples. They are not verified Gampaha-specific legal instructions.
- All rows remain synthetic draft action templates, not verified legal answers or legal ground truth.
- Every row is marked NEEDS_OFFICIAL_VERIFICATION and human_review_required=true.
- Do not assume local-authority procedures, fees, timelines, office locations, documents, or licence applicability are confirmed.
- Verify current legislation, official sources, responsible authority, exact activity and local requirements before using any row for model training or user-facing recommendations.

## Files
- `western_province_sme_action_dataset_360.csv`: spreadsheet-friendly format.
- `western_province_sme_action_dataset_360.jsonl`: one JSON object per line.

## Recommended use
Use as a regional prototype / annotation seed. Before evaluation or fine-tuning, build a human-reviewed gold set from official sources. Split train/validation/test by legal rule/source/scenario family to reduce leakage.
