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

COLORS = {"Black": "#000", "Grey": "#666", "Gray": "#666", "Brown": "#654321", "Tan": "#D2B48C"}

# --- MASTER LIST (For Name Cleaning & Out-of-Stock Detection) ---
MASTER_LIST = [
    "Black Basketweave Cloth with Black Leatherette Bolsters",
    "Black Real Leather",
    "Grey Basketweave Cloth with Grey Leatherette Bolsters",
    "Grey Rodeo Plaid Cloth with Black Leatherette Bolsters",
    "Brown Microweave Cloth with Brown Leatherette Bolsters",
    "Brown Microweave Cloth with Black Leatherette Bolsters",
    "Grey Five Bar Cloth with Black Leatherette Bolsters",
    "MB Rodeo Grey Cloth with Black Leatherette Bolsters",
    "Black Cloth with Black Leatherette Bolsters",
    "Black Corduroy Cloth with Black Leatherette Bolsters",
    "Black Pepita Cloth with Black Leatherette Bolsters",
    "Black & Brown / Brown Microweave Cloth with Black Leatherette Bolsters",
    "Real Leather", 
    "Black Leatherette"
]

def get_color_box(title):
    found_color = "#ccc" 
    if title:
        for k, v in COLORS.items():
            if k.upper() in title.upper():
                found_color = v
                break
    return f'<span class="box" style="background-color: {found_color};"></span>'

def clean_title(raw_title):
    t = str(raw_title)
    if ' / ' in t:
        t = t.split(' / ')[-1].strip()
    t = t.split(' - ')[0].strip()
    return t

def fetch_seat_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
    # HTML HEADER
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>')
    h.append('body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }')
    h.append('h3 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 0; }')
    h.append('.date { font-size: 0.8em; color: #666; float: right; font-weight: normal; margin-top: 5px; }')
    h.append('table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }')
    h.append('.title { background-color: #f4f4f4; padding: 10px; margin: 0; border-left: 5px solid #333; font-weight: bold; font-size: 1.1em; }')
    h.append('th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em; }')
    h.append('td { padding: 10px; border-bottom: 1px solid #eee; vertical-align: middle; }')
    h.append('.box { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; border: 1px solid #ccc; vertical-align: middle; }')
    h.append('a { text-decoration: none; }')
    h.append('a:hover { text-decoration: underline; }')
    h.append('.avail { color: #27ae60; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }')
    h.append('.pre { color: #e67e22; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }')
    h.append('.out-box { display: inline-block; color: #aaa; background: linear-gradient(to top left, transparent 46%, #999 49%, #999 51%, transparent 54%); }')
    h.append('.out-text { color: #999; font-style: italic; font-size: 0.9em; }')
    h.append('</style></head><body>')
    
    h.append(f'<h3>Scheel-Mann Vario Seats In Stock in Portland <span class="date">Updated: {update_time}</span></h3>')

    for model, url in PRODUCTS.items():
        try:
            print(f"--- Processing {model} ---")
            
            # Track which Master items we found
            found_master_items = set()
            
            h.append(f'<div class="title">{model}</div>')
            h.append('<table><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>')
            link = SHOP_LINKS.get(model, "#")

            # 1. PROCESS LIVE ITEMS (Allows Duplicates/Multiple Batches)
            try:
                resp = requests.get(url, headers=headers)
                if resp.status_code == 200:
                    variants = resp.json().get('variants', [])
                    
                    for v in variants:
                        raw = v.get('title', '')
                        clean = clean_title(raw)
                        
                        # Only process if it matches one of our Known Master Items
                        # This filters out "Option 12345" or "Default Title" junk
                        matched_master_name = None
                        for m in MASTER_LIST:
                            if m in clean or clean in m:
                                matched_master_name = m
                                found_master_items.add(m) # Mark as found
                                break
                        
                        if matched_master_name and v.get('available', False):
                            # It's a valid seat and it's available!
                            color = get_color_box(matched_master_name)
                            is_pre = "PRE-ORDER" in raw.upper() or "PRODUCTION" in raw.upper()
                            
                            if is_pre:
                                disp = f'{color} {matched_master_name}'
                                stat = f'<a href="{link}" target="_parent"><span class="pre">Pre-Order</span></a>'
                            else:
                                disp = f'{color} {matched_master_name}'
                                stat = f'<a href="{link}" target="_parent"><span class="avail">In Stock</span></a>'
                            
                            h.append(f'<tr><td>{disp}</td><td>{stat}</td></tr>')

            except Exception as e:
                print(f"Error fetching live: {e}")

            # 2. PROCESS MISSING ITEMS (Force "Out of Stock" display)
            for m in MASTER_LIST:
                if m not in found_master_items:
                    # If we didn't see it in the live scan, it's sold out
                    color = get_color_box(m)
                    disp = f'{color} <div class="out-box">{m}</div>'
                    stat = '<span class="out-text">Out of Stock</span>'
                    h.append(f'<tr><td>{disp}</td><td>{stat}</td></tr>')

            h.append('</tbody></table>')

        except Exception as e:
            print(f"Critical Error: {e}")
            
    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))

if __name__ == "__main__":
    fetch_seat_data()
