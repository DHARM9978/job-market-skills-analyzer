
from collections import Counter
from itertools import combinations

import pandas as pd

from utils.constants import COL_SKILLS_LIST, COL_TITLE, COL_SALARY


def _get_skills(row):
    """Return valid skill names from a row."""
    if not isinstance(row, (list, tuple, set)):
        return []

    return [
        skill.strip()
        for skill in row
        if isinstance(skill, str) and skill.strip()
    ]


def top_skills(df, top_n=15):
    """Return the most frequent skills and their share of listings."""
    columns = {
        "Skill": pd.Series(dtype="object"),
        "Count": pd.Series(dtype="int64"),
        "Share": pd.Series(dtype="float64"),
    }

    if df is None or df.empty or COL_SKILLS_LIST not in df.columns:
        return pd.DataFrame(columns)

    counter = Counter()

    for row in df[COL_SKILLS_LIST]:
        counter.update(_get_skills(row))

    out = pd.DataFrame(
        counter.most_common(top_n),
        columns=["Skill", "Count"],
    )

    # Counter may be empty after filtering, so set dtypes explicitly.
    if out.empty:
        return pd.DataFrame(columns)

    out["Count"] = pd.to_numeric(
        out["Count"], errors="coerce"
    ).fillna(0).astype("int64")

    out["Share"] = (
        out["Count"].astype("float64") / len(df) * 100
    ).round(1)

    return out


def skills_for_title(df, title, top_n=8):
    """Return the most frequent skills for a selected job title."""
    if (
        df is None
        or df.empty
        or COL_TITLE not in df.columns
        or COL_SKILLS_LIST not in df.columns
    ):
        return pd.DataFrame({
            "Skill": pd.Series(dtype="object"),
            "Count": pd.Series(dtype="int64"),
        })

    subset = df[df[COL_TITLE] == title]
    counter = Counter()

    for row in subset[COL_SKILLS_LIST]:
        counter.update(_get_skills(row))

    return pd.DataFrame(
        counter.most_common(top_n),
        columns=["Skill", "Count"],
    )


def skill_salary_premium(df, top_n=12):
    """Compare average salary for each skill with the overall average."""
    if (
        df is None
        or df.empty
        or COL_SALARY not in df.columns
        or COL_SKILLS_LIST not in df.columns
    ):
        return pd.DataFrame()

    salaries = pd.to_numeric(df[COL_SALARY], errors="coerce")
    overall = salaries.mean()

    if pd.isna(overall):
        return pd.DataFrame()

    counter = Counter()

    for row in df[COL_SKILLS_LIST]:
        counter.update(_get_skills(row))

    rows = []

    for skill, count in counter.most_common(top_n * 2):
        mask = df[COL_SKILLS_LIST].apply(
            lambda row: skill in _get_skills(row)
        )

        average = salaries.loc[mask].mean()

        if pd.notna(average):
            premium = (
                round((average - overall) / overall * 100, 1)
                if overall != 0
                else 0
            )

            rows.append({
                "Skill": skill,
                "Listings": count,
                "Avg_Salary": average,
                "Premium_%": premium,
            })

    if not rows:
        return pd.DataFrame()

    return (
        pd.DataFrame(rows)
        .sort_values("Avg_Salary", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def skill_cooccurrence_matrix(df, top_n=10):
    """Build a matrix showing which skills occur together."""
    if df is None or df.empty or COL_SKILLS_LIST not in df.columns:
        return [], []

    counter = Counter()

    for row in df[COL_SKILLS_LIST]:
        counter.update(set(_get_skills(row)))

    top = [skill for skill, _ in counter.most_common(top_n)]
    positions = {skill: index for index, skill in enumerate(top)}

    matrix = [[0] * len(top) for _ in top]

    for row in df[COL_SKILLS_LIST]:
        present = set(_get_skills(row)) & set(top)

        for skill in present:
            matrix[positions[skill]][positions[skill]] = counter[skill]

        for first, second in combinations(present, 2):
            i = positions[first]
            j = positions[second]
            matrix[i][j] += 1
            matrix[j][i] += 1

    return top, matrix


def skill_gap(user_skills, target_skills):
    """Compare a user's skills with the skills required for a target role."""
    user_set = {
        skill.strip().lower()
        for skill in user_skills
        if isinstance(skill, str) and skill.strip()
    }

    target = {
        skill.strip().lower(): skill
        for skill in target_skills
        if isinstance(skill, str) and skill.strip()
    }

    have = [
        original for normalized, original in target.items()
        if normalized in user_set
    ]

    missing = [
        original for normalized, original in target.items()
        if normalized not in user_set
    ]

    return {
        "have": have,
        "missing": missing,
        "match_pct": len(have) / len(target) * 100 if target else 0,
    }
