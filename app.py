import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="A1 SUPREME V66", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS "QUÉT SẠCH" LOGO & TRÀN VIỀN (ÉP IPAD PHẢI HIỂN THỊ) ---
st.markdown("""
<style>
    /* DIỆT TẬN GỐC LOGO VƯƠNG MIỆN & CHỮ STREAMLIT */
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}

    /* ÉP TRÀN VIỀN TỐI ĐA */
    .block-container { padding: 0.5rem !important; }
    .stApp { background-color: #000000; color: white; }

    /* RÙA Q68 LẤP LÁNH */
    .turtle-box { 
        width: 100px; height: 100px; border-radius: 50%; 
        border: 4px solid #FFD700; overflow: hidden; margin: 0 auto;
        box-shadow: 0 0 25px #FFD700; animation: glow 2s infinite alternate;
    }
    @keyframes glow { from {box-shadow: 0 0 10px #FFD700;} to {box-shadow: 0 0 35px #FFD700;} }
    
    /* KHUNG GIÁ VÀNG */
    .price-tag { 
        background: #1a1a00; padding: 15px; border-radius: 12px; border: 3px solid #ffff00; 
        text-align: center; font-size: 28px; font-weight: bold; color: #ffff00;
    }

    /* MÃ QR */
    .qr-white { background: white; padding: 10px; border-radius: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. KHỞI TẠO DỮ LIỆU ---
if 'lang' not in st.session_state: st.session_state.lang = 'VI'
if 'sig' not in st.session_state: st.session_state.sig = None

L = {'VI': {'sel': "CHỌN COI", 'pre': "⚡ DỰ BÁO AI", 'qr': "QUÉT ĐĂNG KÝ"},
     'EN': {'sel': "SELECT COIN", 'pre': "⚡ AI PREDICT", 'qr': "REGISTER"}}[st.session_state.lang]

# --- 4. GIAO DIỆN CHÍNH ---
col_main, col_side = st.columns([3.2, 1])

with col_main:
    # Nút ngôn ngữ
    if st.button(f"🌐 {st.session_state.lang}"):
        st.session_state.lang = 'EN' if st.session_state.lang == 'VI' else 'VI'
        st.rerun()

    coin = st.selectbox(L['sel'], ["BTCUSDT", "ETHUSDT", "LTCUSDT"], index=0)
    price = 76181.75 if coin == "BTCUSDT" else 55.23
    st.markdown(f'<div class="price-tag">{coin}: {price:,.2f} USD</div>', unsafe_allow_html=True)
    
    # BIỂU ĐỒ TRADINGVIEW
    components.html(f"""
        <div id="tv" style="height:530px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:{coin}", "interval": "1H", "theme": "dark", "container_id": "tv"}});</script>
    """, height=540)

with col_side:
    # 🐢 RÙA Q68
    st.markdown(f"""
    <div style="text-align:center;">
    <div class="turtle-box"><img src="https://img.freepik.com/free-vector/cute-turtle-cartoon-character_1308-41076.jpg" width="100%"></div>
        <div style="color:gold; font-weight:bold; font-size:24px; margin-top:5px;">Q68</div>
        <div style="color:white; font-size:16px;">A1 COMMANDER</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(L['pre'], use_container_width=True):
        st.session_state.sig = random.choice(["BUY", "HOLD", "SELL"])

    # HIỂN THỊ TÍN HIỆU
    s = st.session_state.sig
    st.success("BUY / MUA") if s == "BUY" else st.warning("HOLD") if s == "HOLD" else st.error("SELL / BÁN") if s == "SELL" else st.write("")

    # MÃ QR ĐĂNG KÝ
    st.markdown(f'<div class="qr-white"><img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://a1pro-global.com" width="100%"></div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:white;'>{L['qr']}</p>", unsafe_allow_html=True)

# BẢNG CHỈ SỐ VĨ MÔ
st.table(pd.DataFrame([{"Chỉ số": "DXY", "Giá": "106.25"}, {"Chỉ số": "Dow Jones", "Giá": "39,280"}]))
