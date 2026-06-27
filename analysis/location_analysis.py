import pandas as pd
from utils.constants import COL_LOCATION, COL_STATE, COL_SALARY, COL_INDUSTRY, COL_TITLE, CITY_COORDS, COL_LAT, COL_LON

def jobs_by_location(df):


    # Remove Unknown / India locations
    df = df[
        ~df[COL_LOCATION]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["unknown", "india", ""])
    ]

    

    out = (
        df.groupby(COL_LOCATION, observed=True)
        .agg(
            Listings=(COL_LOCATION, "count"),
            Avg_Salary=(COL_SALARY, "mean")
        )
        .reset_index()
        .sort_values("Listings", ascending=False)
    )

    if COL_LAT in df.columns and COL_LON in df.columns:
        coords = df.groupby(COL_LOCATION)[[COL_LAT, COL_LON]].mean()
        out = out.join(coords, on=COL_LOCATION)
        out = out.rename(columns={COL_LAT: "Lat", COL_LON: "Lon"})
    else:
        out["Lat"] = out[COL_LOCATION].map(
            lambda c: CITY_COORDS.get(c, (None, None))[0]
        )
        out["Lon"] = out[COL_LOCATION].map(
            lambda c: CITY_COORDS.get(c, (None, None))[1]
        )

    return out


def jobs_by_state(df):
    if COL_STATE not in df.columns or df[COL_STATE].isna().all():
        return pd.DataFrame()
    return (df.dropna(subset=[COL_STATE]).groupby(COL_STATE, observed=True)
            .agg(Listings=(COL_STATE,"count"), Avg_Salary=(COL_SALARY,"mean"))
            .reset_index().sort_values("Listings",ascending=False))

def top_industry_per_location(df):
    idx = df.groupby(COL_LOCATION, observed=True)[COL_INDUSTRY].agg(
        lambda s: s.value_counts().index[0] if len(s) else "—")
    return idx.reset_index().rename(columns={COL_INDUSTRY:"Top_Industry"})

def location_industry_pivot(df):
    return pd.pivot_table(df, index=COL_LOCATION, columns=COL_INDUSTRY,
                          values=COL_TITLE, aggfunc="count", fill_value=0, observed=True)
