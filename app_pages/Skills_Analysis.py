import streamlit as st
from utils.session_manager import init_session_state
from utils.data_loader import get_active_dataframe
from utils.constants import COL_TITLE
from components.sidebar import render_sidebar_branding
from components.page_filters import filter_skills
from components.page_container import page_container
from components.chart_cards import chart_card
from analysis.skill_analysis import top_skills, skills_for_title
from visualizations.skill_charts import top_skills_bar, skill_cooccurrence_heatmap, skill_premium_bar

init_session_state()
render_sidebar_branding()
df = get_active_dataframe()
filtered = filter_skills(df)

with page_container("Skills Analysis","Which skills are most in demand, pay a premium, and appear together.","🛠️"):
    if filtered.empty:
        st.warning("No listings match the current filters.")
    else:
        c1,c2 = st.columns([3,2])
        with c1:
            with chart_card("Most In-Demand Skills","🔥"):
                st.plotly_chart(top_skills_bar(filtered), use_container_width=True, config={"displayModeBar":False})
        with c2:
            with chart_card("Salary Premium by Skill","💎","% above/below market average"):
                fig = skill_premium_bar(filtered)
                if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
                else:   st.info("Not enough salary data to compute premiums.")
        with chart_card("Skill Co-occurrence","🔗","Which top skills appear together in the same listing"):
            st.plotly_chart(skill_cooccurrence_heatmap(filtered), use_container_width=True, config={"displayModeBar":False})
        with chart_card("Skills by Job Title","🔍"):
            titles = sorted(filtered[COL_TITLE].unique())
            chosen = st.selectbox("Select a role", titles, key="skill_title_sel")
            role_skills = skills_for_title(filtered, chosen, top_n=10)
            if role_skills.empty: st.info("No skill data for this role under the current filters.")
            else:                  st.dataframe(role_skills, use_container_width=True, hide_index=True)
        with chart_card("All Top Skills — Full Table","📋"):
            st.dataframe(top_skills(filtered, 30), use_container_width=True, hide_index=True)
