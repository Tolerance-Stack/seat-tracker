import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f.js",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl.js",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima.js",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new.js"
}

SHOP_LINKS = {
    "Vario F": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "Vario F XXL": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "Vario F Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "Vario F XXL Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
}

# --- SMART MATCHING RULES ---
# Instead of exact names, we match by KEYWORDS.
# Format: ("Display Name", ["Must Have Word 1", "Must Have Word 2"])
SEAT_DEFINITIONS = [
    ("Black Basketweave", ["Black", "Basketweave"]),
    ("Black Real Leather", ["Black", "Real", "Leather"]),
    ("Grey Basketweave", ["Grey", "Basketweave"]),
    ("Grey Rodeo Plaid", ["Grey", "Rodeo"]),
    ("Brown Microweave", ["Brown", "Microweave"]),
    ("Black Leatherette", ["Black", "Leatherette"]),
    ("Grey Five Bar", ["Grey", "Five", "Bar"]),
    ("Black Corduroy", ["Black", "Corduroy"]),
    ("Black Pepita", ["Black", "Pepita"]),
    ("Real Leather", ["Real", "Leather"]) # Catch-all for Klima
]

COLORS = {"Black": "#000", "Grey": "#666", "Gray": "#666", "Brown": "#654321", "Tan": "#D2B48C"}

def get_color_box(title):
    c = "#ccc" 
    if title:
        for k, v in COLORS.items():
            if k.upper() in title.upper():
                c = v
                break
    return f'<span class="box" style="background-color: {c};"></span>'

def fetch_seat_data():
    ua = {'User-Agent': 'Mozilla/5.0'}
    now = datetime.now().strftime("%H:%M UTC")
    
    # HTML HEADER
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<meta http-equiv="cache-control" content="no-cache">')
    h.append('<style>')
    h.append('body { font-family: sans-serif; padding: 10px; }')
    h.append('h3 { border-bottom: 2px solid #333; padding-bottom: 10px; }')
    h.append('.ver { background: #663399; color: white; padding: 2px 5px; border-radius: 3px; font-size: 0.8em; }') # Purple Badge
    h.append('.date { font-size: 0.8em; color: #666; float: right; }')
    h.append('table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }')
    h.append('.title { background: #f4f4f4; padding: 10px; font-weight: bold; }')
    h.append('th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; }')
    h.append('td { padding: 10px; border-bottom: 1px solid #eee; }')
    h.append('.box { display: inline-block; width: 12px; height: 12px; margin-right: 8px; border: 1px solid #ccc; }')
    h.append('a { text-decoration: none; color: #27ae60; font-weight: bold; }')
    h.append('a.pre { color: #e67e22; }')
    h.append('</style></head><body>')
    
    # v4.0 Badge (Purple)
    h.append(f'<h3>In Stock in Portland <span class="ver">v4.0</span> <span class="date">{now}</span></h3>')

    for model, url in PRODUCTS.items():
        try:
            print(f"Checking {model}...")
            
            rows = ""
            link = SHOP_LINKS.get(model, "#")

            try:
                resp = requests.get(url, headers=ua)
                if resp.status_code == 200:
                    for v in resp.json().get('variants', []):
                        raw_title = v.get('title', '')
                        
                        # Only process Available items
                        if v.get('available', False):
                            
                            # --- SMART MATCHING LOGIC ---
                            display_name = None
                            for name, keywords in SEAT_DEFINITIONS:
                                # Check if ALL keywords are in the raw title
                                if all(k.upper() in raw_title.upper() for k in keywords):
                                    display_name = name
                                    break
                            
                            # If we found a match, display it
                            if display_name:
                                box = get_color_box(display_name)
                                is_pre = "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper()
                                
                                # If it's the second pre-order batch, let's keep it visible
                                # We use the Display Name we defined to keep the list clean
                                
                                row_start = f'<tr><td>{box} {display_name}</td>'
                                
                                if is_pre:
                                    stat = f'<td><a href="{link}" target="_parent" class="pre">Pre-Order</a></td></tr>'
                                else:
                                    stat = f'<td><a href="{link}" target="_parent">In Stock</a></td></tr>'
                                
                                rows += row_start + stat
            except:
                pass

            if rows:
                h.append(f'<div class="title">{model}</div>')
                h.append('<table><thead><tr><th width="70%">Option</th><th>Status</th></tr></thead><tbody>')
                h.append(rows)
                h.append('</tbody></table>')

        except Exception as e:
            print(f"Error: {e}")
            
    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))

if __name__ == "__main__":
    fetch_seat_data()
