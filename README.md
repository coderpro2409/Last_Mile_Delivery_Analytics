# Last-Mile Delivery Analytics 📦🚚

A Streamlit-based interactive dashboard for exploring last-mile delivery performance, uncovering delay patterns, and identifying operational bottlenecks across weather, traffic, vehicle types, areas, and agent profiles.

## 📋 Overview

**LogiSight Analytics** is a data analytics application that transforms raw delivery data into actionable insights. It helps logistics teams understand **where and why deliveries get delayed** by providing a suite of interactive visualizations and key performance indicators (KPIs).

The dashboard is built with **Streamlit**, **Pandas**, **NumPy**, and **Plotly Express**, and is designed to work with a CSV dataset containing delivery records. If the primary dataset is unavailable, the app can automatically fall back to synthetic demo data so the dashboard remains fully explorable.

## ✨ Features

The dashboard provides the following core analytics modules:

| Module | Description |
|--------|-------------|
| **KPI Summary** | At-a-glance metrics: total deliveries, average delivery time, percentage of late deliveries, and average agent rating. |
| **Delay Analyzer** | Grouped bar chart showing average delivery time by **weather** and **traffic** conditions—revealing how storms and traffic jams add the most minutes. |
| **Vehicle Comparison** | Bar chart ranking vehicle types (motorcycle, scooter, van, bicycle) by average delivery time. |
| **Agent Performance** | Scatter plot of agent rating vs. delivery time, colored by age group, to assess whether higher-rated or older agents finish faster. |
| **Area Heatmap** | Interactive heatmap (Regional Bottleneck Finder) showing average delivery time by **area** and **traffic** level—darker cells mark the slowest combinations. |
| **Category Visualizer** | Box plot of delivery time distribution by product category, highlighting categories with slow or unpredictable delivery. |
| **Additional Insights** | Delivery time distribution histogram with late-threshold line, percentage of late deliveries by traffic level, monthly average delivery time trend, and deliveries per area. |

All charts are fully interactive and update dynamically based on the sidebar filters (weather, traffic, vehicle, category, area).

## 🛠️ Tech Stack

- **Python** ≥ 3.9
- **Streamlit** ≥ 1.50 — web app framework
- **Pandas** ≥ 2.0 — data manipulation
- **NumPy** ≥ 1.24 — numerical operations
- **Plotly Express** ≥ 5.20 — interactive visualizations

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- `pip` package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/coderpro2409/Last_Mile_Delivery_Analytics.git
   cd Last_Mile_Delivery_Analytics
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Dashboard

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

### Data Setup

The app expects a CSV file named **`Last mile Delivery Data.csv`** in the repository root. If the file is missing, you can:

- **Upload your own CSV** via the sidebar file uploader.
- **Enable the "Use synthetic demo data"** checkbox in the sidebar to explore the dashboard with generated data.

## 📊 Dataset Schema

The dashboard works with a CSV containing the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `Order_ID` | Integer | Unique order identifier |
| `Agent_Age` | Integer | Delivery agent's age |
| `Agent_Rating` | Float | Agent rating (1–5) |
| `Order_Date` | Date | Date of the order |
| `Weather` | Categorical | Sunny, Cloudy, Stormy, Sandstorms, Fog, Windy |
| `Traffic` | Categorical | Low, Medium, High, Jam |
| `Vehicle` | Categorical | motorcycle, scooter, van, bicycle |
| `Area` | Categorical | Urban, Metropolitian, Semi-Urban, Other |
| `Delivery_Time` | Numeric | Delivery time in minutes |
| `Category` | Categorical | Clothing, Electronics, Sports, Cosmetics, Grocery, Books, Toys |

**Late Delivery Definition:** A delivery is flagged as late if its delivery time exceeds **mean + 1 standard deviation** of all deliveries in the cleaned dataset.

## 🧹 Data Cleaning Pipeline

The `clean_data()` function performs the following steps:

1. Strips whitespace from column names.
2. Removes duplicate rows.
3. Normalizes categorical columns and treats placeholder values (`""`, `"nan"`, `"NaN"`, `"None"`) as missing.
4. Converts `Delivery_Time`, `Agent_Rating`, and `Agent_Age` to numeric types.
5. Drops rows missing the target (`Delivery_Time`) or key categorical columns.
6. Fills missing numeric values with the median.
7. Filters out non-positive delivery times.
8. Creates derived fields: `Agent_Age_Group` (age buckets), `Month` (from `Order_Date`), and `Is_Late` (late delivery flag).

## 📁 Project Structure

```
Last_Mile_Delivery_Analytics/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── Last mile Delivery Data.csv  # (Optional) Primary dataset
```

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## 📄 License

This project does not currently include a license file. Please contact the repository owner for licensing information.

## 🙏 Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Visualizations powered by [Plotly](https://plotly.com/python/)
- Data analysis with [Pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/)

---

**LogiSight Analytics** — turning last-mile delivery data into actionable operational intelligence.
