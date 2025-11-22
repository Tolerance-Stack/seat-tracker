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

# ADDED "Real Leather" to the black color mapping
COLORS = {
    "Black": "#000", 
    "Real Leather": "#000",
    "Grey": "#666", 
    "Gray": "#666", 
    "Brown": "#654321", 
    "Tan": "#D2B48C"
}

def get_color_box(title):
    c = "#ccc" # Default gray
    if title:
        for k, v in COLORS.items():
            if k.upper() in title.upper():
                c = v
                break
    return f'<span class="box" style="background-color: {c};"></span>'

def clean_title(raw):
    t = str(raw)
    if ' / ' in t:
        t = t.split(' / ')[-1].strip()
    t = t.split(' - ')[0].strip()
    return t

def fetch_seat_data():
    ua = {'User-Agent': 'Mozilla/5.0'}
    now = datetime.now().strftime("%b %d at %H:%M UTC")
    
    # Start HTML
    html = ""
    html += '<!DOCTYPE html><html><head>'
    html += '<meta http-equiv="refresh" content="300">'
    html += '<style>'
    html += 'body { font-family: sans-serif; padding: 10px; }'
    html += 'h3 { border-bottom: 2px solid #333; padding-bottom: 10px; }'
    html += '.date { font-size: 0.8em; color: #666; float: right; }'
    html += 'table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }'
    html += '.title { background: #f4f4f4; padding: 10px; font-weight: bold; }'
    html += 'th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; }'
    html += 'td { padding: 10px; border-bottom: 1px solid #eee; }'
    html += '.box { display: inline-block; width: 12px; height: 12px; margin-right: 8px; border: 1px solid #ccc; }'
    html += 'a { text-decoration: none; color: #27ae60; font-weight: bold; }'
    html += 'a.pre { color: #e67e22; }'
    html += '</style></head><body>'
    
    html += f'<h3>Scheel-Mann Vario Seats In Stock in Portland <span class="date">{now}</span></h3>'

    for model, url in PRODUCTS.items():
        try:
            print(f"Checking {model}...")
            resp = requests.get(url, headers=ua)
            
            if resp.status_code == 200:
                data = resp.json()
                variants = data.get('variants', [])
                
                rows = ""
                link = SHOP_LINKS.get(model, "#")

                for v in variants:
                    if v.get('available', False):
                        raw = v.get('title') or "Unknown"
                        clean = clean_title(raw)
                        box = get_color_box(clean)
                        
                        is_pre = "PRE-ORDER" in str(raw).upper()
                        
                        # Build row parts separately
                        row_start = "<tr><td>" + box + " " + clean + "</td>"
                        
                        if is_pre:
                            status = f'<td><a href="{link}" target="_parent" class="pre">Pre-Order</a></td></tr>'
                        else:
                            status = f'<td><a href="{link}" target="_parent">In Stock</a></td></tr>'
                        
                        rows += row_start + status

                if rows:
                    html += f'<div class="title">{model}</div>'
                    html += '<table><thead><tr><th width="70%">Option</th><th>Status</th></tr></thead><tbody>'
                    html += rows
                    html += '</tbody></table>'

        except Exception as e:
            print(f"Error: {e}")
            
    html += '</body></html>'
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    fetch_seat_data()
