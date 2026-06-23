import plotly.express as px
from components.theme_manager import themed_plotly_layout
from analysis.location_analysis import jobs_by_location

def jobs_map(df, height=500):
    agg = jobs_by_location(df).dropna(subset=["Lat","Lon"])
    if agg.empty: return None
    fig = px.scatter_mapbox(
        agg, lat="Lat", lon="Lon", size="Listings", color="Avg_Salary",
        hover_name=list(agg.columns)[0],
        hover_data={"Listings":True,"Avg_Salary":":.0f","Lat":False,"Lon":False},
        color_continuous_scale="Blues", size_max=50, zoom=3.8,
        center={"lat":22.5,"lon":80}, mapbox_style="carto-positron",
        title="Job Density & Average Pay by City",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Avg Salary"))
    return themed_plotly_layout(fig, height)
