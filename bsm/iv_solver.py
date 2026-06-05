from scipy.optimize import brentq
from .pricer import bsm_price

def implied_volatility(market_price, S, K, T, r, option_type='call'):
    """
    Solves for IV using Brent's method.
    Returns IV as decimal (0.25 = 25%) or None if no solution.
    """
    if T <= 0 or market_price <= 0:
        return None

    intrinsic = max(S - K, 0) if option_type == 'call' else max(K - S, 0)
    if market_price < intrinsic:
        return None

    try:
        iv = brentq(
            lambda sigma: bsm_price(S, K, T, r, sigma, option_type) - market_price,
            a=1e-6,   # Lower bound: near 0% IV
            b=10.0,   # Upper bound: 1000% IV
            xtol=1e-6,
            maxiter=500
        )
        return round(iv, 4)
    except (ValueError, RuntimeError):
        return None