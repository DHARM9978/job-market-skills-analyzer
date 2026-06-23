import streamlit as st

def render_skeleton(count=1):
    for _ in range(count):
        st.markdown('<div class="sk-skeleton"></div>', unsafe_allow_html=True)

def with_spinner(msg="Crunching numbers…"):
    return st.spinner(msg)
