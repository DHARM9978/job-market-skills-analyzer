"""Core Plotly chart builders — all styled via themed_plotly_layout."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from assets.color_palette import CATEGORICAL_SEQUENCE
from components.theme_manager import themed_plotly_layout

def bar_chart(df, x, y, color=None, title="", height=380, text_auto=True, orientation="v"):
    fig = px.bar(df,x=x,y=y,color=color,orientation=orientation,title=title,
                 color_discrete_sequence=CATEGORICAL_SEQUENCE,
                 text_auto=".2s" if text_auto else False)
    fig.update_traces(marker_line_width=0)
    return themed_plotly_layout(fig, height)

def horizontal_bar(df, x, y, title="", height=380):
    fig = px.bar(df,x=x,y=y,orientation="h",title=title,
                 color_discrete_sequence=CATEGORICAL_SEQUENCE, text=x)
    fig.update_traces(marker_line_width=0, texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    return themed_plotly_layout(fig, height)

def pie_chart(df, names, values, title="", height=380, hole=0.55):
    fig = px.pie(df,names=names,values=values,title=title,hole=hole,
                 color_discrete_sequence=CATEGORICAL_SEQUENCE)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return themed_plotly_layout(fig, height)

def line_chart(df, x, y, color=None, title="", height=380, markers=True):
    fig = px.line(df,x=x,y=y,color=color,title=title,markers=markers,
                  color_discrete_sequence=CATEGORICAL_SEQUENCE)
    fig.update_traces(line_width=2.5)
    return themed_plotly_layout(fig, height)

def box_chart(df, x, y, color=None, title="", height=420):
    fig = px.box(df,x=x,y=y,color=color,title=title,
                 color_discrete_sequence=CATEGORICAL_SEQUENCE, points=False)
    return themed_plotly_layout(fig, height)

def scatter_chart(df, x, y, color=None, size=None, hover_name=None, title="", height=420):
    fig = px.scatter(df,x=x,y=y,color=color,size=size,hover_name=hover_name,
                     title=title,color_discrete_sequence=CATEGORICAL_SEQUENCE,opacity=0.72)
    return themed_plotly_layout(fig, height)

def histogram_chart(df, x, nbins=30, title="", height=380):
    fig = px.histogram(df,x=x,nbins=nbins,title=title,
                       color_discrete_sequence=CATEGORICAL_SEQUENCE)
    fig.update_traces(marker_line_width=0)
    return themed_plotly_layout(fig, height)

def treemap_chart(df, path, values, title="", height=420):
    fig = px.treemap(df,path=path,values=values,title=title,
                     color_discrete_sequence=CATEGORICAL_SEQUENCE)
    return themed_plotly_layout(fig, height)

def heatmap_chart(z, x_labels, y_labels, title="", height=420):
    fig = go.Figure(data=go.Heatmap(z=z,x=x_labels,y=y_labels,
                                     colorscale="Blues",hoverongaps=False))
    fig.update_layout(title=title)
    return themed_plotly_layout(fig, height)

def radar_chart(categories, values, name="Profile", title="", height=420):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values+[values[0]], theta=categories+[categories[0]],
        fill="toself", name=name, line_color="#4A7FC0",
        fillcolor="rgba(74,127,192,0.15)"))
    fig.update_layout(title=title, polar=dict(radialaxis=dict(visible=True)))
    return themed_plotly_layout(fig, height)
