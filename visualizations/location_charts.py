import pandas as pd

from utils.constants import (
    COL_LOCATION,
    COL_STATE,
    COL_INDUSTRY,
    COL_TITLE
)

from visualizations.charts import (
    horizontal_bar,
    treemap_chart
)

from analysis.location_analysis import (
    jobs_by_location,
    jobs_by_state
)


def listings_by_location_bar(df):
    """
    Bar chart showing total job listings by city.
    """
    agg = jobs_by_location(df)

    if agg.empty:
        return None

    return horizontal_bar(
        agg,
        x="Listings",
        y=COL_LOCATION,
        title="Listings by City"
    )


def avg_salary_by_location_bar(df):
    """
    Bar chart showing average salary by city.
    Requires 'Avg_Salary' column from jobs_by_location().
    """
    agg = jobs_by_location(df)

    if agg.empty:
        return None

    if "Avg_Salary" not in agg.columns:
        return None

    agg = agg.sort_values(
        by="Avg_Salary",
        ascending=False
    )

    return horizontal_bar(
        agg,
        x="Avg_Salary",
        y=COL_LOCATION,
        title="Average Salary by City"
    )


def listings_by_state_bar(df):
    """
    Bar chart showing total job listings by state.
    """
    agg = jobs_by_state(df)

    if agg.empty:
        return None

    return horizontal_bar(
        agg,
        x="Listings",
        y=COL_STATE,
        title="Listings by State"
    )


def location_industry_treemap(df):
    """
    Treemap showing City → Industry distribution.
    """

    df = df.copy()

    df = df[
        ~df[COL_LOCATION]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["unknown", "india", ""])
    ]

    if df.empty:
        return None

    df["Job_Count"] = 1

    return treemap_chart(
        df,
        path=[COL_LOCATION, COL_INDUSTRY],
        values="Job_Count",
        title="City → Industry Breakdown"
    )