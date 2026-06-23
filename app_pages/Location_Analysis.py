import streamlit as st
from utils.session_manager import init_session_state
from utils.data_loader import get_active_dataframe
from utils.constants import COL_LOCATION, COL_STATE
from components.sidebar import render_sidebar_branding
from components.page_filters import filter_location
from components.page_container import page_container
from components.chart_cards import chart_card
from analysis.location_analysis import jobs_by_location, jobs_by_state, top_industry_per_location
from visualizations.location_charts import listings_by_location_bar, avg_salary_by_location_bar, listings_by_state_bar, location_industry_treemap
from visualizations.maps import jobs_map

init_session_state()
render_sidebar_branding()
df = get_active_dataframe()
filtered = filter_location(df)

with page_container("Location Analysis","Where the jobs are concentrated — city and state level.","📍"):
    if filtered.empty:
        st.warning("No listings match the current filters.")
    else:
        with chart_card("Interactive City Map","🗺️","Bubble size = listings, colour = average salary"):
            fig = jobs_map(filtered)
            if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            else:   st.info("No mappable location data for the current filters.")
        c1,c2 = st.columns(2)
        with c1:
            with chart_card("Listings by City","🏙️"):
                st.plotly_chart(listings_by_location_bar(filtered), use_container_width=True, config={"displayModeBar":False})
        with c2:
            with chart_card("Avg. Salary by City","💰"):
                st.plotly_chart(avg_salary_by_location_bar(filtered), use_container_width=True, config={"displayModeBar":False})
        state_fig = listings_by_state_bar(filtered)
        if state_fig:
            with chart_card("Listings by State","🗺️"):
                st.plotly_chart(state_fig, use_container_width=True, config={"displayModeBar":False})
        with chart_card("City → Industry Breakdown","🏭"):
            st.plotly_chart(location_industry_treemap(filtered), use_container_width=True, config={"displayModeBar":False})
        with chart_card("City Summary Table","📑"):
            summary = jobs_by_location(filtered).drop(columns=["Lat","Lon"], errors="ignore")
            industries = top_industry_per_location(filtered)
            summary = summary.merge(industries, on=COL_LOCATION, how="left")
            st.dataframe(summary.style.format({"Avg_Salary":"₹{:,.0f}"}), use_container_width=True, hide_index=True)
