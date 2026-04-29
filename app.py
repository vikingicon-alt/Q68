import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- 1. GIAO DIỆN CHUẨN IPAD ---
st.set_page_config(page_title="Q68 SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    .main { background-color: #080a0c; }
    .price-box { font-size: 48px; font-weight: 900; color: #ffffff; line-height: 1; }
    .status-btn {
        padding: 15px; border-radius: 12px; text-align: center;
        font-weight: 800; font-size: 20px; color: #444;
        background: #15191d; border: 1px solid #2d3439;
    }
    .buy-active { background: #00ff88 !important; color: #000 !important; box-shadow: 0 0 20px #00ff8888; border: none; }
    .sell-active { background: #ff4b4b !important; color: #fff !important; box-shadow: 0 0 20px #ff4b4b88; border: none; }
    .hold-active { background: #ffaa00 !important; color: #000 !important; box-shadow: 0 0 20px #ffaa0088; border: none; }
    .sub-t { font-size: 11px; display: block; opacity: 0.8; font-weight: 400; color: inherit; }
</style>
""", unsafe_allow_html=True)

# --- 2. ĐIỀU KHIỂN SIDEBAR ---
with st.sidebar:
    st.markdown("## 🐢 Q68 SYSTEM v10")
    lang = st.radio("Ngôn ngữ", ["VN", "EN"], horizontal=True)
    t = {"VN": ["TÀI SẢN", "KHUNG GIỜ", "MUA", "CHỜ", "BÁN", "Tín hiệu"], 
         "EN": ["ASSET", "TF", "BUY", "HOLD", "SELL", "Signal"]}[lang]
    assets = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "PAXG": "PAXG-USD", "XRP": "XRP-USD", "LTC": "LTC-USD"}
    asset_key = st.selectbox(t[0], list(assets.keys()))
    tf = st.select_slider(t[1], options=["5m", "15m", "1h", "4h", "1D"], value="1h")

# --- 3. XỬ LÝ DỮ LIỆU & AI (EMA20, MACD, RSI) ---
@st.cache_data(ttl=15)
def get_data(sym, interval):
    d = yf.download(assets[sym], period="5d", interval=interval, progress=False)
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
    df = d.reset_index()
    df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()
    e1 = df['Close'].ewm(span=12, adjust=False).mean()
    e2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['M'] = e1 - e2
    df['S'] = df['M'].ewm(span=9, adjust=False).mean()
    dt = df['Close'].diff(); g = (dt.where(dt > 0, 0)).rolling(14).mean(); l = (-dt.where(dt < 0, 0)).rolling(14).mean()
    df['R'] = 100 - (100 / (1 + (g/l)))
    return df

df = get_data(asset_key, tf)
last = df.iloc[-1]

# --- 4. KHU VỰC TÍN HIỆU CÓ NÃO ---
# Logic phân tích AI Project A1
status = "HOLD"
if last['Close'] > last['EMA'] and last['M'] > last['S']:
    status = "BUY"
elif last['Close'] < last['EMA'] or last['M'] < last['S']:
    status = "SELL"

c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
with c1:
    st.markdown(f'<div class="price-box">${float(last["Close"]):,.2f}</div>', unsafe_allow_html=True)
    st.markdown(f"**{asset_key}** | {tf}")

with c2:
    act = "buy-active" if status == "BUY" else ""
    st.markdown(f'<div class="status-btn {act}">{t[2]}<span class="sub-t">{t[5] if status=="BUY" else ""}</span></div>', unsafe_allow_html=True)
with c3:
    act = "hold-active" if status == "HOLD" else ""
    st.markdown(f'<div class="status-btn {act}">{t[3]}<span class="sub-t">Wait</span></div>', unsafe_allow_html=True)
with c4:
    act = "sell-active" if status == "SELL" else ""
    st.markdown(f'<div class="status-btn {act}">{t[4]}<span class="sub-t">{t[5] if status=="SELL" else ""}</span></div>', unsafe_allow_html=True)

# --- 5. BIỂU ĐỒ 3 TẦNG: NẾN, VOLUME, MACD/RSI ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])

# Tầng 1: Nến & EMA
fig.add_trace(go.Candlestick(x=df.iloc[:,0], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['EMA'], line=dict(color='#FFD700', width=2)), row=1, col=1)

# Tầng 2: Volume cột Xanh/Đỏ
v_c = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.iloc[:,0], y=df['Volume'], marker_color=v_c), row=2, col=1)

# Tầng 3: MACD & RSI
fig.add_trace(go.Bar(x=df.iloc[:,0], y=df['M']-df['S'], marker_color='#333333'), row=3, col=1)
fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['M'], line=dict(color='#00d1ff')), row=3, col=1)
fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['R'], line=dict(color='#ffffff', width=1)), row=3, col=1)

fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False, margin=dict(l=5, r=5, t=10, b=10))
fig.update_yaxes(side="right")
st.plotly_chart(fig, use_container_width=True)
