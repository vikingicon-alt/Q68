import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go

# --- 1. CẤU TRÚC GIAO DIỆN PRESTIGE GOLDEN (XÓA SẠCH LỖI KHUNG ĐÈ) ---
st.set_page_config(page_title="A1 PRESTIGE V41", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    /* Xóa bỏ mọi thành phần thừa của Streamlit gây đè ảnh */
    header, footer, .stAppHeader {visibility: hidden !important; display: none !important;}
    .main { background: #000000 !important; color: #FFD700; }
    
    /* Hiệu ứng Rùa Vàng Lấp Lánh Q68 */
    .stImage img {
        filter: drop-shadow(0 0 20px #FFD700);
        border-radius: 50%;
    }
    
    /* Nút bấm Vàng Ánh Kim 3D */
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); 
        color: black; font-weight: 900; border-radius: 12px; height: 50px; border: 2px solid #FFFACD;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.5);
    }
    
    /* Khung tín hiệu bo góc */
    .signal-card {
        padding: 25px; border-radius: 20px; border: 2px solid gold;
        background: rgba(255, 215, 0, 0.05); text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ ĐĂNG NHẬP (LƯU TÀI KHOẢN THỰC) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=200)
        st.markdown("<h1 style='color: gold; font-size: 45px;'>A1 GLOBAL</h1>", unsafe_allow_html=True)
        
        # Ngôn ngữ hoạt động ngay lập tức
        lang = st.radio("CHỌN NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        label_user = "TÀI KHOẢN" if lang == "Tiếng Việt" else "USERNAME"
        label_pwd = "MẬT KHẨU" if lang == "Tiếng Việt" else "PASSWORD"
        
        u = st.text_input(label_user, placeholder="admin")
        p = st.text_input(label_pwd, type="password", placeholder="A1PRO")
        
        if st.button("KÍCH HOẠT HỆ THỐNG V41"):
            if u == "admin" and p == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("❌ Sai thông tin truy cập!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://nrynpp6caudetlbejh8appz.streamlit.app", caption="QUÉT ĐỂ TRUY CẬP")
    st.stop()

# --- 3. KẾT NỐI DỮ LIỆU BINANCE THỰC (CHỐNG TREO - FIX 975B97A2) ---
@st.cache_data(ttl=10) # Tự động làm mới mỗi 10 giây
def fetch_market_data(symbol):
    try:url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
        res = requests.get(url, timeout=5).json()
        df = pd.DataFrame(res, columns=['time','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C']] = df[['O','H','L','C']].astype(float)
        # Chỉ báo A1: EMA20
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        return df
    except Exception as e:
        return None

# --- 4. GIAO DIỆN BÊN TRONG (SIDEBAR VÀNG KIM) ---
with st.sidebar:
    st.markdown("<h2 style='color: gold;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=100)
    st.divider()
    coin = st.selectbox("TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    st.divider()
    st.markdown("### A1 SUPPORT")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=A1-SUPPORT-GOLDEN")
    if st.button("THOÁT HỆ THỐNG"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ BIỂU ĐỒ TRADINGVIEW-STYLE (FIX 6A03B831) ---
df = fetch_market_data(coin)

if df is not None and not df.empty:
    curr = df.iloc[-1]
    
    # 1. Thẻ tín hiệu A1 (Fix lỗi không hiển thị)
    status = "🚀 MUA (UP)" if curr['C'] > curr['EMA20'] else "📉 BÁN (DOWN)"
    color = "#10b981" if "MUA" in status else "#ef4444"
    
    st.markdown(f"""
        <div class="signal-card">
            <h1 style="color: gold; margin: 0;">{coin}</h1>
            <h2 style="color: {color};">{status}</h2>
            <p style="color: #FFD700; font-size: 20px;">GIÁ HIỆN TẠI: ${curr['C']:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Biểu đồ nến chuyên nghiệp (TradingView Style)
    fig = go.Figure(data=[
        go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Nến"),
        go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='gold', width=2), name="EMA20")
    ])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. Thông số kỹ thuật
    c1, c2, c3 = st.columns(3)
    c1.metric("HIGH", f"${curr['H']:,.1f}")
    c2.metric("LOW", f"${curr['L']:,.1f}")
    c3.metric("EMA20", f"${curr['EMA20']:,.1f}")
else:
    # Fix lỗi đứng màn hình (975b97a2)
    st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2 style="color: gold;">🔄 Đang kết nối dữ liệu sàn Binance...</h2>
            <p>Anh vui lòng chờ trong giây lát hoặc bấm nút bên dưới.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("LÀM MỚI DỮ LIỆU"): st.rerun()
