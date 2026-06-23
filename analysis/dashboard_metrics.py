from collections import Counter
import pandas as pd
from utils.constants import COL_LOCATION, COL_COMPANY, COL_SKILLS_LIST, COL_SALARY, COL_TITLE, COL_INDUSTRY

def compute_dashboard_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total_jobs":0,"avg_salary":None,"top_location":"—","top_skill":"—","total_companies":0,"top_industry":"—"}
    all_skills = [s for row in df[COL_SKILLS_LIST] for s in row] if COL_SKILLS_LIST in df.columns else []
    top_skill = Counter(all_skills).most_common(1)[0][0] if all_skills else "—"
    sal = df[COL_SALARY].dropna()
    return {
        "total_jobs": len(df),
        "avg_salary": sal.mean() if not sal.empty else None,
        "top_location": df[COL_LOCATION].value_counts().index[0] if COL_LOCATION in df.columns else "—",
        "top_skill": top_skill,
        "total_companies": df[COL_COMPANY].nunique() if COL_COMPANY in df.columns else 0,
        "top_industry": df[COL_INDUSTRY].value_counts().index[0] if COL_INDUSTRY in df.columns else "—",
    }
