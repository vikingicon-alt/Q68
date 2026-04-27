import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. UI CONFIG ---
st.set_page_config(page_title="Q68 V27", layout="wide")

st.markdown("""
<style>
header, footer, #MainMenu {visibility: hidden !important;}
.main { background-color: #020617 !important; }
[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 2px solid #FFD700;
    min-width: 300px !important;
}
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #FFD700, #B8860B);
    color: black;
    font-weight: 900;
    border-radius: 12px;
    height: 50px;
}
.status-box {
    padding: 25px;
    background: #161b22;
    border: 3px solid #FFD700;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# --- 2. AUTH ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=150)
        lang = st.radio("LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        pwd = st.text_input("PASSWORD", type="password")

        if st.button("LOGIN"):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=10)
def fetch_data(symbol, interval):
    endpoints = [
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=200",
        f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=200",
        f"https://api2.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=200"
    ]

    for url in endpoints:
        try:
            res = requests.get(url, timeout=10).json()
            if isinstance(res, list):
                df = pd.DataFrame(res, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])

                df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)

                # FIX TIME INDEX
                df['T'] = pd.to_datetime(df['T'], unit='ms')
                df.set_index('T', inplace=True)

                # EMA
                df['EMA20'] = df['C'].ewm(span=20).mean()
                df['EMA50'] = df['C'].ewm(span=50).mean()

                # RSI chuẩn
                delta = df['C'].diff()
                gain = delta.clip(lower=0)
                loss = -delta.clip(upper=0)

                avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
                avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()

                rs = avg_gain / (avg_loss + 1e-10)
                df['RSI'] = 100 - (100 / (1 + rs))

                return df
        except:
            continue

    return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚡ Q68 MASTER")
    coin = st.selectbox("COIN", ["BTCUSDT","ETHUSDT","SOLUSDT","PAXGUSDT"])
    tf = st.selectbox("TIMEFRAME", ["15m","1h","4h","1d"])

    if st.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. LOAD DATA ---
df = fetch_data(coin, tf)

if df is not None:

    curr = df.iloc[-1]
    p = curr['C']
    r = curr['RSI']
    e20 = curr['EMA20']
    e50 = curr['EMA50']

    # --- SIGNAL ENGINE (CẢI TIẾN) ---
    if p > e20 > e50 and r < 60:
        msg, clr = "🚀 BUY", "#22c55e"
    elif p < e20 < e50 and r > 40:
        msg, clr = "🔻 SELL", "#ef4444"
    else:
        msg, clr = "⏳ WAIT", "#f59e0b"

    st.markdown(f"<div class='status-box'><h1 style='color:{clr}'>{msg}</h1></div>", unsafe_allow_html=True)

    # --- CHART ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7,0.3])

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['O'],
        high=df['H'],
        low=df['L'],
        close=df['C']
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50"))

    fig.add_trace(go.Bar(x=df.index, y=df['V'], name="Volume"), row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- METRICS ---
    c1,c2,c3 = st.columns(3)
    c1.metric("PRICE", f"${p:,.2f}")
    c2.metric("RSI", f"{r:.2f}")
    c3.metric("EMA20", f"{e20:,.2f}")

else:
    st.warning("⚠️ Kết nối lỗi - đang thử lại...")
    time.sleep(2)
    st.rerun()
