import numpy as np
from scipy.stats import norm

def bsm_prices(S,K,T,r,sigma,option_type='call'):
    """
    Note 
    S : current price, K : Strike Price, T : Time to expiry in years days/365
    r : Risk Free rate usually in india is 0.065 and forusa is 0.05 
    sigma: Implied Volatility indecimal """
    if T <=0:
        #AT EXPIRY
        if option_type == 'call':
                return max(S-K,0)
        return max(K-S,0)
    d1 = (np.log(S/K) + (r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)

    if option_type =='call':
         price = S *norm.cdf(d1)-K*np.exp(-r*T)*norm.cdf(d2)
    else:
         price = K *np.exp(-r*T)*norm.cdf(-d2) - S *norm.cdf(-d1)
    return price


def compute_greeks(S,K,T,r,sigma,option_type = 'call'):
     """ CALCULATE and Return ALL 5 GREEKS"""
     if T<=0:
          return {g: 0.0 for g in ['delta','gamma','vega','theta','rho']}
     d1=(np.log(S/K))+(r+0.5*sigma**2)*T/ (sigma* np.sqrt(T))
     d2 = d1-sigma*np.sqrt(T)

     #Delta
     if option_type == 'call':
          delta = norm.cdf(d1)
     else:
          delta = norm.cdf(d1)-1
     #gamma 
     gamma = norm.pdf(d1) / (S*sigma * np.sqrt(T))
     # Theta (per calendar day)
     theta_base = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
     if option_type == 'call':
        theta = (theta_base - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
     else:
        theta = (theta_base + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365

     # Vega (per 1% move in IV)
     vega = S * norm.pdf(d1) * np.sqrt(T) / 100

     # Rho (per 1% move in rate)
     if option_type == 'call':
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
     else:
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
     return {
        'delta': round(delta, 4),
        'gamma': round(gamma, 4),
        'theta': round(theta, 4),
        'vega':  round(vega, 4),
        'rho':   round(rho, 4)
    }

