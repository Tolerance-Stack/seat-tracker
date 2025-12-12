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

SHOP_LINKS = {
    "Vario F": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "Vario F XXL": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "Vario F Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "Vario F XXL Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
}

MASTER_LIST = [
    "Black Basketweave Cloth with Black Leatherette Bolsters",
    "Black Real Leather",
    "Grey Basketweave Cloth with Grey Leatherette Bolsters",
    "Grey Rodeo Plaid Cloth with Black Leatherette Bolsters",
    "Brown Microweave Cloth with Brown Leatherette Bolsters",
    "Brown Microweave Cloth with Black Leatherette Bolsters",
    "Grey Five Bar Cloth with Black Leatherette Bolsters",
    "MB Rodeo Grey Cloth with Black Leatherette Bolsters",
    "Black Cloth with Black Leatherette Bolsters",
    "Black Corduroy Cloth with Black Leatherette Bolsters",
    "Black Pepita Cloth with Black Leatherette Bolsters",
    "Black & Brown / Brown Microweave Cloth with Black Leatherette Bolsters",
    "Real Leather", 
    "Black Leatherette"
]

COLORS = {
    "Black": "#000", "Real Leather": "#000", "Grey": "#666", 
    "Gray": "#666", "Brown": "#654321", "Tan": "#D2B48C"
}

def get_color_box(title):
    c = "#ccc" 
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
    now = datetime.now().strftime("%H:%M UTC")
    
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:20px;} table{width:100%;border-collapse:collapse;} th,td{padding:10px;border-bottom:1px solid #ddd;} .ver{background:blue;color:white;padding:3px;}</style></head><body>')
    
    # UPDATE THIS VERSION NUMBER
    h.append(f'<h3>In Stock in Portland <span class="ver">v11.0</span> <span class="date">{now}</span></h3>')

    for model, url in PRODUCTS.items():
        try:
            print(f"--- CHECKING {model} ---") # DEBUG
            
            rows = ""
            link = SHOP_LINKS.get(model, "#")
            resp = requests.get(url, headers=ua)
            
            if resp.status_code != 200:
                print(f"ERROR: Failed to fetch {url} (Status: {resp.status_code})")
                continue

            data = resp.json()
            variants = data.get('product', {}).get('variants', [])
            
            print(f"Found {len(variants)} total variants in JSON.") # DEBUG

            for v in variants:
                # DEBUG: Print every single item it finds so we see why it fails
                raw_title = v.get('title', 'Unknown')
                is_available = v.get('available', False)
                clean = clean_title(raw_title)
                
                print(f"   Analyzed: '{raw_title}' | Available: {is_available} | Cleaned: '{clean}'") # DEBUG

                if is_available:
                    matched_master = None
                    for m in MASTER_LIST:
                        if m in clean or clean in m:
                            matched_master = m
                            break
                    
                    if matched_master:
                        print(f"      >>> MATCH! Adding to list.") # DEBUG
                        box = get_color_box(matched_master)
                        stat = f'<td><a href="{link}" target="_parent">In Stock</a></td></tr>'
                        rows += f'<tr><td>{box} {matched_master}</td>{stat}'
                    else:
                        print(f"      >>> NO MATCH in Master List.") # DEBUG
                else:
                    print(f"      >>> SKIP (Not Available)") # DEBUG

            if rows:
                h.append(f'<div class="title"><b>{model}</b></div><table><tbody>{rows}</tbody></table><br>')

        except Exception as e:
            print(f"CRASH ERROR on {model}: {e}")
            
    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))

if __name__ == "__main__":
    fetch_seat_data()
