import pandas as pd
from utils.constants import COL_SALARY, COL_TITLE, COL_LOCATION, COL_INDUSTRY, COL_EXPERIENCE

def salary_overview(df):
    s = df[COL_SALARY].dropna()
    if s.empty: return {"mean":None,"median":None,"min":None,"max":None,"std":None,"p25":None,"p75":None}
    return {"mean":s.mean(),"median":s.median(),"min":s.min(),"max":s.max(),
            "std":s.std(),"p25":s.quantile(0.25),"p75":s.quantile(0.75)}

def avg_salary_by(df, group_col, top_n=None):
    out = (df.dropna(subset=[COL_SALARY]).groupby(group_col, observed=True)[COL_SALARY]
           .agg(avg_salary="mean", median_salary="median", count="count")
           .reset_index().sort_values("avg_salary", ascending=False))
    return out.head(top_n) if top_n else out

def highest_paying_titles(df, top_n=10):
    return avg_salary_by(df, COL_TITLE, top_n)

def salary_by_experience(df):
    return (df.dropna(subset=[COL_SALARY,COL_EXPERIENCE])
            .groupby(COL_EXPERIENCE, observed=True)[COL_SALARY].mean()
            .reset_index().sort_values(COL_EXPERIENCE))
