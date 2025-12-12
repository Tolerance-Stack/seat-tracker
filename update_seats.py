import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
# We use the JSON feed to get deep data (Policies, Options, etc.)
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

# --- MASTER LIST ---
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
    
    # HTML HEADER
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<meta http-equiv="cache-control" content="no-cache">')
    h.append('<style>')
    h.append('body { font-family: sans-serif; padding: 10px; }')
    h.append('h3 { border-bottom: 2px solid #333; padding-bottom: 10px; }')
    h.append('.ver { background: #3498db; color: white; padding: 2px 5px; border-radius: 3px; font-size: 0.8em; }')
    h.append('.date { font-size: 0.8em; color: #666; float: right; }')
    h.append('table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }')
    h.append('.title { background: #f4f4f4; padding: 10px; font-weight: bold; }')
    h.append('th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; }')
    h.append('td { padding: 10px; border-bottom: 1px solid #eee; }')
    h.append('.box { display: inline-block; width: 12px; height: 12px; margin-right: 8px; border: 1px solid #ccc; }')
    h.append('a { text-decoration: none; color: #27ae60; font-weight: bold; }')
    h.append('a.pre { color: #e67e22; }')
    h.append('</style></head><body>')
    
    # v8.0 Badge (Blue)
    h.append(f'<h3>In Stock in Portland <span class="ver">v8.0</span> <span class="date">{now}</span></h3>')

    for model, url in PRODUCTS.items():
        try:
            print(f"Checking {model}...")
            
            rows = ""
            link = SHOP_LINKS.get(model, "#")

            try:
                # REQUEST JSON FEED
                resp = requests.get(url, headers=ua)
                if resp.status_code == 200:
                    data = resp.json()
                    variants = data.get('product', {}).get('variants', [])
                    
                    for v in variants:
                        # CHECK IF AVAILABLE (Buyable)
                        if v.get('available', False):
                            
                            # GATHER DATA POINTS
                            raw_title = v.get('title', '')
                            option1 = v.get('option1') or ""
                            option2 = v.get('option2') or ""
                            policy = v.get('inventory_policy', '')
                            
                            clean = clean_title(raw_title)

                            # CHECK MATCH AGAINST MASTER LIST
                            matched_master = None
                            for m in MASTER_LIST:
                                if m in clean or clean in m:
                                    matched_master = m
                                    break
                            
                            if matched_master:
                                box = get_color_box(matched_master)
                                
                                # --- THE SMART DETECTIVE LOGIC ---
                                # 1. Check Title Text
                                text_flag = "PRE-ORDER" in raw_title.upper() or "PRODUCTION" in raw_title.upper()
                                # 2. Check Option Text (Hidden dropdown values)
                                opt_flag = "PRE-ORDER" in option1.upper() or "PRODUCTION" in option1.upper()
                                # 3. Check Inventory Policy ('continue' means selling without stock)
                                policy_flag = (policy == 'continue')

                                # If ANY flag is true, it is Pre-Order
                                is_pre = text_flag or opt_flag or policy_flag
                                
                                row_start = f'<tr><td>{box} {matched_master}</td>'
                                
                                if is_pre:
                                    stat = f'<td><a href="{link}" target="_parent" class="pre">Pre-Order</a></td></tr>'
                                else:
                                    stat = f'<td><a href="{link}" target="_parent">In Stock</a></td></tr>'
                                
                                rows += row_start + stat

            except Exception as e:
                print(f"JSON Error: {e}")

            if rows:
                h.append(f'<div class="title">{model}</div>')
                h.append('<table><thead><tr><th width="70%">Option</th><th>Status</th></tr></thead><tbody>')
                h.append(rows)
                h.append('</tbody></table>')

        except Exception as e:
            print(f"Error: {e}")
            
    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))

if __name__ == "__main__":
    fetch_seat_data()
