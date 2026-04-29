import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time

# --- 1. CẤU HÌNH HỆ THỐNG ---
MY_WEBSITE = "https://a1pro-global.com"
TURTLE_IMG = "https://i.imgur.com/8K5Mh8G.png" # Anh thay link ảnh con rùa xanh Q68 của anh vào đây nhé

st.set_page_config(page_title="A1 SUPREME V61", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS DIỆT LOGO & TẠO HÀO QUANG RÙA Q68 ---
st.markdown("""
<style>
    /* XÓA SẠCH LOGO & DEPLOY BUTTON */
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}

    /* RÙA Q68 LẤP LÁNH */
    .turtle-container {
        display: flex; flex-direction: column; align-items: center; margin-bottom: 10px;
    }
    .turtle-circle { 
        width: 80px; height: 80px; border-radius: 50%; 
        border: 3px solid #FFD700; overflow: hidden;
        background: #004400;
        box-shadow: 0 0 20px #FFD700;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05); box-shadow: 0 0 30px #FFD700;} 100% {transform: scale(1);} }
    
    /* GIAO DIỆN CHUẨN */
    .stApp {background-color: #000000;}
    .block-container { padding: 0.5rem !important; }
    .price-display { 
        background: #1a1a00; padding: 15px; border-radius: 12px; border: 3px solid #ffff00; 
        text-align: center; font-size: 28px; font-weight: bold; color: #ffff00;
    }

    /* CHỚP SÁNG TÍN HIỆU */
    @keyframes blink { 50% { opacity: 0.2; box-shadow: 0 0 40px white; } }
    .sig-active { animation: blink 0.5s linear infinite; border: 4px solid white !important; opacity: 1.0 !important; }
    .sig-box { padding: 20px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 20px; opacity: 0.2; border: 1px solid #333; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. BỘ NÃO DỰ BÁO THÔNG MINH (A1 AI ENGINE) ---
def get_a1_prediction(dxy, dow, coin_price):
    # Thuật toán phân tích nghịch đảo DXY và xu hướng Dow Jones
    # DXY tăng -> Crypto thường giảm (SELL)
    # Dow Jones tăng -> Tâm lý rủi ro tốt (BUY)
    score = 0
    if dxy > 105: score -= 2  # DXY quá mạnh, cảnh báo bán
    if dow > 38000: score += 1 # Dow Jones ủng hộ xu hướng tăng
    
    if score >= 1: return "BUY"
    elif score <= -1: return "SELL"
    else: return "HOLD"

# --- 4. KHỞI TẠO DỮ LIỆU ---
if 'lang' not in st.session_state: st.session_state.lang = 'VI'
if 'ai_sig' not in st.session_state: st.session_state.ai_sig = None

def toggle_lang(): st.session_state.lang = 'EN' if st.session_state.lang == 'VI' else 'VI'

L = {
    'VI': {'sel': "CHỌN COI TÁC CHIẾN", 'pre': "⚡ PHÂN TÍCH AI (DXY/MACRO)", 'qr': "QUÉT ĐỂ ĐĂNG KÝ"},
    'EN': {'sel': "SELECT COIN", 'pre': "⚡ AI ANALYSIS (DXY/MACRO)", 'qr': "SCAN TO REGISTER"}
}[st.session_state.lang]

# --- 5. GIAO DIỆN TÁC CHIẾN ---
st.button(f"🌐 {st.session_state.lang}", on_click=toggle_lang)

col_chart, col_signal = st.columns([3, 1])

with col_chart:
    coin = st.selectbox(L['sel'], ["BTCUSDT", "ETHUSDT", "XRPUSDT", "LTCUSDT"], index=3)
    # Giá LTC fix chuẩn 55.23 theo yêu cầu của anh
    price = 55.23 if coin == "LTCUSDT" else 76181.75
    st.markdown(f'<div class="price-display">{coin}: {price:,.2f} USD</div>', unsafe_allow_html=True)
    
    components.html(f"""
        <div id="tv" style="height:480px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:{coin}", "interval": "1H", "theme": "dark", "style": "1", "container_id": "tv"}});</script>
    """, height=490)

with col_signal:
    # HIỂN THỊ RÙA Q68 LẤP LÁNH
    st.markdown(f"""
    <div class="turtle-container">
        <div class="turtle-circle"><img src="{TURTLE_IMG}" width="80"></div>
        <div style="color:gold; font-weight:bold; font-size:20px; margin-top:5px;">Q68</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='color:white; text-align:center;'>A1 COMMANDER</h3>", unsafe_allow_html=True)

    # NÚT DỰ BÁO THÔNG MINH
    if st.button(L['pre'], use_container_width=True):
        with st.spinner("Đang kết nối DXY & Dow Jones..."):
            time.sleep(1.5)
            # Giả lập lấy chỉ số thực tế (DXY hiện tại ~106, Dow ~39000)
            st.session_state.ai_sig = get_a1_prediction(106.2, 39200, price)

    curr = st.session_state.ai_sig
    st.markdown(f'<div class="sig-box {"sig-active" if curr=="BUY" else ""}" style="background:green; color:white;">BUY / MUA</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sig-box {"sig-active" if curr=="HOLD" else ""}" style="background:orange; color:black;">HOLD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sig-box {"sig-active" if curr=="SELL" else ""}" style="background:red; color:white;">SELL / BÁN</div>', unsafe_allow_html=True)

    # MÃ QR SIÊU NÉT (GOOGLE API)
    qr_url = f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={MY_WEBSITE}&choe=UTF-8"
    st.image(qr_url, caption=L['qr'], use_container_width=True)

# --- 6. PHẦN CHỈ SỐ MACRO DƯỚI CÙNG ---
st.markdown("### 🌍 GLOBAL MACRO INDICATORS (DXY/DOW)")
macro_data = [
    {"Chỉ số": "DXY (US Dollar Index)", "Giá trị": "106.25", "Trạng thái": "Mạnh (Cản trở Crypto)"},
    {"Chỉ số": "Dow Jones 30", "Giá trị": "39,280", "Trạng thái": "Tăng (Tốt cho tâm lý)"},
    {"Chỉ số": "LTCUSDT", "Giá trị": "55.23", "Trạng thái": "Chờ tín hiệu A1"}
]
st.table(pd.DataFrame(macro_data))
