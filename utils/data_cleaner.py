import pandas as pd
from utils.constants import (
    COL_TITLE, COL_COMPANY, COL_LOCATION, COL_STATE, COL_SALARY, COL_SKILLS,
    COL_EXPERIENCE, COL_INDUSTRY, COL_SKILLS_LIST, COL_EXP_BRACKET,
    COL_DATE_POSTED, EXPERIENCE_BRACKETS,
)

def _bracket(years):
    try:
        y = float(years)
        if pd.isna(y): return "Unknown"
    except: return "Unknown"
    for lo, hi, label in EXPERIENCE_BRACKETS:
        if lo <= y <= hi: return label
    return "Unknown"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --------------------------------------------------
    # Clean text columns
    # --------------------------------------------------
    for col in [
        COL_TITLE,
        COL_COMPANY,
        COL_LOCATION,
        COL_STATE,
        COL_INDUSTRY,
    ]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"nan": None, "None": None})
            )

    # --------------------------------------------------
    # Convert numeric/date columns
    # --------------------------------------------------
    if COL_SALARY in df.columns:
        df[COL_SALARY] = pd.to_numeric(
            df[COL_SALARY],
            errors="coerce"
        )

    if COL_EXPERIENCE in df.columns:
        df[COL_EXPERIENCE] = pd.to_numeric(
            df[COL_EXPERIENCE],
            errors="coerce"
        )

    if COL_DATE_POSTED in df.columns:
        df[COL_DATE_POSTED] = pd.to_datetime(
            df[COL_DATE_POSTED],
            errors="coerce",
            utc=True
        )

    # --------------------------------------------------
    # Drop rows missing required fields
    # --------------------------------------------------
    required_cols = [
        c for c in [COL_TITLE, COL_LOCATION]
        if c in df.columns
    ]

    if required_cols:
        df = df.dropna(subset=required_cols)

        for col in required_cols:
            df = df[df[col].astype(str).str.strip() != ""]

    # --------------------------------------------------
    # DEBUG (temporary)
    # --------------------------------------------------
    print("Columns:", df.columns.tolist())

    if COL_SKILLS_LIST in df.columns and len(df) > 0:
        print(
            "Skills_List sample type:",
            type(df[COL_SKILLS_LIST].iloc[0])
        )

    # --------------------------------------------------
    # Remove duplicates WITHOUT hashing list columns
    # --------------------------------------------------
    if COL_SKILLS_LIST in df.columns:

        dedupe_cols = [
            c for c in df.columns
            if c != COL_SKILLS_LIST
        ]

        df = (
            df.drop_duplicates(subset=dedupe_cols)
            .reset_index(drop=True)
        )

    else:
        df = (
            df.drop_duplicates()
            .reset_index(drop=True)
        )

    # --------------------------------------------------
    # Build Skills_List safely
    # --------------------------------------------------
    if COL_SKILLS in df.columns:

        df[COL_SKILLS_LIST] = (
            df[COL_SKILLS]
            .fillna("")
            .astype(str)
            .apply(
                lambda s: [
                    x.strip()
                    for x in s.split(",")
                    if x.strip()
                ]
            )
        )

    else:

        df[COL_SKILLS_LIST] = [
            [] for _ in range(len(df))
        ]

    # --------------------------------------------------
    # Experience brackets
    # --------------------------------------------------
    if COL_EXPERIENCE in df.columns:

        df[COL_EXP_BRACKET] = (
            df[COL_EXPERIENCE]
            .apply(_bracket)
        )

    else:

        df[COL_EXP_BRACKET] = "Unknown"

    return df