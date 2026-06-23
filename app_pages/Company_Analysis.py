import streamlit as st
from utils.session_manager import init_session_state
from utils.data_loader import get_active_dataframe
from utils.helpers import format_currency
from utils.constants import COL_COMPANY
from components.sidebar import render_sidebar_branding
from components.page_filters import filter_company
from components.page_container import page_container
from components.chart_cards import chart_card
from components.metric_cards import render_metric_card
from analysis.company_analysis import company_profile
from visualizations.company_charts import top_hiring_companies_bar, highest_paying_companies_bar

init_session_state()
render_sidebar_branding()
df = get_active_dataframe()
filtered = filter_company(df)

with page_container("Company Analysis","Who's hiring the most, who pays the best, and what each company focuses on.","🏢"):
    if filtered.empty:
        st.warning("No listings match the current filters.")
    else:
        c1,c2 = st.columns(2)
        with c1:
            with chart_card("Top Hiring Companies","📋"):
                st.plotly_chart(top_hiring_companies_bar(filtered), use_container_width=True, config={"displayModeBar":False})
        with c2:
            with chart_card("Highest-Paying Companies","💰"):
                st.plotly_chart(highest_paying_companies_bar(filtered), use_container_width=True, config={"displayModeBar":False})
        with chart_card("Company Deep-Dive","🔍"):
            companies = sorted(filtered[COL_COMPANY].unique())
            chosen = st.selectbox("Choose a company", companies, key="comp_sel")
            profile = company_profile(filtered, chosen)
            if not profile:
                st.info("No data for this company under the current filters.")
            else:
                c1,c2,c3 = st.columns(3)
                with c1: render_metric_card("Total Listings", str(profile["listings"]),              "📋")
                with c2: render_metric_card("Avg. Salary",    format_currency(profile["avg_salary"]),"💰")
                with c3: render_metric_card("Top Industry",   profile["top_industry"],               "🏭")
                st.markdown("**Top roles posted:**")
                st.dataframe(profile["top_roles"], use_container_width=True, hide_index=True)
