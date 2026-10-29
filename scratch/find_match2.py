import requests

rec = requests.get('http://127.0.0.1:8000/api/business/record/fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec').json()
b_input = dict(rec.get('business_input', {}))

# Check what slider changes produce:
# Viability Delta: -2.3% (-0.023)
# Feasible: -6.5% (-0.065)
# Conditional: +8.5% (+0.085)
# Infeasible: -2.0% (-0.02)
# Notice: -0.065 + 0.5 * 0.085 = -0.065 + 0.0425 = -0.0225 = -2.3%! That is EXACT!

# Let's test combinations of budget or capital:
for budget in [30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 120000, 150000, 200000, 300000]:
    mod_input = dict(b_input)
    mod_input['monthly_budget_lkr'] = float(budget)
    resp = requests.post('http://127.0.0.1:8000/api/business/simulate?baseline_record_id=fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec', json=mod_input)
    res = resp.json()
    pd = res.get('probability_deltas', {})
    if abs(pd.get('Feasible', 0) - (-0.065)) < 0.005:
        print(">>> MATCH FOUND IN BUDGET:", budget, pd)
        break

for cust in range(5, 100, 5):
    mod_input = dict(b_input)
    mod_input['expected_customers_per_day'] = cust
    resp = requests.post('http://127.0.0.1:8000/api/business/simulate?baseline_record_id=fcbccdcd-bafe-42d3-b6e5-89d45a2da1ec', json=mod_input)
    res = resp.json()
    pd = res.get('probability_deltas', {})
    if abs(pd.get('Feasible', 0) - (-0.065)) < 0.005:
        print(">>> MATCH FOUND IN CUST:", cust, pd)
        break
