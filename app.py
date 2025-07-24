import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
from pathlib import Path
import yfinance as yf
from dateutil.relativedelta import relativedelta
import numpy as np 
# ──────────────────────────────────────────────────────────────
# Constants to be used in the entire scripts
# ──────────────────────────────────────────────────────────────

TAG_BUCKETS = {
        "Value":                ["Undervalued", "Fair Value", "Overvalued"],
        "Growth":               ["High Growth", "Low Growth"],
        "Quality":              ["High Quality", "Average Quality", "Lower Quality"],
        "Defensive":            ["High Defense", "Average Defense", "Low Defense"],
        "Risk & Momentum":      ["Strong risk adjusted gains", "Average risk adjusted gains", "Poor risk adjusted gains"],
    }

COLUMN_MAP = {
        "Value": "Value",
        "Growth": "Growth",
        "Quality": "Quality",
        "Defensive": "Defensive",
        "Risk & Momentum": "Risk_Momentum",
    }

# ──────────────────────────────────────────────────────────────
# Data loading / caching
# ──────────────────────────────────────────────────────────────

@st.cache_data
def fetch_cluster_data():
    path = Path(__file__).resolve().parent / "artifacts" / "final_data"
    transformed = pd.read_parquet(path / "transformed_final_data.parquet")
    merged      = pd.read_parquet(path / "merged_final_data.parquet")
    return transformed, merged

@st.cache_data
def get_meta_data():
    path = Path(__file__).resolve().parent / "artifacts"
    return pd.read_csv(path / "metadata.csv")
@st.cache_data
def get_price_data(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    return yf.download(ticker, start=start_date, end=end_date)

# ──────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────

def price_chart(df: pd.DataFrame, ticker: str):
    if df is None or df.empty or "Close" not in df:
        st.warning("No valid price data to plot.")
        return
    fig = px.line(df, x=df.index, y=df["Close"].squeeze(),
                  title=f"{ticker} Stock Price")
    st.plotly_chart(fig, use_container_width=True)

def get_filtered_df(df : pd.DataFrame, selections : dict[str, list[str]]) -> pd.DataFrame:
    df = df.copy()
    mask = np.ones(len(merged_data), dtype=bool)
    for bucket, tags in selections.items():
        if tags:
            col = COLUMN_MAP[bucket]
            mask &= df[col].isin(tags)
    return df[mask]

# ──────────────────────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Smart Stock Explorer", layout="wide")
st.sidebar.title("🔍 Smart Stock Explorer")

mode = st.sidebar.radio("Mode", ["Stock Lookup", "Smart Search"])
transformed_data, merged_data = fetch_cluster_data()
meta_data = get_meta_data()

# ──────────────────────────────────────────────────────────────
# Stock Lookup mode (fixed)
# ──────────────────────────────────────────────────────────────

if mode == "Stock Lookup":
    st.header("🔎 Stock Lookup")
    st.sidebar.markdown(
        """
        ## Use Stock Lookup to view :
        - Historical price chart for any S&P 500 ticker  
        - Company profile (sector, industry, country, description)  
        - Key performance statistics (Sharpe, drawdown, return, volatility, beta)  
        - Factor‑driven clustering tags (Value, Growth, Quality, Defensive, Risk & Momentum).
        """
    )

    # Sidebar inputs
    ticker_input = st.sidebar.text_input("Ticker symbol", value="AAPL")
    ticker = ticker_input.upper().strip()
    start_date = st.sidebar.date_input("Start date", value=date(2020, 1, 1))
    end_date = st.sidebar.date_input("End date", value=date.today())
    fetch = st.sidebar.button("Get Price Data")

    # On fetch, load data into session
    if fetch and ticker:
        data = get_price_data(ticker, start_date, end_date)
        st.session_state.price_data = data
        st.session_state.ticker = ticker

    # Retrieve from session or empty
    df = st.session_state.get("price_data", pd.DataFrame())
    current_ticker = st.session_state.get("ticker", "")

    # Initial prompt
    if current_ticker == "":
        st.info("Use the sidebar to enter a ticker and dates, then click **Get Price Data**.")
    else:
        if df.empty:
            st.error("No data returned for that symbol.")
        else:
            price_chart(df, current_ticker)

            tabs = st.tabs(["About Company", "Price Data", "Stats", "Smart Tags"])
            about, price_tab, stats_tab, tags_tab = tabs

            with about:
                st.subheader("Company Profile")
                row = meta_data[meta_data["ticker"] == current_ticker]
                if row.empty:
                    st.warning("No metadata found.")
                else:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Sector",   row["sector"].iat[0])
                    c2.metric("Industry", row["industry"].iat[0])
                    c3.metric("Country",  row["country"].iat[0])
                    with st.expander("Business Summary"):
                        st.write(row["businesssummary"].iat[0])

            with price_tab:
                st.subheader("Historical Prices")
                st.dataframe(df, use_container_width=True)

            with stats_tab:
                st.subheader("Key Statistics (3‑year window)")
                stats = merged_data[merged_data["ticker"] == current_ticker]
                if stats.empty:
                    st.warning("No stats available.")
                else:
                    sr = stats["sharpe_ratio"].iat[0]
                    md = stats["max_drawdown"].iat[0]
                    bt = stats["beta"].iat[0]
                    vo = stats["volatility"].iat[0]
                    re = stats["annual_return"].iat[0]

                    r1, r2, r3 = st.columns(3)
                    r1.metric("Sharpe Ratio",      f"{sr:.2f}")
                    r2.metric("Max Drawdown",      f"{md:.2%}")
                    r3.metric("Annual Return",     f"{re:.2%}")

                    r4, r5, _ = st.columns(3)
                    r4.metric("Annual Volatility", f"{vo:.2%}")
                    r5.metric("Beta vs S&P 500",   f"{bt:.2f}")
                
                st.write("Note: Stats calculation is based on a 3-year window from 22 april 2022 till 22 april 2025"
                " Update comminng soon to get latest stats.")

            with tags_tab:
                st.subheader("Factor‑Driven Tags")
                tags = merged_data[merged_data["ticker"] == current_ticker]
                if tags.empty:
                    st.warning("No tags found.")
                else:
                    for col, emoji in [
                        ("Value","💰"),("Growth","🚀"),
                        ("Quality","🏭"),("Defensive","🛡️"),
                        ("Risk_Momentum","📈")
                    ]:
                        tag_val = tags[col].iat[0]
                        with st.expander(f"{emoji} {tag_val}"):
                            st.write("Explanation coming soon…")


# ──────────────────────────────────────────────────────────────
# Smart Search mode 
# ──────────────────────────────────────────────────────────────
else:  # Smart Search
    # Sidebar controls
    st.sidebar.header("🧠 Smart Search Controls")
    st.sidebar.info("🚧 Test phase: currently supports only S&P 500 data.")

    selections = {}
    for bucket , tag in TAG_BUCKETS.items():
        choose = st.sidebar.multiselect(bucket, tag, key=bucket)
        if choose:
            selections[bucket] = choose

    st.sidebar.subheader("Slider Settings")
    top_n = st.sidebar.slider("Select top N filtered stocks", min_value= 5, max_value= 50,value=10, step=1) 
    run_search    = st.sidebar.button("Run Search")
    show_glossary = st.sidebar.checkbox("Show Detailed Tag Glossary")

    # Main pane
    st.header("🧠 Smart Search")

    if show_glossary:
        # Glossary only
        st.subheader("Factor Spectra Explained")
        st.markdown("""
**Value (Valuation Spectrum)**  
Trailing P/E and Price-to-Sales ratios represent how expensive or cheap the stock is relative to sector peers.

**Growth (Business Momentum)**  
Revenue growth and ROA represent whether the company is expanding quickly and using assets efficiently.

**Quality (Operational Strength)**  
Profit margin and ROA represent how consistently and profitably the firm operates.

**Defensive (Balance-Sheet Resilience)**  
Current ratio and Debt-to-Equity show that companies with ample liquidity and low leverage are better positioned to weather economic downturns.

**Momentum & Risk (Trend Stability)**  
Three-year Sharpe ratio and maximum drawdown indicate whether the price rises steadily without harsh crashes.
""")
        st.markdown("---")
        st.subheader("All Tag Details")
        st.markdown("""
**Value Tags**  
- **Undervalued**: Low P/E & P/S vs sector peers — may be underpriced.  
- **Fair Value**: Trading near sector median — reasonably priced.  
- **Overvalued**: High P/E & P/S vs peers — possibly overhyped.

**Growth Tags**  
- **High Growth**: Strong revenue growth and high ROA.  
- **Low Growth**: Below‑median growth or weak ROA.

**Quality Tags**  
- **High Quality**: Robust profit margins and efficient asset use.  
- **Average Quality**: Profitability in line with peers.  
- **Lower Quality**: Thin margins or low ROA.

**Defensive Tags**  
- **High Defense**: High liquidity & low leverage — very resilient.  
- **Average Defense**: Sector‑average liquidity & debt.  
- **Low Defense**: Low liquidity or high leverage — riskier.

**Risk & Momentum Tags**  
- **Strong Risk‑Adjusted Gains**: High Sharpe & shallow drawdowns.  
- **Average Risk‑Adjusted Gains**: Moderate Sharpe & drawdowns.  
- **Poor Risk‑Adjusted Gains**: Low Sharpe & deep drawdowns.
""")
    else:
        # Initial description + search UI
        if not run_search:
            st.markdown("""
## Smart Search: Find the right stock in clicks

**What is Smart Search?**  
A fast and intuitive way to explore stocks based on **meaningful financial characteristics** like value, growth, and quality, while accounting for industry differences using **sector-neutral analysis**.  
**Sector‑neutral analysis** means the stock is compared only to its **sector peers**, so you get truly fair and meaningful insights among industries.

---

**How it works:**  
- First, we **sector‑neutralize** key metrics (like P/E, P/S, ROA, margins, volatility) so comparisons are **fair and peer-relative**.  
- Then we group stocks into **clusters** based on their profiles across five essential buckets:  
  - `Value`  
  - `Growth`  
  - `Quality`  
  - `Defensive Strength`  
  - `Risk & Momentum`  
- Finally, each stock is tagged with its most defining trait in each category, so you instantly know where it stands.

---

**What you can do with it:**  
- **Undervalued** → find stocks that are cheap relative to peers  
- **High Growth** → find companies expanding quickly with strong ROA  
- **High Quality** → find businesses with consistent, strong margins  
- **High Defense** → find firms with ample liquidity & low leverage  
- **Strong Risk‑Adjusted Gains** → find stocks with smooth, high Sharpe returns  

---

**Use the sidebar to select any tag and click _Run Search_**  
You’ll instantly see:  
- A **Top 10 list** ranked by distance to the cluster center
- The **complete list** of all matching stocks
            """)
        else:
            
            if len(selections) == 0:
                st.write("Please select at least one tag in the sidebar.")

            else:
                filtered_data = get_filtered_df(merged_data, selections)
                if filtered_data.shape[0] == 0:
                    st.write("No matching stocks found. Please try again with different tags.")
                else:
                    if len(selections) == 1:
                        only_bucket = next(iter(selections))
                        core_name    = COLUMN_MAP[only_bucket] 
                        distance_col = f"{core_name}_distance"
                        top_10 = filtered_data.sort_values(distance_col, ascending=True).head(top_n)
                    else:
                        top_10 = filtered_data.sort_values("sharpe_ratio", ascending=False).head(top_n)
                    
                    st.write(f"{filtered_data.shape[0]} matching stocks found.")    
                    end_date = datetime.now()
                    start_date = (end_date - relativedelta(years=5))

                    stock_list = top_10["ticker"].tolist() + ["SPY"]
                    price_raw = get_price_data(stock_list, start_date, end_date)['Close']
                    price_norm = price_raw.divide(price_raw.iloc[0])

                    # assume price_norm is a DataFrame whose columns are tickers, index is datetime
                    fig = px.line(price_norm, 
                            labels={'index':'Date', 'value':'Normalized Price'},
                            title=f"Normalized Price Chart")

                    # override just the SPX trace to white  
                    fig.update_traces(
                                selector=dict(name="SPY"),   
                                line=dict(color="white", width=2) 
                                    )

                    st.plotly_chart(fig, use_container_width=True)

                    port, s_data, data  = st.tabs(["Portfolio",f"Selected {top_n} stocks", "Full list of Filtered stocks"])
                    with port:
                        st.header("Portfolio: How the filtered stocks performed")
                        st.write(""" **Methodology**:
                                 
                                    **Benchmark**: S&P 500
                                    **Tagging date**: 22 April 2025
                                    **Ranking**: Stocks were ordered by their distance to the cluster centre.
                                    **Portfolio**: Top‑N names were given equal weights.
                                    **Status**: The performance is after the tagging is done and what will happen if you invest 10000 USD.
                                    """)

                        price_raw.index = pd.to_datetime(price_raw.index).tz_localize(None)
                        cutoff = "2025-04-22"
                        price_recent = price_raw.loc[cutoff:]  

                        #cutoff = pd.Timestamp("2025-04-22")      # HARD CODED -- AS THE ML ALGO RUNS ON 22 APRIL

                        #price_data = price_raw.loc[cutoff:]
                        invested_amount = 10000
                        rets = price_recent.pct_change().dropna()
                        tic = [x for x in rets.columns if x != "SPY"]
                        basket = rets[tic].mean(axis=1)
                        basket_cum = (basket + 1).cumprod().to_frame("Portfolio")
                        spy = (1+rets["SPY"]).cumprod().to_frame("SPY")
                        cum = pd.concat([basket_cum, spy], axis=1)

                        st.line_chart(cum*invested_amount)

                    with s_data:
                        st.header(f"Selected {top_n} stocks")
                        if len(selections) > 1:
                            st.write(top_10[['ticker','sector','sharpe_ratio', 'beta','market_cap','dividend_yield']])
                        else:
                            st.write(top_10[['ticker','sector','sharpe_ratio', 'beta','market_cap','dividend_yield',distance_col]])
                        
                        st.write('Below is the five year price data for the selected stocks')
                        st.write(price_raw)

                    with data:
                        st.header("Full List of Filtered Data")
                        if len(selections) > 1:
                            st.write(filtered_data[['ticker','sector','sharpe_ratio', 'beta','market_cap','dividend_yield']])
                        else:
                            st.write(filtered_data[['ticker','sector','sharpe_ratio', 'beta','market_cap',distance_col]])

