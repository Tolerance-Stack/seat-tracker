import requests
import json
import re
from datetime import datetime

# 1. URLs
# We need both the HTML URL (for the full list) and the JS URL (for live status)
PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new"
}

# 2. Shop Links
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
    return f'<span class="color-box" style="background-color: {found_color};"></span>'

def fetch_seat_data():
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
    html_output = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="refresh" content="300">
    <style>
      body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }
      h3 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 0; }
      .sm-date { font-size: 0.8em; color: #666; float: right; font-weight: normal; margin-top: 5px;}
      .sm-status-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }
      .sm-seat-title { background-color: #f4f4f4; padding: 10px; margin: 0; border-left: 5px solid #333; font-weight: bold; font-size: 1.1em; }
      .sm-status-table th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em;}
      .sm-status-table td { padding: 10px; border-bottom: 1px solid #eee; vertical-align: middle; }
      .color-box { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; border: 1px solid #ccc; vertical-align: middle; }
      a.status-link { text-decoration: none; }
      a.status-link:hover { text-decoration: underline; }
      .status-available { color: #27ae60; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; }
      .status-preorder { color: #e67e22; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; }
      .option-unavailable { position: relative; display: inline-block; color: #666; padding: 0 4px; background: linear-gradient(to top left, transparent 46%, #888 49%, #888 51%, transparent 54%); }
      .text-unavailable { color: #999; font-style: italic; font-size: 0.9em; }
    </style>
    </head>
    <body>
      <h3>Scheel-Mann Status <span class="sm-date">Updated: TIME_STAMP</span></h3>
    """
    html_output = html_output.replace("TIME_STAMP", update_time)

    for model_name, base_url in PRODUCTS.items():
        try:
            print(f"--- Processing {model_name} ---")
            
            # STEP 1: Fetch LIVE status from .js feed (The "Truth")
            js_url = base_url + ".js"
            live_inventory = {}
            try:
                js_response = requests.get(js_url, headers={'User-Agent': 'Mozilla/5.0'})
                if js_response.status_code == 200:
                    js_data = js_response.json()
                    for v in js_data.get('variants', []):
                        # We map ID -> Available Status
                        live_inventory[v['id']] = v.get('available', False)
            except Exception as e:
                print(f"JS Fetch Error: {e}")

            # STEP 2: Fetch FULL LIST from HTML (The "Structure")
            response = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                # Find the main JSON blob
                match = re.search(r'id="ProductJson-product-template">\s*(\{[\s\S]*?\})\s*<\/script>', response.text)
                if not match:
                     match = re.search(r'id="ProductJson-[^"]*">\s*(\{[\s\S]*?\})\s*<\/script>', response.text)

                variants = []
                if match:
                    json_data = json.loads(match.group(1))
                    variants = json_data.get('variants', [])
                
                html_output += f'<div class="sm-seat-title">{model_name}</div>'
                html_output += '<table class="sm-status-table"><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>'
                target_link = SHOP_LINKS.get(model_name, "#")

                for variant in variants:
                    # Identify the variant
                    v_id = variant.get('id')
                    raw_title = variant.get('title') or variant.get('name') or "Unknown"
                    
                    # Clean Title
                    if ' / ' in str(raw_title):
                        clean_title = str(raw_title).split(' / ')[-1].strip()
                    else:
                        clean_title = str(raw_title)
                    clean_title = clean_title.split(' - CURRENTLY')[0].strip()
                    
                    color_box_html = get_color_box(clean_title)
                    
                    # STEP 3: THE MERGE LOGIC
                    # Check if this ID exists in the Live Inventory
                    if v_id in live_inventory:
                        # It is in the live feed, so we trust the live status
                        is_available = live_inventory[v_id]
                    else:
                        # It is NOT in the live feed, so it must be hidden/sold out
                        is_available = False
                    
                    is_preorder = "PRE-ORDER" in str(raw_title).upper() or "PRODUCTION" in str(raw_title).upper()

                    # Display Logic
                    if not is_available:
                        display = f'{color_box_html} <div class="option-unavailable">{clean_title}</div>'
                        status = '<span class="text-unavailable">Out of Stock</span>'
                    elif is_preorder:
                        display = f'{color_box_html} {clean_title}'
                        status = f'<a href="{target_link}" target="_parent" class="status-link"><span class="status-preorder">Pre-Order</span></a>'
                    else:
                        display = f'{color_box_html} {clean_title}'
                        status = f'<a href="{target_link}" target="_parent" class="status-link"><span class="status-available">In Stock</span></a>'

                    html_output += f'<tr><td>{display}</td><td>{status}</td></tr>'
                
                html_output += '</tbody></table>'

        except Exception as e:
            print(f"Error on {model_name}: {e}")
            
    html_output += "</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_output)

if __name__ == "__main__":
    fetch_seat_data()
