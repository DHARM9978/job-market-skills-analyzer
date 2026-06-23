import streamlit as st
from assets.custom_html import kpi_card_html

def render_metric_card(label, value, icon="", sub=""):
    st.markdown(kpi_card_html(label, value, icon, sub), unsafe_allow_html=True)
