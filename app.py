import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json
import time

# --- 1. SETUP GIAO DIỆN ĐẲNG CẤP ---
st.set_page_config(page_title="SENTINEL AI PRO", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #0b0e11; }
    .stButton>button { width: 100%; border-radius: 15px; height: 4em; font-weight: 800; font-size: 20px; border: none; color: white; opacity: 0.1; transition: 0.8s; }
    
    @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); opacity: 1; } 70% { box-shadow: 0 0 30px 15px rgba(0, 255, 136, 0); opacity: 1; } 100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); opacity: 1; } }
    @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); opacity: 1; } 70% { box-shadow: 0 0 30px 15px rgba(255, 75, 75, 0); opacity: 1; } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); opacity: 1; } }
    @keyframes pulse-gold { 0% { box-shadow: 0 0 0 0 rgba(255, 170, 0, 0.7); opacity: 1; } 70% { box-shadow: 0 0 30px 15px rgba(255, 170, 0, 0); opacity: 1; } 100% { box-shadow: 0 0 0 0 rgba(255, 170, 0, 0); opacity: 1; } }
    
    .active-buy { background-color: #00ff88 !important; color: black !important; animation: pulse-green 2s infinite !important; opacity: 1 !important; }
    .active-sell { background-color: #ff4b4b !important; color: white !important; animation: pulse-red 2s infinite !important; opacity: 1 !important; }
    .active-hold { background-color: #ffaa00 !important; color: black !important; animation: pulse-gold 2s infinite !important; opacity: 1 !important; }
    
    .q68-footer { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 28px; opacity: 0.5; letter-spacing: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG ĐIỀU KHIỂN ---
with st.sidebar:
    st.markdown("## 🐢 SENTINEL AI")
    asset_choice = st.selectbox("TÀI SẢN CHIẾN LƯỢC:", ["BITCOIN (BTC)", "ETHEREUM (ETH)", "PAXG (VÀNG)"])
    tf_display = st.select_slider("KHUNG THỜI GIAN (TF):", options=["15m", "30m", "1h", "4h", "1D"], value="30m")
    st.divider()
    st.write("📲 **HỆ THỐNG ĐIỀU HÀNH A1:**")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://A1-PROJECT", width=150)

# --- 3. KẾT NỐI DỮ LIỆU THỜI GIAN THỰC ---
@st.cache_data(ttl=15)
def get_world_class_data(symbol, tf):
    mapping = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "PAXG (VÀNG)": "PAXG-USD"}
    tf_map = {"15m": "15m", "30m": "30m", "1h": "1h", "4h": "1h", "1D": "1d"}
    ticker = mapping.get(symbol, "BTC-USD")
    interval = tf_map.get(tf, "30m")
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={interval}&range=5d"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            raw = json.loads(response.read())
            res = raw['chart']['result'][0]
            df = pd.DataFrame({
                'Date': pd.to_datetime(res['timestamp'], unit='s'),
                'Open': res['indicators']['quote'][0]['open'],
                'High': res['indicators']['quote'][0]['high'],
                'Low': res['indicators']['quote'][0]['low'],
                'Close': res['indicators']['quote'][0]['close'],
                'Volume': res['indicators']['quote'][0]['volume']
            }).dropna()
            # Chỉ báo RSI Đẳng cấp
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain/loss)))
            return df
    except: return None

# Giao diện chính
st.title(f"🐢 {asset_choice.split(' ')[0]} - WORLD PREDICTION")

df = get_world_class_data(asset_choice, tf_display)

if df is not None:
    # HIỂN THỊ GIÁ CHUẨN QUỐC TẾ
    last_price = df['Close'].iloc[-1]
    st.metric(f"GIÁ USD THỰC TẾ ({tf_display})", f"${last_price:,.2f}")

    # --- 4. BIỂU ĐỒ NẾN ĐA TẦNG ---
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.15, 0.25])
    
    # Nến
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Giá"), row=1, col=1)
    
    # Volume
    v_colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=v_colors, name="Khối lượng"), row=2, col=1)
    
    # RSI Sóng Cyan
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], fill='tozeroy', line=dict(color='#00d1ff', width=2), fillcolor='rgba(0, 209, 255, 0.1)', name="RSI"), row=3, col=1)
    
    fig.update_layout(height=700, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=5, b=5))
    fig.update_yaxes(tickprefix="$", tickformat=",", row=1, col=1)
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. LOGIC DỰ BÁO NHỊP THỞ NEON ---
    st.markdown("### 🎯 TÍN HIỆU CHIẾN THUẬT A1")
    rsi_now = df['RSI'].iloc[-1]
    
    b_class = "active-buy" if rsi_now < 30 else ""
    s_class = "active-sell" if rsi_now > 70 else ""
    h_class = "active-hold" if (30 <= rsi_now <= 70) else ""

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<button class="stButton {b_class}">🔥 BUY NOW</button>', unsafe_allow_html=True)
    with c2: st.markdown(f'<button class="stButton {h_class}">⏳ HOLD</button>', unsafe_allow_html=True)
    with c3: st.markdown(f'<button class="stButton {s_class}">❄️ SELL NOW</button>', unsafe_allow_html=True)
else:
    st.error("⚠️ ĐANG KẾT NỐI VỚI VỆ TINH DỮ LIỆU... VUI LÒNG ĐỢI GIÂY LÁT.")

# --- 6. CHỮ Q68 ĐẲNG CẤP ---
st.markdown('<div class="q68-footer">Q68</div>', unsafe_allow_html=True)
