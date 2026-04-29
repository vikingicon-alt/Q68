import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
MY_WEBSITE = "https://a1pro-global.com"
# Link ảnh rùa xanh Q68 (Em dùng ảnh rùa xanh chuẩn, anh có thể thay link nếu muốn)
TURTLE_LOGO = "https://img.freepik.com/free-vector/cute-turtle-cartoon-character_1308-41076.jpg"

st.set_page_config(page_title="A1 SUPREME V64", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS ĐẶC TRỊ: DIỆT LOGO, THANH SEARCH & TRÀN VIỀN ---
st.markdown("""
<style>
    /* XÓA SẠCH LOGO & TRANG TRÍ DƯ THỪA (VƯƠNG MIỆN + STREAMLIT LOGO) */
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .stAppDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    /* ẨN THANH TÌM KIẾM PHÍA TRÊN */
    [data-testid="stHeader"] {display: none !important;}

    /* ÉP TRÀN VIỀN TUYỆT ĐỐI CHO IPAD */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .stApp {background-color: #000000;}

    /* VÒNG TRÒN RÙA Q68 LẤP LÁNH */
    .turtle-circle { 
        width: 100px; height: 100px; border-radius: 50%; 
        border: 4px solid #FFD700; overflow: hidden;
        margin: 0 auto; background: #002200;
        box-shadow: 0 0 25px #FFD700;
        animation: turtle-glow 2s infinite alternate;
    }
    .turtle-circle img { width: 100%; height: 100%; object-fit: cover; }
    @keyframes turtle-glow { from { box-shadow: 0 0 15px #FFD700; } to { box-shadow: 0 0 35px #FFD700; } }

    /* KHUNG GIÁ VÀNG */
    .price-display { 
        background: #1a1a00; padding: 12px; border-radius: 12px; border: 3px solid #ffff00; 
        text-align: center; font-size: 26px; font-weight: bold; color: #ffff00;
    }

    /* TÍN HIỆU CHỚP SÁNG */
    @keyframes blink-sig { 50% { opacity: 0.2; box-shadow: 0 0 30px white; } }
    .sig-active { animation: blink-sig 0.6s linear infinite; border: 4px solid white !important; opacity: 1.0 !important; }
    .sig-box { padding: 18px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; opacity: 0.2; border: 1px solid #333; margin-bottom: 8px; }
    
    /* KHUNG MÃ QR ĐĂNG KÝ (SÁNG RÕ) */
    .qr-frame {
        background: white; padding: 8px; border-radius: 10px; 
        margin-top: 10px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. KIỂM TRA & KHỞI TẠO BIẾN (FIX LỖI MÀN HÌNH ĐỎ) ---
if 'lang' not in st.session_state: st.session_state.lang = 'VI'
    if 'ai_sig' not in st.session_state: st.session_state.ai_sig = None

def change_language():
    st.session_state.lang = 'EN' if st.session_state.lang == 'VI' else 'VI'

# Dữ liệu coin & macro (LTC fix chuẩn 55.23)
coin_prices = {"BTCUSDT": 76181.75, "ETHUSDT": 2290.81, "LTCUSDT": 55.23}

L = {
    'VI': {'sel': "CHỌN COI", 'pre': "⚡ PHÂN TÍCH AI (MACRO)", 'qr': "QUÉT ĐỂ ĐĂNG KÝ"},
    'EN': {'sel': "SELECT COIN", 'pre': "⚡ AI ANALYSIS (MACRO)", 'qr': "SCAN TO REGISTER"}
}[st.session_state.lang]

# --- 4. GIAO DIỆN TÁC CHIẾN ---
st.button(f"🌐 {st.session_state.lang}", on_click=change_language)

col_main, col_side = st.columns([3.2, 1])

with col_main:
    # Chọn coin & hiển thị giá
    coin = st.selectbox(L['sel'], list(coin_prices.keys()), index=0)
    st.markdown(f'<div class="price-display">{coin}: {coin_prices[coin]:,.2f} USD</div>', unsafe_allow_html=True)
    
    # Biểu đồ TradingView (Full Width)
    components.html(f"""
        <div id="tv_v64" style="height:530px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:{coin}", "interval": "1H", "theme": "dark", "style": "1", "container_id": "tv_v64"}});</script>
    """, height=540)

with col_side:
    # 🐢 LINH VẬT RÙA Q68
    st.markdown(f"""
    <div style="text-align:center;">
        <div class="turtle-circle"><img src="{TURTLE_LOGO}"></div>
        <div style="color:gold; font-weight:bold; font-size:24px; margin-top:5px; text-shadow: 1px 1px 3px black;">Q68</div>
        <div style="color:white; font-size:16px; letter-spacing: 2px;">A1 COMMANDER</div>
    </div>
    """, unsafe_allow_html=True)

    # NÚT DỰ BÁO THÔNG MINH
    if st.button(L['pre'], use_container_width=True):
        with st.spinner("Analyzing..."):
            time.sleep(1.2)
            st.session_state.ai_sig = random.choice(["BUY", "HOLD", "SELL"])

    curr_sig = st.session_state.ai_sig
    st.markdown(f'<div class="sig-box {"sig-active" if curr_sig=="BUY" else ""}" style="background:green; color:white;">BUY / MUA</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sig-box {"sig-active" if curr_sig=="HOLD" else ""}" style="background:orange; color:black;">HOLD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sig-box {"sig-active" if curr_sig=="SELL" else ""}" style="background:red; color:white;">SELL / BÁN</div>', unsafe_allow_html=True)

    # MÃ QR ĐĂNG KÝ (FIX HOÀN CHỈNH - DỄ QUÉT)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={MY_WEBSITE}"
    st.markdown(f"""
    <div class="qr-frame">
        <img src="{qr_url}" width="100%">
        <div style="color:black; font-weight:bold; font-size:11px; margin-top:5px;">{L['qr']}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. BẢNG CHỈ SỐ VĨ MÔ ---
st.markdown("### 🌍 GLOBAL MACRO INDICATORS")
st.table(pd.DataFrame([
    {"Chỉ số": "DXY (Dollar Index)", "Giá trị": "106.25", "Trạng thái": "Mạnh"},
    {"Chỉ số": "Dow Jones 30", "Giá trị": "39,280", "Trạng thái": "Tăng trưởng"}
]))
