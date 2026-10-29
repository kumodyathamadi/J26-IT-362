import sqlite3, json

conn = sqlite3.connect('data/component_1.db')
c = conn.cursor()
c.execute("SELECT input_profile, extraction_metadata, original_business_description FROM analysis_records WHERE id='fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec'")
row = c.fetchone()
print('input_profile:', row[0])
print('extraction_metadata:', row[1])
print('original_description:', row[2])
