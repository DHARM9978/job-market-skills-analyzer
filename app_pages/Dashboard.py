import streamlit as st
from utils.session_manager import init_session_state
from utils.data_loader import get_active_dataframe
from components.sidebar import render_sidebar_branding
from components.page_filters import filter_dashboard
from components.page_container import page_container
from components.dashboard_sections import render_dashboard

init_session_state()
render_sidebar_branding()
df = get_active_dataframe()
filtered = filter_dashboard(df)

with page_container("Dashboard","A bird's-eye view of the job market — listings, pay, and demand signals.","📊"):
    if filtered.empty:
        st.warning("No listings match the current filters. Try widening your selection.")
    else:
        render_dashboard(filtered)
