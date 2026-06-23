import streamlit as st
from components.metric_cards import render_metric_card
from utils.helpers import format_currency, format_number

def render_kpi_row(metrics: dict):
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: render_metric_card("Total Jobs",   format_number(metrics.get("total_jobs",0)),       "📋")
    with c2: render_metric_card("Avg. Salary",  format_currency(metrics.get("avg_salary")),        "💰")
    with c3: render_metric_card("Top Location", metrics.get("top_location","—"),                   "📍")
    with c4: render_metric_card("Top Skill",    metrics.get("top_skill","—"),                      "🛠️")
    with c5: render_metric_card("Companies",    format_number(metrics.get("total_companies",0)),   "🏢")
