import requests
import json
from datetime import datetime
import time
import random

# --- CONFIGURATION ---
PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f.json",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl.json",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima.json",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima.json"
}

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

def fetch_seat_data():
    now = datetime.now().strftime("%H:%M UTC")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://scheel-mann.com/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:10px;} h3{border-bottom:2px solid #333;padding-bottom:10px;} .ver{background:#3498db;color:white;padding:2px 5px;border-radius:3px;font-size:0.8em;} .date{font-size:0.8em;color:#666;float:right;} table{width:100%;border-collapse:collapse;margin-bottom:30px;} .title{background:#f4f4f4;padding:10px;font-weight:bold;} td{padding:10px;border-bottom:1px solid #eee;} a{text-decoration:none;color:#27ae60;font-weight:bold;} a.pre{color:#e67e22;} .box{display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid #ccc;vertical-align:middle;}</style></head><body>')
    
    h.append(f'<h3>In Stock in Portland <span class="ver">v16.2</span> <span class="date">{now}</span></h3>')

    print("--- STARTING UPDATE v16.2 ---")

    for model, url in PRODUCTS.items():
        print(f"Checking {model}...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # CACHE BUSTER: Appends a random timestamp query to bypass Cloudflare sticky blocks
                buster_url = f"{url}?nocache={int(time.time())}{random.randint(10,99)}"
                
                time.sleep(10) 
                
                resp = requests.get(buster_url, headers=headers, timeout=15)
                print(f"   Attempt {attempt+1} - Status Code: {resp.status_code}")
                
                if resp.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 15 * (attempt + 1)
                        print(f"   Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("   Failed after 3 attempts.")
                        break
                
                if resp.status_code != 200:
                    print(f"   ERROR: Blocked or Not Found. Content: {resp.text[:100]}")
                    break

                try:
                    data = resp.json()
                except json.JSONDecodeError:
                    print("   ERROR: Response was not JSON.")
                    break

                variants = data.get('product', {}).get('variants', [])
                print(f"   Found {len(variants)} variants.")
                
                rows = ""
                link = SHOP_LINKS.get(model, "#")

                for v in variants:
                    raw_title = v.get('title', '')
                    is_preorder_text = "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper()
                    status_text = "Pre-Order" if is_preorder_text else "In Stock"
                    status_class = "pre" if is_preorder_text else "" 
                    
                    clean = clean_title(raw_title)
                    box = get_color_box(raw_title)
                    rows += f'<tr><td>{box} {clean}</td><td><a href="{link}" target="_parent" class="{status_class}">{status_text}</a></td></tr>'

                if rows:
                    h.append(f'<div class="title">{model}</div><table>{rows}</tbody></table>')
                
                break 

            except Exception as e:
                print(f"   CRASH on {model}: {e}")
                break

    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))
    
    print("--- UPDATE COMPLETE ---")

if __name__ == "__main__":
    fetch_seat_data()
