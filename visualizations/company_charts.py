from utils.constants import COL_COMPANY, COL_SALARY
from visualizations.charts import horizontal_bar
from analysis.company_analysis import top_hiring_companies, highest_paying_companies

def top_hiring_companies_bar(df, top_n=10):
    return horizontal_bar(top_hiring_companies(df, top_n), x="Listings", y=COL_COMPANY, title=f"Top {top_n} Hiring Companies")

def highest_paying_companies_bar(df, top_n=10):
    data = highest_paying_companies(df, top_n)
    return horizontal_bar(data, x=COL_SALARY, y=COL_COMPANY, title=f"Top {top_n} Highest-Paying Companies")
