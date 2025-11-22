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

def get_color_box(title):
    found_color = "#ccc" 
    if title:
        for color_name, hex_code in COLORS.items():
            if color_name.upper() in title.upper():
                found_color = hex_code
                break
    return f'<span class="box" style="background-color: {found_color};"></span>'

def clean_title(raw_title):
    # Remove status text from the dropdown name
    t = str(raw_title)
    t = re.sub(r'\s*-\s*(Sold Out|Unavailable|Pre-Order|In Production).*', '', t, flags=re.IGNORECASE)
    if ' / ' in t:
        t = t.split(' / ')[-1].strip()
    return t.strip()

def fetch_seat_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
    # HTML HEADER
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
    html_parts.append(f'<h3>Scheel-Mann Vario In-Stock Status <span class="date">Updated: {update_time}</span></h3>')

    for model, url in PRODUCTS.items():
        try:
            print(f"--- Processing {model} ---")
            
            # 1. LIVE STATUS (Get the Truth from the AJAX feed)
            live_map = {}
            try:
                js_resp = requests.get(url + ".js", headers=headers)
                if js_resp.status_code == 200:
                    for v in js_resp.json().get('variants', []):
                        live_map[v['id']] = v.get('available', False)
            except:
                pass

            # 2. FULL LIST (Dropdown Scraping)
            variants_found = []
            try:
                resp = requests.get(url, headers=headers)
                if resp.status_code == 200:
                    # Look for <option value="12345">Name</option>
                    matches = re.findall(r'<option\s+value="(\d+)"[^>]*>(.*?)</option>', resp.text)
                    
                    for vid, raw_name in matches:
                        raw_name = raw_name.replace('\n', '').strip()
                        # IMPORTANT: Filter out generic "Select Option" placeholder if it exists
                        if "Select" not in raw_name:
                            variants_found.append({'id': int(vid), 'title': raw_name})
                    
                    print(f"Dropdown Scan found {len(variants_found)} items")

            except Exception as e:
                print(f"Scan Error: {e}")

            # 3. BUILD TABLE
            html_parts.append(f'<div class="title">{model}</div>')
            html_parts.append('<table><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>')
            link = SHOP_LINKS.get(model, "#")

            # Fallback if scan fails
            if not variants_found and live_map:
                 print("Using Live Map backup")
                 variants_found = [{'id': k, 'title': 'Option ' + str(k)} for k in live_map.keys()]

            for v in variants_found:
                vid = v['id']
                raw = v['title']
                clean = clean_title(raw)
                color = get_color_box(clean)
                
                # STATUS LOGIC
                if vid in live_map:
                    is_avail = live_map[vid]
                else:
                    is_avail = False

                is_pre = "PRE-ORDER" in str(raw).upper() or "PRODUCTION" in str(raw).upper()

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
            print(f"Critical Error: {e}")
            
    html_parts.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(html_parts))

if __name__ == "__main__":
    fetch_seat_data()
