import requests
import json
import re
from datetime import datetime

# --- CONFIGURATION ---
SCRAPER_API_KEY = "c288ebe9bae2045147af00f7de7d2c43"

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

def get_inventory_from_html(html, variant_id):
    # Forward search: pinpoint the exact ID and extract the nearest hidden inventory quantity
    fw_pattern = r'["\']id["\']\s*:\s*' + str(variant_id) + r'(?:(?!["\']id["\']\s*:).){0,500}?["\']inventory_quantity["\']\s*:\s*(-?\d+)'
    fw_match = re.search(fw_pattern, html, re.DOTALL)
    if fw_match:
        return int(fw_match.group(1))
        
    # Backward search failsafe
    bw_pattern = r'["\']inventory_quantity["\']\s*:\s*(-?\d+)(?:(?!["\']id["\']\s*:).){0,500}?["\']id["\']\s*:\s*' + str(variant_id)
    bw_match = re.search(bw_pattern, html, re.DOTALL)
    if bw_match:
        return int(bw_match.group(1))
        
    return 1 # Default to in-stock if completely obscured

def fetch_seat_data():
    now = datetime.now().strftime("%H:%M UTC")
    
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:10px;} h3{border-bottom:2px solid #333;padding-bottom:10px;} .ver{background:#3498db;color:white;padding:2px 5px;border-radius:3px;font-size:0.8em;} .date{font-size:0.8em;color:#666;float:right;} table{width:100%;border-collapse:collapse;margin-bottom:30px;} .title{background:#f4f4f4;padding:10px;font-weight:bold;} td{padding:10px;border-bottom:1px solid #eee;} a{text-decoration:none;color:#27ae60;font-weight:bold;} a.pre{color:#e67e22;} .box{display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid #ccc;vertical-align:middle;}</style></head><body>')
    
    h.append(f'<h3>In Stock in Portland <span class="ver">v22.0</span> <span class="date">{now}</span></h3>')

    print("--- STARTING UPDATE v22.0 ---")

    categorized_rows = {m: "" for m in DISPLAY_ORDER}

    for model in DISPLAY_ORDER:
        base_url = PRODUCT_BASE_URLS[model]
        json_url = f"{base_url}.json"
        
        print(f"Fetching Hybrid Data for {model}...")
        
        try:
            # 1. Fetch JSON to get the clean IDs and titles
            j_payload = {'api_key': SCRAPER_API_KEY, 'url': json_url}
            j_resp = requests.get('http://api.scraperapi.com', params=j_payload, timeout=60)
            
            # 2. Fetch HTML to parse the hidden inventory numbers
            h_payload = {'api_key': SCRAPER_API_KEY, 'url': base_url}
            h_resp = requests.get('http://api.scraperapi.com', params=h_payload, timeout=60)
            
            print(f"   JSON Status: {j_resp.status_code} | HTML Status: {h_resp.status_code}")
            
            if j_resp.status_code == 200 and h_resp.status_code == 200:
                data = j_resp.json()
                product = data.get('product', {})
                variants = product.get('variants', [])
                html_content = h_resp.text
                
                print(f"   Found {len(variants)} variants.")
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
                    
                    # Extract real inventory from the raw HTML code using the ID
                    qty = get_inventory_from_html(html_content, variant_id)
                    
                    is_preorder = (qty <= 0)
                    status_text = "Pre-Order" if is_preorder else "In Stock"
                    status_class = "pre" if is_preorder else "" 
                    
                    box = get_color_box(raw_title)
                    row_html = f'<tr><td>{box} {clean}</td><td><a href="{link}" target="_parent" class="{status_class}">{status_text}</a></td></tr>'
                    categorized_rows[model] += row_html
                    
            else:
                print(f"   ERROR: Failed to fetch. JSON: {j_resp.status_code}, HTML: {h_resp.status_code}")
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
