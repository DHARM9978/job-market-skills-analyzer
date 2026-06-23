import pandas as pd
from utils.constants import COL_EXP_BRACKET, COL_SALARY, COL_TITLE, EXPERIENCE_BRACKETS

_ORDER = [label for _,_,label in EXPERIENCE_BRACKETS]

def salary_by_bracket(df):
    return (df.groupby(COL_EXP_BRACKET, observed=True)[COL_SALARY]
            .agg(avg_salary="mean", count="count")
            .reindex(_ORDER).dropna(how="all").reset_index())

def experience_salary_growth(df):
    brackets = salary_by_bracket(df).dropna(subset=["avg_salary"])
    if len(brackets) < 2: return {"entry_avg":0,"senior_avg":0,"growth_pct":0}
    entry, senior = brackets["avg_salary"].iloc[0], brackets["avg_salary"].iloc[-1]
    return {"entry_avg":entry,"senior_avg":senior,"growth_pct":(senior-entry)/entry*100 if entry else 0}
