import sqlite3, json

conn = sqlite3.connect('data/component_1.db')
c = conn.cursor()

# Get created audit entry
c.execute("SELECT inputs_snapshot, result_score, result_label FROM analysis_audit_logs WHERE record_id='fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec' AND action='created'")
row = c.fetchone()
if row and row[0]:
    snapshot = json.loads(row[0])
    orig_bl = {
        "business_input": snapshot,
        "confidence_score": row[1],
        "feasibility_label": row[2]
    }
    
    c.execute("SELECT structured_profile FROM analysis_records WHERE id='fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec'")
    prof_row = c.fetchone()
    if prof_row:
        prof = json.loads(prof_row[0])
        prof["original_baseline"] = orig_bl
        c.execute("UPDATE analysis_records SET structured_profile=? WHERE id='fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec'", (json.dumps(prof),))
        conn.commit()
        print("Updated fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec with original_baseline!")
        print("original_baseline capital:", orig_bl["business_input"].get("available_capital_lkr"))
        print("original_baseline score:", orig_bl["confidence_score"])
