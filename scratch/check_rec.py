import sqlite3, json

conn = sqlite3.connect('data/component_1.db')
c = conn.cursor()
c.execute("PRAGMA table_info(analysis_records)")
cols = [r[1] for r in c.fetchall()]
print('Columns:', cols)

c.execute("SELECT * FROM analysis_records WHERE id='fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec'")
row = c.fetchone()
row_dict = dict(zip(cols, row))
print('business_name:', row_dict.get('business_name'))
prof = json.loads(row_dict.get('structured_profile', '{}'))
print('prof keys:', list(prof.keys()))
print('business_input in prof:', prof.get('business_input'))
print('metadata in prof:', prof.get('metadata'))
