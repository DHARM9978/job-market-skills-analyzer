import pandas as pd
from utils.constants import COL_TITLE, COL_SALARY, COL_LOCATION, COL_INDUSTRY, COL_EXPERIENCE
from visualizations.charts import box_chart, horizontal_bar, line_chart
from analysis.salary_analysis import avg_salary_by, salary_by_experience

def salary_by_title_box(df, top_titles=None):
    plot = df[df[COL_TITLE].isin(top_titles)] if top_titles else df
    return box_chart(plot.dropna(subset=[COL_SALARY]), x=COL_TITLE, y=COL_SALARY, title="Salary Spread by Job Title")

def avg_salary_by_location_bar(df):
    agg = avg_salary_by(df, COL_LOCATION)
    return horizontal_bar(agg, x="avg_salary", y=COL_LOCATION, title="Average Salary by Location")

def avg_salary_by_industry_bar(df):
    agg = avg_salary_by(df, COL_INDUSTRY)
    return horizontal_bar(agg, x="avg_salary", y=COL_INDUSTRY, title="Average Salary by Industry")

def salary_vs_experience_line(df):
    agg = salary_by_experience(df)
    return line_chart(agg, x=COL_EXPERIENCE, y=COL_SALARY, title="Avg. Salary by Years of Experience")
