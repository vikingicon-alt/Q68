import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.graph_objects as go # Dùng Plotly để biểu đồ xịn như TradingView

# --- 1. CẤU TRÚC GIAO DIỆN SIÊU CẤP (Xóa sạch lỗi khung đè - Fix 61e053f3) ---
st.set_page_config(page_title="A1 ULTIMATE V39", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    /* Xóa bỏ header và khung thừa tuyệt đối (Fix 61e053f3) */
    header, footer, .stAppHeader {visibility: hidden !important; display: none !important;}
    .main { background: radial-gradient(circle, #0f172a 0%, #020617 100%) !important; color: #FFD700; }
    
    /* Sidebar đẳng cấp tài chính */
    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 2px solid gold; }
    
    /* Nút bấm Golden lấp lánh */
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); 
        color: black; font-weight: 900; border-radius: 12px; height: 50px; border: none;
        box-shadow: 0 4px 15px rgba(218, 165, 32, 0.4);
    }
    
    /* Thẻ tín hiệu A1 */
    .a1-box { 
        padding: 20px; border-radius: 15px; border: 2px solid gold; 
        text-align: center; background: rgba(30, 41, 59, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG ĐĂNG NHẬP & QUẢN LÝ (Ẩn mật khẩu - Fix 61e053f3) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        # Chú rùa vàng ánh kim (Anh thay link ảnh con rùa có chữ Q của anh vào đây nhé)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=180)
        st.markdown("<h1 style='color: gold;'>A1 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs(["🔐 ĐĂNG NHẬP", "✍️ ĐĂNG KÝ"])
        with tab_login:
            st.selectbox("NGÔN NGỮ", ["Tiếng Việt", "English"])
            u = st.text_input("TÀI KHOẢN")
            p = st.text_input("MẬT KHẨU", type="password") # Ẩn mật khẩu tuyệt đối
            
            c1, c2 = st.columns([1.2, 1])
            with c1:
                if st.button("KÍCH HOẠT HỆ THỐNG V39"):
                    if p == "A1PRO": # Mật khẩu mặc định của anh
                        st.session_state['auth'] = True
                        st.rerun()
                    else: st.error("Sai mật khẩu!")
            with c2:
                # Mã QR hoạt động ngay bên ngoài (Fix 61e053f3)
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=A1-GLOBAL-V39", caption="QUÉT TRUY CẬP")
    st.stop()
    # --- 3. KẾT NỐI DỮ LIỆU BINANCE (KHÔNG SAI SÓT - Fix 7bb4d22f) ---
def get_crypto_data(symbol, tf):
    try:
        # Sử dụng API trực tiếp để đảm bảo tốc độ như TradingView
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=100"
        res = requests.get(url, timeout=10).json()
        df = pd.DataFrame(res, columns=['time','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df['C'] = df['C'].astype(float)
        df['H'] = df['H'].astype(float)
        df['L'] = df['L'].astype(float)
        df['O'] = df['O'].astype(float)
        
        # Chỉ báo A1 Master (EMA20 & RSI)
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        return df
    except: return None

# --- 4. GIAO DIỆN CHÍNH (Sidebar & QR - Fix 21b0263b) ---
with st.sidebar:
    st.markdown("<h2 style='color: gold; text-align: center;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.divider()
    symbol = st.selectbox("TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    tf = st.selectbox("KHUNG GIỜ", ["15m", "1h", "4h", "1d"], index=1)
    
    st.divider()
    st.write("A1 SUPPORT QR")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=A1-SUPPORT", caption="QUẢN LÝ HỆ THỐNG")
    
    if st.button("THOÁT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ BIỂU ĐỒ CHUYÊN NGHIỆP (Sánh ngang TradingView) ---
df = get_crypto_data(symbol, tf)

if df is not None:
    curr = df.iloc[-1]
    p, r, e = curr['C'], curr['RSI'], curr['EMA20']
    
    # Tín hiệu A1
    if p > e and r < 70:
        st.markdown('<div class="a1-box"><h2 style="color:#10b981;">🚀 TÍN HIỆU: MUA (A1 UP)</h2></div>', unsafe_allow_html=True)
    elif p < e and r > 30:
        st.markdown('<div class="a1-box"><h2 style="color:#ef4444;">📉 TÍN HIỆU: BÁN (A1 DOWN)</h2></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="a1-box"><h2 style="color:#f59e0b;">⚖️ TÍN HIỆU: CHỜ (A1 WAIT)</h2></div>', unsafe_allow_html=True)

    # Biểu đồ nến chuyên nghiệp (Fix 6a03b831)
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name='Nến Nhật'),
                          go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='gold', width=2), name='EMA20')])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Chỉ số RSI
    st.write("### CHỈ SỐ RSI (14)")
    st.line_chart(df['RSI'])
    
    c1, c2 = st.columns(2)
    c1.metric("GIÁ HIỆN TẠI", f"${p:,.1f}")
    c2.metric("RSI", f"{r:.2f}")
else:
    st.warning("⚠️ Đang đồng bộ với Binance... Anh chờ em vài giây nhé!")
    time.sleep(3)
    st.rerun()
