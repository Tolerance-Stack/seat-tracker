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

def get_color_box(title):
    found_color = "#ccc" 
    if title:
        for color_name, hex_code in COLORS.items():
            if color_name.upper() in title.upper():
                found_color = hex_code
                break
    return f'<span class="box" style="background-color: {found_color};"></span>'

def clean_title(raw_title):
    # Remove " / " prefix (e.g. "Black / Black Basketweave")
    t = str(raw_title)
    if ' / ' in t:
        t = t.split(' / ')[-1].strip()
    # Remove status text like " - CURRENTLY IN PRODUCTION"
    t = t.split(' - ')[0].strip()
    return t

def fetch_seat_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
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
    html_parts.append('.box { display: inline-block; width: 12px; height: 12px; border-radius: 2px;
