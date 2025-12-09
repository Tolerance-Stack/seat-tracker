import requests
import re
from datetime import datetime

# --- CONFIGURATION ---
PRODUCTS = {
    "Vario F": "https://scheel-mann.com/products/vario-f",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima-new"
}

SHOP_LINKS = {
    "Vario F": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "Vario F XXL": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "Vario F Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "Vario F XXL Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
}

# --- MANUAL OVERRIDE ---
# If the robot ever misses one, just add the seat name here to FORCE it to be Pre-Order.
# Example: FORCE_PREORDER = ["Black Real Leather"]
FORCE_PREORDER = []

# --- SMART MATCHING RULES ---
SEAT_DEFINITIONS = [
    ("Black Basketweave", ["Black", "Basketweave"]),
    ("Black Real Leather", ["Black", "Real", "Leather"]),
    ("Grey Basketweave", ["Grey", "Basketweave"]),
    ("Grey Rodeo Plaid", ["Grey", "Rodeo"]),
    ("Brown Microweave", ["Brown", "Microweave"]),
    ("Black Leatherette", ["Black", "Leatherette"]),
    ("Grey Five Bar", ["Grey", "Five", "Bar"]),
    ("Black Corduroy", ["Black", "Corduroy"]),
    ("Black Pepita", ["Black", "Pepita"]),
    ("Real Leather", ["Real", "Leather"])
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

def fetch_seat_data():
    # Use generic browser headers to see the page as a human does
    ua = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    now = datetime.now().strftime("%H:%M UTC")
    
    # HTML HEADER
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<meta http-equiv="cache-control" content="no-cache">')
    h.append('<style>')
    h.append('body { font-family: sans-serif; padding: 10px; }')
    h.append('h3 { border-bottom: 2px solid #333; padding-bottom: 10px; }')
    h.append('.ver { background: #e67e22; color: white; padding: 2px 5px; border-radius: 3px; font-size: 0.8em; }')
    h.append('.date { font-size: 0.8em; color: #666; float: right; }')
    h.append('table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }')
    h.append('.title { background: #f4f4f4; padding: 10px; font-weight: bold; }')
    h.append('th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; }')
    h.append('td { padding: 10px; border-bottom: 1px solid #eee; }')
    h.append('.box { display: inline-block; width: 12px; height: 12px; margin-right: 8px; border: 1px solid #ccc; }')
    h.append('a { text-decoration: none; color: #27ae60; font-weight: bold; }')
    h.append('a.pre { color: #e67e22; }')
    h.append('</style></head><body>')
    
    # v6.0 Badge (Orange)
    h.append(f'<h3>In Stock in Portland <span class="ver">v6.0</span> <span class="date">{now}</span></h3>')

    for model, url in PRODUCTS.items():
        try:
            print(f"Checking {model}...")
            
            rows = ""
            link = SHOP_LINKS.get(model, "#")

            try:
                # 1. DOWNLOAD RAW HTML
                resp = requests.get(url, headers=ua)
                if resp.status_code == 200:
                    html_text = resp.text
                    
                    # 2. FIND ALL OPTION TAGS (The Dropdown Menu)
                    # We capture the full text inside the option tag
                    # Regex explanation: <option (any attributes)> (capture text) </option>
                    options = re.findall(r'<option[^>]*>(.*?)</option>', html_text, re.IGNORECASE | re.DOTALL)
                    
                    # Also grab the JS "ProductJson" blob as a backup source of titles
                    # Some themes put the full "Production" text in the JSON title
                    json_titles = []
                    json_match = re.search(r'"variants":\s*(\[\{.*?\}\])', html_text)
                    if json_match:
                        try:
                            # Extract titles from JSON blob
                            j_data = json.loads(json_match.group(1))
                            json_titles = [x.get('title', '') for x in j_data if x.get('available')]
                        except:
                            pass

                    # Combine sources (Dropdown text + JSON titles)
                    all_source_text = options + json_titles

                    # 3. PROCESS EACH SEAT DEFINITION
                    for name, keywords in SEAT_DEFINITIONS:
                        
                        # Look for this seat in our gathered text
                        found_text_matches = []
                        for text in all_source_text:
                            # Check if ALL keywords are in this text line
                            if all(k.upper() in text.upper() for k in keywords):
                                # Filter out "Select Option" junk
                                if "Select" not in text:
                                    found_text_matches.append(text)
                        
                        # Remove duplicates
                        found_text_matches = list(set(found_text_matches))
                        
                        # 4. DETERMINE STATUS FOR THIS SEAT
                        for match_text in found_text_matches:
                            box = get_color_box(name)
                            
                            # Check for "Pre-Order" triggers in the text
                            upper_text = match_text.upper()
                            is_pre = "PRODUCTION" in upper_text or "PRE-ORDER" in upper_text
                            
                            # Manual Override Check
                            if name in FORCE_PREORDER:
                                is_pre = True
                            
                            row_start = f'<tr><td>{box} {name}</td>'
                            
                            if is_pre:
                                stat = f'<td><a href="{link}" target="_parent" class="pre">Pre-Order</a></td></tr>'
                            else:
                                stat = f'<td><a href="{link}" target="_parent">In Stock</a></td></tr>'
                            
                            rows += row_start + stat

            except Exception as e:
                print(f"Scan Error: {e}")

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
