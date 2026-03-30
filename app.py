import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UFO Sightings Explorer",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global dark-theme CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background-color: #0d0d0d; }
  [data-testid="stSidebar"]          { background-color: #141414; }
  [data-testid="stHeader"]           { background-color: #0d0d0d; }
  h1, h2, h3, h4, p, label, span    { color: #e0e0e0 !important; }
  .metric-card {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 10px; padding: 18px 22px; text-align: center;
  }
  .metric-value { font-size: 2rem; font-weight: 700; color: #ff4b4b !important; }
  .metric-label { font-size: 0.82rem; color: #888 !important; letter-spacing: 0.05em; text-transform: uppercase; }
  .chart-title  { font-size: 1rem; font-weight: 600; color: #ccc !important;
                  letter-spacing: 0.04em; margin-bottom: 4px; }
  .chart-sub    { font-size: 0.78rem; color: #666 !important; margin-bottom: 12px; }
  hr { border-color: #2a2a2a; }
</style>
""", unsafe_allow_html=True)

PLOT_BG   = "#0d0d0d"
PAPER_BG  = "#0d0d0d"
GRID_COL  = "#1e1e1e"
FONT_COL  = "#cccccc"
ACCENT    = "#ff4b4b"

def styled_fig(fig, height=380):
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COL, family="Inter, sans-serif", size=12),
        margin=dict(l=50, r=30, t=30, b=50),
        height=height,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="#2a2a2a",
            font=dict(color=FONT_COL, size=11),
        ),
        xaxis=dict(showgrid=True, gridcolor=GRID_COL, zeroline=False,
                   tickfont=dict(color=FONT_COL)),
        yaxis=dict(showgrid=True, gridcolor=GRID_COL, zeroline=False,
                   tickfont=dict(color=FONT_COL)),
    )
    return fig

# ── Load & cache data ───────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("scrubbed.csv", low_memory=False)
    df["duration (seconds)"] = pd.to_numeric(df["duration (seconds)"], errors="coerce")
    df["datetime"]   = pd.to_datetime(df["datetime"], errors="coerce")
    df["year"]       = df["datetime"].dt.year
    df["hour"]       = df["datetime"].dt.hour
    df["month"]      = df["datetime"].dt.month
    df["latitude"]   = pd.to_numeric(df["latitude"],   errors="coerce")
    df["longitude "] = pd.to_numeric(df["longitude "], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

df_raw = load_data()

# ── Sidebar filters ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛸 Filters")
    st.markdown("---")

    countries_available = sorted(df_raw["country"].dropna().unique().tolist())
    selected_countries  = st.multiselect(
        "Country",
        options=countries_available,
        default=["us"],
        help="Filter by country of sighting"
    )

    year_min = int(df_raw["year"].min())
    year_max = int(df_raw["year"].max())
    year_range = st.slider(
        "Year Range",
        min_value=year_min,
        max_value=year_max,
        value=(1990, 2013),
        step=1
    )

    shapes_available = sorted(df_raw["shape"].dropna().unique().tolist())
    selected_shapes  = st.multiselect(
        "UFO Shape",
        options=shapes_available,
        default=[],
        help="Leave blank to include all shapes"
    )

    st.markdown("---")
    st.markdown(
        "<span style='color:#555;font-size:0.75rem;'>"
        "Data: NUFORC via Kaggle<br>"
        "UC3DVS10 · Assessment 2 · Task 1"
        "</span>",
        unsafe_allow_html=True,
    )

# ── Apply filters ───────────────────────────────────────────────────────────────
df = df_raw.copy()
if selected_countries:
    df = df[df["country"].isin(selected_countries)]
df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
if selected_shapes:
    df = df[df["shape"].isin(selected_shapes)]

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='font-size:2rem;font-weight:700;letter-spacing:0.05em;'>"
    "🛸 UFO Sightings Explorer"
    "</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#666;margin-top:-14px;'>Interactive dashboard · NUFORC dataset · "
    + f"{year_range[0]}–{year_range[1]}"
    + "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── KPI row ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
metrics = [
    (k1, f"{len(df):,}",           "Total Sightings"),
    (k2, f"{df['country'].nunique():,}", "Countries"),
    (k3, f"{df['shape'].nunique():,}",   "Distinct Shapes"),
    (k4, f"{df['city'].nunique():,}",    "Unique Cities"),
]
for col, val, label in metrics:
    with col:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-value'>{val}</div>"
            f"<div class='metric-label'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Sightings over time  (full width)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='chart-title'>SIGHTINGS OVER TIME</div>"
    "<div class='chart-sub'>Annual count of reported UFO sightings — note the surge after NUFORC went online in 1995</div>",
    unsafe_allow_html=True,
)

yearly = df.groupby("year").size().reset_index(name="count")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=yearly["year"], y=yearly["count"],
    mode="lines",
    line=dict(color="#555", width=1.5),
    fill="tozeroy",
    fillcolor="rgba(255,75,75,0.06)",
    hovertemplate="<b>%{x}</b><br>Sightings: %{y:,}<extra></extra>",
    showlegend=False,
))
fig1.add_trace(go.Scatter(
    x=yearly["year"], y=yearly["count"],
    mode="lines+markers",
    line=dict(color=ACCENT, width=2.5),
    marker=dict(size=4, color=ACCENT),
    hovertemplate="<b>%{x}</b><br>Sightings: %{y:,}<extra></extra>",
    name="Annual sightings",
))

# 1995 annotation — internet effect
if year_range[0] <= 1995 <= year_range[1]:
    val_1995 = yearly[yearly["year"] == 1995]["count"].values
    if len(val_1995):
        fig1.add_annotation(
            x=1995, y=val_1995[0],
            text="1995 · NUFORC<br>goes online",
            showarrow=True, arrowhead=2,
            arrowcolor="#aaa", arrowsize=1, arrowwidth=1.5,
            ax=60, ay=-50,
            font=dict(size=11, color="#aaa"),
            bgcolor="#1a1a1a", bordercolor="#444", borderpad=4,
        )

fig1 = styled_fig(fig1, height=320)
fig1.update_layout(showlegend=False, xaxis=dict(title=None), yaxis=dict(title="Sightings"))
st.plotly_chart(fig1, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 + CHART 3  —  side by side
# ══════════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns([1, 1])

# ── CHART 2  Hour of day ───────────────────────────────────────────────────────
with col_left:
    st.markdown(
        "<div class='chart-title'>WHEN DO UFOs APPEAR?</div>"
        "<div class='chart-sub'>Distribution of sightings by hour of day — peak: 9–10 pm</div>",
        unsafe_allow_html=True,
    )
    hourly = df.groupby("hour").size().reset_index(name="count").dropna()
    hourly = hourly[hourly["hour"].between(0, 23)]

    peak_hour = hourly.loc[hourly["count"].idxmax(), "hour"]
    colors_hour = [ACCENT if h == peak_hour else "#2a4a6a" for h in hourly["hour"]]

    fig2 = go.Figure(go.Bar(
        x=hourly["hour"],
        y=hourly["count"],
        marker_color=colors_hour,
        hovertemplate="<b>%{x}:00</b><br>Sightings: %{y:,}<extra></extra>",
    ))
    fig2 = styled_fig(fig2, height=340)
    fig2.update_layout(
        xaxis=dict(title="Hour of Day (24h)", dtick=3,
                   tickvals=list(range(0, 24, 3)),
                   ticktext=["12am","3am","6am","9am","12pm","3pm","6pm","9pm"]),
        yaxis=dict(title="Sightings"),
    )
    fig2.add_annotation(
        x=peak_hour, y=hourly["count"].max(),
        text=f" Peak: {int(hourly['count'].max()):,}",
        showarrow=False,
        font=dict(size=11, color=ACCENT),
        xanchor="left", yanchor="bottom",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── CHART 3  Shape trends over time ───────────────────────────────────────────
with col_right:
    st.markdown(
        "<div class='chart-title'>SHAPE TRENDS OVER TIME</div>"
        "<div class='chart-sub'>Top shapes by year — triangle sightings grew 15× since 1990</div>",
        unsafe_allow_html=True,
    )

    TOP_N   = 5
    top_shapes = df["shape"].value_counts().head(TOP_N).index.tolist()
    shape_year = (
        df[df["shape"].isin(top_shapes)]
        .groupby(["year", "shape"])
        .size()
        .reset_index(name="count")
    )

    palette = [ACCENT, "#4ecdc4", "#ffe66d", "#a8dadc", "#6c757d"]
    fig3    = go.Figure()
    for i, shape in enumerate(top_shapes):
        sub = shape_year[shape_year["shape"] == shape]
        is_triangle = (shape == "triangle")
        fig3.add_trace(go.Scatter(
            x=sub["year"], y=sub["count"],
            mode="lines",
            name=shape.capitalize(),
            line=dict(
                color=palette[i],
                width=3 if is_triangle else 1.8,
                dash="solid",
            ),
            opacity=1.0 if (i == 0 or is_triangle) else 0.55,
            hovertemplate=f"<b>{shape.capitalize()}</b><br>Year: %{{x}}<br>Sightings: %{{y:,}}<extra></extra>",
        ))

    fig3 = styled_fig(fig3, height=340)
    fig3.update_layout(
        xaxis=dict(title=None),
        yaxis=dict(title="Sightings"),
        legend=dict(orientation="h", y=-0.22, x=0),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Geographic map (US only when US selected)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    "<div class='chart-title'>WHERE DO SIGHTINGS OCCUR?</div>"
    "<div class='chart-sub'>Geographic distribution — bubble size = number of sightings per city</div>",
    unsafe_allow_html=True,
)

map_df = (
    df.dropna(subset=["latitude", "longitude "])
    .groupby(["city", "state", "country", "latitude", "longitude "])
    .size()
    .reset_index(name="count")
)
map_df = map_df.sort_values("count", ascending=False).head(500)

scope = "usa" if selected_countries == ["us"] else "world"

fig4 = go.Figure(go.Scattergeo(
    lat=map_df["latitude"],
    lon=map_df["longitude "],
    text=map_df["city"].str.title() + ", " + map_df["country"].str.upper(),
    customdata=map_df["count"],
    hovertemplate="<b>%{text}</b><br>Sightings: %{customdata:,}<extra></extra>",
    marker=dict(
        size=np.clip(np.log1p(map_df["count"]) * 3, 3, 24),
        color=map_df["count"],
        colorscale=[[0, "#1a1a2e"], [0.4, "#e94560"], [1, ACCENT]],
        opacity=0.75,
        line=dict(width=0),
        colorbar=dict(
            title="Sightings",
            titlefont=dict(color=FONT_COL),
            tickfont=dict(color=FONT_COL),
            bgcolor="#141414",
            bordercolor="#2a2a2a",
        ),
    ),
))
fig4.update_geos(
    scope=scope,
    bgcolor=PLOT_BG,
    showland=True, landcolor="#1a1a1a",
    showocean=True, oceancolor="#0d0d0d",
    showcoastlines=True, coastlinecolor="#2a2a2a",
    showlakes=True, lakecolor="#0d0d0d",
    showcountries=True, countrycolor="#2a2a2a",
    showsubunits=True, subunitcolor="#222222",
    framecolor="#2a2a2a",
)
fig4.update_layout(
    paper_bgcolor=PAPER_BG,
    geo=dict(bgcolor=PLOT_BG),
    margin=dict(l=0, r=0, t=10, b=10),
    height=420,
    font=dict(color=FONT_COL),
)
st.plotly_chart(fig4, use_container_width=True)

# ── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='color:#444;font-size:0.75rem;text-align:center;'>"
    "Data source: National UFO Reporting Center (NUFORC) via Kaggle · "
    "UC3DVS10 Data Visualisation · Assessment 2 Task 1 · Ceazar Jay Mamburam"
    "</p>",
    unsafe_allow_html=True,
)
