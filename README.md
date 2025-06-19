# Factor Buckets — A Sector-Neutral K-Means Pipeline for S&P 500 Stocks  
*Converting a flood of raw ratios into stock styles you can act on.*


[Read the full Medium article](https://medium.com/@rmmrinal.q/from-fundamentals-to-factor-buckets-a-k-means-clustering-approach-to-stock-styles-498c5de72504)

---

## 📌 TL;DR
This repo shows how to let the **data shape itself into the stories investors already use, turning metric overload into actionable stock lists** (“Undervalued”, “High
Growth”, “Prime Quality”).  
A lightweight, sector-neutral K-Means pipeline turns 21 fundamentals for every
S&P 500 stock into five factor buckets and a handful of intuitive style tiers,
followed by a 7-week forward sanity test.

---

## ✅ What’s working today 

| Module | Status | Notes |
|--------|--------|-------|
| **Data pull** | **Done** | 21 fundamentals + daily OHLC via *yfinance* → store in database PostGreSQL - Vercel|
| **Cleaning** | **Done** | sector-median impute · Yeo-Johnson transform · sector-neutral robust scaling · winsorise ±5 z |
| **Feature screen** | **Done** | Spread-Ratio > 4 % filter |
| **Clustering** | **Done** | Separate K-Means per factor; *k* chosen by Elbow + Silhouette + DB + bootstrap ARI |
| **Cluster labels** | **Done** | Clear names (Undervalued, High Growth, etc.) |
| **Mini-portfolio smoke test** | **Done** | Value-Seeker · Growth-Chaser · Composite blend |
| **Medium write-up** | **Part 1 published** | Link above |

---

## 🚧 Work in progress

* **Streamlit deployment** – interactive screener (“Show me cheap stocks with steady margins”) - linking code so they all wrok together
* * **LLM query layer** – translate plain English prompts into saved filters.  
* **Robust data sources** – investigating *Financial Modeling Prep*, *SecAPI*, and point-in-time fundamentals to reduce survivorship bias.  
* **Multi-year back-test** – rolling Window + sector-neutral returns, transaction-cost model.   
* **Ranking engine** – within-bucket scoring by z-score distance to centroid.  

Feel free to reach out.

---

