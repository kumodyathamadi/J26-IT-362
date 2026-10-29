import yaml
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

with open(REPO_ROOT / 'data/compliance/rulebook/draft_rules.yaml', encoding='utf-8') as f:
    rulebook = yaml.safe_load(f)

for o in rulebook['obligations']:
    doc_id = o['evidence']['doc_id']
    page_num = o['evidence']['page']
    quote = o['evidence']['quote'].strip()
    
    json_path = REPO_ROOT / f'data/text/{doc_id}.json'
    with open(json_path, encoding='utf-8') as pf:
        pages = json.load(pf)
    
    matching_page = next((p for p in pages if p['page'] == page_num), None)
    if not matching_page:
        print(f"FAIL: Page {page_num} not found in {doc_id}")
        sys.exit(1)
        
    page_text = " ".join(matching_page['text'].split())
    quote_clean = " ".join(quote.split())
    
    if quote_clean.lower() in page_text.lower():
        print(f"VERIFIED: {o['id']} in {doc_id} (Page {page_num})")
    else:
        print(f"MISMATCH: {o['id']} in {doc_id} (Page {page_num})")
        print("Expected:", quote_clean[:100])
        print("Page text snippet:", page_text[:200])
