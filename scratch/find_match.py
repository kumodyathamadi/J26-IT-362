import requests

rec = requests.get('http://127.0.0.1:8000/api/business/record/fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec').json()
b_input = dict(rec.get('business_input', {}))

for cap in [100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1200000, 1400000]:
    mod_input = dict(b_input)
    mod_input['available_capital_lkr'] = float(cap)
    resp = requests.post('http://127.0.0.1:8000/api/business/simulate?baseline_record_id=fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec', json=mod_input)
    res = resp.json()
    pd = res.get('probability_deltas', {})
    vd = res.get('viability_delta', 0)
    print(f"Cap: {cap} | Viab Delta: {vd:.3f} | Pred: {res.get('prediction')} | Score: {res.get('confidence_score')} | Deltas: {pd}")
    if abs(pd.get('Feasible', 0) - (-0.065)) < 0.005:
        print(">>> MATCH FOUND! Cap:", cap)
