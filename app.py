import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- 1. THIẾT KẾ TERMINAL THƯƠNG MẠI ---
st.set_page_config(page_title="Project A1 - Global Terminal", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    /* Nút bấm hiệu ứng Pro */
    .btn-wrap { display: flex; gap: 10px; margin: 15px 0; }
    .status-node {
        flex: 1; height: 55px; border-radius: 6px; display: flex; 
        align-items: center; justify-content: center; font-weight: 800;
        background: #2b3139; color: #848e9c; font-size: 20px;
        border: 1px solid #474d57; transition: 0.3s;
    }
    .active-buy { background: #02c076 !important; color: white !important; box-shadow: 0 0 20px rgba(2,192,118,0.5); border: none; }
    .active-sell { background: #cf304a !important; color: white !important; box-shadow: 0 0 20px rgba(207,48,74,0.5); border: none; }
    .active-hold { background: #f0b90b !important; color: black !important; border: none; }
    
    /* Header Giá Luxury */
    .price-tag { font-size: 55px; font-weight: 800; color: #02c076; line-height: 1; letter-spacing: -1px; }
    .price-red { color: #cf304a !important; }
    
    /* Khung QR Luxury */
    .qr-container { background: white; padding: 15px; border-radius: 12px; margin-top: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG QUẢN TRỊ SIDEBAR ---
with st.sidebar:
    st.markdown("# 🌐 PROJECT A1")
    lang = st.radio("Language / Ngôn ngữ", ["English", "Tiếng Việt"], horizontal=True)
    t = {
        "English": ["Asset", "Interval", "Indicators", "QR Payment", "System Status: Online"],
        "Tiếng Việt": ["Tài sản", "Khung giờ", "Chỉ báo", "Thanh toán QR", "Hệ thống: Trực tuyến"]
    }[lang]
    
    st.success(t[4])
    st.divider()
    
    asset = st.selectbox(t[0], ["BTC", "ETH", "PAXG", "SOL", "BNB"])
    tf = st.selectbox(t[1], ["15m", "1h", "4h", "1d"], index=1)
    
    st.divider()
    show_ema = st.toggle("EMA 25/99", True)
    show_vol = st.toggle("Volume", True)
    show_macd = st.toggle("MACD PRO", True)
    show_rsi = st.toggle("RSI (30/70)", True)

    # KHUNG QR THANH TOÁN QUỐC TẾ (Đã bổ sung theo yêu cầu)
    st.divider()
    st.markdown(f"### 💳 {t[3]}")
    qr_data = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=A1_GLOBAL_PAYMENT"
    st.image(qr_data, caption="Project A1 Payment Gateway")

# --- 3. CORE DỮ LIỆU CHUẨN XÁC ---
@st.cache_data(ttl=10)
def fetch_global_data(symbol, interval):
    m = {"BTC": "BTC-USD", "ETH": "ETH-USD", "PAXG": "PAXG-USD", "SOL": "SOL-USD", "BNB": "BNB-USD"}
    df = yf.download(m[symbol], period="5d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    # Indicators
    df['EMA25'] = df['Close'].ewm(span=25).mean()
    df['EMA99'] = df['Close'].ewm(span=99).mean()
    exp1 = df['Close'].ewm(span=12).mean(); exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2; df['Sig'] = df['MACD'].ewm(span=9).mean()
    # RSI 14
    delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + g/l))
    return df

df = fetch_global_data(asset, tf)
last, prev = df.iloc[-1], df.iloc[-2]

# AI Prediction
signal = "HOLD"
if last['Close'] > last['EMA25'] and last['MACD'] > last['Sig']: signal = "BUY"
elif last['Close'] < last['EMA25'] or last['MACD'] < last['Sig']: signal = "SELL"

# --- 4. GIAO DIỆN TERMINAL CHÍNH ---
p_color = "price-red" if last['Close'] < prev['Close'] else ""
st.markdown(f'<div style="color:#848e9c; font-weight:500;">{asset}/USDT • {tf} MARKET</div>', unsafe_allow_html=True)
st.markdown(f'<div class="price-tag {p_color}">${last["Close"]:,.2f}</div>', unsafe_allow_html=True)

# Hệ thống nút bấm 300% Đẳng cấp
st.markdown(f"""
<div class="btn-wrap">
    <div class="status-node {'active-buy' if signal == 'BUY' else ''}">BUY</div>
    <div class="status-node {'active-hold' if signal == 'HOLD' else ''}">HOLD</div>
    <div class="status-node {'active-sell' if signal == 'SELL' else ''}">SELL</div>
</div>
""", unsafe_allow_html=True)

# --- 5. BIỂU ĐỒ TRADINGVIEW CLONE ---
fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                    row_heights=[0.55, 0.1, 0.15, 0.2])
t_ax = 'Date' if 'Date' in df.columns else 'Datetime'

# Tầng 1: Candle
fig.add_trace(go.Candlestick(x=df[t_ax], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                             increasing_line_color='#02c076', decreasing_line_color='#cf304a'), row=1, col=1)
if show_ema:
    fig.add_trace(go.Scatter(x=df[t_ax], y=df['EMA25'], line=dict(color='#f0b90b', width=1.2), name="EMA25"), row=1, col=1)

# Tầng 2: Volume
if show_vol:
    v_c = ['#02c076' if df['Open'].iloc[i] < df['Close'].iloc[i] else '#cf304a' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df[t_ax], y=df['Volume'], marker_color=v_c, opacity=0.3), row=2, col=1)

# Tầng 3: MACD
if show_macd:
    fig.add_trace(go.Bar(x=df[t_ax], y=df['MACD']-df['Sig'], marker_color='#474d57'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df[t_ax], y=df['MACD'], line=dict(color='#2962FF', width=1.5)), row=3, col=1)

# Tầng 4: RSI BẢN THƯƠNG MẠI (Có biên màu)
if show_rsi:
    fig.add_trace(go.Scatter(x=df[t_ax], y=df['RSI'], line=dict(color='#ffffff', width=2)), row=4, col=1)
    # Thêm dải vùng 30-70 chuyên nghiệp
    fig.add_hrect(y0=30, y1=70, fillcolor="#7b3af5", opacity=0.1, line_width=0, row=4, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#cf304a", opacity=0.5, row=4, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#02c076", opacity=0.5, row=4, col=1)
    fig.update_yaxes(range=[10, 90], row=4, col=1)

fig.update_layout(height=750, template="plotly_dark", xaxis_rangeslider_visible=False, 
                  margin=dict(l=0,r=0,t=0,b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
fig.update_yaxes(side="right", gridcolor="#1e2329")
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
