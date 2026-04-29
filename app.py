import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- TỐI ƯU GIAO DIỆN CÂN ĐỐI ---
st.set_page_config(page_title="A1 Master", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .price-box { font-size: 45px; font-weight: 900; color: #02c076; margin: 0; padding: 0; }
    .price-red { color: #cf304a !important; }
    .status-btn {
        height: 40px; border-radius: 5px; display: flex; align-items: center; justify-content: center;
        font-weight: 800; background: #2b3139; color: #848e9c; font-size: 16px; border: 1px solid #474d57;
    }
    .buy-active { background: #02c076 !important; color: white !important; }
    .sell-active { background: #cf304a !important; color: white !important; }
    .hold-active { background: #f0b90b !important; color: black !important; }
</style>
""", unsafe_allow_html=True)

# --- THANH CHỈNH BÊN HÔNG GỌN GÀNG ---
with st.sidebar:
    st.markdown("### 🔐 QR LOGIN")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=A1_LOGIN", width=100)
    st.divider()
    asset = st.selectbox("Tài sản", ["BTC", "ETH", "PAXG", "LTC", "XRP", "BNB"], index=1)
    tf = st.selectbox("Khung giờ", ["15m", "1h", "4h", "1d"], index=1)
    st.divider()
    st.caption("🔴 EMA7 | 🟣 EMA99")

# --- LẤY DỮ LIỆU CHUẨN ---
@st.cache_data(ttl=10)
def get_data(symbol, interval):
    m = {"BTC":"BTC-USD", "ETH":"ETH-USD", "PAXG":"PAXG-USD", "LTC":"LTC-USD", "XRP":"XRP-USD", "BNB":"BNB-USD"}
    df = yf.download(m[symbol], period="5d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df['RED'] = df['Close'].ewm(span=7, adjust=False).mean()
    df['PURPLE'] = df['Close'].ewm(span=99, adjust=False).mean()
    e12 = df['Close'].ewm(span=12, adjust=False).mean(); e26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = e12 - e26; df['Sig'] = df['MACD'].ewm(span=9, adjust=False).mean()
    delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + g/l))
    return df

df = get_data(asset, tf)
last, prev = df.iloc[-1], df.iloc[-2]

# --- HIỂN THỊ GIÁ & NÚT ---
p_style = "price-red" if last['Close'] < prev['Close'] else ""
st.markdown(f'<p class="price-box {p_style}">${last["Close"]:,.2f}</p>', unsafe_allow_html=True)

sig = "HOLD"
if last['Close'] > last['PURPLE'] and last['MACD'] > last['Sig']: sig = "BUY"
elif last['Close'] < last['PURPLE']: sig = "SELL"

c1, c2, c3, c4 = st.columns([1,1,1,4])
with c1: st.markdown(f'<div class="status-btn {"buy-active" if sig=="BUY" else ""}">BUY</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="status-btn {"hold-active" if sig=="HOLD" else ""}">HOLD</div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="status-btn {"sell-active" if sig=="SELL" else ""}">SELL</div>', unsafe_allow_html=True)

# --- BIỂU ĐỒ 3 TẦNG: NẾN, VOL, RSI (FIX CỘT GIÁ) ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.2, 0.2])
t_ax = 'Date' if 'Date' in df.columns else 'Datetime'

# Tầng 1: Nến + Đỏ + Tím
fig.add_trace(go.Candlestick(x=df[t_ax], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#02c076', decreasing_line_color='#cf304a'), row=1, col=1)
fig.add_trace(go.Scatter(x=df[t_ax], y=df['RED'], line=dict(color='#cf304a', width=2), name="RED"), row=1, col=1)
fig.add_trace(go.Scatter(x=df[t_ax], y=df['PURPLE'], line=dict(color='#9c27b0', width=3), name="PURPLE"), row=1, col=1)

# Tầng 2: Volume đậm
v_c = ['#02c076' if df['Open'].iloc[i] < df['Close'].iloc[i] else '#cf304a' for i in range(len(df))]
fig.add_trace(go.Bar(x=df[t_ax], y=df['Volume'], marker_color=v_c, opacity=1.0), row=2, col=1)

# Tầng 3: RSI hiện rõ
fig.add_trace(go.Scatter(x=df[t_ax], y=df['RSI'], line=dict(color='#ffffff', width=2)), row=3, col=1)
fig.add_hrect(y0=30, y1=70, fillcolor="#7b3af5", opacity=0.15, row=3, col=1)

# Fix cột giá bên phải & tỉ lệ iPad
fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=5, r=40, t=5, b=5), showlegend=False)
fig.update_yaxes(side="right", gridcolor="#1e2329")
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
