import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- CẤU HÌNH GIAO DIỆN BINANCE PRO ---
st.set_page_config(page_title="Q68 Premier Terminal", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .nav-btn {
        flex: 1; height: 50px; border-radius: 4px; display: flex; 
        align-items: center; justify-content: center; font-weight: 700;
        background: #2b3139; color: #848e9c; font-size: 16px; border: 1px solid #474d57;
    }
    .active-buy { background: #02c076 !important; color: white !important; }
    .active-sell { background: #cf304a !important; color: white !important; }
    .active-hold { background: #f0b90b !important; color: black !important; }
    .price-large { font-size: 52px; font-weight: 700; color: #02c076; line-height: 1; }
    .price-red { color: #cf304a !important; }
    .qr-box { background: white; padding: 10px; border-radius: 8px; text-align: center; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: HỆ THỐNG ĐIỀU KHIỂN & QR ---
with st.sidebar:
    st.markdown("## ⚙️ BẢNG ĐIỀU KHIỂN")
    lang = st.radio("Ngôn ngữ", ["Tiếng Việt", "English"], horizontal=True)
    t = {
        "Tiếng Việt": ["Tài sản", "Khung giờ", "Chỉ báo", "Thanh toán QR"],
        "English": ["Asset", "Timeframe", "Indicators", "QR Payment"]
    }[lang]
    
    asset_key = st.selectbox(t[0], ["BTC", "ETH", "PAXG", "SOL", "BNB"])
    tf = st.selectbox(t[1], ["15m", "1h", "4h", "1d"], index=1)
    
    st.divider()
    show_ema = st.toggle("EMA 25/99", value=True)
    show_vol = st.toggle("Volume", value=True)
    show_macd = st.toggle("MACD", value=True)
    show_rsi = st.toggle("RSI (30-70)", value=True)

    st.divider()
    st.markdown(f"### 💳 {t[3]}")
    # CHỖ ĐỂ MÃ QR CỦA ANH
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=ProjectA1_Payment", caption="Scan to Pay / Donate")

# --- XỬ LÝ DỮ LIỆU ---
@st.cache_data(ttl=10)
def get_pro_data(symbol, interval):
    mapping = {"BTC": "BTC-USD", "ETH": "ETH-USD", "PAXG": "PAXG-USD", "SOL": "SOL-USD", "BNB": "BNB-USD"}
    df = yf.download(mapping[symbol], period="5d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    # Indicators
    df['EMA25'] = df['Close'].ewm(span=25).mean()
    df['EMA99'] = df['Close'].ewm(span=99).mean()
    exp1 = df['Close'].ewm(span=12).mean(); exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2; df['Sig'] = df['MACD'].ewm(span=9).mean()
    # RSI 14 chuẩn
    delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))
    return df
    df = get_pro_data(asset_key, tf)
last = df.iloc[-1]
prev = df.iloc[-2]

# Logic AI
signal = "HOLD"
if last['Close'] > last['EMA25'] and last['MACD'] > last['Sig']: signal = "BUY"
elif last['Close'] < last['EMA25'] or last['MACD'] < last['Sig']: signal = "SELL"

# --- UI CHÍNH ---
p_color = "price-red" if last['Close'] < prev['Close'] else ""
st.markdown(f'<div style="color:#848e9c">{asset_key} / USDT • {tf}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="price-large {p_color}">${last["Close"]:,.2f}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="display: flex; gap: 8px; margin: 15px 0;">
    <div class="nav-btn {'active-buy' if signal == 'BUY' else ''}">BUY</div>
    <div class="nav-btn {'active-hold' if signal == 'HOLD' else ''}">HOLD</div>
    <div class="nav-btn {'active-sell' if signal == 'SELL' else ''}">SELL</div>
</div>
""", unsafe_allow_html=True)

# --- BIỂU ĐỒ NÂNG CẤP ĐA TẦNG ---
h_ratios = [0.5, 0.1, 0.2, 0.2] # Nến, Vol, MACD, RSI
fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=h_ratios)
t_col = 'Date' if 'Date' in df.columns else 'Datetime'

# 1. Candlestick
fig.add_trace(go.Candlestick(x=df[t_col], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                             increasing_line_color='#02c076', decreasing_line_color='#cf304a'), row=1, col=1)
if show_ema:
    fig.add_trace(go.Scatter(x=df[t_col], y=df['EMA25'], line=dict(color='#f0b90b', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df[t_col], y=df['EMA99'], line=dict(color='#e841de', width=1)), row=1, col=1)

# 2. Volume
if show_vol:
    colors = ['#02c076' if df['Open'].iloc[i] < df['Close'].iloc[i] else '#cf304a' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df[t_col], y=df['Volume'], marker_color=colors, opacity=0.4), row=2, col=1)

# 3. MACD
if show_macd:
    fig.add_trace(go.Bar(x=df[t_col], y=df['MACD']-df['Sig'], marker_color='#474d57'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df[t_col], y=df['MACD'], line=dict(color='#2962FF', width=1.5)), row=3, col=1)

# 4. RSI CỰC NÉT (CÓ BIÊN 30-70)
if show_rsi:
    fig.add_trace(go.Scatter(x=df[t_col], y=df['RSI'], line=dict(color='#ffffff', width=2)), row=4, col=1)
    # Thêm đường biên 30 và 70
    fig.add_hline(y=70, line_dash="dash", line_color="#cf304a", line_width=1, row=4, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#02c076", line_width=1, row=4, col=1)
    fig.update_yaxes(range=[0, 100], row=4, col=1)

fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
fig.update_yaxes(side="right", gridcolor="#1e2329")
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
