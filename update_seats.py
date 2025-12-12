import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f.json",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl.json",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima.json",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new.json"
}

def fetch_seat_data():
    now = datetime.now().strftime("%H:%M UTC")
    
    # HTML Header
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:20px;} table{width:100%;border-collapse:collapse;margin-bottom:20px;} th,td{padding:8px;border-bottom:1px solid #ddd;} .ver{background:red;color:white;padding:3px;font-size:0.8em;} .instock{color:green;font-weight:bold;} .out{color:#ccc;}</style></head><body>')
    
    # NEW VERSION NUMBER
    h.append(f'<h3>Inventory Diagnostic Mode <span class="ver">v12.0 - RAW DATA</span> <span class="date">{now}</span></h3>')
    h.append('<p><i>Showing ALL data found on Scheel-mann.com...</i></p>')

    headers = {'User-Agent': 'Mozilla/5.0'}

    for model, url in PRODUCTS.items():
        h.append(f'<h4>{model}</h4>')
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                h.append(f'<p style="color:red">Error: Could not load data (Code {resp.status_code})</p>')
                continue

            data = resp.json()
            variants = data.get('product', {}).get('variants', [])
            
            if not variants:
                h.append('<p>No items found in file.</p>')
            
            # Start Table
            h.append('<table><tr><th>Product Name</th><th>Stock Status</th></tr>')
            
            for v in variants:
                title = v.get('title', 'Unknown Name')
                available = v.get('available', False)
                
                # LOGIC: Show EVERYTHING. Green if available, Grey if not.
                if available:
                    status = '<span class="instock">IN STOCK</span>'
                else:
                    status = '<span class="out">Out of Stock</span>'
                    
                h.append(f'<tr><td>{title}</td><td>{status}</td></tr>')
                
            h.append('</table>')

        except Exception as e:
            h.append(f'<p style="color:red">Script Error: {e}</p>')

    h.append('</body></html>')
    
    # Save the file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))

if __name__ == "__main__":
    fetch_seat_data()
