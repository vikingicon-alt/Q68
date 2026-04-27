import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. CẤU TRÚC GIAO DIỆN SIÊU CỨNG (FIX LỖI MẤT NGÔN NGỮ & MÉO) ---
st.set_page_config(page_title="Q68 V26", layout="wide")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #020617 !important; }
    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 2px solid #FFD700; min-width: 300px !important; }
    .st-emotion-cache-16idsys p { color: #FFD700; font-weight: bold; font-size: 18px; }
    div.stButton > button { width: 100%; background: linear-gradient(135deg, #FFD700, #B8860B); color: black; font-weight: 900; border-radius: 12px; height: 50px; }
    .status-box { padding: 25px; background: #161b22; border: 3px solid #FFD700; border-radius: 20px; text-align: center; margin-bottom: 30px; box-shadow: 0 0 25px rgba(255, 215, 0, 0.4); }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ TRẠNG THÁI ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=160)
        st.markdown("<h2 style='color: gold;'>A1 GLOBAL SYSTEM</h2>", unsafe_allow_html=True)
        # Fix lỗi mất chọn ngôn ngữ bằng cách tích hợp thẳng vào đây
        lang = st.radio("CHỌN NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        pwd = st.text_input("PASSWORD (A1PRO)", type="password")
        if st.button("KÍCH HOẠT V26"):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

# --- 3. ĐỘNG CƠ DỮ LIỆU ĐẶC BIỆT (CHỐNG TREO THANH VÀNG) ---
@st.cache_data(ttl=5)
def fetch_a1_data(symbol, interval):
    # Thử nhiều cổng kết nối khác nhau để iPad không chặn
    endpoints = [
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100",
        f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100",
        f"https://api2.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    ]
    for url in endpoints:
        try:
            res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}).json()
            if isinstance(res, list) and len(res) > 50:
                df = pd.DataFrame(res, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
                df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
                # Tính toán A1
                df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
                diff = df['C'].diff()
                u, d = (diff.where(diff > 0, 0)).rolling(14).mean(), (-diff.where(diff < 0, 0)).rolling(14).mean()
                df['RSI'] = 100 - (100 / (1 + (u / (d + 1e-10))))
                return df
        except: continue
    return None

# --- 4. SIDEBAR CÂN ĐỐI (FIX MÉO V25) ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=120)
    st.markdown("<h2 style='color: gold; margin-top: -10px;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    coin = st.selectbox("CHỌN MÃ", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    tfs = {"15m":"15 Phút", "1h":"1 Giờ", "4h":"4 Giờ", "1d":"1 Ngày", "1w":"1 Tuần", "1M":"1 Tháng"}
    tf = st.selectbox("KHUNG GIỜ", list(tfs.keys()), format_func=lambda x: tfs[x], index=1)
    st.divider()
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app")
    if st.button("LOGOUT / THOÁT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHIẾN THUẬT ---
df = fetch_a1_data(coin, tf)

if df is not None:
    curr = df.iloc[-1]
    p, r, e = curr['C'], curr['RSI'], curr['EMA20']
    
    # Tín hiệu đèn A1
    if p > e and r < 68: msg, clr = "LỆNH: MUA (BUY)", "#22c55e"
    elif p < e and r > 32: msg, clr = "LỆNH: BÁN (SELL)", "#ef4444"
    else: msg, clr = "LỆNH: CHỜ (WAIT)", "#f59e0b"
    
    st.markdown(f'<div class="status-box"><h1 style="color:{clr}; margin:0;">{msg}</h1></div>', unsafe_allow_html=True)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Giá"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['V'], marker_color='gray', name="Volume"), row=2, col=1)
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("GIÁ", f"${p:,.1f}")
    c2.metric("RSI", f"{r:.2f}")
    c3.metric("EMA20", f"{e:,.1f}")
else:
    # Cơ chế "Cứu vãn" khi bị kẹt thanh vàng
    st.error("⚠️ iPad đang chặn kết nối. Em đang thử lại cổng dự phòng...")
    time.sleep(2)
    st.rerun()
