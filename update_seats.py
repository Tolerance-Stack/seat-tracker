import requests
import json
import re
from datetime import datetime

# 1. URLs
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

def clean_title(raw_title):
    if ' / ' in str(raw_title):
        ct = str(raw_title).split(' / ')[-1].strip()
    else:
        ct = str(raw_title)
    return ct.split(' - CURRENTLY')[0].strip()

def fetch_seat_data():
    # Use a real browser User-Agent to prevent blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
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
            
            # 1. Get JS Data (Reliable List & Status)
            js_variants = []
            live_inventory = {} # Dictionary to store True/False status by ID
            
            try:
                js_url = base_url + ".js"
                js_response = requests.get(js_url, headers=headers)
                if js_response.status_code == 200:
                    js_data = js_response.json()
                    js_variants = js_data.get('variants', [])
                    for v in js_variants:
                        live_inventory[v['id']] = v.get('available', False)
            except Exception as e:
                print(f"JS Fetch Warning: {e}")

            # 2. Get HTML Data (Deep Scan for hidden items)
            html_variants = []
            try:
                response = requests.get(base_url, headers=headers)
                if response.status_code == 200:
                    match = re.search(r'id="ProductJson-product-template">\s*(\{[\s\S]*?\})\s*<\/script>', response.text)
                    if not match:
                         match = re.search(r'id="ProductJson-[^"]*">\s*(\{[\s\S]*?\})\s*<\/script>', response.text)
                    
                    if match:
                        json_data = json.loads(match.group(1))
                        html_variants = json_data.get('variants', [])
                    else:
                        # Fallback to 'var meta' logic
                        match_meta = re.search(r'var meta = (\{[\s\S]*?"variants":[\s\S]*?\});', response.text)
                        if match_meta:
                            json_data = json.loads(match_meta.group(1))
                            html_variants = json_data.get('product', {}).get('variants', [])
            except Exception as e:
                print(f"HTML Fetch Warning: {e}")

            # 3. SAFETY NET LOGIC
            # If HTML scan found items, use them (preferred). 
            # If HTML scan found 0 items (failed), use JS variants (backup).
            if len(html_variants) > 0:
                final_list = html_variants
                source = "HTML (Deep Scan)"
            else:
                final_list = js_variants
                source = "JS (Backup)"
            
            print(f"Using source: {source} with {len(final_list)} items")

            # 4. Build Table
            html_output += f'<div class="sm-seat-title">{model_name}</div>'
            html_output += '<table class="sm-status-table"><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>'
            target_link = SHOP_LINKS.get(model_name, "#")

            for variant in final_list:
                v_id = variant.get('id')
                raw_title = variant.get('title') or variant.get('name') or "Unknown"
                
                cleaned_title_text = clean_title(raw_title)
                color_box_html = get_color_box(cleaned_title_text)
                
                # MERGE STATUS LOGIC
                # If we have live inventory data for this ID, use it.
                # If not (e.g. hidden item found in HTML but not JS), assume Unavailable.
                if v_id in live_inventory:
                    is_available = live_inventory[v_id]
                else:
                    # If we are using JS source, we trust the variant's own 'available' flag
                    # If we are using HTML source and it's missing from JS, it's unavailable.
                    if source == "JS (Backup)":
                         is_available = variant.get('available', False)
                    else:
                         is_available = False

                is_preorder = "PRE-ORDER" in str(raw_title).upper() or "PRODUCTION" in str(raw_title).upper()

                if not is_available:
                    display = f'{color_box_html} <div class="option-unavailable">{cleaned_title_text}</div>'
                    status = '<span class="text-unavailable">Out of Stock</span>'
                elif is_preorder:
                    display = f'{color_box_html} {cleaned_title_text}'
                    status = f'<a href="{target_link}" target="_parent" class="status-link"><span class="status-preorder">Pre-Order</span></a>'
                else:
                    display = f'{color_box_html} {cleaned_title_text}'
                    status = f'<a href="{target_link}" target="_parent" class="status-link"><span class="status-available">In Stock</span></a>'

                html_output += f'<tr><td>{display}</td><td>{status}</td></tr>'
            
            html_output += '</tbody></table>'

        except Exception as e:
            print(f"
