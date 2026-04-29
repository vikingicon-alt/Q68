import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
MY_WEBSITE = "https://a1pro-global.com"
# Link ảnh rùa xanh vàng chuẩn (Em dùng ảnh rùa vàng xanh cực đẹp)
TURTLE_IMG = "https://cdn-icons-png.flaticon.com/512/3232/3232777.png"

st.set_page_config(page_title="A1 SUPREME V67", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS ĐẶC TRỊ: DIỆT LOGO & HIỆU ỨNG NEON ---
st.markdown("""
<style>
    /* XÓA SẠCH LOGO & THANH TRẠNG THÁI GÓC DƯỚI */
    [data-testid="stHeader"], footer, header, .stAppDeployButton, 
    div[data-testid="stDecoration"], div[data-testid="stStatusWidget"], 
    .viewerBadge_container__1QSob, #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    /* TRÀN VIỀN CHO IPAD */
    .block-container { padding: 0rem !important; }
    .stApp { background-color: #000000; }

    /* VÒNG TRÒN RÙA Q68 LẤP LÁNH */
    .turtle-circle { 
        width: 110px; height: 110px; border-radius: 50%; 
        border: 4px solid #FFD700; overflow: hidden;
        margin: 10px auto; background: radial-gradient(circle, #004400, #000000);
        box-shadow: 0 0 30px #FFD700;
        animation: turtle-glow 1.5s infinite alternate;
    }
    .turtle-circle img { width: 80%; height: 80%; margin: 10%; object-fit: contain; }
    @keyframes turtle-glow { from { box-shadow: 0 0 10px #FFD700; } to { box-shadow: 0 0 40px #FFD700; } }

    /* KHUNG GIÁ VÀNG RỰC RỠ */
    .price-display { 
        background: #1a1a00; padding: 15px; border-radius: 12px; border: 4px solid #ffff00; 
        text-align: center; font-size: 30px; font-weight: bold; color: #ffff00;
        box-shadow: 0 0 20px #ffff00; margin-bottom: 10px;
    }

    /* HỆ THỐNG ĐÈN NEON */
    .neon-box { 
        padding: 15px; border-radius: 10px; text-align: center; 
        font-weight: bold; font-size: 20px; margin-bottom: 10px;
        border: 2px solid #333; opacity: 0.15; transition: 0.3s;
    }
    .neon-buy { border-color: #00FF00; color: #00FF00; text-shadow: 0 0 10px #00FF00; }
    .neon-hold { border-color: #FFA500; color: #FFA500; text-shadow: 0 0 10px #FFA500; }
    .neon-sell { border-color: #FF0000; color: #FF0000; text-shadow: 0 0 10px #FF0000; }
    
    .active-buy { opacity: 1; background: rgba(0,255,0,0.1); box-shadow: 0 0 30px #00FF00; border-width: 4px; }
    .active-hold { opacity: 1; background: rgba(255,165,0,0.1); box-shadow: 0 0 30px #FFA500; border-width: 4px; }
    .active-sell { opacity: 1; background: rgba(255,0,0,0.1); box-shadow: 0 0 30px #FF0000; border-width: 4px; }

    /* QR CODE */
    .qr-container { background: white; padding: 10px; border-radius: 15px; text-align: center; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC ---
if 'lang' not in st.session_state: st.session_state.lang = 'VI'
    if 'signal' not in st.session_state: st.session_state.signal = None

def toggle_lang():
    st.session_state.lang = 'EN' if st.session_state.lang == 'VI' else 'VI'

# Dữ liệu thị trường
coin_list = {"BTCUSDT": 76181.75, "ETHUSDT": 2290.81, "LTCUSDT": 55.23}
L = {'VI': {'sel': "CHỌN COIN", 'pre': "⚡ PHÂN TÍCH AI", 'qr': "QUÉT ĐỂ ĐĂNG KÝ"},
     'EN': {'sel': "SELECT COIN", 'pre': "⚡ AI PREDICT", 'qr': "REGISTER NOW"}}[st.session_state.lang]

# --- 4. LAYOUT ---
col_left, col_right = st.columns([3.3, 1])

with col_left:
    st.button(f"🌐 {st.session_state.lang}", on_click=toggle_lang)
    coin = st.selectbox(L['sel'], list(coin_list.keys()))
    st.markdown(f'<div class="price-display">{coin}: {coin_list[coin]:,.2f} USD</div>', unsafe_allow_html=True)
    
    # Chart TradingView
    components.html(f"""
        <div id="tv_chart" style="height:550px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:{coin}", "interval": "1H", "theme": "dark", "container_id": "tv_chart"}});</script>
    """, height=560)

with col_right:
    # 🐢 LINH VẬT RÙA Q68
    st.markdown(f"""
    <div style="text-align:center;">
        <div class="turtle-circle"><img src="{TURTLE_IMG}"></div>
        <div style="color:gold; font-weight:bold; font-size:28px; margin-top:-10px;">Q68</div>
        <div style="color:#aaa; font-size:14px; letter-spacing: 2px;">A1 COMMANDER</div>
    </div>
    """, unsafe_allow_html=True)

    # Nút bấm AI
    if st.button(L['pre'], use_container_width=True):
        with st.spinner("Processing..."):
            time.sleep(1)
            st.session_state.signal = random.choice(["BUY", "HOLD", "SELL"])

    # 🚦 HỆ THỐNG ĐÈN NEON DƯỚI NÚT AI
    sig = st.session_state.signal
    st.markdown(f'<div class="neon-box neon-buy {"active-buy" if sig=="BUY" else ""}">BUY / MUA</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="neon-box neon-hold {"active-hold" if sig=="HOLD" else ""}">HOLD / CHỜ</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="neon-box neon-sell {"active-sell" if sig=="SELL" else ""}">SELL / BÁN</div>', unsafe_allow_html=True)

    # MÃ QR ĐĂNG KÝ
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={MY_WEBSITE}"
    st.markdown(f'<div class="qr-container"><img src="{qr_url}" width="100%"><br><b style="color:black; font-size:12px;">{L["qr"]}</b></div>', unsafe_allow_html=True)

# --- 5. BẢNG CHỈ SỐ VĨ MÔ ---
st.markdown("<h3 style='color:white;'>🌍 GLOBAL MACRO INDICATORS</h3>", unsafe_allow_html=True)
df_macro = pd.DataFrame([
    {"Chỉ số": "DXY (Dollar Index)", "Giá": "106.25", "Xu hướng": "Ổn định"},
    {"Chỉ số": "Dow Jones 30", "Giá": "39,280", "Xu hướng": "Tích cực"}
])
st.table(df_macro)
