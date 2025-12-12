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

# Simplified Master List to match your raw data better
MASTER_LIST = [
    "Black Basketweave", "Black Real Leather", "Grey Basketweave", 
    "Grey Rodeo", "Brown Microweave", "Grey Five Bar", "MB Rodeo", 
    "Black Cloth", "Black Corduroy", "Black Pepita", "Real Leather", "Black Leatherette"
]

def clean_title(raw):
    # Simplifies "Black / Black Basketweave - ... Pre-Order" to just "Black Basketweave"
    t = str(raw).split(' - ')[0].strip()
    return t

def fetch_seat_data():
    now = datetime.now().strftime("%H:%M UTC")
    
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:10px;} h3{border-bottom:2px solid #333;padding-bottom:10px;} .ver{background:#3498db;color:white;padding:2px 5px;border-radius:3px;font-size:0.8em;} .date{font-size:0.8em;color:#666;float:right;} table{width:100%;border-collapse:collapse;margin-bottom:30px;} .title{background:#f4f4f4;padding:10px;font-weight:bold;} td{padding:10px;border-bottom:1px solid #eee;} a{text-decoration:none;color:#27ae60;font-weight:bold;} a.pre{color:#e67e22;}</style></head><body>')
    
    # FINAL VERSION
    h.append(f'<h3>In Stock in Portland <span class="ver">v13.0</span> <span class="date">{now}</span></h3>')

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
                is_available = v.get('available', False)
                
                # INTELLIGENT LOGIC:
                # 1. Is it technically in stock? -> YES
                # 2. Does it say "Pre-Order" in the name? -> YES
                is_preorder = "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper()
                
                # Determine Status
                status_text = ""
                status_class = ""
                
                if is_available:
                    status_text = "In Stock"
                elif is_preorder:
                    status_text = "Pre-Order"
                    status_class = "pre"
                
                # Only show if we have a valid status (Stock OR Pre-Order)
                if status_text:
                    clean = clean_title(raw_title)
                    rows += f'<tr><td>{clean}</td><td><a href="{link}" target="_parent" class="{status_class}">{status_text}</a></td></tr>'

            if rows:
                h.append(f'<div class="title">{model}</div><table>{rows}</tbody></table>')

        except Exception as e:
            pass # Keep silent on errors for the clean version

    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))

if __name__ == "__main__":
    fetch_seat_data()
