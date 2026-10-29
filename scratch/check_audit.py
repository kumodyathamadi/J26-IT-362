import sqlite3, json

conn = sqlite3.connect('data/component_1.db')
c = conn.cursor()
c.execute("SELECT id, action, result_label, result_score, inputs_snapshot, created_at FROM analysis_audit_logs WHERE record_id='fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec' ORDER BY created_at ASC")
rows = c.fetchall()
print(f"Found {len(rows)} audit entries:")
for r in rows:
    print('Action:', r[1], '| Score:', r[3], '| Time:', r[5])
    snap = json.loads(r[4]) if r[4] else {}
    print('   Capital in snapshot:', snap.get('available_capital_lkr'))
    print('   Budget in snapshot:', snap.get('monthly_budget_lkr'))
