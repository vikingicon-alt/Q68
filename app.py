import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- CONFIG ---
st.set_page_config(page_title="SENTINEL AI - PRO", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        font-weight: bold; font-size: 18px;
    }
    .buy-btn { background-color: #00ff88 !important; color: black !important; box-shadow: 0 0 20px #00ff88; border: none; }
    .sell-btn { background-color: #ff4b4b !important; color: white !important; box-shadow: 0 0 20px #ff4b4b; border: none; }
    .hold-btn { background-color: #ffaa00 !important; color: black !important; box-shadow: 0 0 20px #ffaa00; border: none; }
    .q68-footer {
        position: fixed; bottom: 15px; left: 50%; transform: translateX(-50%);
        color: #ffffff; font-weight: 900; font-size: 24px; opacity: 0.8;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎮 CONTROL PANEL")
    asset = st.selectbox("ASSET:", ["BITCOIN (BTC)", "ETHEREUM (ETH)", "GOLD (PAXG)"])
    tf = st.select_slider("TIMEFRAME:", options=["15m", "30m", "1h", "4h", "1D", "1W", "1M"], value="30m")
    st.divider()
    st.write("📲 **SCAN APP:**")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://A1-PROJECT-APP", width=150)

# --- DYNAMIC TITLE ---
asset_name = asset.split(" ")[0]
st.title(f"🚀 {asset_name} - TREND PREDICTION")

# --- DATA SIMULATION ---
data = pd.DataFrame({
    'Open': [10, 12, 11, 14, 13] * 10,
    'High': [15, 16, 14, 18, 17] * 10,
    'Low': [8, 9, 10, 11, 12] * 10,
    'Close': [12, 11, 14, 13, 16] * 10,
    'Volume': [100, 200, 150, 300, 250] * 10,
    'RSI': [40, 55, 60, 45, 75] * 10
})

# --- CHARTS ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close']), row=1, col=1)
vol_colors = ['#ff4b4b' if data['Open'][i] > data['Close'][i] else '#00ff88' for i in range(len(data))]
fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=vol_colors), row=2, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], fill='tozeroy', line=dict(color='#00d1ff'), fillcolor='rgba(0, 209, 255, 0.15)'), row=3, col=1)
fig.update_layout(height=650, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# --- SIGNALS ---
st.markdown("### 🎯 STRATEGIC SIGNALS")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<button class="stButton buy-btn">🔥 BUY NOW</button>', unsafe_allow_html=True)
with c2:
    st.markdown('<button class="stButton hold-btn">⏳ HOLD</button>', unsafe_allow_html=True)
with c3:
  st.markdown('<button class="stButton sell-btn">❄️ SELL NOW</button>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown('<div class="q68-footer">Q68</div>', unsafe_allow_html=True)
  
