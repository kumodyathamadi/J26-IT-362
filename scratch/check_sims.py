import sqlite3, json

conn = sqlite3.connect('data/component_1.db')
c = conn.cursor()
c.execute("SELECT structured_profile FROM analysis_records WHERE id='fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec'")
row = c.fetchone()
prof = json.loads(row[0])
sc = prof.get('scenario_analysis', {})
print('scenario_analysis keys:', list(sc.keys()))
for sim in sc.get('what_if_simulations', []):
    print('Simulation:', sim.get('title') or sim.get('scenario_name'))
    print('  modifications:', sim.get('modifications'))
    print('  probability_deltas:', sim.get('probability_deltas'))
    print('  new_prediction:', sim.get('new_prediction'))
    print('  confidence_score:', sim.get('confidence_score'))
