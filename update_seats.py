import requests
import json
import re
from datetime import datetime

# --- CONFIGURATION ---
PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new"
}

SHOP_LINKS = {
    "Vario F": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "Vario F XXL": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "Vario F Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "Vario F XXL Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
}

COLORS = {"Black": "#000", "Grey": "#666", "Gray": "#666", "Brown": "#654321", "Tan": "#D2B48C"}

# --- THE MASTER LIST ---
# Since the website hides sold out items, we hardcode the options we want to track.
# This guarantees they appear in the table.
MASTER_VARIANTS = [
    "Black Basketweave Cloth with Black Leatherette Bolsters",
    "Black Real Leather",
    "Grey Basketweave Cloth with Grey Leatherette Bolsters",
    "Grey Rodeo Plaid Cloth with Black Leatherette Bolsters",
    "Brown Microweave Cloth with Brown Leatherette Bolsters",
    "Brown Microweave Cloth with Black Leatherette Bolsters",
    "Black & Brown / Brown Microweave Cloth with Black Leatherette Bolsters"
]

def get_color_box(title):
    found_color = "#ccc" 
    if title:
        for color_name, hex_code in COLORS.items():
            if color_name.upper() in title.upper():
                found_color = hex_code
                break
    return f'<span class="box" style="background-color: {found_color};"></span>'

def clean_title(raw_title):
    t = str(raw_title)
    if ' / ' in t:
        t = t.split(' / ')[-1].strip()
    return t.split(' - CURRENTLY')[0].strip()

def fetch_seat_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
    html_parts = []
    html_parts.append('<!DOCTYPE html><html><head>')
    html_parts.append('<meta http-equiv="refresh" content="300">')
    html_parts.append('<style>')
    html_parts.append('body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }')
    html_parts.append('h3 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 0; }')
    html_parts.append('.date { font-size: 0.8em; color: #666; float: right; font-weight: normal; margin-top: 5px;}')
    html_parts.append('table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }')
    html_parts.append('.title { background-color: #f4f4f4; padding: 10px; margin: 0; border-left: 5px solid #333; font-weight: bold; font-size: 1.1em; }')
    html_parts.append('th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em;}')
    html_parts.append('td { padding: 10px; border-bottom: 1px solid #eee; vertical-align: middle; }')
    html_parts.append('.box { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; border: 1px solid #ccc; vertical-align: middle; }')
    html_parts.append('a { text-decoration: none; }')
    html_parts.append('a:hover { text-decoration: underline; }')
    html_parts.append('.avail { color: #27ae60; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }')
    html_parts.append('.pre { color: #e67e22; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }')
    html_parts.append('.out-box { position: relative; display: inline-block; color: #666; padding: 0 4px; background: linear-gradient(to top left, transparent 46%, #888 49%, #888 51%, transparent 54%); }')
    html_parts.append('.out-text { color: #999; font-style: italic; font-size: 0.9em; }')
    html_parts.append('</style></head><body>')
    html_parts.append(f'<h3>Scheel-Mann Status <span class="date">Updated: {update_time}</span></h3>')

    for model, url in PRODUCTS.items():
        try:
            print(f"--- Processing {model} ---")
            
            # 1. GET LIVE DATA (The "Truth" about what is active)
            live_items = []
            try:
                js_resp = requests.get(url + ".js", headers=headers)
                if js_resp.status_code == 200:
                    live_items = js_resp.json().get('variants', [])
            except Exception as e:
                print(f"JS Error: {e}")

            # 2. BUILD THE ROW DATA
            # We start with our Master List of expected seats
            # We also merge in any new ones found in the live feed that we missed
            
            # Normalize names for comparison
            processed_rows = []
            
            # Create a dictionary of live items for fast lookup by cleaned name
            live_lookup = {}
            for v in live_items:
                raw = v.get('title') or "Unknown"
                # Remove prefixes for matching
                clean_name = clean_title(raw)
                live_lookup[clean_name] = v

            # Merge Master List + Live Found List
            all_variant_names = sorted(list(set(MASTER_VARIANTS + list(live_lookup.keys()))))

            html_parts.append(f'<div class="title">{model}</div>')
            html_parts.append('<table><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>')
            link = SHOP_LINKS.get(model, "#")

            for name in all_variant_names:
                # Clean the name for display
                clean = clean_title(name)
                
                # We filter out some junk combinations if needed
                if "Default Title" in clean: continue

                color = get_color_box(clean)
                
                # STATUS CHECK
                if clean in live_lookup:
                    # It exists in the live feed!
                    v = live_lookup[clean]
                    is_avail = v.get('available', False)
                    raw_title = v.get('title', '')
                    is_pre = "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper()
                else:
                    # It is NOT in the live feed -> It is definitely Out of Stock
                    is_avail = False
                    is_pre = False

                # DISPLAY LOGIC
                if not is_avail:
                    disp = f'{color} <div class="out-box">{clean}</div>'
                    stat = '<span class="out-text">Out of Stock</span>'
                elif is_pre:
                    disp = f'{color} {clean}'
                    stat = f'<a href="{link}" target="_parent"><span class="pre">Pre-Order</span></a>'
                else:
                    disp = f'{color} {clean}'
                    stat = f'<a href="{link}" target="_parent"><span class="avail">In Stock</span></a>'

                html_parts.append(f'<tr><td>{disp}</td><td>{stat}</td></tr>')
            
            html_parts.append('</tbody></table>')

        except Exception as e:
            print(f"Error: {e}")
            
    html_parts.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(html_parts))

if __name__ == "__main__":
    fetch_seat_data()
