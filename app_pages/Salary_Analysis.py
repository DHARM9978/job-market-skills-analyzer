import streamlit as st
from utils.session_manager import init_session_state
from utils.data_loader import get_active_dataframe
from utils.helpers import format_currency
from components.sidebar import render_sidebar_branding
from components.page_filters import filter_salary
from components.page_container import page_container
from components.chart_cards import chart_card
from components.metric_cards import render_metric_card
from analysis.salary_analysis import salary_overview, highest_paying_titles
from visualizations.salary_charts import salary_by_title_box, avg_salary_by_location_bar, avg_salary_by_industry_bar, salary_vs_experience_line

init_session_state()
render_sidebar_branding()
df = get_active_dataframe()
filtered = filter_salary(df)

with page_container("Salary Analysis","How pay varies by role, location, industry, and experience.","💰"):
    if filtered.empty:
        st.warning("No listings match the current filters.")
    else:
        stats = salary_overview(filtered)
        c1,c2,c3,c4 = st.columns(4)
        with c1: render_metric_card("Average",    format_currency(stats["mean"]),   "💵")
        with c2: render_metric_card("Median",     format_currency(stats["median"]), "📊")
        with c3: render_metric_card("Lowest",     format_currency(stats["min"]),    "⬇️")
        with c4: render_metric_card("Highest",    format_currency(stats["max"]),    "⬆️")

        top_titles = highest_paying_titles(filtered, 8)["Job_Title"].tolist()
        with chart_card("Salary Spread by Job Title","📦","Box-plot of salary distribution for top 8 roles by average pay"):
            st.plotly_chart(salary_by_title_box(filtered, top_titles), use_container_width=True, config={"displayModeBar":False})
        c1,c2 = st.columns(2)
        with c1:
            with chart_card("Avg. Salary by Location","📍"):
                st.plotly_chart(avg_salary_by_location_bar(filtered), use_container_width=True, config={"displayModeBar":False})
        with c2:
            with chart_card("Avg. Salary by Industry","🏭"):
                st.plotly_chart(avg_salary_by_industry_bar(filtered), use_container_width=True, config={"displayModeBar":False})
        with chart_card("Salary vs. Years of Experience","📈"):
            st.plotly_chart(salary_vs_experience_line(filtered), use_container_width=True, config={"displayModeBar":False})
        with chart_card("Highest-Paying Roles","🏆"):
            tbl = highest_paying_titles(filtered, 15).rename(columns={"avg_salary":"Avg Salary","median_salary":"Median Salary","count":"Listings"})
            st.dataframe(tbl.style.format({"Avg Salary":"₹{:,.0f}","Median Salary":"₹{:,.0f}"}), use_container_width=True, hide_index=True)
