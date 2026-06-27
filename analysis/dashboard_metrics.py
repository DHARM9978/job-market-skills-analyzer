from collections import Counter
import pandas as pd

from utils.constants import (
COL_LOCATION,
COL_COMPANY,
COL_SKILLS_LIST,
COL_SALARY,
COL_TITLE,
COL_INDUSTRY,
)

def compute_dashboard_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_jobs": 0,
            "avg_salary": None,
            "top_location": "—",
            "top_skill": "—",
            "total_companies": 0,
            "top_industry": "—",
        }

    # Top Skill
    all_skills = []

    if COL_SKILLS_LIST in df.columns:
        for row in df[COL_SKILLS_LIST]:
            if isinstance(row, list):
                all_skills.extend(row)

    top_skill = (
        Counter(all_skills).most_common(1)[0][0]
        if all_skills
        else "—"
    )

    # Salary
    sal = df[COL_SALARY].dropna()

    avg_salary = (
        sal.mean()
        if not sal.empty
        else None
    )

    # Top Location (Ignore Unknown / India)
    top_location = "—"

    if COL_LOCATION in df.columns:

        valid_locations = df[COL_LOCATION].dropna()

        valid_locations = valid_locations[
            ~valid_locations.astype(str)
            .str.strip()
            .str.lower()
            .isin(["unknown", "india", ""])
        ]

        if not valid_locations.empty:
            top_location = valid_locations.value_counts().index[0]

    # Top Industry
    top_industry = "—"

    if COL_INDUSTRY in df.columns:

        valid_industries = df[
            df[COL_INDUSTRY].notna()
        ][COL_INDUSTRY]

        if not valid_industries.empty:
            top_industry = valid_industries.value_counts().index[0]

    return {
        "total_jobs": len(df),
        "avg_salary": avg_salary,
        "top_location": top_location,
        "top_skill": top_skill,
        "total_companies": (
            df[COL_COMPANY].nunique()
            if COL_COMPANY in df.columns
            else 0
        ),
        "top_industry": top_industry,
    }
