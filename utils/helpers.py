import math
from utils.constants import CURRENCY_SYMBOL, LAKH, CRORE

def _nan(v):
    if v is None: return True
    try: return math.isnan(float(v))
    except: return False

def format_currency(amount, compact=True):
    if _nan(amount): return "Not disclosed"
    if not compact: return f"{CURRENCY_SYMBOL}{amount:,.0f}"
    if amount >= CRORE: return f"{CURRENCY_SYMBOL}{amount/CRORE:.2f}Cr"
    if amount >= LAKH:  return f"{CURRENCY_SYMBOL}{amount/LAKH:.1f}L"
    return f"{CURRENCY_SYMBOL}{amount:,.0f}"

def format_number(value):
    if _nan(value): return "—"
    if value >= 1_000_000: return f"{value/1_000_000:.1f}M"
    if value >= 1_000:     return f"{value/1_000:.1f}K"
    return f"{value:,.0f}"

def format_percent(value, decimals=1):
    if _nan(value): return "—"
    return f"{value:.{decimals}f}%"

def safe_divide(num, den, default=0.0):
    return num / den if den else default

def truncate(text, length=30):
    text = str(text)
    return text if len(text) <= length else text[:length-1] + "…"
