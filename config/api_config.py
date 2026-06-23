"""
Adzuna API credentials.

HOW TO GET THESE:
  Register at https://developer.adzuna.com/ → create an application →
  copy the App ID and App Key into the two variables below.

CREDENTIALS ARE ALREADY SET for this build.
>>> config/api_config.py  ←  APP_ID and APP_KEY live here <<<
"""

# ↓↓ Adzuna App ID ↓↓
APP_ID  = "de75124c"                        # ← APP_ID

# ↓↓ Adzuna App Key ↓↓
APP_KEY = "ca750e967b32f311e30f49acccf9dec6"  # ← APP_KEY

# ---------------------------------------------------------------------------
# Search settings
# ---------------------------------------------------------------------------
COUNTRY          = "in"          # India  (gb=UK, us=USA, au=Australia …)
MAX_PAGES        = 4             # pages to fetch on startup (50 results/page)
RESULTS_PER_PAGE = 50            # Adzuna max is 50
CACHE_TTL_SECONDS = 1800         # 30 min cache so repeated page visits are fast

# Optional keyword filter — leave blank for all jobs
WHAT_FILTER = ""                 # e.g. "data analyst", "python developer"


def is_configured() -> bool:
    """Returns True when both credentials have been filled in."""
    return bool(APP_ID.strip()) and bool(APP_KEY.strip())
