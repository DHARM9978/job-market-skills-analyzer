from contextlib import contextmanager
import streamlit as st

@contextmanager
def chart_card(title="", icon="", subtitle=""):
    with st.container(border=True):
        if title:
            st.markdown(
                f'<div class="sk-card-title">{icon}&nbsp;{title}</div>'
                + (f'<div class="sk-card-sub">{subtitle}</div>' if subtitle else ""),
                unsafe_allow_html=True,
            )
        yield
