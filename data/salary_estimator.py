# -*- coding: utf-8 -*-
"""
salary_estimator.py
───────────────────
Adzuna India API listings almost never include salary_min / salary_max
(salary_is_predicted = 0 on virtually every Indian result). This module
fills the gap so that salary charts and KPIs still work when the app is
running on live API data.

HOW IT WORKS
────────────
1. Build a lookup table from the bundled jobs_dataset.csv (which has real
   Indian salary data by job title, location, experience bracket).
2. When the API pipeline calls enrich_salary(), each API row gets an
   estimated salary by matching its Job_Title (fuzzy) + Experience.
3. A new column  Salary_Estimated = True  is added so the UI can be
   transparent (charts label it as "Estimated" in the subtitle).
4. Rows that already have a real salary (salary_min/salary_max present)
   are left untouched.

FILE TO CHANGE:  data/data_processor.py  (calls enrich_salary at the end)
"""

import logging
import difflib

import numpy as np
import pandas as pd

from utils.constants import DEFAULT_DATA_PATH, COL_SALARY, COL_TITLE, COL_EXPERIENCE

logger = logging.getLogger(__name__)

# ── Build the lookup table once at module load (cheap — 1000 row CSV) ──────
_lookup: pd.DataFrame | None = None


def _get_lookup() -> pd.DataFrame:
    """
    Returns a DataFrame indexed by (Job_Title, experience_bracket) with
    columns [median_salary, mean_salary, p25, p75].
    Falls back to a title-only lookup if experience doesn't help.
    """
    global _lookup
    if _lookup is not None:
        return _lookup

    try:
        df = pd.read_csv(DEFAULT_DATA_PATH)
        df[COL_SALARY]     = pd.to_numeric(df[COL_SALARY],     errors="coerce")
        df[COL_EXPERIENCE] = pd.to_numeric(df[COL_EXPERIENCE], errors="coerce")
        df = df.dropna(subset=[COL_SALARY])

        # Title-level aggregation (used as primary key)
        title_agg = (
            df.groupby(COL_TITLE)[COL_SALARY]
            .agg(median="median", mean="mean", p25=lambda x: x.quantile(0.25),
                 p75=lambda x: x.quantile(0.75))
            .reset_index()
        )
        _lookup = title_agg
        logger.info(
            "Salary lookup table built: %d unique job titles from sample dataset",
            len(title_agg)
        )
    except Exception as exc:
        logger.warning("Could not build salary lookup table: %s", exc)
        _lookup = pd.DataFrame()

    return _lookup


def _known_titles() -> list:
    lkp = _get_lookup()
    return lkp[COL_TITLE].tolist() if not lkp.empty else []


def _fuzzy_match(title: str, known: list) -> str | None:
    """
    Case-insensitive fuzzy match of an API job title against the known
    lookup keys.  Returns the best match if similarity > 0.45, else None.
    """
    if not known or not title:
        return None
    t = title.lower().strip()
    candidates = {k.lower(): k for k in known}

    # Direct substring match first (fast path)
    for lower, original in candidates.items():
        if lower in t or t in lower:
            return original

    # Fallback: difflib sequence match
    matches = difflib.get_close_matches(t, candidates.keys(), n=1, cutoff=0.45)
    return candidates[matches[0]] if matches else None


def enrich_salary(df: pd.DataFrame) -> pd.DataFrame:
    """
    For every row where Salary is NaN (typical for Adzuna India listings),
    estimate salary from the lookup table using Job_Title matching.

    Called at the END of standardize_adzuna_data() in data_processor.py.
    Safe to call on sample/upload data too — rows with existing salary
    values are never overwritten.

    Returns the same DataFrame with Salary filled and Salary_Estimated flag.
    """
    df = df.copy()

    if COL_SALARY not in df.columns:
        df[COL_SALARY] = np.nan
    if "Salary_Estimated" not in df.columns:
        df["Salary_Estimated"] = False

    missing_mask = df[COL_SALARY].isna()
    if not missing_mask.any():
        logger.debug("enrich_salary: no missing salaries — nothing to do")
        return df

    lkp    = _get_lookup()
    known  = _known_titles()
    global_median = lkp["median"].mean() if not lkp.empty else 2_000_000

    logger.info(
        "Estimating salary for %d/%d rows with no API salary data",
        missing_mask.sum(), len(df)
    )

    def _estimate(row):
        if pd.notna(row[COL_SALARY]):
            return row[COL_SALARY], False        # already has a salary

        matched = _fuzzy_match(str(row.get(COL_TITLE, "")), known)
        if matched:
            row_lkp = lkp[lkp[COL_TITLE] == matched].iloc[0]
            base    = row_lkp["median"]

            # ±10% jitter based on experience so distribution looks realistic
            exp    = row.get(COL_EXPERIENCE, 2)
            factor = 1.0
            try:
                exp = float(exp)
                if   exp <= 1:  factor = 0.92
                elif exp <= 3:  factor = 0.98
                elif exp <= 5:  factor = 1.04
                elif exp <= 7:  factor = 1.10
                else:           factor = 1.17
            except (TypeError, ValueError):
                pass

            return round(base * factor, 0), True
        else:
            return round(global_median, 0), True

    results = df.apply(_estimate, axis=1, result_type="expand")
    results.columns = [COL_SALARY, "Salary_Estimated"]

    # Only overwrite where salary was missing
    df.loc[missing_mask, COL_SALARY]          = results.loc[missing_mask, COL_SALARY]
    df.loc[missing_mask, "Salary_Estimated"]  = results.loc[missing_mask, "Salary_Estimated"]

    estimated_count = df["Salary_Estimated"].sum()
    logger.info(
        "Salary estimation complete: %d estimated, %d original API values",
        estimated_count, len(df) - estimated_count
    )
    return df
