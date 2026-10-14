"""LogiSight Analytics - Last-Mile Delivery Performance Dashboard (FA-2)."""
import os

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Last-Mile Delivery Dashboard", page_icon="🚚", layout="wide")

DATA_FILE = "Last mile Delivery Data.csv"  # put the dataset next to app.py in the GitHub repo
CAT_COLS = ["Weather", "Traffic", "Vehicle", "Category", "Area"]


# ---------------------------------------------------------------- Stage 4
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw delivery data and add calculated fields."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates()

    # Normalise text columns; treat 'NaN'/blank placeholders as missing.
    for c in CAT_COLS:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip().replace({"": np.nan, "nan": np.nan, "NaN": np.nan, "None": np.nan})

    for c in ["Delivery_Time", "Agent_Rating", "Agent_Age"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Missing values: drop rows with no target / key category, fill numeric gaps with median.
    df = df.dropna(subset=["Delivery_Time"] + [c for c in CAT_COLS if c in df.columns])
    df["Agent_Rating"] = df["Agent_Rating"].fillna(df["Agent_Rating"].median())
    df["Agent_Age"] = df["Agent_Age"].fillna(df["Agent_Age"].median())
    df = df[df["Delivery_Time"] > 0]

    # Calculated fields
    df["Agent_Age_Group"] = pd.cut(
        df["Agent_Age"], bins=[0, 24, 40, 200], labels=["<25", "25-40", "40+"]
    ).astype(str)

    if "Order_Date" in df.columns:
        df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce", dayfirst=False)
        df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
        df.loc[df["Order_Date"].isna(), "Month"] = np.nan

    # Late delivery: time > mean + 1 std (brief's definition), computed on full cleaned data
    threshold = df["Delivery_Time"].mean() + df["Delivery_Time"].std()
    df["Is_Late"] = df["Delivery_Time"] > threshold
    df.attrs["late_threshold"] = threshold
    return df


@st.cache_data(show_spinner="Loading data...")
def load_data(file_bytes=None) -> pd.DataFrame:
    if file_bytes is not None:
        raw = pd.read_csv(file_bytes)
    elif os.path.exists(DATA_FILE):
        raw = pd.read_csv(DATA_FILE)
    else:
        return None
    return clean_data(raw)


def demo_data(n=4000, seed=7) -> pd.DataFrame:
    """Synthetic data in the same schema, only used if no dataset is available."""
    rng = np.random.default_rng(seed)
    w = rng.choice(["Sunny", "Cloudy", "Stormy", "Sandstorms", "Fog", "Windy"], n)
    t = rng.choice(["Low", "Medium", "High", "Jam"], n, p=[.25, .3, .25, .2])
    v = rng.choice(["motorcycle", "scooter", "van", "bicycle"], n, p=[.5, .3, .15, .05])
    area = rng.choice(["Urban", "Metropolitian", "Semi-Urban", "Other"], n, p=[.3, .5, .1, .1])
    cat = rng.choice(["Clothing", "Electronics", "Sports", "Cosmetics", "Grocery", "Books", "Toys"], n)
    rating = np.clip(rng.normal(4.6, .35, n), 1, 5).round(1)
    age = rng.integers(20, 50, n)
    base = (90 + 15 * pd.Series(t).map({"Low": 0, "Medium": 1, "High": 2, "Jam": 4}).values
            + 8 * pd.Series(w).map({"Sunny": 0, "Cloudy": 1, "Fog": 2, "Windy": 1, "Stormy": 4, "Sandstorms": 4}).values
            + 12 * (area == "Metropolitian") + 6 * (cat == "Electronics") - 10 * (rating - 4.6))
    dt = np.clip(base + rng.normal(0, 25, n), 10, None).round()
    dates = pd.to_datetime("2022-02-11") + pd.to_timedelta(rng.integers(0, 60, n), unit="D")
    return pd.DataFrame(dict(Order_ID=range(n), Agent_Age=age, Agent_Rating=rating, Order_Date=dates,
                             Weather=w, Traffic=t, Vehicle=v, Area=area, Delivery_Time=dt, Category=cat))


# ---------------------------------------------------------------- Stage 6: data source
st.title("🚚 Last-Mile Delivery Performance Dashboard")
st.caption("LogiSight Analytics · explore where and why deliveries get delayed")

df = load_data()
if df is None:
    st.sidebar.warning(f"`{DATA_FILE}` not found in the repo.")
    up = st.sidebar.file_uploader("Upload delivery CSV", type="csv")
    if up is not None:
        df = load_data(up)
    elif st.sidebar.checkbox("Use synthetic demo data", value=False):
        df = clean_data(demo_data())
        st.info("Showing synthetic demo data, not the real dataset.")
if df is None:
    st.info("Add the dataset (`amazon_delivery.csv`) to the repository, or upload a CSV in the sidebar.")
    st.stop()

threshold = df.attrs.get("late_threshold", df["Delivery_Time"].mean() + df["Delivery_Time"].std())

# ---------------------------------------------------------------- Stage 6: sidebar filters
st.sidebar.header("Filters")
filters = {}
for col in CAT_COLS:
    opts = sorted(df[col].dropna().unique())
    filters[col] = st.sidebar.multiselect(col, opts, default=opts, key=col)

view = df
for col, sel in filters.items():
    view = view[view[col].isin(sel)]

if view.empty:
    st.warning("No deliveries match the current filters. Widen your selection.")
    st.stop()

# ---------------------------------------------------------------- KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Deliveries", f"{len(view):,}")
k2.metric("Avg delivery time", f"{view['Delivery_Time'].mean():.1f} min",
          delta=f"{view['Delivery_Time'].mean() - df['Delivery_Time'].mean():+.1f} vs overall", delta_color="inverse")
k3.metric("% late deliveries", f"{view['Is_Late'].mean() * 100:.1f}%")
k4.metric("Avg agent rating", f"{view['Agent_Rating'].mean():.2f}")
st.caption(f"Late = delivery time above mean + 1 std of all deliveries ({threshold:.0f} min).")

LABELS = {"Delivery_Time": "Avg delivery time (min)", "Agent_Rating": "Agent rating"}

# ---------------------------------------------------------------- Stage 5: compulsory charts
st.subheader("1 · Delay Analyzer")
st.caption("Storms and traffic jams add the most minutes to a delivery.")
g = view.groupby(["Weather", "Traffic"], as_index=False)["Delivery_Time"].mean()
fig = px.bar(g, x="Weather", y="Delivery_Time", color="Traffic", barmode="group",
             labels=LABELS, title="Average delivery time by weather and traffic")
st.plotly_chart(fig, width="stretch")

c1, c2 = st.columns(2)
with c1:
    st.subheader("2 · Vehicle Comparison")
    st.caption("Shows which vehicle type is fastest on average.")
    g = view.groupby("Vehicle", as_index=False)["Delivery_Time"].mean().sort_values("Delivery_Time")
    fig = px.bar(g, x="Vehicle", y="Delivery_Time", color="Vehicle", text_auto=".1f",
                 labels=LABELS, title="Average delivery time by vehicle")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")
with c2:
    st.subheader("5 · Category Visualizer")
    st.caption("Tall, high boxes mark categories with slow or unpredictable delivery.")
    fig = px.box(view, x="Category", y="Delivery_Time", color="Category",
                 labels={"Delivery_Time": "Delivery time (min)"}, title="Delivery time distribution by category")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

st.subheader("3 · Agent Performance")
st.caption("Do higher-rated or older agents finish faster? Colour = age group.")
order = [x for x in ["<25", "25-40", "40+"] if x in view["Agent_Age_Group"].unique()]
sample = view.sample(min(len(view), 5000), random_state=1)  # keep scatter responsive
fig = px.scatter(sample, x="Agent_Rating", y="Delivery_Time", color="Agent_Age_Group",
                 category_orders={"Agent_Age_Group": order}, opacity=0.5,
                 labels={"Agent_Rating": "Agent rating", "Delivery_Time": "Delivery time (min)",
                         "Agent_Age_Group": "Agent age"},
                 title="Agent rating vs delivery time" + (" (random sample of 5,000)" if len(view) > 5000 else ""))
st.plotly_chart(fig, width="stretch")

st.subheader("4 · Area Heatmap (Regional Bottleneck Finder)")
st.caption("Darker cells mark areas and traffic levels with the longest times.")
hm = view.pivot_table(index="Area", columns="Traffic", values="Delivery_Time", aggfunc="mean")
fig = px.imshow(hm, text_auto=".0f", aspect="auto", color_continuous_scale="YlOrRd",
                labels=dict(color="Avg time (min)"), title="Average delivery time by area and traffic")
st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- optional visuals
st.subheader("Additional Insights")
o1, o2 = st.columns(2)
with o1:
    fig = px.histogram(view, x="Delivery_Time", nbins=40, title="Delivery time distribution",
                       labels={"Delivery_Time": "Delivery time (min)"})
    fig.add_vline(x=threshold, line_dash="dash", line_color="red", annotation_text="late threshold")
    st.plotly_chart(fig, width="stretch")
with o2:
    late = view.groupby("Traffic", as_index=False)["Is_Late"].mean()
    late["Is_Late"] *= 100
    fig = px.bar(late, x="Traffic", y="Is_Late", title="% late deliveries by traffic",
                 labels={"Is_Late": "% late"}, text_auto=".1f")
    st.plotly_chart(fig, width="stretch")
o3, o4 = st.columns(2)
with o3:
    if "Month" in view.columns and view["Month"].notna().any():
        m = view.groupby("Month", as_index=False)["Delivery_Time"].mean()
        st.plotly_chart(px.line(m, x="Month", y="Delivery_Time", markers=True, labels=LABELS,
                                title="Monthly average delivery time"), width="stretch")
with o4:
    if "Order_ID" in view.columns:
        a = view.groupby("Area", as_index=False)["Order_ID"].count().rename(columns={"Order_ID": "Deliveries"})
        st.plotly_chart(px.bar(a, x="Area", y="Deliveries", title="Deliveries per area"), width="stretch")

with st.expander("View cleaned data"):
    st.dataframe(view.head(500))