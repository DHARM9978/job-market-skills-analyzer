"""
Sidebar branding, data-source status, and API connection info.
Sidebar is always visible — collapse button is hidden via CSS.
"""
import streamlit as st
from utils.constants import SESSION_DATA_SOURCE_KEY, SESSION_API_ERROR_KEY
from utils.data_loader import reset_to_default
from assets.custom_html import status_html
from config import api_config


def render_sidebar_branding():
    st.sidebar.markdown(
        """
        <div style="padding:0.2rem 0 0.8rem 0;">
            <div style="font-size:1.15rem;font-weight:800;color:#2D3748;letter-spacing:-0.02em;">
                📊 SkillScope
            </div>
            <div style="font-size:0.75rem;color:#6B7280;margin-top:0.1rem;">
                Decode the job market. Find your edge.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    src   = st.session_state.get(SESSION_DATA_SOURCE_KEY)
    error = st.session_state.get(SESSION_API_ERROR_KEY)

    if src == "api":
        st.sidebar.markdown(
            status_html("🟢 Live Adzuna API data", "api"), unsafe_allow_html=True
        )
    elif src == "upload":
        fname = st.session_state.get("uploaded_filename", "custom file")
        st.sidebar.markdown(
            status_html(f"🟣 Uploaded: {fname}", "upload"), unsafe_allow_html=True
        )
        if st.sidebar.button("↺ Revert to API / sample data", use_container_width=True):
            reset_to_default()
            st.rerun()
    elif src == "sample":
        st.sidebar.markdown(
            status_html("🟡 Using sample dataset", "sample"), unsafe_allow_html=True
        )
        # Show why API isn't being used
        if error:
            with st.sidebar.expander("ℹ️ Why sample data?"):
                if api_config.is_configured():
                    st.error(f"API error: {error}", icon="⚠️")
                else:
                    st.caption(
                        "API credentials not set in `config/api_config.py`. "
                        "Currently using bundled sample CSV as fallback."
                    )
    else:
        st.sidebar.markdown(
            status_html("⏳ Loading data…", "sample"), unsafe_allow_html=True
        )

    st.sidebar.divider()
