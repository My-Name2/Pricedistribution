import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

st.title("Daily Price Distribution with Z-Scores")

# User Inputs
tickers_input = st.text_input("Enter tickers (comma-separated):", "AAPL, MSFT")
num_days = st.number_input("Enter the number of days", min_value=30, max_value=2000, value=252)

# Process tickers
tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

if st.button("Analyze"):
    results = []

    for ticker in tickers:
        df = yf.download(ticker, period=f"{num_days}d", interval="1d")

        if df.empty:
            st.warning(f"No data available for {ticker}")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        price_column = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        price_values = df[price_column].dropna().values

        if len(price_values) < 2:
            st.warning(f"{ticker} does not have enough data.")
            continue

        today_price = price_values[-1]
        mean_price = price_values.mean()
        std_price = price_values.std()
        z_score_price = (today_price - mean_price) / std_price if std_price != 0 else float("nan")
        percentile_rank_price = stats.percentileofscore(price_values, today_price)

        results.append((ticker, price_values, today_price, z_score_price, percentile_rank_price))

    # Sort tickers by Z-score
    results.sort(key=lambda x: x[3])

    # Plotting
    for ticker, price_values, today_price, z_score_price, percentile_rank_price in results:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(price_values, bins=30, kde=True, color='skyblue', ax=ax)
        plt.axvline(today_price, color='red', linestyle='--', linewidth=2)
        plt.title(f"{ticker} - Price Distribution")
        plt.xlabel("Price")
        plt.ylabel("Frequency")
        st.pyplot(plt)
        plt.clf()

        st.write(f"**{ticker} Statistics:**")
        st.write(f"- Today's Price: {today_price:.2f}")
        st.write(f"- Z-Score: {z_score_price:.2f}")
        st.write(f"- Percentile Rank: {percentile_rank_price:.2f}%")
