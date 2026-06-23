"""
Renders the shared sidebar filter panel (location, industry, experience,
salary range, skill search) and returns the filtered dataframe. Used by
every analysis page so filters stay consistent across the app.
"""

import streamlit as st
import pandas as pd

from utils.constants import (
    COL_LOCATION, COL_INDUSTRY, COL_EXPERIENCE, COL_SALARY,
    COL_TITLE, COL_SKILLS,
)


def render_filters(df: pd.DataFrame, key_prefix: str = "f") -> pd.DataFrame:
    st.sidebar.markdown("### 🔎 Filters")

    locations = sorted(df[COL_LOCATION].dropna().unique().tolist())
    industries = sorted(df[COL_INDUSTRY].dropna().unique().tolist())
    titles = sorted(df[COL_TITLE].dropna().unique().tolist())

    sel_locations = st.sidebar.multiselect(
        "Location", locations, default=[], key=f"{key_prefix}_loc",
        placeholder="All locations",
    )
    sel_industries = st.sidebar.multiselect(
        "Industry", industries, default=[], key=f"{key_prefix}_ind",
        placeholder="All industries",
    )
    sel_titles = st.sidebar.multiselect(
        "Job Title", titles, default=[], key=f"{key_prefix}_title",
        placeholder="All job titles",
    )

    exp_min, exp_max = int(df[COL_EXPERIENCE].min()), int(df[COL_EXPERIENCE].max())
    sel_exp = st.sidebar.slider(
        "Experience (years)", exp_min, exp_max, (exp_min, exp_max), key=f"{key_prefix}_exp",
    )

    sal_min, sal_max = int(df[COL_SALARY].min()), int(df[COL_SALARY].max())
    sel_salary = st.sidebar.slider(
        "Salary range (₹)", sal_min, sal_max, (sal_min, sal_max),
        step=10000, key=f"{key_prefix}_sal", format="₹%d",
    )

    skill_query = st.sidebar.text_input(
        "Skill contains", placeholder="e.g. Python", key=f"{key_prefix}_skill"
    )

    filtered = df.copy()
    if sel_locations:
        filtered = filtered[filtered[COL_LOCATION].isin(sel_locations)]
    if sel_industries:
        filtered = filtered[filtered[COL_INDUSTRY].isin(sel_industries)]
    if sel_titles:
        filtered = filtered[filtered[COL_TITLE].isin(sel_titles)]
    filtered = filtered[
        (filtered[COL_EXPERIENCE] >= sel_exp[0]) & (filtered[COL_EXPERIENCE] <= sel_exp[1])
    ]
    filtered = filtered[
        (filtered[COL_SALARY] >= sel_salary[0]) & (filtered[COL_SALARY] <= sel_salary[1])
    ]
    if skill_query.strip():
        filtered = filtered[
            filtered[COL_SKILLS].str.contains(skill_query.strip(), case=False, na=False)
        ]

    if st.sidebar.button("↺ Reset filters", use_container_width=True, key=f"{key_prefix}_reset"):
        for k in [f"{key_prefix}_loc", f"{key_prefix}_ind", f"{key_prefix}_title",
                  f"{key_prefix}_exp", f"{key_prefix}_sal", f"{key_prefix}_skill"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.sidebar.caption(f"Showing **{len(filtered):,}** of {len(df):,} listings")

    return filtered
