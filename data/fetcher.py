import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import streamlit as st  # <-- ADD THIS IMPORT

# FIX 1: Cache data for 5 minutes so users moving sliders don't spam Yahoo
@st.cache_data(ttl=300)
def fetch_options_chain(ticker: str):
    """
    Returns:
      spot_price  : float
      expiries    : list of date strings
      chain       : dict keyed by expiry → {calls: df, puts: df}
    """
    # FIX 2: Create a custom request session with a standard browser User-Agent
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Pass the session to the Ticker object
    stock = yf.Ticker(ticker, session=session)

    # FIX: fast_info can fail; add fallback to history
    try:
        # Note: yfinance attribute spelling is typically case-sensitive camelCase or snake_case 
        # based on version. If 'last_price' fails, 'lastPrice' is the alternative fallback.
        spot_price = stock.fast_info['last_price']
    except Exception:
        hist = stock.history(period="1d")
        if hist.empty:
            raise ValueError(f"Could not fetch price for {ticker}")
        spot_price = float(hist['Close'].iloc[-1])

    expiries = stock.options

    chain = {}
    # Fetching up to 6 expiries
    for exp in expiries[:6]:
        try:
            opt = stock.option_chain(exp)
            cols = ['strike', 'lastPrice', 'bid', 'ask', 'impliedVolatility', 'volume', 'openInterest']

            calls = opt.calls[cols].copy()
            puts  = opt.puts[cols].copy()

            # FIX: Clean IV — Yahoo sometimes returns 0 or astronomically high values
            for df in (calls, puts):
                df['impliedVolatility'] = df['impliedVolatility'].apply(
                    lambda iv: iv if (pd.notna(iv) and 0.001 < iv < 20.0) else float('nan')
                )

            chain[exp] = {'calls': calls, 'puts': puts}
        except Exception:
            # If one specific expiry fails, keep moving so the whole app doesn't crash
            continue

    return spot_price, list(expiries), chain


def time_to_expiry(expiry_str: str) -> float:
    """Returns T in years"""
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
    T = (expiry - datetime.now()).days / 365
    return max(T, 1/365)  # FIX: min 1 day to avoid T=0 in Greeks