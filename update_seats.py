import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
SCRAPER_API_KEY = "c288ebe9bae2045147af00f7de7d2c43"
TARGET_URL = "https://scheel-mann.com/collections/stocked-seating/products.json?limit=250"

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

TARGET_MODELS = [
    "Vario F XXL Klima",
    "Vario F XXL",
    "Vario F Klima",
    "Vario F"
]

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
    now = datetime.now().strftime("%H:%M UTC")
    
    h = []
    h.append('<!DOCTYPE html><html><head>')
    h.append('<meta http-equiv="refresh" content="300">')
    h.append('<style>body{font-family:sans-serif;padding:10px;} h3{border-bottom:2px solid #333;padding-bottom:10px;} .ver{background:#3498db;color:white;padding:2px 5px;border-radius:3px;font-size:0.8em;} .date{font-size:0.8em;color:#666;float:right;} table{width:100%;border-collapse:collapse;margin-bottom:30px;} .title{background:#f4f4f4;padding:10px;font-weight:bold;} td{padding:10px;border-bottom:1px solid #eee;} a{text-decoration:none;color:#27ae60;font-weight:bold;} a.pre{color:#e67e22;} .box{display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid #ccc;vertical-align:middle;}</style></head><body>')
    
    h.append(f'<h3>In Stock in Portland <span class="ver">v19.0</span> <span class="date">{now}</span></h3>')

    print("--- STARTING UPDATE v19.0 ---")

    try:
        print("Fetching data through ScraperAPI residential proxy...")
        payload = {'api_key': SCRAPER_API_KEY, 'url': TARGET_URL}
        
        # Increased timeout to 60s because residential proxies route through actual home networks
        resp = requests.get('http://api.scraperapi.com', params=payload, timeout=60)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            products = data.get('products', [])
            print(f"Found {len(products)} total products in collection.")
            
            categorized_rows = {m: "" for m in TARGET_MODELS}

            for p in products:
                p_title = p.get('title', '')
                variants = p.get('variants', [])
                
                matched_model = None
                for m in TARGET_MODELS:
                    if m.upper()
