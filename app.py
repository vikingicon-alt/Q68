import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN SIÊU CẤP ---
st.set_page_config(page_title="A1 GOLDEN ETERNITY", layout="wide")

st.markdown("""
<style>
    header, footer, .stAppHeader {visibility: hidden !important; display: none !important;}
    .main { background: #000000 !important; color: #FFD700; }
    
    /* Con rùa Q68 Vàng lấp lánh */
    .stImage img { border-radius: 15px; border: 2px solid gold; box-shadow: 0 0 20px #FFD700; }
    
    /* Nút bấm Vàng 3D */
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728);
        color: black; font-weight: bold; border-radius: 10px; height: 50px; border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ TÀI KHOẢN (FIX LỖI ĐĂNG KÝ) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user_db' not in st.session_state: st.session_state['user_db'] = {"admin": "A1PRO"}

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=180)
        st.markdown("<h1 style='color: gold;'>Q68 MASTER</h1>", unsafe_allow_html=True)
        
        lang = st.radio("LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        L = {"u": "Tài khoản", "p": "Mật khẩu", "b": "KÍCH HOẠT"} if lang == "Tiếng Việt" else {"u": "Username", "p": "Password", "b": "LOGIN"}
        
        tab_in, tab_up = st.tabs([L['u'], "ĐĂNG KÝ / REGISTER"])
        with tab_in:
            u = st.text_input(L['u'], key="u_login")
            p = st.text_input(L['p'], type="password", key="p_login")
            if st.button(L['b']):
                if u in st.session_state['user_db'] and st.session_state['user_db'][u] == p:
                    st.session_state['auth'] = True
                    st.rerun()
                else: st.error("❌ Sai thông tin!")
        with tab_up:
            nu = st.text_input("Tạo tên mới", key="nu")
            np = st.text_input("Tạo mật khẩu", type="password", key="np")
            if st.button("XÁC NHẬN TẠO"):
                if nu and np:
                    st.session_state['user_db'][nu] = np
                    st.success("✅ Đã tạo! Mời anh quay lại đăng nhập.")
        
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://nrynpp6caudetlbejh8appz.streamlit.app")
    st.stop()

# --- 3. ĐỘNG CƠ DỮ LIỆU BINANCE (AN TOÀN TUYỆT ĐỐI) ---
def fetch_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
        r = requests.get(url, timeout=5).json()
        if isinstance(r, list) and len(r) > 0:
            df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
            df[['O','H','L','C']] = df[['O','H','L','C']].astype(float)
            df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
            return df
    except: return None
    return None

# --- 4. GIAO DIỆN BÊN TRONG ---
with st.sidebar:
    st.markdown("<h2 style='color: gold;'>A1 SYSTEM</h2>", unsafe_allow_html=True)
    pair = st.selectbox("CẶP TÀI SẢN", ["BTCUSDT", "ETHUSDT", "PAXGUSDT"])
    st.divider()
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=A1-SUPPORT")
    if st.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

df = fetch_data(pair)
if df is not None:
    curr = df.iloc[-1]
    st.markdown(f"### 📊 THỊ TRƯỜNG {pair}")
    
    # Biểu đồ Plotly (Như TradingView)
    fig = go.Figure(data=[
        go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Nến"),
        go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='gold', width=2), name="EMA20")
    ])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    col1.metric("GIÁ HIỆN TẠI", f"${curr['C']:,.2f}")
    if curr['C'] > curr['EMA20']:
        col2.success("🚀 TÍN HIỆU: MUA (A1 UP)")
    else:
        col2.error("📉 TÍN HIỆU: BÁN (A1 DOWN)")
else:
    st.warning("🔄 Đang lấy dữ liệu... Anh chờ em chút nhé!")
    time.sleep(2)
    st.rerun()
