"""SkillScope — Job Market Analyzer entry point."""
import streamlit as st
from assets.app_config import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

pages = [
    st.Page("app_pages/Dashboard.py",        title="Dashboard",         icon="📊", default=True),
    st.Page("app_pages/Salary_Analysis.py",  title="Salary Analysis",   icon="💰"),
    st.Page("app_pages/Skills_Analysis.py",  title="Skills Analysis",   icon="🛠️"),
    st.Page("app_pages/Location_Analysis.py",title="Location Analysis", icon="📍"),
    st.Page("app_pages/Company_Analysis.py", title="Company Analysis",  icon="🏢"),
    st.Page("app_pages/Recommendations.py",  title="Recommendations",   icon="🎯"),
    st.Page("app_pages/Upload_Data.py",      title="Upload Data",       icon="📤"),
]

st.navigation(pages).run()
