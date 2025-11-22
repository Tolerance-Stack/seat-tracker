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

# --- HELPER FUNCTIONS ---
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

# --- MAIN SCRIPT ---
def fetch_seat_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="refresh" content="300">
    <style>
      body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }
      h3 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 0; }
      .date { font-size: 0.8em; color: #666; float: right; font-weight: normal; margin-top: 5px;}
      table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }
      .title { background-color: #f4f4f4; padding: 10px; margin: 0; border-left: 5px solid #333; font-weight: bold; font-size: 1.1em; }
      th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em;}
      td { padding: 10px; border-bottom: 1px solid #eee; vertical-align: middle; }
      .box { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; border: 1px solid #ccc; vertical-align: middle; }
      a { text-decoration: none; }
      a:hover { text-decoration: underline; }
      .avail { color: #27ae60; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
      .pre { color: #e67e22; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
      .out-box { position: relative; display: inline-block; color: #666; padding: 0 4px; background: linear-gradient(to top left, transparent 46%, #888 49%, #888 51%, transparent 54%); }
      .out-text { color: #999; font-style: italic; font-size: 0.9em; }
    </style>
    </head>
    <body>
      <h3>Scheel-Mann Status <span class="date">Updated: TIME_STAMP</span></h3>
    """
    html = html.replace("TIME_STAMP", update_time)

    for model, url in PRODUCTS.items():
        try:
            print(f"--- Processing {model} ---")
            
            # 1. LIVE STATUS (Truth Source)
            live_map = {}
            try:
                js_resp = requests.get(url + ".js", headers=headers)
                if js_resp.status_code == 200:
                    for v in js_resp.json().get('variants', []):
                        live_map[v['id']] = v.get('available', False)
            except:
                pass

            # 2. FULL LIST (Smart Hunter)
            variants = []
            try:
                resp = requests.get(url, headers=headers)
                if resp.status_code == 200:
                    # Find ALL script tags containing JSON
                    candidates = re.findall(r'<script[^>]*application/json[^>]*>([\s\S]*?)</script>', resp.text)
                    
                    # Also look for the standard Shopify ProductJson tags
                    candidates += re.findall(r'id="ProductJson-[^"]*">\s*(\{[\s\S]*?\})\s*<\/script>', resp.text)

                    best_candidate = []
                    for c in candidates:
                        try:
                            data = json.loads(c)
                            # Some JSONs are wrapped in 'product', some are direct
                            vs = data.get('variants') or data.get('product', {}).get('variants', [])
                            
                            # We want the list with the MOST items (The Main Product)
                            if len(vs) > len(best_candidate):
                                best_candidate = vs
                        except:
                            continue
                    
                    variants = best_candidate

            except Exception as e:
                print(f"HTML Scan Error: {e}")

            # 3. SAFETY FALLBACK
            source_type = "HTML"
            if not variants:
                print("Using JS Backup")
                # Re-fetch JS list to use as main list
                if live_map: 
                     # We fetch the JS again to get the full object structure
                     js_bk = requests.get(url + ".js", headers=headers).json().get('variants', [])
                     variants = js_bk
                     source_type = "JS"

            # 4. BUILD TABLE
            html += f'<div class="title">{model}</div>'
            html += '<table><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>'
            link = SHOP_LINKS.get(model, "#")

            for v in variants:
                vid = v.get('id')
                raw = v.get('title') or v.get('name') or "Unknown"
                clean = clean_title(raw)
                color = get_color_box(clean)
                
                # MERGE STATUS LOGIC
                if vid in live_map:
                    is_avail = live_map[vid]
                else:
                    # If using JS source, trust item. If HTML source, missing means out.
                    is_avail = v.get('available', False) if source_type == "JS" else False

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

                html += f'<tr><td>{disp}</td><td>{stat}</td></tr>'
            
            html += '</tbody></table>'

        except Exception as e:
            print(f"Error: {e}")
            
    html += "</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    fetch_seat_data()
