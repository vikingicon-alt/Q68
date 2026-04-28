import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. CẤU TRÚC GIAO DIỆN PRESTIGE (FIX 4FE920D8 & CC629488) ---
st.set_page_config(page_title="A1 SUPREME V42", layout="wide", page_icon="🐢")

# CSS Cao cấp để xóa sạch khung thừa và tạo hiệu ứng Vàng lấp lánh
st.markdown("""
<style>
    header, footer, .stAppHeader {visibility: hidden !important; display: none !important;}
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%) !important; color: #FFD700; }
    
    /* Hiệu ứng Rùa Vàng lấp lánh lơ lửng */
    .golden-turtle {
        filter: drop-shadow(0 0 20px #FFD700);
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }

    /* Nút bấm Vàng Ánh Kim 3D chuyên nghiệp */
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        color: black; font-weight: 900; border-radius: 12px; height: 55px; border: 1px solid #FFFACD;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.4); transition: all 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 6px 25px rgba(255, 215, 0, 0.6); }

    /* Khung thông tin tài chính */
    .metric-container { background: rgba(255, 215, 0, 0.05); border: 1px solid gold; border-radius: 15px; padding: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG QUẢN LÝ TRẠNG THÁI (FIX CC629488) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'users' not in st.session_state: st.session_state['users'] = {"admin": "A1PRO"} # Tài khoản gốc của anh
if 'lang' not in st.session_state: st.session_state['lang'] = "Tiếng Việt"

# --- 3. MÀN HÌNH ĐĂNG NHẬP HOÀN HẢO ---
if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        # Chú rùa vàng Q68 của anh (Fix 4fe920d8)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=220)
        st.markdown("<h1 style='color: gold; font-size: 50px; margin-top:-20px;'>A1 GLOBAL</h1>", unsafe_allow_html=True)
        
        st.session_state['lang'] = st.selectbox("NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"])
        L = {"user": "TÀI KHOẢN", "pwd": "MẬT KHẨU", "btn": "KÍCH HOẠT A1"} if st.session_state['lang'] == "Tiếng Việt" else {"user": "USERNAME", "pwd": "PASSWORD", "btn": "ACTIVATE A1"}
        
        tab_log, tab_reg = st.tabs([f"🔒 {L['user']}", f"📝 ĐĂNG KÝ"])
        with tab_log:
            u_in = st.text_input(L['user'], key="login_u")
            p_in = st.text_input(L['pwd'], type="password", key="login_p")
            if st.button(L['btn']):
                if u_in in st.session_state['users'] and st.session_state['users'][u_in] == p_in:
                    st.session_state['auth'] = True
                    st.rerun()
                else: st.error("❌ Thông tin không chính xác!")
        with tab_reg:
            u_new = st.text_input("TẠO TÀI KHOẢN MỚI")
            p_new = st.text_input("TẠO MẬT KHẨU MỚI", type="password")
            if st.button("XÁC NHẬN ĐĂNG KÝ"):
                if u_new and p_new:
                    st.session_state['users'][u_new] = p_new
                    st.success("✅ Đăng ký thành công! Mời anh quay lại đăng nhập.")
        
        # Mã QR dẫn đến hệ thống của anh (Fix cc629488)
        st.markdown("<br>", unsafe_allow_html=True)
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=130x130&data=https://nrynpp6caudetlbejh8appz.streamlit.app", caption="QR TRUY CẬP HỆ THỐNG")
    st.stop()

# --- 4. ĐỘNG CƠ DỮ LIỆU BINANCE CHỐNG LỖI (FIX 7BB4D22F & 975B97A2) ---
def fetch_safe_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=150"
        res = requests.get(url, timeout=10).json()
        if isinstance(res, list) and len(res) > 50:
            df = pd.DataFrame(res, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
            df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
            df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
            # Tính RSI cho anh soi tín hiệu
            delta = df['C'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            return df
    except: return None
    return None

# --- 5. GIAO DIỆN ĐIỀU KHIỂN BÊN TRONG ---
with st.sidebar:
    st.markdown("<h2 style='color: gold;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=120)
    st.divider()
    coin = st.selectbox("CHỌN TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    tf = st.selectbox("KHUNG GIỜ", ["15m", "1h", "4h", "1d"], index=1)
    st.divider()
    # QR Support
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=A1-SUPPORT-SUPREME")
    if st.button("THOÁT HỆ THỐNG"):
        st.session_state['auth'] = False
        st.rerun()

# --- 6. HIỂN THỊ BIỂU ĐỒ & TÍN HIỆU A1 ---
data = fetch_safe_data(coin, tf)

if data is not None and not data.empty:
    curr = data.iloc[-1]
    
    # Khối tín hiệu A1 Master
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### 📈 BIỂU ĐỒ {coin} ({tf})")
    with col2:
        signal = "🚀 MUA (UP)" if curr['C'] > curr['EMA20'] else "📉 BÁN (DOWN)"
        sig_color = "#10b981" if "MUA" in signal else "#ef4444"
        st.markdown(f"<div class='metric-container'><h2 style='color:{sig_color}; margin:0;'>{signal}</h2></div>", unsafe_allow_html=True)

    # Biểu đồ Nến & EMA20 & RSI (Fix 6a03b831)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    # Nến & EMA
    fig.add_trace(go.Candlestick(x=data.index, open=data['O'], high=data['H'], low=data['L'], close=data['C'], name="Nến"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA20'], line=dict(color='gold', width=2), name="EMA20"), row=1, col=1)
    # RSI
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='#ff00ff'), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)
    
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Thống kê nhanh
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("GIÁ", f"${curr['C']:,.2f}")
    m2.metric("RSI", f"{curr['RSI']:.2f}")
    m3.metric("KHỐI LƯỢNG", f"{curr['V']:,.1f}")
    m4.metric("EMA CÁCH", f"{(curr['C']-curr['EMA20']):,.1f}")

else:
    # Xử lý khi lỗi mạng iPad (Fix 975b97a2)
    st.markdown("""
        <div style="text-align: center; padding: 100px;">
            <h1 style="color: gold;">🔄 ĐANG KHỞI ĐỘNG DỮ LIỆU A1...</h1>
            <p>Hệ thống đang kết nối với máy chủ tài chính. Anh vui lòng đợi trong giây lát.</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.rerun()
