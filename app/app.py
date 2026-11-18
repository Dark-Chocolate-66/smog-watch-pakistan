"""Smog Watch Pakistan - one-page app (M3 skeleton).

Run from the repo root:  streamlit run app/app.py
Needs app/data/app_data.csv (built in the Colab notebook).
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Smog Watch Pakistan", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "app_data.csv"
BAND_ORDER = ["Good-Moderate", "Sensitive", "Unhealthy", "Severe"]
BAND_COLORS = ["#8fc86b", "#f2c94c", "#f2994a", "#c0392b"]


@st.cache_data
def load_data(path):
    return pd.read_csv(path, parse_dates=["date"])


if not DATA_PATH.exists():
    st.error(f"Data file not found: {DATA_PATH}. Build app_data.csv in the notebook and put it there.")
    st.stop()

df = load_data(DATA_PATH)

# ---------- Sidebar: choices ----------
st.sidebar.header("Choose")
city = st.sidebar.selectbox("City", sorted(df["city"].unique()))

city_df = df[df["city"] == city].sort_values("date")
first_day, last_day = city_df["date"].min().date(), city_df["date"].max().date()
default_start = max(first_day, (city_df["date"].max() - pd.Timedelta(days=365)).date())
start, end = st.sidebar.slider("Date range", min_value=first_day, max_value=last_day,
                               value=(default_start, last_day))

view = city_df[(city_df["date"].dt.date >= start) & (city_df["date"].dt.date <= end)]

# ---------- Title ----------
st.title("Smog Watch Pakistan")
st.caption("Daily air quality and weather for six Pakistani cities. Values come from the CAMS "
           "model via Open-Meteo (modelled, not measured by ground sensors).")

if view.empty:
    st.warning("No days in this range.")
    st.stop()

# ---------- Latest day snapshot ----------
latest = city_df.iloc[-1]
st.subheader(f"{city}: latest day in the data ({latest['date'].date()})")
c1, c2, c3, c4 = st.columns(4)
c1.metric("PM2.5 (daily mean, µg/m³)", f"{latest['pm2_5_mean']:.1f}")
c2.metric("AQI band", str(latest["aqi_band4"]))
c3.metric("Day type (regime)", str(latest["regime_name"]))
c4.metric("Unusual day?", "Yes" if latest["flag_iso"] else "No")
st.caption("Next-day prediction will be added after the full model evaluation (M4).")

# ---------- Chart: PM2.5 over time with unusual days ----------
st.subheader("PM2.5 over time")
flagged = view[view["flag_iso"]]
line = alt.Chart(view).mark_line().encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("pm2_5_mean:Q", title="PM2.5 daily mean (µg/m³)"),
)
points = alt.Chart(flagged).mark_circle(color="red", size=70).encode(
    x="date:T",
    y="pm2_5_mean:Q",
    tooltip=["date:T", "pm2_5_mean:Q", "aqi_band4:N"],
)
st.altair_chart((line + points).properties(height=320).interactive(), width='stretch')
st.caption("Red dots are days flagged as unusual by Isolation Forest (it looks at the whole daily profile).")

# ---------- Bands and regimes ----------
left, right = st.columns(2)

with left:
    st.subheader("Days per AQI band")
    bands = (view["aqi_band4"].value_counts().reindex(BAND_ORDER, fill_value=0)
             .rename_axis("band").reset_index(name="days"))
    bar = alt.Chart(bands).mark_bar().encode(
        x=alt.X("band:N", sort=BAND_ORDER, title=None),
        y=alt.Y("days:Q", title="Days"),
        color=alt.Color("band:N", sort=BAND_ORDER, legend=None,
                        scale=alt.Scale(domain=BAND_ORDER, range=BAND_COLORS)),
    )
    st.altair_chart(bar.properties(height=260), width='stretch')

with right:
    st.subheader("Day types (regimes)")
    regimes = (view.groupby("regime_name")
               .agg(days=("date", "count"), avg_pm25=("pm2_5_mean", "mean"),
                    avg_wind=("wind_mean", "mean"), avg_temp=("temp_mean", "mean"))
               .round(1).sort_values("days", ascending=False))
    st.dataframe(regimes, width='stretch')

# ---------- Unusual days table ----------
with st.expander("Unusual days in this range"):
    cols = ["date", "pm2_5_mean", "aqi_band4", "regime_name", "flag_iqr", "flag_db", "flag_iso"]
    unusual = view[view[["flag_iqr", "flag_db", "flag_iso"]].any(axis=1)]
    st.dataframe(unusual[cols].sort_values("pm2_5_mean", ascending=False), width='stretch')
