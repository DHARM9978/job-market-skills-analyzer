import streamlit as st
from utils.session_manager import init_session_state
from utils.data_loader import get_active_dataframe
from utils.helpers import format_currency
from assets.custom_html import badge_html
from components.sidebar import render_sidebar_branding
from components.page_filters import filter_recommendations
from components.page_container import page_container
from components.chart_cards import chart_card
from components.metric_cards import render_metric_card
from analysis.recommendation_engine import full_recommendation
from analysis.market_trends import market_concentration
from visualizations.trend_charts import salary_by_bracket_bar, versatile_skills_bar, experience_curve_bar, skill_combo_bar

init_session_state()
render_sidebar_branding()
df = get_active_dataframe()
params = filter_recommendations(df)

with page_container("Recommendations","Personalised role matches, salary estimates, and skill-gap analysis.","🎯"):
    tab1, tab2 = st.tabs(["🎯 My Best-Fit Roles", "📈 Market Pulse"])

    with tab1:
        skills = params["current_skills"]
        exp    = params["experience_years"]
        desired = params["desired_role"]

        if not skills:
            st.info("👈 Add your current skills in the sidebar to get personalised recommendations.")
        else:
            result = full_recommendation(df, skills, exp)
            if result["best_title"] is None:
                st.warning("No overlapping roles found for those skills. Try adding more skills.")
            else:
                best   = desired or result["best_title"]
                salary = result["salary_estimate"]
                gap    = result["skill_gap"]

                st.success(f"**Best-fit role:** {best}")
                c1,c2,c3 = st.columns(3)
                with c1: render_metric_card("Estimated Low",    format_currency(salary["low"]),  "📉")
                with c2: render_metric_card("Estimated Median", format_currency(salary["mid"]),  "🎯")
                with c3: render_metric_card("Estimated High",   format_currency(salary["high"]), "📈")

                with chart_card("Top Matching Roles","📋","Ranked by how well your skills overlap with each role's requirements"):
                    st.dataframe(
                        result["title_matches"].style.format({"Avg_Salary":"₹{:,.0f}","Match_%":"{:.1f}%"}),
                        use_container_width=True, hide_index=True)

                c1,c2 = st.columns(2)
                with c1:
                    with chart_card("Skills You Have","✅"):
                        if gap["have"]:
                            st.markdown(" ".join(badge_html(s,"green") for s in gap["have"]), unsafe_allow_html=True)
                        else:
                            st.caption("None of the target skills detected yet.")
                with c2:
                    with chart_card("Skills to Learn","📚",f"Skill match: {gap['match_pct']:.0f}%"):
                        if gap["missing"]:
                            st.markdown(" ".join(badge_html(s,"amber") for s in gap["missing"]), unsafe_allow_html=True)
                        else:
                            st.success("You already cover all key skills for this role! 🎉")

    with tab2:
        st.caption("This is a snapshot dataset — these are structural signals, not time-series trends.")
        conc = market_concentration(df)
        c1,c2 = st.columns(2)
        with c1: render_metric_card("Leading Industry", conc["leading_industry"], "🏭")
        with c2: render_metric_card("Top-3 Industry Share", f"{conc['top3_industry_share']:.1f}%", "📊")
        with chart_card("Salary by Experience Bracket","💼"):
            st.plotly_chart(salary_by_bracket_bar(df), use_container_width=True, config={"displayModeBar":False})
        c1,c2 = st.columns(2)
        with c1:
            with chart_card("Most Versatile Skills","🧭","Spans the widest range of job titles"):
                st.plotly_chart(versatile_skills_bar(df), use_container_width=True, config={"displayModeBar":False})
        with c2:
            with chart_card("Steepest Pay Growth by Role","🚀"):
                fig = experience_curve_bar(df)
                if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
                else:   st.info("Not enough experience variety in the data.")
        fig2 = skill_combo_bar(df)
        if fig2:
            with chart_card("Skills That Travel Together","🔗"):
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
