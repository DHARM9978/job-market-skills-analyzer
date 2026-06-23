from collections import Counter
from itertools import combinations
import pandas as pd
from utils.constants import COL_SKILLS_LIST, COL_TITLE, COL_INDUSTRY, COL_SALARY, COL_EXPERIENCE

def most_versatile_skills(df, top_n=10):
    skill_to_titles = {}
    for title, skills in zip(df[COL_TITLE], df[COL_SKILLS_LIST]):
        for s in skills: skill_to_titles.setdefault(s,set()).add(title)
    rows = [{"Skill":s,"Roles_Covered":len(t)} for s,t in skill_to_titles.items()]
    return pd.DataFrame(rows).sort_values("Roles_Covered",ascending=False).head(top_n)

def market_concentration(df):
    share = (df[COL_INDUSTRY].value_counts(normalize=True)*100).round(1)
    if share.empty: return {"top3_industry_share":0,"leading_industry":"—","leading_industry_share":0}
    return {"top3_industry_share":share.head(3).sum(),"leading_industry":share.index[0],"leading_industry_share":share.iloc[0]}

def steepest_experience_curves(df, top_n=5):
    if COL_EXPERIENCE not in df.columns or COL_SALARY not in df.columns: return pd.DataFrame()
    rows=[]
    for title, grp in df.groupby(COL_TITLE, observed=True):
        grp = grp.dropna(subset=[COL_EXPERIENCE,COL_SALARY])
        if grp[COL_EXPERIENCE].nunique()<2: continue
        low  = grp[grp[COL_EXPERIENCE]<=grp[COL_EXPERIENCE].quantile(0.33)][COL_SALARY].mean()
        high = grp[grp[COL_EXPERIENCE]>=grp[COL_EXPERIENCE].quantile(0.66)][COL_SALARY].mean()
        if pd.isna(low) or pd.isna(high) or low==0: continue
        rows.append({"Job_Title":title,"Low_Exp_Avg":low,"High_Exp_Avg":high,"Growth_%":(high-low)/low*100})
    return pd.DataFrame(rows).sort_values("Growth_%",ascending=False).head(top_n)

def emerging_skill_combo(df, top_n=8):
    counter=Counter()
    for skills in df[COL_SKILLS_LIST]:
        for a,b in combinations(sorted(set(skills)),2): counter[(a,b)]+=1
    return pd.DataFrame([{"Pair":f"{a} + {b}","Count":c} for (a,b),c in counter.most_common(top_n)])
