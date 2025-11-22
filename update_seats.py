import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
# We map the "Handle" (the last part of the URL) to the Display Name
HANDLE_MAP = {
    "vario-f": "Vario F",
    "vario-f-xxl": "Vario F XXL",
    "vario-f-klima": "Vario F Klima",
    "vario-f-xxl-klima-new": "Vario F XXL Klima"
}

# Map Handles to YOUR shop links
SHOP_LINKS = {
    "vario-f": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-seat",
    "vario-f-xxl": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-xxl-seat",
    "vario-f-klima": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat",
    "vario-f-xxl-klima-new": "https://www.tolerance-stack.com/product-page/scheel-mann-vario-f-klima-seat"
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
    update_time = datetime.now().strftime("%b %d at %H:%M UTC")
    
    # Start HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="refresh" content="300">
    <style>
      body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }
      h3 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 0; }
      .date { font-size: 0.8em; color: #666; float: right; font-weight: normal; margin-top: 5px;}
      table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }
      .title { background-color: #f4f4f4; padding: 10px; margin: 0; border-left: 5px solid #333; font-weight: bold; font-size: 1.1em; }
      th { text-align: left; padding: 10px; border-bottom: 1px solid #ccc; color: #555; font-size: 0.9em;}
      td { padding: 10px; border-bottom: 1px solid #eee; vertical-align: middle; }
      .box { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; border: 1px solid #ccc; vertical-align: middle; }
      a { text-decoration: none; }
      a:hover { text-decoration: underline; }
      .avail { color: #27ae60; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
      .pre { color: #e67e22; font-weight: bold; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
      .out-box { position: relative; display: inline-block; color: #666; padding: 0 4px; background: linear-gradient(to top left, transparent 46%, #888 49%, #888 51%, transparent 54%); }
      .out-text { color: #999; font-style: italic; font-size: 0.9em; }
    </style>
    </head>
    <body>
