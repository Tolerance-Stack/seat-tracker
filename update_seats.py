import requests
import re
from datetime import datetime

# --- CONFIGURATION ---
# We map the Product Title in the RSS feed to your Website Link
# Note: The keys here must match the Titles in the RSS feed (Vario F, Vario F XXL, etc.)
PRODUCT_MAP = {
    "Vario F": {
        "link": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
        "feed_url": "https://scheel-mann.com/products/vario-f.atom" # The specific product RSS feed
    },
    "Vario F XXL": {
        "link": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
        "feed_url": "https://scheel-mann.com/products/vario-f-xxl.atom"
    },
    "Vario F Klima": {
        "link": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
        "feed_url": "https://scheel-mann.com/products/vario-f-klima.atom"
    },
    "Vario F XXL Klima - NEW": { # Note: The feed might use the full name "Vario F XXL Klima - NEW"
        "link": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
        "feed_url": "https://scheel-mann.com/products/vario-f-xxl-klima-new.atom"
    }
}

COLORS = {"Black": "#000", "Grey": "#666", "Gray": "#666", "Brown": "#654321", "Tan": "#D2B48C"}

# --- HELPERS ---
def get_color_box(title):
    found_color = "#ccc" 
    if title:
        for color_name, hex_code in COLORS.items():
            if color_name.upper() in title.upper():
                found_color = hex_code
                break
    return f'<span class="box" style="background-color: {found_color};"></span>'

def clean_title(raw_title):
    t = str(raw_title)
    if ' / ' in t:
        t = t.split(' / ')[-1].strip()
    return t.split(' - CURRENTLY')[0].strip()

def fetch_seat_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
    # HTML HEADER
    html_parts = []
    html_parts.append('<!DOCTYPE html><html><head>')
    html_parts.append('<meta http-equiv="refresh" content="300">')
    html_parts.append('<style>')
    html_parts.append('body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }')
    html_parts.append('h3 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 0; }')
    html_parts.append('.date { font-size: 0.8em; color: #666; float: right; font-weight: normal; margin-top: 5px;}')
    html_parts.append('table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }')
    html_parts.append('.title { background-color: #f4f4f4; padding: 10px; margin: 0; border-left: 5px solid #333; font-weight: bold; font-size: 1.1em; }')
    html_parts.append('th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em;}')
    html_parts.append('td { padding: 10px; border-bottom: 1px solid #eee; vertical-align: middle; }')
    html_parts.append('.box { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; border: 1px solid #ccc; vertical-align: middle; }')
    html_parts.append('a { text-decoration: none; }')
    html_parts.append('a:hover { text-decoration: underline; }')
    html_parts.append('.avail { color: #27ae60; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }')
    html_parts.append('.pre { color: #e67e22; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }')
    html_parts.append('.out-box { position: relative; display: inline-block; color: #666; padding: 0 4px; background: linear-gradient(to top left, transparent 46%, #888 49%, #888 51%, transparent 54%); }')
    html_parts.append('.out-text { color: #999; font-style: italic; font-size: 0.9em; }')
    html_parts.append('</style></head><body>')
    html_parts.append(f'<h3>Scheel-Mann Status <span class="date">Updated: {update_time}</span></h3>')

    for name, data in PRODUCT_MAP.items():
        try:
            print(f"--- Processing {name} via ATOM Feed ---")
            
            # 1. LIVE STATUS (JS Feed - The Truth for Active Items)
            # We convert the .atom URL back to .js to check current stock status
            js_url = data['feed_url'].replace('.atom', '.js')
            live_map = {}
            try:
                js_resp = requests.get(js_url, headers=headers)
                if js_resp.status_code == 200:
                    for v in js_resp.json().get('variants', []):
                        live_map[str(v['id'])] = v.get('available', False)
            except Exception as e:
                print(f"JS Error: {e}")

            # 2. FULL LIST (ATOM Feed - The Backdoor)
            variants_found = []
            try:
                # Fetch the RSS/Atom feed for the product
                atom_resp = requests.get(data['feed_url'], headers=headers)
                
                if atom_resp.status_code == 200:
                    xml_text = atom_resp.text
                    
                    # Regex to find <s:variant> blocks
                    # These blocks contain <s:id> and <s:title>
                    # We regex strictly because XML parsing can be brittle with namespaces
                    variant_blocks = re.findall(r'<s:variant>([\s\S]*?)</s:variant>', xml_text)
                    
                    for block in variant_blocks:
                        # Extract ID
                        id_match = re.search(r'<s:id>(\d+)</s:id>', block)
                        # Extract Title
                        title_match = re.search(r'<s:title>([\s\S]*?)</s:title>', block)
                        
                        if id_match and title_match:
                            vid = id_match.group(1)
                            vtitle = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '')
                            variants_found.append({'id': vid, 'title': vtitle})
                    
                    print(f"Atom Scan found {len(variants_found)} items")
            except Exception as e:
                print(f"Atom Error: {e}")

            # 3. BUILD TABLE
            display_name = name.replace(" - NEW", "") # Clean up display name
            html_parts.append(f'<div class="title">{display_name}</div>')
            html_parts.append('<table><thead><tr><th width="65%">Option</th><th>Status</th></tr></thead><tbody>')
            link = data['link']

            if not variants_found:
                html_parts.append('<tr><td colspan="2">No data found via Atom feed.</td></tr>')

            for v in variants_found:
                vid = v['id']
                raw = v['title']
                clean = clean_title(raw)
                color = get_color_box(clean)
                
                # HYBRID LOGIC:
                # If ID is in Live Map -> Use Live Status
                # If ID is missing from Live Map -> It means it's Sold Out (Hidden)
                if vid in live_map:
                    is_avail = live_map[vid]
                else:
                    is_avail = False

                is_pre = "PRE-ORDER" in str(raw).upper() or "PRODUCTION" in str(raw).upper()

                if not is_avail:
                    disp = f'{color} <div class="out-box">{clean}</div>'
                    stat = '<span class="out-text">Out of Stock</span>'
                elif is_pre:
                    disp = f'{color} {clean}'
                    stat = f'<a href="{link}" target="_parent"><span class="pre">Pre-Order</span></a>'
                else:
                    disp = f'{color} {clean}'
                    stat = f'<a href="{link}" target="_parent"><span class="avail">In Stock</span></a>'

                html_parts.append(f'<tr><td>{disp}</td><td>{stat}</td></tr>')
            
            html_parts.append('</tbody></table>')

        except Exception as e:
            print(f"Critical Error: {e}")
            
    html_parts.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(html_parts))

if __name__ == "__main__":
    fetch_seat_data()
