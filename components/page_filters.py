"""Page-specific sidebar filter panels."""
import pandas as pd
import streamlit as st
from utils.constants import (
    COL_TITLE, COL_LOCATION, COL_STATE, COL_SALARY,
    COL_INDUSTRY, COL_EXPERIENCE, COL_EXP_BRACKET,
    COL_DATE_POSTED, COL_SKILLS_LIST,
)

def _clear(prefix):
    if st.sidebar.button("↺ Clear filters", use_container_width=True, key=f"{prefix}_clear"):
        for k in [k for k in st.session_state if k.startswith(f"{prefix}_")]:
            del st.session_state[k]
        st.rerun()

def _count(original, filtered):
    pct = int(len(filtered)/len(original)*100) if len(original) else 0
    st.sidebar.caption(f"**{len(filtered):,}** of {len(original):,} listings ({pct}%)")
    return filtered

# ── Dashboard ──────────────────────────────────────────────────────────────
def filter_dashboard(df):
    st.sidebar.subheader("🔍 Filters")
    cats = sorted(df[COL_INDUSTRY].dropna().unique())
    sel_cats = st.sidebar.multiselect("Job Category", cats, key="dash_cat", placeholder="All categories")
    locs = sorted(df[COL_LOCATION].dropna().unique())
    sel_locs = st.sidebar.multiselect("Location", locs, key="dash_loc", placeholder="All locations")
    sel_dates = None
    if COL_DATE_POSTED in df.columns:
        dates = df[COL_DATE_POSTED].dropna()
        if not dates.empty:
            mn, mx = dates.min().date(), dates.max().date()
            if mn < mx:
                sel_dates = st.sidebar.date_input("Date Range", (mn, mx), mn, mx, key="dash_dates")
    out = df.copy()
    if sel_cats:  out = out[out[COL_INDUSTRY].isin(sel_cats)]
    if sel_locs:  out = out[out[COL_LOCATION].isin(sel_locs)]
    if sel_dates and len(sel_dates) == 2 and COL_DATE_POSTED in df.columns:
        s = pd.Timestamp(sel_dates[0], tz="UTC"); e = pd.Timestamp(sel_dates[1], tz="UTC")
        out = out[(out[COL_DATE_POSTED] >= s) & (out[COL_DATE_POSTED] <= e)]
    _clear("dash"); return _count(df, out)

# ── Skills Analysis ────────────────────────────────────────────────────────
def filter_skills(df):
    st.sidebar.subheader("🔍 Filters")
    all_skills = sorted({s for row in df[COL_SKILLS_LIST] for s in row}) if COL_SKILLS_LIST in df.columns else []
    sel_skills = st.sidebar.multiselect("Skill", all_skills[:100], key="skill_sk", placeholder="Any skill")
    levels = sorted([b for b in df[COL_EXP_BRACKET].unique() if b != "Unknown"])
    sel_exp = st.sidebar.multiselect("Experience Level", levels, key="skill_exp", placeholder="All levels")
    cats = sorted(df[COL_INDUSTRY].dropna().unique())
    sel_cats = st.sidebar.multiselect("Job Category", cats, key="skill_cat", placeholder="All categories")
    out = df.copy()
    if sel_skills: out = out[out[COL_SKILLS_LIST].apply(lambda lst: any(s in lst for s in sel_skills))]
    if sel_exp:    out = out[out[COL_EXP_BRACKET].isin(sel_exp)]
    if sel_cats:   out = out[out[COL_INDUSTRY].isin(sel_cats)]
    _clear("skill"); return _count(df, out)

# ── Salary Analysis ────────────────────────────────────────────────────────
def filter_salary(df):
    st.sidebar.subheader("🔍 Filters")
    roles = sorted(df[COL_TITLE].dropna().unique())
    sel_roles = st.sidebar.multiselect("Job Role", roles, key="sal_role", placeholder="All roles")
    locs = sorted(df[COL_LOCATION].dropna().unique())
    sel_locs = st.sidebar.multiselect("Location", locs, key="sal_loc", placeholder="All locations")
    levels = sorted([b for b in df[COL_EXP_BRACKET].unique() if b != "Unknown"])
    sel_exp = st.sidebar.multiselect("Experience Level", levels, key="sal_exp", placeholder="All levels")
    sel_sal = None
    if COL_SALARY in df.columns:
        s_data = df[COL_SALARY].dropna()
        if not s_data.empty:
            mn, mx = int(s_data.min()), int(s_data.max())
            if mn < mx:
                sel_sal = st.sidebar.slider("Salary Range (₹)", mn, mx, (mn, mx), step=10_000, key="sal_range", format="₹%d")
    out = df.copy()
    if sel_roles: out = out[out[COL_TITLE].isin(sel_roles)]
    if sel_locs:  out = out[out[COL_LOCATION].isin(sel_locs)]
    if sel_exp:   out = out[out[COL_EXP_BRACKET].isin(sel_exp)]
    if sel_sal:   out = out[(out[COL_SALARY] >= sel_sal[0]) & (out[COL_SALARY] <= sel_sal[1])]
    _clear("sal"); return _count(df, out)

# ── Location Analysis ──────────────────────────────────────────────────────
def filter_location(df):
    st.sidebar.subheader("🔍 Filters")
    if COL_STATE in df.columns and df[COL_STATE].notna().any():
        states = sorted(df[COL_STATE].dropna().unique())
        sel_states = st.sidebar.multiselect("State", states, key="loc_state", placeholder="All states")
    else:
        sel_states = []
    cities = sorted(df[COL_LOCATION].dropna().unique())
    sel_cities = st.sidebar.multiselect("City", cities, key="loc_city", placeholder="All cities")
    cats = sorted(df[COL_INDUSTRY].dropna().unique())
    sel_cats = st.sidebar.multiselect("Job Category", cats, key="loc_cat", placeholder="All categories")
    levels = sorted([b for b in df[COL_EXP_BRACKET].unique() if b != "Unknown"])
    sel_exp = st.sidebar.multiselect("Experience Level", levels, key="loc_exp", placeholder="All levels")
    out = df.copy()
    if sel_states and COL_STATE in df.columns: out = out[out[COL_STATE].isin(sel_states)]
    if sel_cities: out = out[out[COL_LOCATION].isin(sel_cities)]
    if sel_cats:   out = out[out[COL_INDUSTRY].isin(sel_cats)]
    if sel_exp:    out = out[out[COL_EXP_BRACKET].isin(sel_exp)]
    _clear("loc"); return _count(df, out)

# ── Company Analysis ───────────────────────────────────────────────────────
def filter_company(df):
    st.sidebar.subheader("🔍 Filters")
    locs = sorted(df[COL_LOCATION].dropna().unique())
    sel_locs = st.sidebar.multiselect("Location", locs, key="comp_loc", placeholder="All locations")
    cats = sorted(df[COL_INDUSTRY].dropna().unique())
    sel_cats = st.sidebar.multiselect("Industry", cats, key="comp_cat", placeholder="All industries")
    levels = sorted([b for b in df[COL_EXP_BRACKET].unique() if b != "Unknown"])
    sel_exp = st.sidebar.multiselect("Experience Level", levels, key="comp_exp", placeholder="All levels")
    out = df.copy()
    if sel_locs: out = out[out[COL_LOCATION].isin(sel_locs)]
    if sel_cats: out = out[out[COL_INDUSTRY].isin(sel_cats)]
    if sel_exp:  out = out[out[COL_EXP_BRACKET].isin(sel_exp)]
    _clear("comp"); return _count(df, out)

# ── Recommendations ────────────────────────────────────────────────────────
def filter_recommendations(df):
    """Returns a user-profile dict instead of a filtered DataFrame."""
    st.sidebar.subheader("👤 Your Profile")
    roles = sorted(df[COL_TITLE].dropna().unique())
    desired_role = st.sidebar.selectbox("Desired Role", ["(auto-match)"] + list(roles), key="rec_role")
    all_skills = sorted({s for row in df[COL_SKILLS_LIST] for s in row}) if COL_SKILLS_LIST in df.columns else []
    current_skills = st.sidebar.multiselect("Your Skills", all_skills[:100], key="rec_skills", placeholder="Select skills…")
    extra_text = st.sidebar.text_input("…or type skills (comma-sep)", key="rec_text", placeholder="Python, SQL, AWS")
    level_map = {"Entry (0–1 yr)": 0.5, "Junior (2–3 yrs)": 2, "Mid (4–5 yrs)": 4,
                 "Senior (6–7 yrs)": 6, "Lead (8+ yrs)": 9}
    sel_level = st.sidebar.selectbox("Experience Level", list(level_map.keys()), index=1, key="rec_exp")
    extra = [s.strip() for s in extra_text.split(",") if s.strip()]
    combined = list(dict.fromkeys(current_skills + extra))
    return {
        "desired_role": None if desired_role == "(auto-match)" else desired_role,
        "current_skills": combined,
        "experience_level": sel_level,
        "experience_years": level_map[sel_level],
    }
