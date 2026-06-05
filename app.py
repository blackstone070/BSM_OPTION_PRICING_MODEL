import streamlit as st
import pandas as pd
from data.fetcher import fetch_options_chain, time_to_expiry
from bsm.pricer import bsm_price, compute_greeks
from bsm.iv_solver import implied_volatility
from charts.visualisations import payoff_diagram, volatility_skew, iv_surface

st.set_page_config(page_title="BSM Options Pricer", layout="wide",
                   page_icon="📈")
st.title("📈 BSM Options Pricer & Greeks Dashboard")

# ── Sidebar inputs ──────────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    ticker    = st.text_input("Ticker", value="AAPL").upper()
    r         = st.slider("Risk-Free Rate (%)", 1.0, 10.0, 5.0) / 100
    load_btn  = st.button("Load Options Chain", type="primary")

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

spot    = st.session_state['spot']
expiries = st.session_state['expiries']
chain   = st.session_state['chain']

st.metric("Spot Price", f"${spot:.2f}")

# ── Expiry + Strike selector ─────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    expiry = st.selectbox("Expiry", expiries[:6])
with col2:
    opt_type = st.selectbox("Option Type", ["call", "put"])
with col3:
    position = st.selectbox("Position", ["long", "short"])

T = time_to_expiry(expiry)
calls_df = chain[expiry]['calls']
puts_df  = chain[expiry]['puts']
df       = calls_df if opt_type == 'call' else puts_df

atm_idx  = (df['strike'] - spot).abs().idxmin()
strike   = st.select_slider(
    "Strike", options=df['strike'].tolist(),
    value=df.loc[atm_idx, 'strike']
)

# ── BSM Price + Greeks ───────────────────────────────────
row        = df[df['strike'] == strike].iloc[0]
mid_price  = (row['bid'] + row['ask']) / 2 if row['bid'] > 0 else row['lastPrice']

# Use market IV if available, else solve for it
market_iv = row['impliedVolatility']
if pd.isna(market_iv) or market_iv <= 0:
    market_iv = implied_volatility(mid_price, spot, strike, T, r, opt_type) or 0.25

bsm_val = bsm_price(spot, strike, T, r, market_iv, opt_type)
greeks  = compute_greeks(spot, strike, T, r, market_iv, opt_type)

# ── Display Greeks ───────────────────────────────────────
st.subheader("Greeks")
g1, g2, g3, g4, g5, g6 = st.columns(6)
g1.metric("BSM Price",  f"${bsm_val:.2f}")
g2.metric("Delta  Δ",   greeks['delta'])
g3.metric("Gamma  Γ",   greeks['gamma'])
g4.metric("Theta  Θ",   greeks['theta'])
g5.metric("Vega   ν",   greeks['vega'])
g6.metric("Rho    ρ",   greeks['rho'])

# ── Charts ────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["P&L Payoff", "Volatility Skew", "IV Surface"])

with tab1:
    st.plotly_chart(
        payoff_diagram(spot, strike, mid_price, opt_type, position),
        use_container_width=True
    )

with tab2:
    skew_df = calls_df if opt_type == 'call' else puts_df
    skew_df = skew_df.dropna(subset=['impliedVolatility'])
    st.plotly_chart(
        volatility_skew(
            skew_df['strike'].tolist(),
            skew_df['impliedVolatility'].tolist(),
            expiry, spot
        ),
        use_container_width=True
    )

with tab3:
    st.plotly_chart(iv_surface(chain, spot), use_container_width=True)