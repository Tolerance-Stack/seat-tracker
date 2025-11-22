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
    html_parts.append('</style></head><body>')
    html_parts.append(f'<h3>Scheel-Mann Status <span class="date">Updated: {update_time}</span></h3>')

    for model, url in PRODUCTS.items():
        try:
            print(f"--- Processing {model} ---")
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                variants = data.get('variants', [])
                
                html_parts.append(f'<div class="title">{model}</div>')
                html_parts.append('<table><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>')
                link = SHOP_LINKS.get(model, "#")

                for v in variants:
                    raw = v.get('title') or "Unknown"
                    clean = clean_title(raw)
                    color = get_color_box(clean)
                    
                    is_avail = v.get('available', False)
                    is_pre = "PRE-ORDER" in str(raw).upper() or "PRODUCTION" in str(raw).upper()

                    if is_avail:
                        if is_pre:
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
