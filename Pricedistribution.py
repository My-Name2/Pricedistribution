import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

st.title("Daily Price and Return Distribution with Z-Scores")

# User Inputs
tickers_input = st.text_input("Enter tickers (comma-separated):", "AAPL, MSFT")
timeframe_option = st.selectbox("Select timeframe", ["Custom Days", "1 Year", "2 Years", "3 Years", "5 Years", "10 Years", "Max"])

if timeframe_option == "Custom Days":
    num_days = st.number_input("Enter the number of days", min_value=30, max_value=5000, value=252)
else:
    timeframe_mapping = {
        "1 Year": "1y",
        "2 Years": "2y",
        "3 Years": "3y",
        "5 Years": "5y",
        "10 Years": "10y",
        "Max": "max"
    }
    period = timeframe_mapping[timeframe_option]

# Process tickers
tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

if st.button("Analyze"):
    results = []

    for ticker in tickers:
        if timeframe_option == "Custom Days":
            df = yf.download(ticker, period=f"{num_days}d", interval="1d")
        else:
            df = yf.download(ticker, period=period, interval="1d")

        if df.empty:
            st.warning(f"No data available for {ticker}")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        price_column = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        price_values = df[price_column].dropna().values
        returns = df[price_column].pct_change().dropna().values * 100

        if len(price_values) < 2:
            st.warning(f"{ticker} does not have enough data.")
            continue

        today_price = price_values[-1]
        mean_price = price_values.mean()
        std_price = price_values.std()
        z_score_price = (today_price - mean_price) / std_price if std_price != 0 else float("nan")
        percentile_rank_price = stats.percentileofscore(price_values, today_price)

        results.append((ticker, price_values, returns, today_price, z_score_price, percentile_rank_price))

    # Sort tickers by Z-score
    results.sort(key=lambda x: x[4])

    # Plotting
    for ticker, price_values, returns, today_price, z_score_price, percentile_rank_price in results:
        fig, axes = plt.subplots(1, 2, figsize=(18, 5))

        sns.histplot(price_values, bins=30, kde=True, color='skyblue', ax=axes[0])
        axes[0].axvline(today_price, color='red', linestyle='--', linewidth=2)
        axes[0].set_title(f"{ticker} - Price Distribution")
        axes[0].set_xlabel("Price")
        axes[0].set_ylabel("Frequency")

        sns.histplot(returns, bins=30, kde=True, color='orange', ax=axes[1])
        axes[1].axvline(returns[-1], color='red', linestyle='--', linewidth=2)
        axes[1].set_title(f"{ticker} - Return Distribution (%)")
        axes[1].set_xlabel("Daily Return (%)")
        axes[1].set_ylabel("Frequency")

        st.pyplot(fig)
        plt.clf()

        st.write(f"**{ticker} Statistics:**")
        st.write(f"- Today's Price: {today_price:.2f}")
        st.write(f"- Price Z-Score: {z_score_price:.2f}")
        st.write(f"- Price Percentile Rank: {percentile_rank_price:.2f}%")
