import os
import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
ZENROWS_API_KEY = os.environ.get("ZENROWS_API_KEY")

PRODUCT_BASE_URLS = {
    "Vario F": "https://scheel-mann.com/products/vario-f",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima"
}

DISPLAY_ORDER = [
    "Vario F",
    "Vario F Klima",
    "Vario F XXL",
    "Vario F XXL Klima"
]

SHOP_LINKS = {
    "Vario F": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "Vario F XXL": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "Vario F Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "Vario F XXL Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
}

COLORS = {
    "Black": "#000", "Real Leather": "#000", "Grey": "#666", 
    "Gray": "#666", "Brown": "#654321", "Tan": "#D2B48C"
}

def get_color_box(title):
    c = "#ccc" 
    if title:
        for k, v in COLORS.items():
            if k.upper() in title.upper():
                c = v
                break
    return f'<span class="box" style="background-color: {c};"></span>'

def clean_title(raw):
    t = str(raw)
    if ' / ' in t:
        t = t.split(' / ')[-1].strip()
    t = t.split(' - ')[0].strip()
    return t

def check_variant_html_for_preorder(base_url, variant_id):
    # Fetch the exact page render for this specific seat color
    variant_url = f"{base_url}?variant={variant_id}"
    payload = {'apikey': ZENROWS_API_KEY, 'url': variant_url, 'antibot': 'true'}
    try:
        resp = requests.get('https://api.zenrows.com/v1/', params=payload, timeout=45)
        if resp.status_code == 200:
            html = resp.text.lower()
            # Look for the exact warning text from the yellow banner
            if "out of stock and is available for pre-order" in html or "currently out of stock" in html:
                return True
    except Exception as e:
        pass
    return False

def fetch_seat_data():
    now = datetime.now().strftime("%H:%M UTC")
    
    if not ZENROWS_API_KEY:
        print("CRASH: ZenRows API Key not found in environment variables.")
        return
        
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:10px;} h3{border-bottom:2px solid #333;padding-bottom:10px;} .ver{background:#3498db;color:white;padding:2px 5px;border-radius:3px;font-size:0.8em;} .date{font-size:0.8em;color:#666;float:right;} table{width:100%;border-collapse:collapse;margin-bottom:30px;} .title{background:#f4f4f4;padding:10px;font-weight:bold;} td{padding:10px;border-bottom:1px solid #eee;} a{text-decoration:none;color:#27ae60;font-weight:bold;} a.pre{color:#e67e22;} .box{display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid #ccc;vertical-align:middle;}</style></head><body>')
    
    h.append(f'<h3>In Stock in Portland <span class="ver">v25.1</span> <span class="date">{now}</span></h3>')

    print("--- STARTING UPDATE v25.1 ---")

    categorized_rows = {m: "" for m in DISPLAY_ORDER}

    for model in DISPLAY_ORDER:
        base_url = PRODUCT_BASE_URLS[model]
        json_url = f"{base_url}.json"
        
        print(f"Fetching {model}...")
        
        try:
            # 1. Fetch JSON to get the variant IDs via ZenRows
            j_payload = {'apikey': ZENROWS_API_KEY, 'url': json_url, 'antibot': 'true'}
            j_resp = requests.get('https://api.zenrows.com/v1/', params=j_payload, timeout=60)
            
            if j_resp.status_code == 200:
                data = j_resp.json()
                variants = data.get('product', {}).get('variants', [])
                
                print(f"   Found {len(variants)} variants. Checking individual URLs...")
                link = SHOP_LINKS.get(model, "#")
                seen_titles = set()
                
                for v in variants:
                    raw_title = v.get('title', '')
                    if raw_title.lower() == 'default title':
                        continue
                        
                    clean = clean_title(raw_title)
                    if clean in seen_titles:
                        continue
                    seen_titles.add(clean)
                    
                    variant_id = v.get('id')
                    
                    # 2. Fetch the specific URL for this exact variant to read the page text via ZenRows
                    is_preorder = check_variant_html_for_preorder(base_url, variant_id)
                    
                    status_text = "Pre-Order" if is_preorder else "In Stock"
                    status_class = "pre" if is_preorder else "" 
                    print(f"      - {clean}: {status_text}")
                    
                    box = get_color_box(raw_title)
                    row_html = f'<tr><td>{box} {clean}</td><td><a href="{link}" target="_parent" class="{status_class}">{status_text}</a></td></tr>'
                    categorized_rows[model] += row_html
            else:
                print(f"   ERROR: Failed to fetch JSON. Status: {j_resp.status_code}")
        except Exception as e:
            print(f"   CRASH: {e}")

    for model in DISPLAY_ORDER:
        rows = categorized_rows[model]
        if rows:
            h.append(f'<div class="title">{model}</div><table>{rows}</tbody></table>')

    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))
    
    print("--- UPDATE COMPLETE ---")

if __name__ == "__main__":
    fetch_seat_data()
