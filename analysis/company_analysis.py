import pandas as pd
from utils.constants import COL_COMPANY, COL_SALARY, COL_INDUSTRY, COL_TITLE

def top_hiring_companies(df, top_n=10):
    return (df.groupby(COL_COMPANY, observed=True)
            .agg(Listings=(COL_COMPANY,"count"), Avg_Salary=(COL_SALARY,"mean"))
            .reset_index().sort_values("Listings",ascending=False).head(top_n))

def highest_paying_companies(df, top_n=10):
    return (df.dropna(subset=[COL_SALARY]).groupby(COL_COMPANY, observed=True)[COL_SALARY]
            .mean().reset_index().sort_values(COL_SALARY,ascending=False).head(top_n))

def company_profile(df, company):
    sub = df[df[COL_COMPANY]==company]
    if sub.empty: return {}
    top_roles = sub[COL_TITLE].value_counts().head(5).rename_axis("Job_Title").reset_index(name="Listings")
    return {
        "listings": len(sub),
        "avg_salary": sub[COL_SALARY].mean() if COL_SALARY in sub.columns else None,
        "top_industry": sub[COL_INDUSTRY].value_counts().index[0] if COL_INDUSTRY in sub.columns else "—",
        "top_roles": top_roles,
    }
