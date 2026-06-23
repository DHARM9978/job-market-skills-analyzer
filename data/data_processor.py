"""
Maps raw Adzuna JSON (after pd.json_normalize) → app canonical schema.

ROOT CAUSE OF THE API CRASH (now fixed here):
─────────────────────────────────────────────
The original code did:
    salary_min = pd.to_numeric(raw.get("salary_min"), errors="coerce")
    salary_max = pd.to_numeric(raw.get("salary_max"), errors="coerce")
    out[COL_SALARY] = pd.concat([salary_min, salary_max], axis=1).mean(...)

When salary_min / salary_max columns are ABSENT from the Adzuna response
(common for Indian listings where salary_is_predicted = 0), raw.get()
returns None.  pd.to_numeric(None, errors='coerce') returns the SCALAR
np.float64(nan) — not a Series or DataFrame.  pd.concat() requires Series
or DataFrames, so it raises:
    TypeError: cannot concatenate object of type '<class 'numpy.float64'>'; 
               only Series and DataFrame objs are valid

FIX: _safe_salary_col() always returns a pd.Series of the correct length,
even when the column is missing entirely from the response.

LOCATION PARSING FIX:
─────────────────────
Adzuna India returns location.area = ["India"] (single element — no state/
city breakdown).  The old code assumed at least 2 elements.  _state_city()
now handles any list length gracefully.
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
    FIX for the pd.concat crash.

    Safely extracts a numeric salary column from the raw DataFrame.
    If the column is absent (raw_df.get() returns None, which
    pd.to_numeric() would silently convert to np.float64(nan) — a scalar
    that breaks pd.concat), this function returns a NaN Series of the
    correct length instead.

    Args:
        raw_df  : the json_normalized Adzuna response DataFrame
        col_name: "salary_min" or "salary_max"
    Returns:
        pd.Series of float, same length as raw_df, NaN where data is missing
    """
    if col_name in raw_df.columns:
        return pd.to_numeric(
            raw_df[col_name], errors="coerce"
        ).reset_index(drop=True)

    # Column entirely absent — return properly-shaped NaN Series
    logger.debug("Column '%s' absent from API response; using NaN Series", col_name)
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
    """
    FIX for location parsing.

    Adzuna India returns location.area = ["India"]  (single element).
    Old code assumed len >= 2 and crashed/returned wrong values.

    Handles:
        ["India"]                  → (None, "India")
        ["India", "Karnataka"]     → ("Karnataka", "Karnataka")
        ["India", "Karnataka", "Bangalore"] → ("Karnataka", "Bangalore")
    """
    if not isinstance(area, list) or len(area) == 0:
        return None, None
    if len(area) == 1:
        return None, area[0]          # only country — no city/state breakdown
    if len(area) == 2:
        return area[1], area[1]       # state only
    return area[1], area[-1]          # state + city (normal case)


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
    Map a raw (json_normalized) Adzuna results DataFrame onto the app's
    canonical column schema.  All fixes for the crash and the location
    parsing issue are applied here.
    """
    if raw.empty:
        logger.warning("standardize_adzuna_data called with empty DataFrame")
        return pd.DataFrame()

    logger.info("Standardizing %d rows from Adzuna API", len(raw))

    out = pd.DataFrame()
    out.index = range(len(raw))

    # ── Core text fields ───────────────────────────────────────────────────
    out[COL_TITLE]       = raw.get("title",
                           pd.Series(["Unspecified Role"] * len(raw))).fillna("Unspecified Role").values
    out[COL_COMPANY]     = raw.get("company.display_name",
                           pd.Series(["Unknown Company"] * len(raw))).fillna("Unknown Company").values
    out[COL_DESCRIPTION] = raw.get("description",
                           pd.Series([""] * len(raw))).fillna("").values
    out[COL_INDUSTRY]    = raw.get("category.label",
                           pd.Series(["Other"] * len(raw))).fillna("Other").values
    out[COL_DATE_POSTED] = pd.to_datetime(
        raw.get("created"), errors="coerce", utc=True
    )

    # ── Salary (FIX: use _safe_salary_col to avoid scalar/concat crash) ───
    sal_min = _safe_salary_col(raw, "salary_min")   # always a Series now
    sal_max = _safe_salary_col(raw, "salary_max")   # always a Series now

    # Both are guaranteed Series here — pd.concat is safe
    salary_df       = pd.concat([sal_min, sal_max], axis=1)
    out[COL_SALARY] = salary_df.mean(axis=1, skipna=True)

    logger.debug(
        "Salary coverage: %d/%d rows have a value",
        out[COL_SALARY].notna().sum(), len(out)
    )

    # ── Location (FIX: handle single-element area list) ───────────────────
    if "location.area" in raw.columns:
        pairs              = raw["location.area"].apply(_state_city)
        out[COL_STATE]     = [p[0] for p in pairs]
        cities_from_area   = [p[1] for p in pairs]
        fallback_display   = (
            raw["location.display_name"]
            if "location.display_name" in raw.columns
            else pd.Series(["Unknown"] * len(raw))
        )
        out[COL_LOCATION]  = [
            cities_from_area[i] or str(fallback_display.iloc[i])
            for i in range(len(cities_from_area))
        ]
    else:
        out[COL_LOCATION]  = (
            raw.get("location.display_name",
            pd.Series(["Unknown"] * len(raw))).fillna("Unknown").values
        )
        out[COL_STATE]     = None

    # ── Real lat/lon when Adzuna provides it ──────────────────────────────
    if "latitude"  in raw.columns:
        out[COL_LAT] = pd.to_numeric(raw["latitude"],  errors="coerce").values
    if "longitude" in raw.columns:
        out[COL_LON] = pd.to_numeric(raw["longitude"], errors="coerce").values

    # ── Job type ──────────────────────────────────────────────────────────
    out[COL_JOB_TYPE] = raw.apply(_job_type, axis=1).values

    # ── Experience (extracted from description text) ───────────────────────
    exp_series      = out[COL_DESCRIPTION].apply(_exp_from_text)
    fallback_exp    = int(exp_series.dropna().median()) if not exp_series.dropna().empty else 2
    out[COL_EXPERIENCE]         = exp_series.fillna(fallback_exp)
    out["Experience_Estimated"] = exp_series.isna()

    # ── Skills filled downstream by data/skill_extractor.py ───────────────
    out[COL_SKILLS] = ""

    logger.info(
        "Standardized: %d rows, salary coverage %.0f%%, location='%s' (sample)",
        len(out),
        out[COL_SALARY].notna().mean() * 100,
        out[COL_LOCATION].iloc[0] if len(out) else "—",
    )

    print("Salary count:", out[COL_SALARY].notna().sum())
    print("Salary median:", out[COL_SALARY].median())
    print("Salary sample:")
    print(out[COL_SALARY].head(20))


    return out
