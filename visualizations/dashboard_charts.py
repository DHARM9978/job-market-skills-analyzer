import pandas as pd
from utils.constants import COL_INDUSTRY, COL_SALARY, COL_LOCATION, COL_EXPERIENCE, COL_TITLE
from visualizations.charts import pie_chart, histogram_chart, horizontal_bar, scatter_chart

def industry_split_chart(df): 
    c = df[COL_INDUSTRY].value_counts().reset_index(); c.columns=[COL_INDUSTRY,"Count"]
    return pie_chart(c, names=COL_INDUSTRY, values="Count", title="Listings by Industry")

def salary_distribution_chart(df):
    return histogram_chart(df.dropna(subset=[COL_SALARY]), x=COL_SALARY, nbins=30, title="Salary Distribution")

def top_locations_chart(df, top_n=8):
    c = df[COL_LOCATION].value_counts().head(top_n).reset_index(); c.columns=[COL_LOCATION,"Listings"]
    return horizontal_bar(c, x="Listings", y=COL_LOCATION, title="Top Hiring Locations")

def experience_vs_salary_scatter(df):
    return scatter_chart(df.dropna(subset=[COL_SALARY,COL_EXPERIENCE]),
                         x=COL_EXPERIENCE, y=COL_SALARY, color=COL_INDUSTRY,
                         hover_name=COL_TITLE, title="Experience vs Salary")
