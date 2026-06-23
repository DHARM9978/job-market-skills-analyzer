import streamlit as st
from assets.custom_html import page_header_html

def render_header(title, subtitle="", icon="", section="Analytics"):
    st.markdown(page_header_html(title, subtitle, icon, section), unsafe_allow_html=True)
