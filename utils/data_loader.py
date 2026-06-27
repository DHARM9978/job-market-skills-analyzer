# -*- coding: utf-8 -*-
"""
Data loading orchestration — single entry point called by every page.

Priority order:
  1. User-uploaded file  (session key DATA_SOURCE_UPLOAD)
  2. Adzuna live API     (credentials in config/api_config.py)
  3. Bundled sample CSV  (always available — never crashes the app)

SALARY NOTE:
  Adzuna India does not return salary_min/salary_max for individual listings.
  The data_processor.py calls salary_estimator.enrich_salary() to fill those
  NaNs from the bundled sample dataset, so salary KPIs/charts work with API data.
"""

import io
import logging

import pandas as pd
import streamlit as st

from config import api_config
from config.api_config import CACHE_TTL_SECONDS
from data.api_fetcher import fetch_jobs, AdzunaFetchError
from data.data_processor import standardize_adzuna_data
from data.skill_extractor import enrich_with_skills
from utils.data_cleaner import clean_data
from utils.column_detector import detect_columns, apply_mapping
from utils.constants import (
    DEFAULT_DATA_PATH, SESSION_DATA_KEY, SESSION_DATA_SOURCE_KEY,
    SESSION_API_ERROR_KEY, DATA_SOURCE_API, DATA_SOURCE_UPLOAD, DATA_SOURCE_SAMPLE,
)

logger = logging.getLogger(__name__)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def _fetch_and_build_api_df() -> tuple:
    """
    Fetch Adzuna → standardize (includes salary enrichment) → extract skills → clean.
    Returns (df, error_message | None).  Cached for CACHE_TTL_SECONDS.
    """
    try:
        logger.info("Starting Adzuna API fetch …")
        raw = fetch_jobs()

        if raw.empty:
            return pd.DataFrame(), "Adzuna returned 0 results."

        # standardize_adzuna_data now calls enrich_salary() internally so
        # salary is populated even for Indian listings without salary_min/max
        std      = standardize_adzuna_data(raw)
        enriched = enrich_with_skills(std, text_col="Description")
        cleaned  = clean_data(enriched)

        logger.info(
            "API pipeline complete: %d rows, salary coverage %.0f%%",
            len(cleaned),
            cleaned["Salary"].notna().mean() * 100 if "Salary" in cleaned.columns else 0,
        )
        return cleaned, None

    except AdzunaFetchError as exc:
        logger.error("AdzunaFetchError: %s", exc)
        return pd.DataFrame(), str(exc)

    except Exception as exc:
        logger.exception("Unexpected error in API pipeline")
        return pd.DataFrame(), f"Unexpected error while processing API data: {exc}"


@st.cache_data(show_spinner=False)
def _load_sample() -> pd.DataFrame:
    return clean_data(pd.read_csv(DEFAULT_DATA_PATH))


@st.cache_data(show_spinner=False)
def _load_uploaded(file_bytes: bytes, extension: str) -> pd.DataFrame:
    if extension == "xlsx":
        raw = pd.read_excel(io.BytesIO(file_bytes))
    else:
        raw = pd.read_csv(io.BytesIO(file_bytes))
    return clean_data(apply_mapping(raw, detect_columns(raw)))


def get_active_dataframe() -> pd.DataFrame:
    """Returns the current active dataset (upload > API > sample)."""

    # 1. Uploaded file
    if st.session_state.get(SESSION_DATA_SOURCE_KEY) == DATA_SOURCE_UPLOAD:
        df = st.session_state.get(SESSION_DATA_KEY)
        if df is not None and not df.empty:
            return df

    # 2. Live API
    if api_config.is_configured():
        df, err = _fetch_and_build_api_df()
        if not df.empty:
            st.session_state[SESSION_DATA_KEY]        = df
            st.session_state[SESSION_DATA_SOURCE_KEY] = DATA_SOURCE_API
            st.session_state[SESSION_API_ERROR_KEY]   = None
            return df
        st.session_state[SESSION_API_ERROR_KEY] = err
        logger.warning("API failed (%s) — falling back to sample data", err)
    else:
        st.session_state[SESSION_API_ERROR_KEY] = (
            "Add APP_ID + APP_KEY in config/api_config.py to use live data"
        )

    # 3. Bundled sample CSV
    df = _load_sample()
    st.session_state[SESSION_DATA_KEY] = df
    if st.session_state.get(SESSION_DATA_SOURCE_KEY) != DATA_SOURCE_UPLOAD:
        st.session_state[SESSION_DATA_SOURCE_KEY] = DATA_SOURCE_SAMPLE
    return df


def apply_uploaded_file(file_bytes: bytes, filename: str, extension: str) -> tuple:
    from utils.validators import validate_dataframe
    df         = _load_uploaded(file_bytes, extension)
    ok, errors = validate_dataframe(df)
    if ok:
        st.session_state[SESSION_DATA_KEY]        = df
        st.session_state[SESSION_DATA_SOURCE_KEY] = DATA_SOURCE_UPLOAD
        st.session_state["uploaded_filename"]      = filename
    return df, errors


def reset_to_default():
    st.session_state[SESSION_DATA_KEY]        = None
    st.session_state[SESSION_DATA_SOURCE_KEY] = None
    st.session_state["uploaded_filename"]      = None
    _fetch_and_build_api_df.clear()
