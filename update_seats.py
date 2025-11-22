import requests
import json
import re
from datetime import datetime

# 1. URLs (Deep Scan)
URLS = {
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

# 3. Color Codes
COLORS = {
    "Black": "#000000",
    "Grey": "#666666",
    "Gray": "#666666",
    "Brown": "#654321",
    "Tan": "#D2B48C"
}

def get_color_box(title):
    found_color = "#ccc" 
    if title:
        for color_name, hex_code in COLORS.items():
            if color_name.upper() in title.upper():
                found_color = hex_code
                break
    return f'<span class="color-box" style="background-color: {found_color};"></span>'

def clean_variant_title(raw_title):
    """Robust cleaner that handles empty or weird titles."""
    if not raw_title:
        return "Unknown Option"
        
    # 1. Remove 'Black /' style prefixes
    if ' / ' in raw_title:
        parts = raw_title.split(' / ')
        if len(parts) > 1 and parts[-1].strip():
            title = parts[-1].strip()
        else:
            title = raw_title
    else:
        title = raw_title
        
    # 2. Remove 'CURRENTLY IN PRODUCTION' noise
    title = title.split(' - CURRENTLY')[0].strip()
    
    return title

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
      
      .option-unavailable { 
        position: relative; 
        display: inline-block; 
        color: #666; 
        padding: 0 4px;
        background: linear-gradient(to top left, transparent 46%, #888 49%, #888 51%, transparent 54%); 
      }
      .text-unavailable { color: #999; font-style: italic; font-size: 0.9em; }
    </style>
    </head>
    <body>
      <h3>Scheel-Mann Status <span class="sm-date">Updated: TIME_STAMP</span></h3>
    """
    html_output = html_output.replace("TIME_STAMP", update_time)

    for model_name, url in URLS.items():
        try:
            print(f"--- Deep Scanning {model_name} ---")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                # 1. Try finding the main product-template JSON first
                match = re.search(r'id="ProductJson-product-template">\s*(\{[\s\S]*?\})\s*<\/script>', response.text)
                
                # 2. If not found, try generic regex
                if not match:
                     match = re.search(r'id="ProductJson-[^"]*">\s*(\{[\s\S]*?\})\s*<\/script>', response.text)

                variants = []
                if match:
                    json_data = json.loads(match.group(1))
                    variants = json_data.get('variants', [])
                else:
                    # 3. Fallback to 'var meta'
                    match_fallback = re.search(r'var meta = (\{[\s\S]*?"variants":[\s\S]*?\});', response.text)
                    if match_fallback:
                         json_data = json.loads(match_fallback.group(1))
                         variants = json_data.get('product', {}).get('variants', [])
                
                html_output += f'<div class="sm-seat-title">{model_name}</div>'
                # This was the line that broke before, it is fixed now:
                html_output += '<table class="sm-status-table"><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>'
                target_link = SHOP_LINKS.get(model_name, "#")

                for variant in variants:
                    raw_title = variant.get('title') or variant.get('name') or variant.get('public_title') or variant.get('option1') or "Unknown Variant"
                    
                    clean_title = clean_variant_title(raw_title)
                    color_box_html = get_color_box(clean_title)
                    
                    is_available = variant.get('available', False)
                    is_preorder = "PRE-ORDER" in str(raw_title).upper() or "PRODUCTION" in str(raw_title).upper()

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
