import requests
import json
import re
from datetime import datetime

# --- CONFIGURATION ---
SCRAPER_API_KEY = "c288ebe9bae2045147af00f7de7d2c43"

# Target exact product URLs to eliminate collection duplicates
PRODUCT_URLS = {
    "Vario F": "https://scheel-mann.com/products/vario-f",
    "Vario F Klima": "https://scheel-mann.com/products/vario-f-klima",
    "Vario F XXL": "https://scheel-mann.com/products/vario-f-xxl",
    "Vario F XXL Klima": "https://scheel-mann.com/products/vario-f-xxl-klima"
}

# Determines the order they print on your website
DISPLAY_ORDER = [
    "Vario F",
    "Vario F Klima",
    "Vario F XXL",
    "Vario F XXL Klima"
]

SHOP_LINKS = {
    "Vario F": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "Vario F XXL": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "Vario F Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "Vario F XXL Klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
}

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

def extract_variants_from_html(html):
    # Method 1: Look for standard Shopify JSON blocks containing the hidden inventory quantity
    blocks = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
    for block in blocks:
        try:
            data = json.loads(block.strip())
            variants = data.get('product', {}).get('variants') or data.get('variants')
            if variants:
                results = []
                for v in variants:
                    title = v.get('title', '')
                    qty = v.get('inventory_quantity', 1)
                    policy = v.get('inventory_policy', 'deny')
                    # Logic: If stock is 0 and they allow backorders, it triggers the yellow banner
                    status = "Pre-Order" if (qty <= 0 and policy == 'continue') else "In Stock"
                    results.append({'title': title, 'status': status})
                if results:
                    return results
        except:
            continue
    
    # Method 2: Fallback regex parsing if JSON blocks are obscured by Javascript
    match = re.search(r'"variants":\s*(\[.*?\])\s*,\s*"(?:options|images|vendor|media)"', html, re.DOTALL)
    if not match:
        match = re.search(r'var meta = .*?"variants":\s*(\[.*?\])\s*\}', html, re.DOTALL)
        
    if match:
        results = []
        variants_str = match.group(1)
        variant_strings = re.split(r'},{', variants_str)
        for v_str in variant_strings:
            t_match = re.search(r'"title":\s*"([^"]+)"', v_str)
            q_match = re.search(r'"inventory_quantity":\s*(-?\d+)', v_str)
            p_match = re.search(r'"inventory_policy":\s*"([^"]+)"', v_str)
            
            if t_match:
                title = t_match.group(1)
                qty = int(q_match.group(1)) if q_match else 1
                policy = p_match.group(1) if p_match else 'deny'
                status = "Pre-Order" if (qty <= 0 and policy == 'continue') else "In Stock"
                results.append({'title': title, 'status': status})
        if results:
            return results
            
    return []

def fetch_seat_data():
    now = datetime.now().strftime("%H:%M UTC")
    
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:10px;} h3{border-bottom:2px solid #333;padding-bottom:10px;} .ver{background:#3498db;color:white;padding:2px 5px;border-radius:3px;font-size:0.8em;} .date{font-size:0.8em;color:#666;float:right;} table{width:100%;border-collapse:collapse;margin-bottom:30px;} .title{background:#f4f4f4;padding:10px;font-weight:bold;} td{padding:10px;border-bottom:1px solid #eee;} a{text-decoration:none;color:#27ae60;font-weight:bold;} a.pre{color:#e67e22;} .box{display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid #ccc;vertical-align:middle;}</style></head><body>')
    
    h.append(f'<h3>In Stock in Portland <span class="ver">v20.0</span> <span class="date">{now}</span></h3>')

    print("--- STARTING UPDATE v20.0 ---")

    categorized_rows = {m: "" for m in DISPLAY_ORDER}

    for model in DISPLAY_ORDER:
        target_url = PRODUCT_URLS[model]
        print(f"Scraping HTML for {model}...")
        
        try:
            payload = {'api_key': SCRAPER_API_KEY, 'url': target_url}
            resp = requests.get('http://api.scraperapi.com', params=payload, timeout=60)
            print(f"   Status Code: {resp.status_code}")
            
            if resp.status_code == 200:
                variants = extract_variants_from_html(resp.text)
                print(f"   Found {len(variants)} variants.")
                
                link = SHOP_LINKS.get(model, "#")
                
                # Double-failsafe to ensure a color never prints twice in the same category
                seen_titles = set()
                
                for v in variants:
                    raw_title = v['title']
                    if raw_title.lower() == 'default title':
                        continue
                    
                    clean = clean_title(raw_title)
                    if clean in seen_titles:
                        continue
                    seen_titles.add(clean)
                    
                    status_text = v['status']
                    status_class = "pre" if status_text == "Pre-Order" else "" 
                    box = get_color_box(raw_title)
                    
                    row_html = f'<tr><td>{box} {clean}</td><td><a href="{link}" target="_parent" class="{status_class}">{status_text}</a></td></tr>'
                    categorized_rows[model] += row_html
                    
            else:
                print(f"   ERROR: Failed to fetch HTML.")
        except Exception as e:
            print(f"   CRASH: {e}")

    # Build final page
    for model in DISPLAY_ORDER:
        rows = categorized_rows[model]
        if rows:
            h.append(f'<div class="title">{model}</div><table>{rows}</tbody></table>')

    h.append('</body></html>')
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("".join(h))
    
    print("--- UPDATE COMPLETE ---")

if __name__ == "__main__":
    fetch_seat_data()
