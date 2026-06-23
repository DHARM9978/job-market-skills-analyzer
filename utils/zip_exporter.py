"""
ZIP export utility.

Creates an in-memory ZIP archive containing:
  1. The current active dataset as CSV
  2. Key analysis result tables as individual CSVs
  3. A human-readable summary text file

Everything is built in memory (io.BytesIO) so Streamlit can serve it via
st.download_button without writing anything to disk.
"""

import io
import zipfile
import datetime
import logging

import pandas as pd

from utils.constants import COL_SALARY, COL_SKILLS_LIST
from analysis.dashboard_metrics    import compute_dashboard_metrics
from analysis.salary_analysis      import highest_paying_titles, avg_salary_by
from analysis.skill_analysis        import top_skills, skill_salary_premium
from analysis.location_analysis    import jobs_by_location
from analysis.company_analysis     import top_hiring_companies

logger = logging.getLogger(__name__)


def _df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to UTF-8 CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def _build_summary(df: pd.DataFrame, metrics: dict) -> str:
    """Generate a plain-text summary report."""
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "=" * 60,
        "  SkillScope — Job Market Analysis Summary",
        f"  Generated : {now}",
        "=" * 60,
        "",
        "HEADLINE METRICS",
        "-" * 40,
        f"  Total Listings     : {metrics.get('total_jobs', 0):,}",
        f"  Average Salary     : ₹{metrics.get('avg_salary', 0):,.0f}" if metrics.get('avg_salary') else "  Average Salary     : Not disclosed",
        f"  Top Hiring Location: {metrics.get('top_location', '—')}",
        f"  Top Skill          : {metrics.get('top_skill', '—')}",
        f"  Companies Hiring   : {metrics.get('total_companies', 0):,}",
        "",
        "INCLUDED FILES IN THIS ZIP",
        "-" * 40,
        "  dataset.csv              — Full active dataset",
        "  top_skills.csv           — Most in-demand skills",
        "  salary_by_role.csv       — Average salary per job title",
        "  salary_by_location.csv   — Average salary per city",
        "  top_companies.csv        — Top hiring companies",
        "  jobs_by_location.csv     — Listing count per city",
        "",
        "HOW TO USE",
        "-" * 40,
        "  Open any CSV in Excel / Google Sheets for further analysis.",
        "  The dataset.csv can be re-uploaded via the Upload Data page.",
        "",
        "=" * 60,
    ]
    return "\n".join(lines)


def build_zip(df: pd.DataFrame) -> tuple:
    """
    Build a ZIP archive from the current active DataFrame.

    Returns:
        (zip_bytes: bytes, filename: str, error: str | None)
        On failure returns (None, None, error_message).
    """
    if df is None or df.empty:
        return None, None, "No data available to export."

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"skillscope_export_{timestamp}.zip"

    try:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:

            # ── 1. Full dataset ──────────────────────────────────────────
            export_df = df.drop(
                columns=[c for c in [COL_SKILLS_LIST, "Experience_Estimated"]
                         if c in df.columns],
                errors="ignore"
            )
            zf.writestr("dataset.csv", _df_to_csv_bytes(export_df))
            logger.info("ZIP: added dataset.csv (%d rows)", len(export_df))

            # ── 2. Top skills ────────────────────────────────────────────
            skills_df = top_skills(df, top_n=50)
            zf.writestr("top_skills.csv", _df_to_csv_bytes(skills_df))

            # ── 3. Salary by role ────────────────────────────────────────
            from utils.constants import COL_TITLE
            sal_role = highest_paying_titles(df, top_n=50)
            zf.writestr("salary_by_role.csv", _df_to_csv_bytes(sal_role))

            # ── 4. Salary by location ────────────────────────────────────
            from utils.constants import COL_LOCATION
            sal_loc  = avg_salary_by(df, COL_LOCATION)
            zf.writestr("salary_by_location.csv", _df_to_csv_bytes(sal_loc))

            # ── 5. Top companies ─────────────────────────────────────────
            companies = top_hiring_companies(df, top_n=50)
            zf.writestr("top_companies.csv", _df_to_csv_bytes(companies))

            # ── 6. Jobs by location ──────────────────────────────────────
            loc_df = jobs_by_location(df).drop(
                columns=[c for c in ["Lat", "Lon"] if c in jobs_by_location(df).columns],
                errors="ignore"
            )
            zf.writestr("jobs_by_location.csv", _df_to_csv_bytes(loc_df))

            # ── 7. Skill salary premium ──────────────────────────────────
            premium = skill_salary_premium(df, top_n=50)
            if not premium.empty:
                zf.writestr("skill_salary_premium.csv", _df_to_csv_bytes(premium))

            # ── 8. Plain-text summary ────────────────────────────────────
            metrics = compute_dashboard_metrics(df)
            summary = _build_summary(df, metrics)
            zf.writestr("SUMMARY.txt", summary.encode("utf-8"))

        buf.seek(0)
        logger.info("ZIP built successfully: %s (%d bytes)", zip_filename, buf.getbuffer().nbytes)
        return buf.getvalue(), zip_filename, None

    except Exception as exc:
        logger.exception("Failed to build ZIP")
        return None, None, f"Failed to create ZIP: {exc}"
