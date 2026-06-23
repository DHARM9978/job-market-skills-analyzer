import datetime, streamlit as st
from assets.custom_html import footer_html

def render_footer():
    st.markdown(footer_html(datetime.datetime.now().year), unsafe_allow_html=True)
