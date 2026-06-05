import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_options_chain(ticker:str):
    """
    Return 
    spot_price: float
    expiry_dates: list of str
    chain: dict key by expiry->{calls:df, puts:df}
    """
    stock =yf.download(ticker)
    spot_price=stock.fast_info['last_price']
    expiries=stock.options

    chain={}
    for exp in expiries[:6]: #fetch last 6 expiries:
        opt=stock.option_chain(exp)
        chain[exp]={
            'calls': opt.calls[['strike','lastPrice','bid','ask','impliedVolatility','volume','openInterest']],
            'puts': opt.puts[['strike','lastPrice','bid','ask','impliedVolatility','volume','openInterest']]
        }
    return spot_price, list(expiries), chain

def time_to_expiry(expiry_str: str)->float:
    expiry=datetime.strptime(expiry_str, "%Y-%m-%d")
    T=(expiry-datetime.now()).days/365
    return max(T,0)