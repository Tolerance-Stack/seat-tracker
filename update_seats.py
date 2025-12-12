import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f.json",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl.json",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima.json",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new.json"
}

SHOP_LINKS = {
    "Vario F": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "Vario F XXL": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "Vario F Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "Vario F XXL Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
}

# Color Mapping for the little boxes
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
    # Cleans "Black / Black Basketweave - CURRENTLY IN PRODUCTION" -> "Black Basketweave"
    t = str(raw)
    if ' / ' in t:
        t = t.split(' / ')[-1].strip()
    t = t.split(' - ')[0].strip()
    return t

def fetch_seat_data():
    now = datetime.now().strftime("%H:%M UTC")
    
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:10px;} h3{border-bottom:2px solid #333;padding-bottom:10px;} .ver{background:#3498db;color:white;padding:2px 5px;border-radius:3px;font-size:0.8em;} .date{font-size:0.8em;color:#666;float:right;} table{width:100%;border-collapse:collapse;margin-bottom:30px;} .title{background:#f4f4f4;padding:10px;font-weight:bold;} td{padding:10px;border-bottom:1px solid #eee;} a{text-decoration:none;color:#27ae60;font-weight:bold;} a.pre{color:#e67e22;} .box{display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid #ccc;vertical-align:middle;}</style></head><body>')
    
    # v15.0 BADGE
    h.append(f'<h3>In Stock in Portland <span class="ver">v15.0</span> <span class="date">{now}</span></h3>')

    headers = {'User-Agent': 'Mozilla/5.0'}

    for model, url in PRODUCTS.items():
        try:
            link = SHOP_LINKS.get(model, "#")
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200: continue

            data = resp.json()
            variants = data.get('product', {}).get('variants', [])
            rows = ""

            for v in variants:
                raw_title = v.get('title', '')
                
                # --- NEW LOGIC START ---
                # Check the NAME for the "Pre-Order" warning.
                is_preorder_text = "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper()
                
                status_text = ""
                status_class = ""
                
                if is_preorder_text:
                    # If name says "Pre-Order", mark it Orange
                    status_text = "Pre-Order"
                    status_class = "pre"
                else:
                    # If name is CLEAN, assume it is IN STOCK (Green)
                    # We ignore the hidden 'available' flag because it lies.
                    status_text = "In Stock"
                    status_class = "" # Default Green style
                
                # --- NEW LOGIC END ---

                if status_text:
                    clean = clean_title(raw_title)
                    box = get_color_box(raw_title)
                    rows += f'<tr><td>{box} {clean}</td><td><a href="{link}" target="_parent" class="{status_class}">{status_text}</a></td></tr>'

            if rows:
                h.append(f'<div class="title">{model}</div><table>{rows}</tbody></table>')

        except Exception as e:
            pass 

    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))

if __name__ == "__main__":
    fetch_seat_data()
