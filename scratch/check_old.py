import sqlite3, json
conn = sqlite3.connect('scratch/old_db.db')
c = conn.cursor()
c.execute("SELECT business_name, structured_profile FROM analysis_records WHERE id='fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec'")
row = c.fetchone()
if row:
    prof = json.loads(row[1])
    bi = prof.get('business_input', {})
    fa = prof.get('feasibility_analysis', {})
    print('OLD Capital:', bi.get('available_capital_lkr'))
    print('OLD Confidence:', fa.get('confidence_score'))
    print('OLD Probabilities:', fa.get('probabilities'))
else:
    print('Not found in old_db')
