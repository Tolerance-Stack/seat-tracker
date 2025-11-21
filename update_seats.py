import requests
import json
from datetime import datetime

# Using the official AJAX feed which drives the "Add to Cart" buttons
PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f.js",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl.js",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima.js",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new.js"
}

def fetch_seat_data():
    # Adding specific time to force you to see if the cache updated
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
    html_output = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="refresh" content="300"> <style>
      body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }
      h3 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 0; }
      .sm-date { font-size: 0.8em; color: #666; float: right; font-weight: normal; margin-top: 5px;}
      
      .sm-status-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 14px; }
      .sm-seat-title { background-color: #f4f4f4; padding: 8px; margin: 0; border-left: 4px solid #333; font-weight: bold; }
      .sm-status-table th { text-align: left; padding: 8px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em;}
      .sm-status-table td { padding: 8px; border-bottom: 1px solid #eee; vertical-align: middle; }
      
      /* STATUS COLORS */
      .status-available { color: #27ae60; font-weight: bold; font-size: 0.9em; letter-spacing: 0.5px; text-transform: uppercase; }
      .status-preorder { color: #e67e22; font-weight: bold; font-size: 0.9em; letter-spacing: 0.5px; text-transform: uppercase; }
      
      /* UNAVAILABLE STYLING (Diagonal Line) */
      .option-unavailable { 
        position: relative; 
        display: inline-block; 
        color: #aaa; 
        padding: 0 4px; 
        /* The diagonal line effect */
        background: linear-gradient(to top left, transparent 46%, #999 49%, #999 51%, transparent 54%); 
      }
      .text-unavailable { color: #ccc; font-style: italic; font-size: 0.9em; }
    </style>
    </head>
    <body>
      <h3>Scheel-Mann Status <span class="sm-date">Generated: TIME_STAMP</span></h3>
    """
    html_output = html_output.replace("TIME_STAMP", update_time)

    for model_name, url in PRODUCTS.items():
        try:
            print(f"--- Processing {model_name} ---")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                data = response.json()
                variants = data.get('variants', [])
                
                html_output += f'<div class="sm-seat-title">{model_name}</div>'
                html_output += '<table class="sm-status-table"><thead><tr><th width="70%">Option</th><th>Status</th></tr></thead><tbody>'
                
                for variant in variants:
                    raw_title = variant.get('title', '')
                    
                    # --- 1. NAME CLEANER ---
                    # Splits "Black / Black Basketweave" -> "Black Basketweave"
                    # Splits "Black / Grey Rodeo" -> "Grey Rodeo"
                    if ' / ' in raw_title:
                        clean_title = raw_title.split(' / ')[-1].strip()
                    else:
                        clean_title = raw_title
                    
                    # Remove the "CURRENTLY IN PRODUCTION" junk from the display name
                    clean_title = clean_title.split(' - CURRENTLY')[0].strip()

                    # --- 2. STATUS LOGIC ---
                    is_available = variant.get('available', False)
                    is_preorder_text = "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper()

                    if not is_available:
                        # CASE 1: Shopify says NO -> Crossed Out
                        display = f'<div class="option-unavailable">{clean_title}</div>'
                        status = '<span class="text-unavailable">Out of Stock</span>'
                    
                    elif is_preorder_text:
                        # CASE 2: Shopify says YES, but text says Pre-Order -> Orange
                        display = clean_title
                        status = '<span class="status-preorder">Pre-Order</span>'
                        
                    else:
                        # CASE 3: Shopify says YES, no notes -> Green
                        display = clean_title
                        status = '<span class="status-available">In Stock</span>'

                    html_output += f'<tr><td>{display}</td><td>{status}</td></tr>'
                
                html_output += '</tbody></table>'
            else:
                print(f"Failed to fetch {model_name}")

        except Exception as e:
            print(f"Error on {model_name}: {e}")
            
    html_output += "</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_output)

if __name__ == "__main__":
    fetch_seat_data()
