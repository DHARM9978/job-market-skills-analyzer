"""
Upload Data & Export page.

Sections:
  1. Upload your own CSV or Excel file
  2. API connection tester
  3. Download current data as a ZIP archive
"""
import streamlit as st
import pandas as pd

from utils.session_manager import init_session_state
from utils.data_loader import apply_uploaded_file, reset_to_default, get_active_dataframe
from utils.validators import validate_file_type, get_file_extension
from utils.column_detector import detect_columns, detection_report, apply_mapping
from utils.constants import DEFAULT_DATA_PATH, SUPPORTED_UPLOAD_TYPES, REQUIRED_COLUMNS
from utils.zip_exporter import build_zip
from components.sidebar import render_sidebar_branding
from components.page_container import page_container
from components.chart_cards import chart_card
from assets.custom_html import badge_html
from data.api_fetcher import test_connection
from config import api_config

init_session_state()
render_sidebar_branding()

with page_container(
    "Upload Data & Export",
    "Upload your own dataset, test the API connection, or export current data as a ZIP.",
    "📤",
    "Data Pipeline",
):
    # ── Sidebar upload controls ──────────────────────────────────────────
    st.sidebar.subheader("📁 Upload Controls")
    st.sidebar.caption(f"Supported: {', '.join(f'.{e}' for e in SUPPORTED_UPLOAD_TYPES)}")
    show_raw    = st.sidebar.checkbox("Show raw preview (before cleaning)", key="up_raw")
    max_preview = st.sidebar.slider("Preview rows", 5, 100, 20, key="up_rows")

    # ══════════════════════════════════════════════════════════════════════
    #  TAB LAYOUT
    # ══════════════════════════════════════════════════════════════════════
    tab_upload, tab_api, tab_export = st.tabs(["📁 Upload File", "🔌 API Status", "⬇️ Download ZIP"])

    # ─────────────────────────────────────────────────────────────────────
    #  TAB 1 — File upload
    # ─────────────────────────────────────────────────────────────────────
    with tab_upload:
        with chart_card("1. Need a template?", "📄"):
            st.markdown(
                "Download the bundled sample to see the expected column structure, "
                "then replace the data with your own."
            )
            with open(DEFAULT_DATA_PATH, "rb") as f:
                st.download_button(
                    "⬇️ Download sample CSV", f,
                    file_name="skillscope_sample.csv",
                    use_container_width=False,
                )
            st.markdown(
                "**Required columns** (names are auto-detected — they don't need to match exactly): "
                + " ".join(badge_html(c, "gray") for c in REQUIRED_COLUMNS),
                unsafe_allow_html=True,
            )

        with chart_card("2. Upload Your File", "📤"):
            uploaded = st.file_uploader(
                "Drop a CSV or Excel (.xlsx) file here",
                type=SUPPORTED_UPLOAD_TYPES,
                key="file_uploader",
            )

        if uploaded:
            if not validate_file_type(uploaded.name):
                st.error(f"Unsupported file type. Please upload: {', '.join(SUPPORTED_UPLOAD_TYPES)}")
            else:
                ext        = get_file_extension(uploaded.name)
                file_bytes = uploaded.getvalue()

                # Column detection preview
                try:
                    raw_preview = (
                        pd.read_excel(file_bytes) if ext == "xlsx"
                        else pd.read_csv(uploaded)
                    )
                    mapping = detect_columns(raw_preview)

                    with chart_card("3. Column Auto-Detection", "🔎"):
                        st.dataframe(
                            pd.DataFrame(detection_report(mapping)),
                            use_container_width=True, hide_index=True,
                        )
                    if show_raw:
                        with chart_card("Raw Preview (before cleaning)", "👁️"):
                            st.dataframe(raw_preview.head(max_preview), use_container_width=True)

                except Exception as e:
                    st.error(f"Could not read file: {e}")
                    st.stop()

                # Clean + validate
                cleaned_df, errors = apply_uploaded_file(file_bytes, uploaded.name, ext)

                if errors:
                    with chart_card("⚠️ Validation Issues", "⚠️"):
                        for err in errors:
                            st.error(err)
                        st.caption("Fix the issues above and re-upload, or continue with the sample/API data.")
                else:
                    with chart_card("4. Cleaned Data Preview", "✅"):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Rows",    f"{len(cleaned_df):,}")
                        c2.metric("Columns", f"{len(cleaned_df.columns):,}")
                        c3.metric("Skills",  "✅ Ready" if "Skills" in cleaned_df.columns else "⚠️ Missing")
                        st.dataframe(cleaned_df.head(max_preview), use_container_width=True, hide_index=True)

                    st.success(f"✅ **{uploaded.name}** loaded — navigate to any analysis page.")
                    st.balloons()

        # Reset button
        if st.session_state.get("data_source") == "upload":
            st.divider()
            if st.button("↺ Revert to API / sample data", use_container_width=False):
                reset_to_default()
                st.rerun()

    # ─────────────────────────────────────────────────────────────────────
    #  TAB 2 — API connection status
    # ─────────────────────────────────────────────────────────────────────
    with tab_api:
        with chart_card("Adzuna API Configuration", "🔌"):
            st.markdown(f"""
            **Credentials file:** `config/api_config.py`

            | Setting | Value |
            |---------|-------|
            | APP_ID  | `{api_config.APP_ID or "NOT SET"}` |
            | APP_KEY | `{"*" * 8 + api_config.APP_KEY[-6:] if api_config.APP_KEY else "NOT SET"}` |
            | Country | `{api_config.COUNTRY}` |
            | Max pages | `{api_config.MAX_PAGES}` |
            | Results / page | `{api_config.RESULTS_PER_PAGE}` |
            """)

        with chart_card("Live Connection Test", "🔍"):
            if st.button("🔄 Test Adzuna connection now", type="primary"):
                with st.spinner("Pinging Adzuna API…"):
                    ok, msg = test_connection()
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
                    st.caption("Check your APP_ID and APP_KEY in `config/api_config.py`.")

            st.caption(
                "The app automatically fetches live data when credentials are set. "
                "If the test fails, the app falls back to the bundled sample dataset silently."
            )

        with chart_card("API Error Log", "📋"):
            api_err = st.session_state.get("api_error_message")
            if api_err:
                st.warning(f"Last API error: {api_err}")
            else:
                st.success("No API errors recorded in this session.")

    # ─────────────────────────────────────────────────────────────────────
    #  TAB 3 — ZIP export
    # ─────────────────────────────────────────────────────────────────────
    with tab_export:
        with chart_card("Export Current Data as ZIP", "📦"):
            st.markdown("""
            Creates a ZIP archive of the **currently active dataset** and key analysis results.

            **Files included in the ZIP:**

            | File | Contents |
            |------|---------|
            | `dataset.csv` | Full active dataset (all rows, cleaned) |
            | `top_skills.csv` | Top 50 most in-demand skills |
            | `salary_by_role.csv` | Average salary per job title |
            | `salary_by_location.csv` | Average salary per city |
            | `top_companies.csv` | Top 50 hiring companies |
            | `jobs_by_location.csv` | Listing count per city |
            | `skill_salary_premium.csv` | Skills vs. salary correlation |
            | `SUMMARY.txt` | Plain-text summary report |
            """)

            # Show current data source
            src = st.session_state.get("data_source", "none")
            src_labels = {
                "api":    "🟢 Live Adzuna API data",
                "upload": "🟣 Uploaded dataset",
                "sample": "🟡 Bundled sample dataset",
            }
            st.info(f"Data source that will be zipped: **{src_labels.get(src, '⚪ Loading…')}**")

            # Generate button
            if st.button("📦 Generate & Download ZIP", type="primary", use_container_width=False):
                df = get_active_dataframe()
                with st.spinner("Building ZIP archive…"):
                    zip_bytes, zip_filename, err = build_zip(df)

                if err:
                    st.error(f"❌ {err}")
                elif zip_bytes:
                    st.success(
                        f"✅ ZIP ready — **{len(zip_bytes)/1024:.0f} KB**, "
                        f"{zip_filename}"
                    )
                    # Immediate download button appears right after generation
                    st.download_button(
                        label=f"⬇️ Download {zip_filename}",
                        data=zip_bytes,
                        file_name=zip_filename,
                        mime="application/zip",
                        use_container_width=False,
                    )
                else:
                    st.warning("No data available to export — navigate to a page first to load data.")
