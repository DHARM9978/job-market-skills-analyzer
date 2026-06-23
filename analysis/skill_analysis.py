from collections import Counter
from itertools import combinations
import pandas as pd
from utils.constants import COL_SKILLS_LIST, COL_TITLE, COL_SALARY

def top_skills(df, top_n=15):
    counter = Counter(s for row in df[COL_SKILLS_LIST] for s in row)
    out = pd.DataFrame(counter.most_common(top_n), columns=["Skill","Count"])
    out["Share"] = (out["Count"]/len(df)*100).round(1)
    return out

def skills_for_title(df, title, top_n=8):
    sub = df[df[COL_TITLE]==title]
    counter = Counter(s for row in sub[COL_SKILLS_LIST] for s in row)
    return pd.DataFrame(counter.most_common(top_n), columns=["Skill","Count"])

def skill_salary_premium(df, top_n=12):
    if COL_SALARY not in df.columns: return pd.DataFrame()
    overall = df[COL_SALARY].mean()
    counter = Counter(s for row in df[COL_SKILLS_LIST] for s in row)
    rows=[]
    for skill,cnt in counter.most_common(top_n*2):
        mask = df[COL_SKILLS_LIST].apply(lambda l: skill in l)
        avg = df.loc[mask,COL_SALARY].mean()
        if pd.notna(avg):
            rows.append({"Skill":skill,"Listings":cnt,"Avg_Salary":avg,
                         "Premium_%":round((avg-overall)/overall*100,1) if overall else 0})
    return pd.DataFrame(rows).sort_values("Avg_Salary",ascending=False).head(top_n)

def skill_cooccurrence_matrix(df, top_n=10):
    counter = Counter(s for row in df[COL_SKILLS_LIST] for s in row)
    top = [s for s,_ in counter.most_common(top_n)]
    matrix = [[0]*len(top) for _ in top]
    for row in df[COL_SKILLS_LIST]:
        present = [s for s in row if s in top]
        for a,b in combinations(present,2):
            i,j = top.index(a),top.index(b)
            matrix[i][j]+=1; matrix[j][i]+=1
        for s in present:
            matrix[top.index(s)][top.index(s)] = counter[s]
    return top, matrix

def skill_gap(user_skills, target_skills):
    user_set = {s.strip().lower() for s in user_skills}
    target = {s.strip().lower():s for s in target_skills}
    have    = [orig for low,orig in target.items() if low in user_set]
    missing = [orig for low,orig in target.items() if low not in user_set]
    return {"have":have,"missing":missing,"match_pct":(len(have)/len(target)*100) if target else 0}
