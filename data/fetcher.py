import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_options_chain(ticker: str):
    """
    Returns:
      spot_price  : float
      expiries    : list of date strings
      chain       : dict keyed by expiry → {calls: df, puts: df}
    """
    stock = yf.Ticker(ticker)

    # FIX: fast_info can fail; add fallback to history
    try:
        spot_price = stock.fast_info['last_price']
    except Exception:
        hist = stock.history(period="1d")
        if hist.empty:
            raise ValueError(f"Could not fetch price for {ticker}")
        spot_price = float(hist['Close'].iloc[-1])

    expiries = stock.options

    chain = {}
    for exp in expiries[:6]:
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

    return spot_price, list(expiries), chain


def time_to_expiry(expiry_str: str) -> float:
    """Returns T in years"""
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
    T = (expiry - datetime.now()).days / 365
    return max(T, 1/365)  # FIX: min 1 day to avoid T=0 in Greeks