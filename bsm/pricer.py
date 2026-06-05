import numpy as np
from scipy.stats import norm

def bsm_price(S, K, T, r, sigma, option_type='call'):
    """
    S     = Current stock price
    K     = Strike price
    T     = Time to expiry in years
    r     = Risk-free rate (0.065 for India, 0.05 for US)
    sigma = Implied volatility as decimal (0.25 = 25%)
    """
    if T <= 0:
        return max(S - K, 0) if option_type == 'call' else max(K - S, 0)

    # FIX: Guard against sigma=0 causing division by zero
    sigma = max(sigma, 1e-6)

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return max(price, 0.0)


def compute_greeks(S, K, T, r, sigma, option_type='call'):
    """Returns all 5 Greeks as a dictionary"""
    if T <= 0:
        return {g: 0.0 for g in ['delta', 'gamma', 'theta', 'vega', 'rho']}

    # FIX: Guard against sigma=0
    sigma = max(sigma, 1e-6)

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Delta
    delta = norm.cdf(d1) if option_type == 'call' else norm.cdf(d1) - 1

    # Gamma — same for call and put; near 0 for deep ITM/OTM (correct math)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

    # Theta — per calendar day
    theta_base = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if option_type == 'call':
        theta = (theta_base - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        theta = (theta_base + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365

    # Vega — per 1% move in IV; near 0 for deep ITM/OTM (correct math)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100

    # Rho — per 1% move in rate
    if option_type == 'call':
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    return {
        'delta': round(delta, 4),
        'gamma': round(gamma, 4),
        'theta': round(theta, 4),
        'vega':  round(vega, 4),
        'rho':   round(rho, 4),
    }