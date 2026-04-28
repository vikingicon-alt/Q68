import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# --- 1. CẤU TRÚC GIAO DIỆN GOLDEN LẤP LÁNH (SỬA LỖI KHUNG ĐỀ - FIX 61e053f3) ---
st.set_page_config(page_title="A1 GOLDEN V40", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    /* Xóa bỏ header và mọi khung thừa (Fix 61e053f3) */
    header, footer, .stAppHeader {visibility: hidden !important; display: none !important;}
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%) !important; color: #FFD700; }
    
    /* Hiệu ứng Rùa Vàng Lấp Lánh và Chữ Q68 */
    .golden-turtle {
        filter: drop-shadow(0 0 15px #FFD700) brightness(1.2);
        animation: glow 2s ease-in-out infinite alternate;
    }
    @keyframes glow { from { filter: drop-shadow(0 0 5px #FFD700); } to { filter: drop-shadow(0 0 25px #DAA520); } }

    /* Nút bấm Vàng Ánh Kim chuyên nghiệp */
    div.stButton > button { 
        width: 100%; background: linear-gradient(45deg, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        color: black; font-weight: 900; border-radius: 10px; height: 50px; border: none;
        box-shadow: 0 4px 15px rgba(218, 165, 32, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG QUẢN LÝ TÀI KHOẢN & NGÔN NGỮ (FIX CC629488) ---
if 'users' not in st.session_state: st.session_state['users'] = {"admin": "A1PRO"} # Tài khoản mặc định
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'lang' not in st.session_state: st.session_state['lang'] = "Tiếng Việt"

# Từ điển ngôn ngữ (Fix lỗi không chuyển được tiếng Anh - cc629488)
text = {
    "Tiếng Việt": {"login": "ĐĂNG NHẬP", "reg": "ĐĂNG KÝ", "user": "TÀI KHOẢN", "pwd": "MẬT KHẨU", "btn": "KÍCH HOẠT V40", "qr": "QUÉT TRUY CẬP"},
    "English": {"login": "LOGIN", "reg": "REGISTER", "user": "USERNAME", "pwd": "PASSWORD", "btn": "ACTIVATE V40", "qr": "SCAN TO ACCESS"}
}

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        # Rùa Vàng Ánh Kim (Em dùng hiệu ứng CSS để làm Squirtle lấp lánh như vàng thật)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=180)
        st.markdown("<h1 style='color: gold; margin-top:-20px;'>Q68 MASTER</h1>", unsafe_allow_html=True)
        
        # Chọn ngôn ngữ (Cập nhật ngay lập tức)
        st.session_state['lang'] = st.selectbox("LANGUAGE / NGÔN NGỮ", ["Tiếng Việt", "English"])
        L = text[st.session_state['lang']]
        
        tab1, tab2 = st.tabs([f"🔒 {L['login']}", f"📝 {L['reg']}"])
        
        with tab1:
            u_input = st.text_input(L['user'], key="u_in")
            p_input = st.text_input(L['pwd'], type="password", key="p_in")
            c1, c2 = st.columns([1.5, 1])
            with c1:
                if st.button(L['btn']):
                    if u_input in st.session_state['users'] and st.session_state['users'][u_input] == p_input:
                        st.session_state['auth'] = True
                        st.rerun()
                    else: st.error("❌ Invalid Login!")
            with c2:
                # Mã QR hoạt động (Dẫn đến trang Streamlit của anh - Fix cc629488)
                st.markdown(f"<p style='font-size:11px; color:gold;'>{L['qr']}</p>", unsafe_allow_html=True)
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://nrynpp6caudetlbejh8appz.streamlit.app")

        with tab2:
            new_u = st.text_input(f"NEW {L['user']}", key="u_reg")
            new_p = st.text_input(f"NEW {L['pwd']}", type="password", key="p_reg")
            if st.button(f"CREATE {L['user']}"):
                if new_u and new_p:
                    st.session_state['users'][new_u] = new_p
                    st.success("✅ Success! Please Login.")
                else: st.warning("Please fill all fields!")
    st.stop()

# --- 3. ĐỘNG CƠ DỮ LIỆU CHỐNG LỖI MÀN HÌNH ĐỎ (FIX C2959BDD) ---
def get_safe_data(symbol):
    try:
        # Sử dụng API Binance trực tiếp, lấy giới hạn nến để iPad mượt
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=50"
        r = requests.get(url, timeout=5).json()
        if isinstance(r, list) and len(r) > 0:
            df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
            df['C'] = df['C'].astype(float)
            df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
            return df
    except: return None
    return None

# --- 4. GIAO DIỆN BÊN TRONG (SIDEBAR GOLDEN) ---
with st.sidebar:
    st.markdown("<h2 style='color: gold; text-align: center;'>A1 GLOBAL</h2>", unsafe_allow_html=True)
    st.divider()
    target = st.selectbox("ASSET", ["BTCUSDT", "ETHUSDT", "PAXGUSDT"])
    
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app")
    if st.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ BIỂU ĐỒ (CHỐNG LỖI INDEX - FIX 7BB4D22F) ---
data = get_safe_data(target)

if data is not None and not data.empty:
    # Fix triệt để lỗi IndexError bằng cách kiểm tra độ dài dataframe (Fix c2959bdd)
    curr_price = data['C'].iloc[-1]
    st.title(f"📊 {target} Market")
    st.metric("PRICE", f"${curr_price:,.2f}")
    st.line_chart(data[['C', 'EMA20']])
    
    if curr_price > data['EMA20'].iloc[-1]:
        st.success("🚀 TÍN HIỆU A1: MUA (BULLISH)")
    else:
        st.error("📉 TÍN HIỆU A1: BÁN (BEARISH)")
else:
    st.error("🔄 Hệ thống đang kết nối lại dữ liệu thị trường... Vui lòng đợi.")
    if st.button("RELOAD"): st.rerun()
