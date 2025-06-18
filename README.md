# Factor Buckets – A K-Means Clustering Approach to Stock Styles  
<sup>“From Fundamentals to Factor Buckets: bridging data overload with narrative-friendly stock lists.”</sup>

[Read the full Medium article](https://medium.com/@your-handle/from-fundamentals-to-factor-buckets-a-clustering-approach-to-stock-styles-for-investors-498c5de72504)

---

## 📌 TL;DR

Most screeners drown investors in ratios; this repo shows how to let the **data
shape itself into the stories investors already use** (“Undervalued”, “High
Growth”, “Prime Quality”).  
A lightweight, sector-neutral K-Means pipeline turns 21 fundamentals for every
S&P 500 stock into five factor buckets and a handful of intuitive style tiers,
followed by a 7-week forward sanity test.

---

## ✅ What’s working today

| Module | Status | Notes |
|--------|--------|-------|
| **Data pull** | **Done** | 21 fundamentals + daily OHLC via *yfinance* → PostgreSQL (**scripts/get_data.py**) |
| **Cleaning** | **Done** | sector-median impute · Yeo-Johnson transform · sector-neutral robust scaling · winsorise ±5 z |
| **Feature screen** | **Done** | Spread-Ratio > 4 % filter |
| **Clustering** | **Done** | Separate K-Means per factor; *k* chosen by Elbow + Silhouette + DB + bootstrap ARI |
| **Cluster labels** | **Done** | Clear names (Undervalued, High Growth, etc.) |
| **Mini-portfolio smoke test** | **Done** | Value-Seeker · Growth-Chaser · Composite blend |
| **Medium write-up** | **Part 1 published** | Link above |

---

## 🚧 Work in progress

* **Robust data sources** – investigating *Financial Modeling Prep*, *SecAPI*, and point-in-time fundamentals to reduce survivorship bias.  
* **Multi-year back-test** – rolling Window + sector-neutral returns, transaction-cost model.  
* **Streamlit front-end** – interactive screener (“Show me cheap stocks with steady margins”).  
* **LLM query layer** – translate plain English prompts into saved filters.  
* **Ranking engine** – within-bucket scoring by z-score distance to centroid.  
* **Part 2 Medium article** – deep dive on back-testing and the UI demo.

Feel free to open issues or PRs if you’d like to help on any of these items.

---

## 🔧 Quick start

```bash
git clone https://github.com/your-handle/factor-buckets.git
cd factor-buckets

# 1) install environment
conda env create -f environment.yml    # or: pip install -r requirements.txt
conda activate factorbuckets

# 2) pull fresh data (skips if already present)
python scripts/get_data.py             # saves parquet files to /data/

# 3) walk through the pipeline
jupyter lab notebooks/01_pipeline.ipynb
