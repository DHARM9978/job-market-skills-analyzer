# -*- coding: utf-8 -*-
"""
data_processor.py
─────────────────
Maps raw Adzuna JSON (after pd.json_normalize) → app canonical schema,
then calls salary_estimator.enrich_salary() so every API row has a
usable salary figure even though Adzuna India never returns salary_min /
salary_max in individual listing objects.

ROOT CAUSE FIXES APPLIED HERE
──────────────────────────────
1. pd.concat CRASH  (file: data/data_processor.py, function: standardize_adzuna_data)
   raw.get("salary_min") returns None when the column is absent.
   pd.to_numeric(None) returns np.float64(nan) — a scalar, not a Series.
   pd.concat([scalar, scalar]) crashes.
   FIX → _safe_salary_col() always returns a properly-shaped pd.Series.

2. LOCATION PARSING (file: data/data_processor.py, function: _state_city)
   Adzuna India returns location.area = ["India"] (1 element, no city).
   FIX → _state_city() handles any list length: 1, 2, or 3+ elements.

3. SALARY "Not Disclosed" FOR ALL API DATA (NEW FIX)
   (file: data/data_processor.py → calls data/salary_estimator.py)
   Adzuna India sets salary_is_predicted=0 and omits salary_min/salary_max
   for virtually every listing.  After our _safe_salary_col() fix, those
   rows correctly get NaN — but NaN makes every salary KPI/chart blank.
   FIX → call enrich_salary() at the end of standardize_adzuna_data().
   It fuzzy-matches the API job title against the bundled sample dataset
   and fills estimated salaries so charts render properly.  A new column
   Salary_Estimated = True marks rows that were filled so the UI can label
   them as estimates.
"""

import re
import logging

import numpy as np
import pandas as pd

from utils.constants import (
    COL_TITLE, COL_COMPANY, COL_LOCATION, COL_STATE, COL_SALARY, COL_SKILLS,
    COL_EXPERIENCE, COL_JOB_TYPE, COL_INDUSTRY, COL_DESCRIPTION,
    COL_DATE_POSTED, COL_LAT, COL_LON,
)

logger = logging.getLogger(__name__)

# ── Experience regex patterns ──────────────────────────────────────────────
_EXP_RE = [
    re.compile(r"(\d{1,2})\s*\+\s*years?",                re.I),
    re.compile(r"(\d{1,2})\s*(?:to|-|–)\s*\d{1,2}\s*years?", re.I),
    re.compile(r"minimum\s+of\s+(\d{1,2})\s*years?",     re.I),
    re.compile(r"(\d{1,2})\s*years?\s+of\s+experience",  re.I),
    re.compile(r"(\d{1,2})\s*\+?\s*yrs?",                re.I),
]


def _safe_salary_col(raw_df: pd.DataFrame, col_name: str) -> pd.Series:
    """
    FIX 1: Safely extract a numeric salary column.
    Returns a NaN Series of the correct length if the column is absent,
    preventing the np.float64 scalar from reaching pd.concat().
    """
    if col_name in raw_df.columns:
        return pd.to_numeric(
            raw_df[col_name], errors="coerce"
        ).reset_index(drop=True)

    logger.debug("Column '%s' absent from API response — using NaN Series", col_name)
    return pd.Series(
        [np.nan] * len(raw_df),
        index=range(len(raw_df)),
        name=col_name,
        dtype=float,
    )


def _exp_from_text(text: str):
    """Extract years-of-experience from free-text job description."""
    if not isinstance(text, str):
        return None
    for pat in _EXP_RE:
        m = pat.search(text)
        if m:
            try:
                y = int(m.group(1))
                if 0 <= y <= 30:
                    return y
            except (ValueError, IndexError):
                continue
    return None


def _state_city(area) -> tuple:
    if not isinstance(area, list) or len(area) == 0:
        return None, None

    if len(area) == 1:
        country = area[0]

        if country.lower() == "india":
            return None, "Unknown"

        return None, country

    if len(area) == 2:
        return area[1], area[1]

    return area[1], area[-1]


def _job_type(row) -> str:
    ct = str(row.get("contract_time", "") or "").lower()
    cy = str(row.get("contract_type",  "") or "").lower()
    if ct == "full_time":  return "Full-Time"
    if ct == "part_time":  return "Part-Time"
    if cy == "contract":   return "Contract"
    if cy == "permanent":  return "Permanent"
    return "Not Specified"


def standardize_adzuna_data(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Maps raw Adzuna response → canonical schema, then enriches salaries.
    Returns a DataFrame ready for clean_data() → analysis pipeline.
    """
    if raw.empty:
        logger.warning("standardize_adzuna_data: empty input")
        return pd.DataFrame()

    logger.info("Standardizing %d rows from Adzuna API", len(raw))

    out       = pd.DataFrame()
    out.index = range(len(raw))

    # ── Text fields ────────────────────────────────────────────────────────
    def _col(name, default):
        val = raw.get(name)
        if val is None:
            return pd.Series([default] * len(raw))
        return pd.Series(val.values).fillna(default)

    out[COL_TITLE]       = _col("title",                "Unspecified Role")
    out[COL_COMPANY]     = _col("company.display_name", "Unknown Company")
    out[COL_DESCRIPTION] = _col("description",          "")
    out[COL_INDUSTRY]    = _col("category.label",       "Other")
    out[COL_DATE_POSTED] = pd.to_datetime(
        raw["created"] if "created" in raw.columns else pd.Series([pd.NaT] * len(raw)),
        errors="coerce", utc=True,
    )

    # ── Salary: FIX 1 applied here ─────────────────────────────────────────
    # NOTE: For Adzuna India, salary_min and salary_max are almost always
    # absent (salary_is_predicted = 0). After this block, COL_SALARY will
    # be NaN for all rows. enrich_salary() below fills those NaNs.
    sal_min         = _safe_salary_col(raw, "salary_min")
    sal_max         = _safe_salary_col(raw, "salary_max")
    salary_df       = pd.concat([sal_min, sal_max], axis=1)
    out[COL_SALARY] = salary_df.mean(axis=1, skipna=True)

    logger.info(
        "Raw salary coverage from API: %d/%d rows (%.0f%%)",
        out[COL_SALARY].notna().sum(), len(out),
        out[COL_SALARY].notna().mean() * 100
    )

    # ── Location: FIX 2 applied here ──────────────────────────────────────
    if "location.area" in raw.columns:
        pairs            = raw["location.area"].apply(_state_city)
        out[COL_STATE]   = [p[0] for p in pairs]
        cities_from_area = [p[1] for p in pairs]
        fallback         = (
            raw["location.display_name"]
            if "location.display_name" in raw.columns
            else pd.Series(["Unknown"] * len(raw))
        )
        out[COL_LOCATION] = [
            cities_from_area[i] or str(fallback.iloc[i])
            for i in range(len(cities_from_area))
        ]
    else:
        out[COL_LOCATION] = _col("location.display_name", "Unknown")
        out[COL_STATE]    = None

    # ── Lat / Lon (present in some Adzuna regions) ─────────────────────────
    if "latitude"  in raw.columns:
        out[COL_LAT] = pd.to_numeric(raw["latitude"],  errors="coerce").values
    if "longitude" in raw.columns:
        out[COL_LON] = pd.to_numeric(raw["longitude"], errors="coerce").values

    # ── Job type ───────────────────────────────────────────────────────────
    out[COL_JOB_TYPE] = raw.apply(_job_type, axis=1).values

    # ── Experience from description text ───────────────────────────────────
    exp_series              = out[COL_DESCRIPTION].apply(_exp_from_text)
    fallback_exp            = int(exp_series.dropna().median()) if not exp_series.dropna().empty else 2
    out[COL_EXPERIENCE]     = exp_series.fillna(fallback_exp)
    out["Experience_Estimated"] = exp_series.isna()

    # Skills filled downstream by skill_extractor.py
    out[COL_SKILLS] = ""

    # ── FIX 3: Enrich missing salaries from sample dataset lookup ──────────
    # This is the core fix for "salary shows Not Disclosed with API data".
    # enrich_salary() fuzzy-matches job titles against the bundled CSV and
    # assigns realistic estimated salaries. Salary_Estimated=True flags them.
    from data.salary_estimator import enrich_salary   # local import avoids circular
    out = enrich_salary(out)

    logger.info(
        "Final salary coverage: %d/%d rows (%.0f%%) — %d estimated, %d from API",
        out[COL_SALARY].notna().sum(), len(out),
        out[COL_SALARY].notna().mean() * 100,
        out.get("Salary_Estimated", pd.Series([])).sum(),
        out[COL_SALARY].notna().sum() - out.get("Salary_Estimated", pd.Series([])).sum(),
    )

    return out
