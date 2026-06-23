import pandas as pd
from utils.constants import COL_TITLE, COL_SKILLS_LIST, COL_SALARY, COL_EXPERIENCE
from analysis.skill_analysis import skills_for_title, skill_gap

def recommend_titles(df, user_skills, top_n=5):
    user_set = {s.strip().lower() for s in user_skills if s.strip()}
    if not user_set: return pd.DataFrame(columns=["Job_Title","Match_%","Avg_Salary","Listings"])
    rows=[]
    for title, grp in df.groupby(COL_TITLE, observed=True):
        req = {s.lower() for row in grp[COL_SKILLS_LIST] for s in row}
        if not req: continue
        pct = len(user_set&req)/len(req)*100
        rows.append({"Job_Title":title,"Match_%":round(pct,1),
                     "Avg_Salary":grp[COL_SALARY].mean() if COL_SALARY in grp.columns else None,
                     "Listings":len(grp)})
    return pd.DataFrame(rows).sort_values(["Match_%","Avg_Salary"],ascending=False).head(top_n)

def estimate_salary_range(df, title, experience):
    sub = df[df[COL_TITLE]==title].dropna(subset=[COL_SALARY])
    if sub.empty: return {"low":None,"mid":None,"high":None}
    if COL_EXPERIENCE in sub.columns:
        close = sub[(sub[COL_EXPERIENCE]-experience).abs()<=1]
        sub = close if not close.empty else sub
    return {"low":sub[COL_SALARY].quantile(0.25),"mid":sub[COL_SALARY].median(),"high":sub[COL_SALARY].quantile(0.75)}

def full_recommendation(df, user_skills, experience):
    matches = recommend_titles(df, user_skills, top_n=5)
    if matches.empty: return {"title_matches":matches,"best_title":None}
    best = matches.iloc[0]["Job_Title"]
    target_df = skills_for_title(df, best, top_n=15)
    gap = skill_gap(user_skills, target_df["Skill"].tolist())
    return {
        "title_matches": matches,
        "best_title": best,
        "salary_estimate": estimate_salary_range(df, best, experience),
        "skill_gap": gap,
    }
