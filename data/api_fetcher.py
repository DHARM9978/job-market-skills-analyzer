"""
Adzuna API client — fetches job listings, handles pagination and errors.

Every public function returns (df, error_str) so callers can show a
friendly message instead of crashing the Streamlit app.
"""

import logging
import requests
import pandas as pd

from config import api_config

logger    = logging.getLogger(__name__)
BASE_URL  = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
TIMEOUT   = 15  # seconds


class AdzunaFetchError(Exception):
    pass


def _build_params(results_per_page: int = None) -> dict:
    params = {
        "app_id":           api_config.APP_ID,
        "app_key":          api_config.APP_KEY,
        "results_per_page": results_per_page or api_config.RESULTS_PER_PAGE,
        "content-type":     "application/json",
    }
    if api_config.WHAT_FILTER.strip():
        params["what"] = api_config.WHAT_FILTER.strip()
    return params


def fetch_page(page: int, results_per_page: int = None) -> dict:
    """Fetch one page. Raises AdzunaFetchError on any problem."""
    if not api_config.is_configured():
        raise AdzunaFetchError(
            "API credentials are missing — add APP_ID & APP_KEY to config/api_config.py"
        )

    url    = BASE_URL.format(country=api_config.COUNTRY, page=page)
    params = _build_params(results_per_page)

    logger.info("Fetching Adzuna page %d …", page)
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        raise AdzunaFetchError("Cannot reach Adzuna API — check your internet connection.")
    except requests.exceptions.Timeout:
        raise AdzunaFetchError(f"Adzuna API timed out after {TIMEOUT}s.")
    except requests.exceptions.RequestException as exc:
        raise AdzunaFetchError(f"Network error: {exc}") from exc

    if resp.status_code == 401:
        raise AdzunaFetchError(
            "Adzuna rejected the credentials — double-check APP_ID and APP_KEY."
        )
    if resp.status_code == 429:
        raise AdzunaFetchError("Adzuna rate limit hit — wait a minute and retry.")
    if resp.status_code != 200:
        raise AdzunaFetchError(
            f"Adzuna returned HTTP {resp.status_code}: {resp.text[:200]}"
        )

    try:
        data = resp.json()
    except ValueError:
        raise AdzunaFetchError("Adzuna returned invalid JSON.") from None

    results = data.get("results", [])
    logger.info("Page %d: %d results (total available: %s)", page, len(results), data.get("count"))
    return data


def fetch_jobs(max_pages: int = None) -> pd.DataFrame:
    """
    Fetch multiple pages of Adzuna listings.
    Returns a flat DataFrame (columns = json_normalized Adzuna fields).
    Raises AdzunaFetchError on failure — caller handles it.
    """
    max_pages = max_pages or api_config.MAX_PAGES
    all_rows  = []

    for page in range(1, max_pages + 1):
        data    = fetch_page(page)
        results = data.get("results", [])
        if not results:
            logger.info("No results on page %d — stopping pagination", page)
            break
        all_rows.extend(results)
        total = data.get("count")
        if total is not None and len(all_rows) >= total:
            break

    if not all_rows:
        logger.warning("Adzuna returned 0 results total")
        return pd.DataFrame()

    df = pd.json_normalize(all_rows)
    logger.info("Fetched %d total listings from Adzuna", len(df))
    return df


def test_connection() -> tuple:
    """Quick 1-result ping. Returns (success: bool, message: str)."""
    if not api_config.is_configured():
        return False, "API credentials are missing."
    try:
        data = fetch_page(1, results_per_page=1)
        count = data.get("count", "?")
        return True, f"Connected — {count:,} total listings available." if isinstance(count, int) else f"Connected — {count} total listings available."
    except AdzunaFetchError as exc:
        return False, str(exc)
