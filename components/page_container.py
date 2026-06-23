from contextlib import contextmanager
import streamlit as st
from components.theme_manager import inject_theme
from components.header import render_header
from components.footer import render_footer

@contextmanager
def page_container(title, subtitle="", icon="", section="Analytics"):
    inject_theme()
    render_header(title, subtitle, icon, section)
    yield
    render_footer()
