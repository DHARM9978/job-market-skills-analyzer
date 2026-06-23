import pandas as pd
from utils.constants import REQUIRED_COLUMNS, SUPPORTED_UPLOAD_TYPES

def validate_dataframe(df):
    if df is None or df.empty:
        return False, ["The file appears to be empty."]
    errors = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing columns after auto-detection: {', '.join(missing)}")
    if COL_SALARY := "Salary":
        if COL_SALARY in df.columns:
            all_nan = pd.to_numeric(df[COL_SALARY], errors="coerce").isna().all()
            if all_nan:
                errors.append("No usable numeric Salary values found.")
    return len(errors) == 0, errors

def validate_file_type(filename):
    name = str(filename).lower()
    return any(name.endswith(f".{ext}") for ext in SUPPORTED_UPLOAD_TYPES)

def get_file_extension(filename):
    return str(filename).lower().rsplit(".", 1)[-1] if "." in str(filename) else ""
