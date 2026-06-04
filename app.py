import streamlit as st

st.set_page_config(
    page_title="BSM OPTION PRICER",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

with st.sidebar:
    st.header("Parameters")
    ticker = st.text_input("Ticker", value="APPL").upper()
    r = st.slider("Risk-Free Rate(%)", 1.0, 10.0, 5.0)
    load_btn = st.button("Load Option Chain", type="primary")

st.title("Black-Scholes-Merton Option Pricing Model")
st.write("Welcome ! This is a place holder for qunatative option dashbaord ")
st.info("In next step we implement BSM formula")