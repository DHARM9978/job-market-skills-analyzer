# 📊 SkillScope — Job Market Analyzer

A full-stack Streamlit app for exploring job-market data: live from the **Adzuna API**, your own uploaded CSV/Excel, or a bundled sample dataset as a fallback.

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app starts immediately using the **bundled sample dataset**. To switch to live Adzuna data, add your credentials first (see below).

---

## 🔑 Adzuna API Setup

1. Register free at https://developer.adzuna.com/
2. Create an application in the Adzuna dashboard.
3. Open **`config/api_config.py`** and paste your credentials:

```python
# config/api_config.py  ← EDIT THIS FILE

APP_ID  = "your_app_id_here"    # ← paste App ID here
APP_KEY = "your_app_key_here"   # ← paste App Key here
```

4. Restart the app — it will automatically fetch live data on startup.

---

## 📁 Project Structure

```
job_market_analyzer/
├── .streamlit/config.toml      ← Streamlit theme (off-white)
├── config/
│   └── api_config.py           ← ★ ADD YOUR APP_ID + APP_KEY HERE ★
├── data/
│   ├── api_fetcher.py          ← Adzuna API client (pagination, error handling)
│   ├── data_processor.py       ← Raw JSON → canonical schema
│   └── skill_extractor.py      ← Extract skills from job descriptions
├── analysis/                   ← Pure data computations (no UI)
├── visualizations/             ← Plotly chart builders
├── components/                 ← Reusable UI building blocks
├── app_pages/                  ← One file per page (7 pages)
├── utils/                      ← Data loading, cleaning, validation, session
├── assets/
│   └── main_theme.css          ← Single professional off-white theme
├── jobs_dataset.csv            ← Bundled sample (1000 listings, India)
├── app.py                      ← Entry point
└── requirements.txt
```

---

## 🗂️ Pages & Their Filters

| Page | Sidebar Filters |
|------|----------------|
| Dashboard | Job Category, Location, Date Range (API data only) |
| Salary Analysis | Job Role, Location, Experience Level, Salary Range |
| Skills Analysis | Skill, Experience Level, Job Category |
| Location Analysis | State, City, Job Category, Experience Level |
| Company Analysis | Location, Industry, Experience Level |
| Recommendations | Desired Role, Your Skills, Experience Level |
| Upload Data | File type selector, preview row count |

---

## 📊 Data Sources (Priority Order)

1. **User Upload** — CSV or Excel (.xlsx), column names auto-detected
2. **Adzuna API** — live job listings (requires credentials in `config/api_config.py`)
3. **Sample CSV** — bundled 1,000-row India dataset (always available as fallback)

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit>=1.36` | Web app framework (st.Page navigation API) |
| `pandas>=2.0` | Data processing |
| `plotly>=5.20` | Interactive charts & maps |
| `requests>=2.31` | Adzuna API HTTP calls |
| `openpyxl>=3.1` | Excel (.xlsx) upload support |
