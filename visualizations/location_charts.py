import pandas as pd
from utils.constants import COL_LOCATION, COL_STATE, COL_INDUSTRY, COL_TITLE
from visualizations.charts import horizontal_bar, treemap_chart
from analysis.location_analysis import jobs_by_location, jobs_by_state

def listings_by_location_bar(df):
    return horizontal_bar(jobs_by_location(df), x="Listings", y=COL_LOCATION, title="Listings by City")

def avg_salary_by_location_bar(df):
    agg = jobs_by_location(df).sort_values("Avg_Salary",ascending=False)
    return horizontal_bar(agg, x="Avg_Salary", y=COL_LOCATION, title="Average Salary by City")

def listings_by_state_bar(df):
    agg = jobs_by_state(df)
    if agg.empty: return None
    return horizontal_bar(agg, x="Listings", y=COL_STATE, title="Listings by State")

def location_industry_treemap(df):
    return treemap_chart(df, path=[COL_LOCATION, COL_INDUSTRY], values=COL_TITLE,
                         title="City → Industry Breakdown")
