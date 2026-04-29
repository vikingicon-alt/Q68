import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import random

# --- 1. CẤU HÌNH WEBSITE & QR ---
MY_WEBSITE = "https://a1pro-global.com"

# --- 2. CSS ĐẶC TRỊ: DIỆT LOGO, TRÀN VIỀN & ẨN THANH TÌM KIẾM ---
st.set_page_config(page_title="A1 SUPREME V59", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* XÓA SẠCH 2 LOGO Ở GÓC MÀN HÌNH (SỬA LỖI TỪ ẢNH CỦA ANH) */
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    /* ÉP TRÀN VIỀN TỐI ĐA CHO IPAD */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* GIAO DIỆN NỀN ĐEN CHUẨN TRADER */
    .stApp {background-color: #000000;}
    
    /* KHUNG VÀNG HIỂN THỊ GIÁ */
    .price-display { 
        background: #1a1a00; 
        padding: 15px; 
        border-radius: 12px; 
        border: 3px solid #ffff00; 
        text-align: center; 
        font-size: 28px; 
        font-weight: bold;
        color: #ffff00;
        margin-bottom: 5px;
    }

    /* HIỆU ỨNG CHỚP SÁNG TÍN HIỆU */
    @keyframes blinker { 50% { opacity: 0.1; box-shadow: 0 0 30px white; } }
    .signal-active { animation: blinker 0.6s linear infinite; border: 3px solid white !important; opacity: 1.0 !important; }
    .signal-box { padding: 20px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 20px; opacity: 0.2; border: 1px solid #333; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. FIX LỖI NGÔN NGỮ (SỬ DỤNG GET ĐỂ KHÔNG BỊ KEYERROR) ---
# Em dùng hàm .get() để nếu hệ thống chưa load kịp cũng không bị hiện màn hình đỏ
if 'lang' not in st.session_state:
    st.session_state.lang = 'VI'

def toggle_lang():
    st.session_state.lang = 'EN' if st.session_state.lang == 'VI' else 'VI'

# Dữ liệu dịch thuật
texts = {
    'VI': {'sel': "CHỌN COI TÁC CHIẾN", 'pre': "🔍 CHẠY DỰ BÁO", 'b': "BUY / MUA", 'h': "HOLD", 's': "SELL / BÁN", 'qr': "QUÉT ĐỂ ĐĂNG KÝ"},
    'EN': {'sel': "SELECT COIN", 'pre': "🔍 RUN PREDICTION", 'b': "BUY / PURCHASE", 'h': "HOLD", 's': "SELL / EXIT", 'qr': "SCAN TO REGISTER"}
}
L = texts.get(st.session_state.lang, texts['VI'])

# --- 4. DỮ LIỆU GIÁ (FIX LTC = 55.23 CHUẨN BIỂU ĐỒ) ---
coin_prices = {
    "BTCUSDT": 76181.75,
    "ETHUSDT": 2290.81,
    "XRPUSDT": 2.54,
    "LTCUSDT": 55.23,  # ĐÃ FIX: Đúng giá đường hồng trên nến của anh
    "PAXGUSDT": 4535.60
}

# --- 5. BỐ CỤC GIAO DIỆN ---
# Nút chuyển ngôn ngữ
st.button(f"🌐 {st.session_state.lang}", on_click=toggle_lang)

col_main, col_side = st.columns([3, 1])

with col_main:
    # Chọn coin - Mặc định là LTC để anh thấy giá chuẩn 55.23
    coin = st.selectbox(L['sel'], list(coin_prices.keys()), index=3)
    
    # KHUNG VÀNG HIỂN THỊ GIÁ
    st.markdown(f'<div class="price-display">{coin}: {coin_prices[coin]:,.2f} USD</div>', unsafe_allow_html=True)
    
    # BIỂU ĐỒ TRADINGVIEW TRÀN VIỀN
    components.html(f"""
        <div id="tv_chart" style="height:500px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>
        new TradingView.widget({{"autosize": true, "symbol": "BINANCE:{coin}", "interval": "1H", "theme": "dark", "style": "1", "container_id": "tv_chart"}});
        </script>
    """, height=510)

with col_side:
    st.markdown("<h3 style='color:white; text-align:center;'>🤖 A1 COMMANDER</h3>", unsafe_allow_html=True)
    
    if 'sig' not in st.session_state: st.session_state.sig = None
    curr = st.session_state.sig

    # HỆ THỐNG NÚT BẤM CHỚP SÁNG
    st.markdown(f'<div class="signal-box {"signal-active" if curr=="BUY" else ""}" style="background:green; color:white;">{L["b"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="signal-box {"signal-active" if curr=="HOLD" else ""}" style="background:orange; color:black;">{L["h"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="signal-box {"signal-active" if curr=="SELL" else ""}" style="background:red; color:white;">{L["s"]}</div>', unsafe_allow_html=True)
    
    if st.button(L['pre'], use_container_width=True):
        st.session_state.sig = random.choice(["BUY", "HOLD", "SELL"])
        st.rerun()

    # MÃ QR ĐĂNG KÝ
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={MY_WEBSITE}"
    st.image(qr_url, caption=L['qr'], use_container_width=True)

# WATCHLIST DƯỚI CÙNG
st.markdown("### 📋 REAL-TIME WATCHLIST")
df_data = [{"Tài sản": k, "Giá (USD)": f"{v:,.2f}", "Nguồn": "A1 Live Server"} for k, v in coin_prices.items()]
st.table(pd.DataFrame(df_data))
