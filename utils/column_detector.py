import re, pandas as pd
from utils.constants import (
    COL_TITLE, COL_COMPANY, COL_LOCATION, COL_STATE, COL_SALARY,
    COL_SKILLS, COL_EXPERIENCE, COL_JOB_TYPE, COL_INDUSTRY,
    COL_DESCRIPTION, COL_DATE_POSTED,
)

_HINTS = {
    COL_TITLE:       ["job_title","jobtitle","title","role","position"],
    COL_COMPANY:     ["company","employer","organisation","organization"],
    COL_LOCATION:    ["location","city","place","region"],
    COL_STATE:       ["state","province"],
    COL_SALARY:      ["salary","ctc","pay","compensation","income"],
    COL_SKILLS:      ["skill","tech_stack","techstack","tools","competenc"],
    COL_EXPERIENCE:  ["experience","exp","years"],
    COL_JOB_TYPE:    ["job_type","jobtype","employment_type"],
    COL_INDUSTRY:    ["industry","sector","domain","field","category"],
    COL_DESCRIPTION: ["description","summary","details","jobdesc"],
    COL_DATE_POSTED: ["date","posted","created","published"],
}

def _norm(name): return re.sub(r"[^a-z0-9]","",str(name).lower())

def detect_columns(df: pd.DataFrame) -> dict:
    normalized = {col: _norm(col) for col in df.columns}
    mapping = {}
    for canon, hints in _HINTS.items():
        found = next(
            (orig for orig, norm in normalized.items()
             if any(h.replace("_","") in norm for h in hints)),
            None
        )
        mapping[canon] = found
    return mapping

def detection_report(mapping: dict) -> list:
    return [
        {"Expected Field": c, "Matched Column": s or "—",
         "Status": "✅ Detected" if s else "⚠️ Not found"}
        for c, s in mapping.items()
    ]

def apply_mapping(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    return df.rename(columns={src: canon for canon, src in mapping.items() if src})
