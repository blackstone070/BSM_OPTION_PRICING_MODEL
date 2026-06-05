import streamlit as st
import pandas as pd
from data.fetcher import fetch_options_chain, time_to_expiry
from bsm.pricer import bsm_price, compute_greeks
from bsm.iv_solver import implied_volatility
from charts.visualisations import payoff_diagram, volatility_skew, iv_surface

st.set_page_config(page_title="BSM Options Pricer", layout="wide", page_icon="📈")
st.title("📈 BSM Options Pricer & Greeks Dashboard")

# ── Sidebar inputs ──────────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    ticker   = st.text_input("Ticker", value="AAPL").upper()
    r        = st.slider("Risk-Free Rate (%)", 1.0, 10.0, 5.0) / 100
    load_btn = st.button("Load Options Chain", type="primary")

if load_btn or 'chain' not in st.session_state:
    with st.spinner(f"Fetching {ticker} options chain..."):
        try:
            spot, expiries, chain = fetch_options_chain(ticker)
            st.session_state.update(
                {'spot': spot, 'expiries': expiries, 'chain': chain, 'ticker': ticker}
            )
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
            st.stop()

spot     = st.session_state['spot']
expiries = st.session_state['expiries']
chain    = st.session_state['chain']

st.metric("Spot Price", f"${spot:.2f}")

# ── Expiry + Strike selector ─────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    # Safely handle empty expiry arrays
    expiry = st.selectbox("Expiry", expiries[:6] if expiries else ["No options to select"])
with col2:
    opt_type = st.selectbox("Option Type", ["call", "put"])
with col3:
    position = st.selectbox("Position", ["long", "short"])

# ── Protected Analytics Block ────────────────────────────
if expiries and expiry != "No options to select" and chain:
    T = time_to_expiry(expiry)
    
    calls_df = chain[expiry]['calls']
    puts_df  = chain[expiry]['puts']
    df       = calls_df if opt_type == 'call' else puts_df
    
    # 1. Robust ATM strike selection
    strikes_list = df['strike'].tolist()
    atm_strike   = min(strikes_list, key=lambda x: abs(x - spot))

    strike = st.select_slider(
        "Strike", options=strikes_list,
        value=atm_strike
    )

    # 2. Better mid-price fallback chain
    row = df[df['strike'] == strike].iloc[0]
    bid, ask, last = row['bid'], row['ask'], row['lastPrice']
    if bid > 0 and ask > 0:
        mid_price = (bid + ask) / 2
    elif last > 0:
        mid_price = last
    else:
        mid_price = 0.01

    # 3. IV Fallbacks & Solvers
    market_iv = row['impliedVolatility']
    iv_source  = "Market IV"

    if pd.isna(market_iv) or market_iv <= 0.001:
        solved_iv = implied_volatility(mid_price, spot, strike, T, r, opt_type)
        if solved_iv and solved_iv > 0:
            market_iv = solved_iv
            iv_source  = "Solved IV"
        else:
            market_iv = 0.25
            iv_source  = "Default IV (25%)"

    bsm_val = bsm_price(spot, strike, T, r, market_iv, opt_type)
    greeks   = compute_greeks(spot, strike, T, r, market_iv, opt_type)

    # 4. Display Greeks Metrics
    st.subheader("Greeks")
    st.caption(f"Implied Volatility: **{market_iv*100:.2f}%** ({iv_source})  |  "
               f"T = {T*365:.0f} days  |  Strike: {strike}  |  Spot: {spot:.2f}")

    g1, g2, g3, g4, g5, g6 = st.columns(6)
    g1.metric("BSM Price",  f"${bsm_val:.2f}", delta=f"Mkt: ${mid_price:.2f}")
    g2.metric("Delta  Δ",   f"{greeks['delta']:.4f}")
    g3.metric("Gamma  Γ",   f"{greeks['gamma']:.4f}")
    g4.metric("Theta  Θ",   f"{greeks['theta']:.4f}")
    g5.metric("Vega   ν",   f"{greeks['vega']:.4f}")
    g6.metric("Rho    ρ",   f"{greeks['rho']:.4f}")

    # Moneyness Warns
    moneyness = spot / strike if opt_type == 'call' else strike / spot
    if moneyness > 1.15:
        st.info(" Deep ITM: Delta ≈ 1, Gamma/Vega ≈ 0 is mathematically correct here.")
    elif moneyness < 0.85:
        st.info(" Deep OTM: Delta ≈ 0, Gamma/Vega ≈ 0 is mathematically correct here.")

    # 5. Render Plotly Charts
    tab1, tab2, tab3 = st.tabs(["P&L Payoff", "Volatility Skew", "IV Surface"])

    with tab1:
        st.plotly_chart(
            payoff_diagram(spot, strike, mid_price, opt_type, position),
            use_container_width=True
        )

    with tab2:
        skew_df = calls_df if opt_type == 'call' else puts_df
        skew_df = skew_df[skew_df['impliedVolatility'] > 0.001].dropna(subset=['impliedVolatility'])
        if len(skew_df) > 1:
            st.plotly_chart(
                volatility_skew(
                    skew_df['strike'].tolist(),
                    skew_df['impliedVolatility'].tolist(),
                    expiry, spot
                ),
                use_container_width=True
            )
        else:
            st.warning("Not enough valid IV data for skew chart on this expiry.")

    with tab3:
        st.plotly_chart(iv_surface(chain, spot), use_container_width=True)

else:
    st.warning("Please wait for options chain data to load fully or try another ticker.")