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

COLORS = {"Black": "#000", "Grey": "#666", "Gray": "#666", "Brown": "#654321", "Tan": "#D2B48C"}

# --- MASTER LIST (For Name Cleaning) ---
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
    
    # HTML HEADER - Short lines for safety
    html = ""
    html += '<!DOCTYPE html><html><head>'
    html += '<meta http-equiv="refresh" content="300">'
    html += '<meta http-equiv="cache-control" content="no-cache">'
    html += '<style>'
    html += 'body { font-family: sans-serif; padding: 10px; }'
    html += 'h3 { border-bottom: 2px solid #333; padding-bottom: 10px; }'
    html += '.ver { background: blue; color: white; padding: 2px 5px; border-radius: 3px; font-size: 0.8em; }'
    html += '.date { font-size: 0.8em; color: #666; float: right; }'
    html += 'table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }'
    html += '.title { background: #f4f4f4; padding: 10px; font-weight: bold; }'
    html += 'th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; }'
    html += 'td { padding: 10px; border-bottom: 1px solid #eee; }'
    html += '.box { display: inline-block; width: 12px; height: 12px; margin-right: 8px; border: 1px solid #ccc; }'
    html += 'a { text-decoration: none; color: #27ae60; font-weight: bold; }'
    html += 'a.pre {
