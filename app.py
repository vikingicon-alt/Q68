import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- 1. PREMIUM INTERFACE ---
st.set_page_config(page_title="Q68 GLOBAL SYSTEM - A1", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #080a0c; }
    .stButton>button { width: 100%; border-radius: 12px; height: 4em; font-weight: 800; font-size: 18px; border: none; color: white; opacity: 0.15; transition: 0.5s; }
    @keyframes neon-glow { 0% { box-shadow: 0 0 5px; transform: scale(1); } 50% { box-shadow: 0 0 25px; transform: scale(1.02); } 100% { box-shadow: 0 0 5px; transform: scale(1); } }
    .active-buy { background-color: #00ff88 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .q68-footer { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 26px; opacity: 0.4; letter-spacing: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MULTI-LANGUAGE & DXY/A1 CONFIG ---
with st.sidebar:
    st.markdown("# 🐢 Q68 A1") 
    lang = st.radio("🌐 LANGUAGE / NGÔN NGỮ:", ["Tiếng Việt", "English"], horizontal=True)
    
    # TỪ ĐIỂN ĐÃ FIX LỖI 3 CÁI ĐÈN
    t = {
        "asset": "TÀI SẢN CHIẾN LƯỢC:" if lang == "Tiếng Việt" else "STRATEGIC ASSET:",
        "tf": "KHUNG THỜI GIAN (TF):" if lang == "Tiếng Việt" else "TIMEFRAME (TF):",
        "scan": "HỆ THỐNG QUẢN TRỊ A1:" if lang == "Tiếng Việt" else "A1 OPERATING SYSTEM:",
        "title": "DỰ BÁO XU HƯỚNG" if lang == "Tiếng Việt" else "TREND PREDICTION",
        "price": "GIÁ THỜI GIAN THỰC" if lang == "Tiếng Việt" else "REAL-TIME PRICE",
        "signal": "🐢 TÍN HIỆU CHIẾN THUẬT A1" if lang == "Tiếng Việt" else "🐢 A1 STRATEGIC SIGNALS",
        "buy_btn": "🔥 MUA NGAY" if lang == "Tiếng Việt" else "🔥 BUY NOW",
        "sell_btn": "❄️ BÁN NGAY" if lang == "Tiếng Việt" else "❄️ SELL NOW",
        "hold_btn": "⏳ CHỜ ĐỢI" if lang == "Tiếng Việt" else "⏳ WAIT / HOLD",
        "macro": "CHỈ SỐ VĨ MÔ (DXY/DOW)" if lang == "Tiếng Việt" else "MACRO INDICATORS (DXY/DOW)"
    }

    asset_choice = st.selectbox(t["asset"], ["BITCOIN (BTC)", "ETHEREUM (ETH)", "PAXG (VÀNG)"])
    tf_choice = st.select_slider(t["tf"], options=["5m", "15m", "30m", "1h", "4h", "1D"], value="1h")
    
    st.divider()
    st.write(f"📲 **{t['scan']}**")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://A1-PROJECT", width=120)
    # --- 3. DXY & MARKET ENGINE ---
@st.cache_data(ttl=15)
def get_macro_data():
    # Giả lập lấy dữ liệu DXY và Dow Jones cho dự án A1
    return {"DXY": 104.5, "DOW": 39000}

@st.cache_data(ttl=15)
def fetch_global_data(symbol, tf):
    mapping = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "PAXG (VÀNG)": "PAXG-USD"}
    ticker = mapping.get(symbol, "BTC-USD")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={tf}&range=5d"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read())['chart']['result'][0]
            df = pd.DataFrame({
                'Date': pd.to_datetime(res['timestamp'], unit='s'),
                'Close': res['indicators']['quote'][0]['close'],
                'Open': res['indicators']['quote'][0]['open'],
                'High': res['indicators']['quote'][0]['high'],
                'Low': res['indicators']['quote'][0]['low'],
                'Volume': res['indicators']['quote'][0]['volume']
            }).dropna()
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            return df
    except: return None

# --- 4. MAIN DASHBOARD ---
macro = get_macro_data()
df = fetch_global_data(asset_choice, tf_choice)

col_main, col_macro = st.columns([4, 1])

with col_main:
    st.title(f"🐢 {asset_choice.split(' ')[0]} - {t['title']}")
    if df is not None:
        # Biểu đồ nến
        fig = go.Figure(data=[go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

with col_macro:
    st.write(f"📊 **{t['macro']}**")
    st.metric("DXY", macro["DXY"], "+0.2%")
    st.metric("DOW", f"{macro['DOW']:,}", "-50")

# --- 5. ĐÈN TÍN HIỆU CHIẾN THUẬT (ĐÃ SỬA LỖI CHUYỂN NGÔN NGỮ) ---
st.markdown(f"### {t['signal']}")

if df is not None:
    price_now = df['Close'].iloc[-1]
    ema_now = df['EMA20'].iloc[-1]
    
    # Logic dự báo của trader kinh tế vĩ mô: Nếu giá > EMA và DXY giảm = MUA
    b_class = "active-buy" if price_now > ema_now else ""
    s_class = "active-sell" if price_now < ema_now else ""
    h_class = "active-hold" if not b_class and not s_class else ""

    c1, c2, c3 = st.columns(3)
    # SỬ DỤNG t["buy_btn"], t["hold_btn"], t["sell_btn"] ĐỂ TỰ ĐỘNG ĐỔI CHỮ
    with c1: st.markdown(f'<button class="stButton {b_class}">{t["buy_btn"]}</button>', unsafe_allow_html=True)
    with c2: st.markdown(f'<button class="stButton {h_class}">{t["hold_btn"]}</button>', unsafe_allow_html=True)
    with c3: st.markdown(f'<button class="stButton {s_class}">{t["sell_btn"]}</button>', unsafe_allow_html=True)
 st.markdown('<div class="q68-footer">Q68 - A1 SYSTEM</div>', unsafe_allow_html=True)
