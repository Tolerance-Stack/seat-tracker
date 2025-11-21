import requests
import json
from datetime import datetime

PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f.json",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl.json",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima.json",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new.json"
}

def fetch_seat_data():
    current_date = datetime.now().strftime("%b %d, %Y")
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }
      h3 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 0; }
      .sm-date { font-size: 0.8em; color: #666; float: right; font-weight: normal; margin-top: 5px;}
      .sm-status-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 14px; }
      .sm-seat-title { background-color: #f4f4f4; padding: 8px; margin: 0; border-left: 4px solid #333; font-weight: bold; }
      .sm-status-table th { text-align: left; padding: 8px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em;}
      .sm-status-table td { padding: 8px; border-bottom: 1px solid #eee; vertical-align: middle; }
      .status-available { color: #27ae60; font-weight: bold; font-size: 0.9em; letter-spacing: 0.5px; text-transform: uppercase; }
      .status-preorder { color: #d35400; font-weight: bold; font-size: 0.9em; letter-spacing: 0.5px; text-transform: uppercase; }
      .option-unavailable { position: relative; display: inline-block; color: #aaa; padding: 0 4px; background: linear-gradient(to top left, transparent 46%, #999 49%, #999 51%, transparent 54%); }
      .text-unavailable { color: #ccc; font-style: italic; font-size: 0.9em; }
    </style>
    </head>
    <body>
      <h3>Scheel-Mann Status <span class="sm-date">Updated: DATE_HERE</span></h3>
    """
    
    html = html.replace("DATE_HERE", current_date)

    for model_name, url in PRODUCTS.items():
        try:
            print(f"--- Checking {model_name} ---")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                data = response.json()
                variants = data.get('product', {}).get('variants', [])
                
                html += f'<div class="sm-seat-title">{model_name}</div>'
                html += '<table class="sm-status-table"><thead><tr><th width="70%">Option</th><th>Status</th></tr></thead><tbody>'
                
                for variant in variants:
                    raw_title = variant.get('title', '')
                    # THE DEBUGGER: This prints the raw data to your GitHub logs
                    print(f"DEBUG: {raw_title} | Available: {variant.get('available')} | Qty: {variant.get('inventory_quantity')}")

                    is_available = variant.get('available', False)
                    clean_title = raw_title.split(' - CURRENTLY')[0].strip()
                    
                    if not is_available:
                        display = f'<div class="option-unavailable">{clean_title}</div>'
                        status = '<span class="text-unavailable">Out of Stock</span>'
                    elif "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper():
                        display = clean_title
                        status = '<span class="status-preorder">Pre-Order</span>'
                    else:
                        display = clean_title
                        status = '<span class="status-available">In Stock</span>'
                    
                    html += f'<tr><td>{display}</td><td>{status}</td></tr>'
                
                html += '</tbody></table>'
            else:
                print(f"Failed to fetch {model_name}: {response.status_code}")
        except Exception as e:
            print(f"Error on {model_name}: {e}")
            
    html += "</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully generated index.html")

if __name__ == "__main__":
    fetch_seat_data()
