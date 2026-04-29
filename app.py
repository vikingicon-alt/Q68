import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- 1. CẤU HÌNH GIAO DIỆN CHUẨN TRADER (IPAD OPTIMIZED) ---
st.set_page_config(page_title="Q68 SYSTEM A9.0", layout="wide", page_icon="🐢")

# CSS để ép màu sắc nút và bố cục cực nét
st.markdown("""
    <style>
    .main { background-color: #080a0c; }
    .price-box { font-size: 48px; font-weight: 900; color: #ffffff; letter-spacing: -1px; }
    .status-btn {
        padding: 15px; border-radius: 12px; text-align: center;
        font-weight: 800; font-size: 20px; color: #444;
        background: #15191d; border: 1px solid #2d3439;
        transition: all 0.3s ease;
    }
    /* Hiệu ứng ĐÈN SÁNG khi có não phân tích */
    .buy-active { background: #00ff88 !important; color: #000 !important; box-shadow: 0 0 25px rgba(0, 255, 136, 0.5); border: none; }
    .sell-active { background: #ff4b4b !important; color: #fff !important; box-shadow: 0 0 25px rgba(255, 75, 75, 0.5); border: none; }
    .hold-active { background: #ffaa00 !important; color: #000 !important; box-shadow: 0 0 25px rgba(255, 170, 0, 0.5); border: none; }
    .sub-text { font-size: 11px; display: block; opacity: 0.8; font-weight: 400; }
    </style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ SIDEBAR ---
with st.sidebar:
    st.markdown("## 🐢 Q68 SYSTEM v9.0")
    lang = st.radio("Language", ["VN", "EN"], horizontal=True)
    t = {"VN": ["TÀI SẢN", "KHUNG GIỜ", "MUA", "CHỜ", "BÁN", "Tín hiệu"], 
         "EN": ["ASSET", "TF", "BUY", "HOLD", "SELL", "Signal"]}[lang]
    
    assets = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "PAXG": "PAXG-USD", "XRP": "XRP-USD", "LTC": "LTC-USD"}
    asset_key = st.selectbox(t[0], list(assets.keys()))
    tf = st.select_slider(t[1], options=["5m", "15m", "1h", "4h", "1D"], value="1h")
    st.divider()
    st.info("AI Model: Project A1 Activated")

# --- 3. BỘ NÃO TÍNH TOÁN (CORE AI) ---
@st.cache_data(ttl=15)
def get_clean_data(sym, interval):
    df = yf.download(assets[sym], period="5d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    # EMA20
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Sig'] = df['MACD'].ewm(span=9, adjust=False).mean()
    # RSI
    delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (g/l)))
    return df

df = get_clean_data(asset_key, tf)
last = df.iloc[-1]

# --- 4. GIAO DIỆN ĐIỀU KHIỂN (VỊ TRÍ VÀNG) ---
status = "HOLD"
if last['Close'] > last['EMA20'] and last['MACD'] > last['Sig']: status = "BUY"
    elif last['Close'] < last['EMA20'] or last['MACD'] < last['Sig']: status = "SELL"

c_p, c_b, c_h, c_s = st.columns([1.5, 1, 1, 1])

with c_p:
    st.markdown(f'<div class="price-box">${float(last["Close"]):,.2f}</div>', unsafe_allow_html=True)
    st.markdown(f"**{asset_key}** | {tf}")

# Hiển thị 3 nút với màu sắc "Có Não"
with c_b: 
    active = "buy-active" if status == "BUY" else ""
    st.markdown(f'<div class="status-btn {active}">{t[2]}<span class="sub-text">{t[5] if status=="BUY" else ""}</span></div>', unsafe_allow_html=True)
with c_h: 
    active = "hold-active" if status == "HOLD" else ""
    st.markdown(f'<div class="status-btn {active}">{t[3]}<span class="sub-text">Wait</span></div>', unsafe_allow_html=True)
with c_s: 
    active = "sell-active" if status == "SELL" else ""
    st.markdown(f'<div class="status-btn {active}">{t[4]}<span class="sub-text">{t[5] if status=="SELL" else ""}</span></div>', unsafe_allow_html=True)

# --- 5. BIỂU ĐỒ 3 TẦNG (NẾN + VOLUME + MACD) ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])

# Tầng 1: Nến & EMA
fig.add_trace(go.Candlestick(x=df.iloc[:,0], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['EMA20'], line=dict(color='#FFD700', width=2), name="EMA20"), row=1, col=1)

# Tầng 2: Volume
v_cols = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.iloc[:,0], y=df['Volume'], marker_color=v_cols, name="Volume"), row=2, col=1)

# Tầng 3: MACD & RSI
fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['MACD'], line=dict(color='#00d1ff'), name="MACD"), row=3, col=1)
fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['Sig'], line=dict(color='#ffaa00'), name="Signal"), row=3, col=1)
fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['RSI'], line=dict(color='#ffffff', width=1), name="RSI"), row=3, col=1)

fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False, margin=dict(l=5, r=5, t=10, b=10))
fig.update_yaxes(side="right")

st.plotly_chart(fig, use_container_width=True)
