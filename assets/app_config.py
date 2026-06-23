"""App-wide configuration constants."""
import os
from utils.constants import APP_TITLE, APP_ICON

PAGE_CONFIG = {
    "page_title":           APP_TITLE,
    "page_icon":            APP_ICON,
    "layout":               "wide",
    # PERMANENT SIDEBAR: always start expanded; CSS hides the collapse button
    "initial_sidebar_state": "expanded",
}

CHART_HEIGHT_SM  = 280
CHART_HEIGHT_MD  = 380
CHART_HEIGHT_LG  = 460
THEME_CSS_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_theme.css")
