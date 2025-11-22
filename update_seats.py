import requests
import json
import re
from datetime import datetime

# 1. URLs to Scrape (Deep Scan Mode)
# We use the actual HTML pages to find hidden/sold-out variants
URLS = {
    "Vario F": "https://scheel-mann.com/products/vario-f",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new"
}

# 2. Your Website Links
# We map the Scheel-Mann model to YOUR specific product page
SHOP_LINKS = {
    "Vario F": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "Vario F XXL": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "Vario F Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "Vario F XXL Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
}

# 3. Color Codes for the Visual Box
COLORS = {
    "Black": "#000000",
    "Grey": "#666666",
    "Gray": "#666666",
    "Brown": "#654321",
    "Tan": "#D2B48C"
}

def get_color_box(title):
    """Returns a simple HTML span with the background color matching the seat name."""
    found_color = "#ccc" # Default light grey
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
      
      /* Table Styles */
      .sm-status-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }
      .sm-seat-title { background-color: #f4f4f4; padding: 10px; margin: 0; border-left: 5px solid #333; font-weight: bold; font-size: 1.1em; }
      .sm-status-table th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em;}
      .sm-status-table td { padding: 10px; border-bottom: 1px solid #eee; vertical-align: middle; }
      
      /* Color Box */
      .color-box { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; border: 1px solid #ccc; vertical-align: middle; }
      
      /* Link Styles */
      a.status-link { text-decoration: none; }
      a.status-link:hover { text-decoration: underline; }

      /* Status Colors */
      .status-available { color: #27ae60; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; }
      .status-preorder { color: #e67e22; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; }
      
      /* Unavailable Styles */
      .option-unavailable { 
        position: relative; 
        display: inline-block; 
        color: #aaa; 
        padding: 0 4px;
        background: linear-gradient(to top left, transparent 46%, #999 49%, #999 51%, transparent 54%); 
      }
      .text-unavailable { color: #ccc; font-style: italic; font-size: 0.9em; }
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
                # Use Regex to find the hidden 'ProductJson' block in the HTML
                match = re.search(r'id="ProductJson-[^"]*">\s*(\{[\s\S]*?\})\s*<\/script>', response.text)
                
                variants = []
                if match:
                    json_data = json.loads(match.group(1))
                    variants = json_data.get('variants', [])
                else:
                    # Fallback if the ID is different
                    match_fallback = re.search(r'var meta = (\{[\s\S]*?"variants":[\s\S]*?\});', response.text)
                    if match_fallback:
                         json_data = json.loads(match_fallback.group(1))
                         variants = json_data.get('product', {}).get('variants', [])
                
                # Start Table for this Seat
                html_output += f'<div class="sm-seat-title">{model_name}</div>'
                html_output += '<table class="sm-status-table"><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>'
                
                # Target Link for this model
                target_link = SHOP_LINKS.get(model_name, "#")

                for variant in variants:
                    raw_title = variant.get('title', '')
                    
                    # 1. Clean Name (Remove prefixes and internal notes)
                    if ' / ' in raw_title:
                        clean_title = raw_title.split(' / ')[-1].strip()
                    else:
                        clean_title = raw_title
                    clean_title = clean_title.split(' - CURRENTLY')[0].strip()

                    # 2. Get Color Box
                    color_box_html = get_color_box(raw_title)
                    
                    # 3. Determine Status
                    is_available = variant.get('available', False)
                    is_preorder = "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper()

                    if not is_available:
                        # SOLD OUT
                        # Note: No link for sold out items
                        display = f'{color_box_html} <div class="option-unavailable">{clean_title}</div>'
                        status = '<span class="text-unavailable">Out of Stock</span>'
                    
                    elif is_preorder:
                        # PRE-ORDER (Linked)
                        display = f'{color_box_html} {clean_title}'
                        status = f'<a href="{target_link}" target="_parent" class="status-link"><span class="status-preorder">Pre-Order</span></a>'
                        
                    else:
                        # IN STOCK (Linked)
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
