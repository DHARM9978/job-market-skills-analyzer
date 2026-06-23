"""
Single-theme injection. No toggle — the app has one professional look.
Charts get a consistent warm-white plotly layout.
"""
import os, streamlit as st
from assets.app_config import THEME_CSS_PATH
from assets.color_palette import CATEGORICAL_SEQUENCE

_FONT_IMPORT = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'


def inject_theme():
    st.markdown(_FONT_IMPORT, unsafe_allow_html=True)
    try:
        with open(THEME_CSS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # graceful if file is missing


def themed_plotly_layout(fig, height: int = 380):
    """Apply professional warm-white layout to any Plotly figure."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2D3748", family="Inter, sans-serif", size=12.5),
        title_font=dict(family="Inter, sans-serif", size=15, color="#2D3748"),
        height=height,
        margin=dict(l=8, r=8, t=44, b=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        hoverlabel=dict(
            bgcolor="#FFFFFF", bordercolor="#E5E2DC",
            font=dict(family="JetBrains Mono, monospace", size=12, color="#2D3748"),
        ),
        colorway=CATEGORICAL_SEQUENCE,
    )
    fig.update_xaxes(
        gridcolor="#E5E2DC", zerolinecolor="#E5E2DC",
        tickfont=dict(family="JetBrains Mono, monospace", size=11, color="#6B7280"),
    )
    fig.update_yaxes(
        gridcolor="#E5E2DC", zerolinecolor="#E5E2DC",
        tickfont=dict(family="JetBrains Mono, monospace", size=11, color="#6B7280"),
    )
    return fig
