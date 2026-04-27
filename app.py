import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# --- 1. THIẾT LẬP BIỂU TƯỢNG Q68 VÀ CHỈ HUY ---
icon_q68 = "https://i.imgur.com/83pZpGv.png"
st.set_page_config(page_title="Q68 - A1 SYSTEM", layout="wide", page_icon="🐢")

# Lệnh xóa vương miện và làm sạch giao diện cho iPad
st.markdown(f"""
    <style>
        header, footer, #MainMenu {{visibility: hidden !important;}}
        div[data-testid="stStatusWidget"] {{display: none !important;}}
        .main {{background-color: #05070a; color: white;}}
        [data-testid="stSidebar"] {{background-color: #0c0f14; border-right: 1px solid #1e2229;}}
        div[class*="viewerBadge"] {{display: none !important;}}
    </style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG BẢO MẬT & ĐĂNG NHẬP ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown(f"<div style='text-align: center;'><img src='{icon_q68}' width='150'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: gold;'>Q68 - A1 SYSTEM GLOBAL</h1>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1,2,1])
    with col_b:
        password = st.text_input("MÃ KÍCH HOẠT CHỈ HUY:", type="password")
        if st.button("KÍCH HOẠT HỆ THỐNG Q68"):
            if password == "A1PRO":
                st.session_state['authenticated'] = True
                st.rerun()
    st.stop()

# --- 3. HỆ THỐNG DỮ LIỆU THỰC & BOT CẢNH BÁO ---
def get_crypto_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100"
    res = requests.get(url).json()
    df = pd.DataFrame(res, columns=['Time','Open','High','Low','Close','Vol','CT','QV','T','TB','TQ','I'])
    df['Close'] = df['Close'].astype(float)
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    return df

# --- 4. GIAO DIỆN ĐIỀU HÀNH SIDEBAR (CON RÙA & CHỈ HUY) ---
with st.sidebar:
    st.image(icon_q68, width=120)
    st.markdown("<h2 style='color: gold; text-align: center;'>CHỈ HUY Q68</h2>", unsafe_allow_html=True)
    st.write("---")
    st.success("🤖 BOT A1: ĐANG TRỰC CHIẾN")
    st.write("**THÔNG SỐ QUÉT:**")
    st.write("- RSI (14)")
    st.write("- EMA 20/50")
    st.write("- Cảnh báo: Telegram/Web")
    if st.button("ĐĂNG XUẤT"):
        st.session_state['authenticated'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHÍNH ---
try:
    df = get_crypto_data()
    price = df['Close'].iloc[-1]
    ema20 = df['EMA20'].iloc[-1]
    
    st.markdown(f"<h1 style='text-align: center; color: gold;'>🐢 Q68 SYSTEM | BITCOIN: ${price:,.2f}</h1>", unsafe_allow_html=True)

    # Biểu đồ chuyên nghiệp
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df['Close'], name='Price', line=dict(color='white', width=2)))
    fig.add_trace(go.Scatter(y=df['EMA20'], name='EMA 20', line=dict(color='cyan', width=1.5)))
    fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="#05070a", plot_bgcolor="#05070a", margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Tín hiệu quyết định từ Bot
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("XU HƯỚNG", "UPTREND" if price > ema20 else "DOWNTREND")
    with c2: 
        status = "🔥 MUA (BUY)" if price > ema20 else "❄️ BÁN (SELL)"
        st.metric("QUYẾT ĐỊNH Q68", status)
    with c3: st.metric("BOT STATUS", "ONLINE")

    # Kiểm tra biến động để Bot báo động (Giả lập thông báo trực tiếp trên App)
    if abs(((price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100) > 1.0:
        st.toast("⚠️ BOT A1: CẢNH BÁO BIẾN ĐỘNG MẠNH!")

except Exception as e:
    st.error("Hệ thống Q68 đang kết nối nguồn dữ liệu thế giới...")

st.button("🔥 KÍCH HOẠT CHIẾN THUẬT TOÀN CẦU", use_container_width=True)
