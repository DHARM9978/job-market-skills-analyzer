import streamlit as st
from components.chart_cards import chart_card
from components.kpi_cards import render_kpi_row
from analysis.dashboard_metrics import compute_dashboard_metrics
from visualizations.dashboard_charts import industry_split_chart, salary_distribution_chart, top_locations_chart, experience_vs_salary_scatter
from visualizations.maps import jobs_map

def render_dashboard(df):
    metrics = compute_dashboard_metrics(df)
    render_kpi_row(metrics)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        with chart_card("Listings by Industry","🏭"):
            st.plotly_chart(industry_split_chart(df), use_container_width=True, config={"displayModeBar":False})
    with c2:
        with chart_card("Salary Distribution","💰"):
            st.plotly_chart(salary_distribution_chart(df), use_container_width=True, config={"displayModeBar":False})
    c3,c4 = st.columns(2)
    with c3:
        with chart_card("Top Hiring Locations","📍"):
            st.plotly_chart(top_locations_chart(df), use_container_width=True, config={"displayModeBar":False})
    with c4:
        with chart_card("Experience vs Salary","📈"):
            st.plotly_chart(experience_vs_salary_scatter(df), use_container_width=True, config={"displayModeBar":False})
    with chart_card("City Map — Job Density & Pay","🗺️"):
        fig = jobs_map(df)
        if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        else:   st.info("No mappable location data available for the current filters.")
