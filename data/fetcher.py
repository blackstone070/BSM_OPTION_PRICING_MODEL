import pandas as pd
from datetime import datetime
from yahooquery import Ticker
import streamlit as st

@st.cache_data(ttl=300)
def fetch_options_chain(ticker_symbol: str):
    """
    Returns:
      spot_price  : float
      expiries    : list of date strings
      chain       : dict keyed by expiry → {calls: df, puts: df}
    """
    # Initialize the Ticker object using yahooquery
    # It automatically handles cookies, crumbs, and browser headers
    stock = Ticker(ticker_symbol)

    # 1. Fetch Spot Price cleanly
    try:
        # returns a nested dict: { 'AAPL': { 'regularMarketPrice': 175.5 } }
        price_data = stock.price[ticker_symbol]
        if isinstance(price_data, dict) and 'regularMarketPrice' in price_data:
            spot_price = float(price_data['regularMarketPrice'])
        else:
            raise ValueError
    except Exception:
        # Fallback to history summary if pricing dict is blocked
        hist = stock.history(period="1d")
        if hist.empty:
            raise ValueError(f"Could not fetch price for {ticker_symbol}")
        spot_price = float(hist['close'].iloc[-1])

    # 2. Get Expiries and Option Chains
    try:
        # yahooquery downloads ALL option chains for all expiries in one single fast API call!
        # This completely avoids running a loop that spams requests
        opt_df = stock.option_chain

        if opt_df is None or opt_df.empty:
            return spot_price, [], {}

        # yahooquery returns a multi-indexed DataFrame where level 0 is 'expiration'
        # Reset index to access 'expiration' and 'optionType' as normal columns
        opt_df = opt_df.reset_index()
        
        # Extract unique expiry strings and convert them to standard formats if needed
        expiries = sorted(opt_df['expiration'].astype(str).unique().tolist())

        chain = {}
        cols_mapping = {
            'strike': 'strike',
            'lastPrice': 'lastPrice',
            'bid': 'bid',
            'ask': 'ask',
            'impliedVolatility': 'impliedVolatility',
            'volume': 'volume',
            'openInterest': 'openInterest'
        }

        # Format up to 6 expiries to match your original structure
        for exp in expiries[:6]:
            # Filter the single master dataframe instead of hitting the network repeatedly!
            exp_data = opt_df[opt_df['expiration'].astype(str) == exp]
            
            calls_raw = exp_data[exp_data['optionType'] == 'calls']
            puts_raw = exp_data[exp_data['optionType'] == 'puts']

            # Keep only your required columns
            calls = calls_raw[list(cols_mapping.keys())].copy()
            puts = puts_raw[list(cols_mapping.keys())].copy()

            # Clean Volatility outliers
            for df in (calls, puts):
                df['impliedVolatility'] = df['impliedVolatility'].apply(
                    lambda iv: iv if (pd.notna(iv) and 0.001 < iv < 20.0) else float('nan')
                )

            chain[exp] = {'calls': calls, 'puts': puts}

        return spot_price, expiries, chain

    except Exception as e:
        st.error(f"Error structuring options data: {e}")
        return spot_price, [], {}


def time_to_expiry(expiry_str: str) -> float:
    """Returns T in years"""
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
    T = (expiry - datetime.now()).days / 365
    return max(T, 1/365)