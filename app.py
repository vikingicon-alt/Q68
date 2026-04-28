import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go

# --- 1. GIAO DIỆN CHUẨN IPAD (FIX KHUNG VÀNG ĐÈ HÌNH) ---
st.set_page_config(page_title="A1 GOLDEN ETERNITY V43.2", layout="wide")

st.markdown("""
<style>
    header, footer, .stAppHeader {visibility: hidden !important; display: none !important;}
    .main { background: #000000 !important; color: #FFD700; }
    .stImage img { border-radius: 15px; border: 2px solid gold; box-shadow: 0 0 20px #FFD700; }
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 45%, #B38728);
        color: black; font-weight: bold; border-radius: 10px; height: 50px; border: none;
    }
    .stTextInput input { background-color: #1a1a1a !important; color: gold !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG TÀI KHOẢN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'db' not in st.session_state: st.session_state['db'] = {"admin": "A1PRO"}

# --- 3. LOGIC ĐĂNG NHẬP (FIX CC629488) ---
if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=180)
        st.markdown("<h1 style='color: gold;'>A1 GLOBAL</h1>", unsafe_allow_html=True)
        
        lang = st.radio("LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        L = {"u": "Tài khoản", "p": "Mật khẩu", "b": "KÍCH HOẠT"} if lang == "Tiếng Việt" else {"u": "Account", "p": "Password", "b": "ACTIVATE"}
        
        t1, t2 = st.tabs([L['u'], "ĐĂNG KÝ"])
        with t1:
            u = st.text_input(L['u'], key="user_login")
            p = st.text_input(L['p'], type="password", key="pass_login")
            if st.button(L['b']):
                if u in st.session_state['db'] and st.session_state['db'][u] == p:
                    st.session_state['auth'] = True
                    st.rerun()
                else: st.error("❌ Thông tin sai!")
        with t2:
            nu = st.text_input("Tên đăng ký")
            np = st.text_input("Mật khẩu mới", type="password")
            if st.button("XÁC NHẬN"):
                if nu and np:
                    st.session_state['db'][nu] = np
                    st.success("✅ Đã tạo! Quay lại đăng nhập.")
    st.stop()

# --- 4. CÔNG CỤ LẤY DỮ LIỆU TỰ ĐỘNG THỬ LẠI (FIX 8BEF1AE9) ---
def get_a1_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
        r = requests.get(url, timeout=10).json()
        if isinstance(r, list) and len(r) >= 100:
            df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
            df[['O','H','L','C']] = df[['O','H','L','C']].astype(float)
            df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
            return df
        return "WAIT"
    except:
        return "ERR"

# --- 5. GIAO DIỆN CHÍNH ---
with st.sidebar:
    st.markdown("<h2 style='color: gold;'>A1 SYSTEM</h2>", unsafe_allow_html=True)
    coin = st.selectbox("CẶP TÀI SẢN", ["BTCUSDT", "ETHUSDT", "PAXGUSDT"])
    if st.button("THOÁT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 6. KIỂM TRA VÀ HIỂN THỊ (FIX TRIỆT ĐỂ LỖI) ---
data = get_a1_data(coin)

if isinstance(data, pd.DataFrame):
    curr = data.iloc[-1]
    st.markdown(f"### 📈 BIỂU ĐỒ A1: {coin}")
    
    fig = go.Figure(data=[
        go.Candlestick(x=data.index, open=data['O'], high=data['H'], low=data['L'], close=data['C'], name="Nến"),
        go.Scatter(x=data.index, y=data['EMA20'], line=dict(color='gold', width=2), name="EMA20")
    ])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2 = st.columns(2)
    c1.metric("GIÁ", f"${curr['C']:,.2f}")
    if curr['C'] > curr['EMA20']:
        c2.success("🚀 TÍN HIỆU: MUA (A1 UP)")
    else:
        c2.error("📉 TÍN HIỆU: BÁN (A1 DOWN)")

elif data == "WAIT":
    st.warning("🔄 Dữ liệu đang nạp... Hệ thống tự động tải lại sau 3 giây.")
    time.sleep(3)
    st.rerun()
else:
    st.error("❌ Lỗi kết nối mạng iPad.")
    if st.button("KẾT NỐI LẠI"): st.rerun()
