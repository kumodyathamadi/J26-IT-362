import requests

rec = requests.get('http://127.0.0.1:8000/api/business/record/fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec').json()
b_input = dict(rec.get('business_input', {}))
print('Baseline Capital:', b_input.get('available_capital_lkr'))
print('Baseline Feasibility:', rec.get('feasibility_analysis'))

# Now test what simulate endpoint does:
mod_input = dict(b_input)
# Change capital to 1,500,000
mod_input['available_capital_lkr'] = 1500000.0

resp = requests.post('http://127.0.0.1:8000/api/business/simulate?baseline_record_id=fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec', json=mod_input)
print('Simulate Status:', resp.status_code)
res = resp.json()
print('Simulate result:')
for k, v in res.items():
    print(f'  {k}: {v}')
