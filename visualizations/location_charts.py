import pandas as pd
from utils.constants import COL_LOCATION, COL_STATE, COL_INDUSTRY, COL_TITLE
from visualizations.charts import horizontal_bar, treemap_chart
from analysis.location_analysis import jobs_by_location, jobs_by_state

def listings_by_location_bar(df):
    return horizontal_bar(jobs_by_location(df), x="Listings", y=COL_LOCATION, title="Listings by City")

def listings_by_location_bar(df):

    agg = jobs_by_location(df)

    print("\n===== DATA GOING TO CHART =====")
    print(agg)

    return horizontal_bar(
        agg,
        x="Listings",
        y=COL_LOCATION,
        title="Listings by City"
    )

def listings_by_state_bar(df):
    agg = jobs_by_state(df)
    if agg.empty: return None
    return horizontal_bar(agg, x="Listings", y=COL_STATE, title="Listings by State")

def location_industry_treemap(df):

    df = df.copy()

    # Remove Unknown locations
    df = df[
        ~df[COL_LOCATION]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["unknown", "india", ""])
        ]

    df["Job_Count"] = 1

    return treemap_chart(
        df,
        path=[COL_LOCATION, COL_INDUSTRY],
        values="Job_Count",
        title="City → Industry Breakdown"
    )