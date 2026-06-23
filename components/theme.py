"""
Kept for backward compatibility only. The app now uses a single professional
theme defined in assets/main_theme.css and injected by components/theme_manager.py.
Font tokens are available here if needed by other modules.
"""
FONT_DISPLAY = "'Inter', 'Segoe UI', sans-serif"
FONT_BODY    = "'Inter', 'Segoe UI', sans-serif"
FONT_MONO    = "'JetBrains Mono', 'Courier New', monospace"

def get_theme_config(theme_name: str = "default") -> dict:
    """Returns a single unified theme config."""
    return {
        "label": "Professional",
        "plotly_template": "plotly_white",
        "font_color": "#2D3748",
        "grid_color": "#E5E2DC",
    }
