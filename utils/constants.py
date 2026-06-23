"""Central constants — single source of truth for column names, paths, and session keys."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_PATH = os.path.join(BASE_DIR, "jobs_dataset.csv")

# ── Canonical column names ─────────────────────────────────────────────────
COL_TITLE       = "Job_Title"
COL_COMPANY     = "Company"
COL_LOCATION    = "Location"
COL_STATE       = "State"
COL_SALARY      = "Salary"
COL_SKILLS      = "Skills"
COL_EXPERIENCE  = "Experience"
COL_JOB_TYPE    = "Job_Type"
COL_INDUSTRY    = "Industry"
COL_DESCRIPTION = "Description"
COL_DATE_POSTED = "Date_Posted"
COL_LAT         = "Lat"
COL_LON         = "Lon"
COL_SKILLS_LIST  = "Skills_List"
COL_EXP_BRACKET  = "Experience_Bracket"

REQUIRED_COLUMNS = [COL_TITLE, COL_COMPANY, COL_LOCATION, COL_SALARY, COL_SKILLS, COL_EXPERIENCE, COL_INDUSTRY]

# ── App meta ───────────────────────────────────────────────────────────────
APP_TITLE   = "SkillScope — Job Market Analyzer"
APP_ICON    = "📊"
APP_TAGLINE = "Decode the job market. Find your edge."

# ── Experience brackets ────────────────────────────────────────────────────
EXPERIENCE_BRACKETS = [
    (0, 1, "Entry (0–1 yr)"),
    (2, 3, "Junior (2–3 yrs)"),
    (4, 5, "Mid (4–5 yrs)"),
    (6, 7, "Senior (6–7 yrs)"),
    (8, 99, "Lead (8+ yrs)"),
]

# ── City coordinates (fallback when API has no lat/lon) ───────────────────
CITY_COORDS = {
    "Delhi":     (28.6139, 77.2090),
    "Mumbai":    (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai":   (13.0827, 80.2707),
    "Pune":      (18.5204, 73.8567),
    "Kolkata":   (22.5726, 88.3639),
    "Noida":     (28.5355, 77.3910),
}

# ── Currency ───────────────────────────────────────────────────────────────
CURRENCY_SYMBOL = "₹"
LAKH  = 100_000
CRORE = 10_000_000

# ── Session state keys ─────────────────────────────────────────────────────
SESSION_DATA_KEY        = "job_market_df"
SESSION_FILTERS_KEY     = "active_filters"
SESSION_DATA_SOURCE_KEY = "data_source"
SESSION_API_ERROR_KEY   = "api_error_message"

DATA_SOURCE_API    = "api"
DATA_SOURCE_UPLOAD = "upload"
DATA_SOURCE_SAMPLE = "sample"

SUPPORTED_UPLOAD_TYPES = ["csv", "xlsx"]
