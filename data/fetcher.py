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
    stock = Ticker(ticker_symbol)

    # 1. Fetch Spot Price safely
    try:
        price_data = stock.price[ticker_symbol]
        if isinstance(price_data, dict) and 'regularMarketPrice' in price_data:
            spot_price = float(price_data['regularMarketPrice'])
        else:
            raise ValueError
    except Exception:
        hist = stock.history(period="1d")
        if hist.empty:
            raise ValueError(f"Could not fetch price for {ticker_symbol}")
        spot_price = float(hist['close'].iloc[-1])

    # 2. Get Expiries and Option Chains safely
    try:
        opt_df = stock.option_chain

        # FIX: yahooquery can return a string error message instead of a DataFrame if blocked
        if not isinstance(opt_df, pd.DataFrame) or opt_df.empty:
            return spot_price, [], {}

        # Reset index to access multi-index columns safely
        opt_df = opt_df.reset_index()
        
        if 'expiration' not in opt_df.columns:
            return spot_price, [], {}
            
        expiries = sorted(opt_df['expiration'].astype(str).unique().tolist())

        chain = {}
        cols_mapping = ['strike', 'lastPrice', 'bid', 'ask', 'impliedVolatility', 'volume', 'openInterest']

        # Format up to 6 expiries
        for exp in expiries[:6]:
            exp_data = opt_df[opt_df['expiration'].astype(str) == exp]
            
            calls_raw = exp_data[exp_data['optionType'] == 'calls']
            puts_raw = exp_data[exp_data['optionType'] == 'puts']

            # Double-check that columns exist before copying
            existing_cols = [c for c in cols_mapping if c in exp_data.columns]
            
            calls = calls_raw[existing_cols].copy()
            puts = puts_raw[existing_cols].copy()

            # Clean Volatility outliers
            if 'impliedVolatility' in existing_cols:
                for df in (calls, puts):
                    df['impliedVolatility'] = df['impliedVolatility'].apply(
                        lambda iv: iv if (pd.notna(iv) and 0.001 < iv < 20.0) else float('nan')
                    )

            chain[exp] = {'calls': calls, 'puts': puts}

        return spot_price, expiries, chain

    except Exception as e:
        # Graceful handling so app components don't experience TypeError cascades
        return spot_price, [], {}

def time_to_expiry(expiry_str: str) -> float:
    """Returns T in years"""
    try:
        expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
        T = (expiry - datetime.now()).days / 365
        return max(T, 1/365)  # Avoid T=0 to prevent division by zero in Greeks
    except Exception:
        return 1/365