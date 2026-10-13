import requests
import json
from datetime import datetime
import time
import urllib.parse

# --- CONFIGURATION ---
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

TARGET_MODELS = [
    "Vario F XXL Klima",
    "Vario F XXL",
    "Vario F Klima",
    "Vario F"
]

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

def fetch_seat_data():
    now = datetime.now().strftime("%H:%M UTC")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
    }

    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:10px;} h3{border-bottom:2px solid #333;padding-bottom:10px;} .ver{background:#3498db;color:white;padding:2px 5px;border-radius:3px;font-size:0.8em;} .date{font-size:0.8em;color:#666;float:right;} table{width:100%;border-collapse:collapse;margin-bottom:30px;} .title{background:#f4f4f4;padding:10px;font-weight:bold;} td{padding:10px;border-bottom:1px solid #eee;} a{text-decoration:none;color:#27ae60;font-weight:bold;} a.pre{color:#e67e22;} .box{display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid #ccc;vertical-align:middle;}</style></head><body>')
    
    h.append(f'<h3>In Stock in Portland <span class="ver">v18.0</span> <span class="date">{now}</span></h3>')

    print("--- STARTING UPDATE v18.0 ---")

    try:
        # 1. Build target URL with cache buster
        target_url = f"https://scheel-mann.com/collections/stocked-seating/products.json?limit=250&nocache={int(time.time())}"
        
        # 2. Encode and append to the proxy service to bypass Shopify's IP block
        encoded_url = urllib.parse.quote(target_url, safe='')
        proxy_url = f"https://api.allorigins.win/raw?url={encoded_url}"
        
        print("Fetching data through proxy to bypass IP block...")
        resp = requests.get(proxy_url, headers=headers, timeout=20)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            products = data.get('products', [])
            print(f"Found {len(products)} total products in collection.")
            
            categorized_rows = {m: "" for m in TARGET_MODELS}

            for p in products:
                p_title = p.get('title', '')
                variants = p.get('variants', [])
                
                matched_model = None
                for m in TARGET_MODELS:
                    if m.upper() in p_title.upper():
                        matched_model = m
                        break
                
                if not matched_model:
                    continue

                link = SHOP_LINKS.get(matched_model, "#")
                
                for v in variants:
                    raw_title = v.get('title', '')
                    
                    display_title = raw_title
                    if display_title.lower() == 'default title':
                        display_title = p_title.replace(matched_model, '').strip(" -")
                        if not display_title:
                            display_title = p_title
                            
                    is_preorder = "PRE-ORDER" in display_title.upper() or "PRODUCTION" in display_title.upper()
                    status_text = "Pre-Order" if is_preorder else "In Stock"
                    status_class = "pre" if is_preorder else "" 
                    
                    clean = clean_title(display_title)
                    box = get_color_box(display_title + " " + p_title)
                    
                    row_html = f'<tr><td>{box} {clean}</td><td><a href="{link}" target="_parent" class="{status_class}">{status_text}</a></td></tr>'
                    categorized_rows[matched_model] += row_html

            for model in reversed(TARGET_MODELS):
                rows = categorized_rows[model]
                if rows:
                    h.append(f'<div class="title">{model}</div><table>{rows}</tbody></table>')
                    
        else:
            print(f"ERROR: Failed to fetch collection. Content: {resp.text[:100]}")
            h.append('<p style="color:red;">Error syncing with Scheel-mann database. Retrying soon.</p>')

    except Exception as e:
        print(f"CRASH: {e}")

    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))
    
    print("--- UPDATE COMPLETE ---")

if __name__ == "__main__":
    fetch_seat_data()
