import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

st.set_page_config(page_title="Q68 AI SYSTEM", layout="wide", page_icon="🐢")

# --- ĐỊNH NGHĨA NGÔN NGỮ ---
lang_data = {
    "VI": {"title": "TÀI SẢN", "tf": "KHUNG GIỜ", "vol": "MẪU VOLUME", "chart": "CHỈ BÁO", "buy": "MUA", "hold": "THEO DÕI", "sell": "BÁN"},
    "EN": {"title": "ASSET", "tf": "TIME FRAME", "vol": "VOLUME STYLE", "chart": "INDICATORS", "buy": "BUY", "hold": "HOLD", "sell": "SELL"}
}

# --- SIDEBAR ---
with st.sidebar:
    lang = st.selectbox("Language / Ngôn ngữ", ["VI", "EN"])
    t = lang_data[lang]
    st.markdown("# 🐢 Q68 SYSTEM")
    assets = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "PAXG": "PAXG-USD", "XRP": "XRP-USD", "LTC": "LTC-USD"}
    asset_key = st.selectbox(t["title"], list(assets.keys()))
    tf = st.select_slider(t["tf"], options=["5m", "15m", "1h", "4h", "1D"], value="1h")
    vol_s = st.radio(t["vol"], ["Mặc định", "Volume + MA20"])
    chart_s = st.multiselect(t["chart"], ["EMA20", "RSI", "MACD"], default=["EMA20"])

# --- XỬ LÝ DỮ LIỆU ---
@st.cache_data(ttl=60)
def get_data(sym, interval):
    df = yf.download(assets[sym], period="5d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    # Chỉ báo
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

df = get_data(asset_key, tf)
last_p = float(df['Close'].iloc[-1])

# --- GIAO DIỆN CHÍNH (VỊ TRÍ ĐẮC ĐỊA) ---
c_title, c_signals = st.columns([1, 2])
with c_title:
    st.markdown(f"## 🐢 {asset_key}")
    st.markdown(f"### ${last_p:,.2f}")

# Tính toán tín hiệu AI
l_c = df['Close'].iloc[-1]; l_e = df['EMA20'].iloc[-1]; l_m = df['MACD'].iloc[-1]; l_s = df['Signal'].iloc[-1]
status = "HOLD"
if l_c > l_e and l_m > l_s: status = "BUY"
elif l_c < l_e or l_m < l_s: status = "SELL"

with c_signals:
    cols = st.columns(3)
    cols[0].markdown(f'<div style="text-align:center; padding:10px; border-radius:10px; background:{"#00ff88" if status=="BUY" else "#1a1c1e"}"><b>{t["buy"]}</b></div>', unsafe_allow_html=True)
    cols[1].markdown(f'<div style="text-align:center; padding:10px; border-radius:10px; background:{"#ffaa00" if status=="HOLD" else "#1a1c1e"}"><b>{t["hold"]}</b></div>', unsafe_allow_html=True)
    cols[2].markdown(f'<div style="text-align:center; padding:10px; border-radius:10px; background:{"#ff4b4b" if status=="SELL" else "#1a1c1e"}"><b>{t["sell"]}</b></div>', unsafe_allow_html=True)

# --- BIỂU ĐỒ ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.25, 0.25], vertical_spacing=0.02)
fig.add_trace(go.Candlestick(x=df.iloc[:,0], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
if "EMA20" in chart_s: fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['EMA20'], line=dict(color='yellow')), row=1, col=1)
if "MACD" in chart_s:
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['MACD'], name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['Signal'], name='Signal'), row=3, col=1)

fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, use_container_width=True)
