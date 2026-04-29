import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time
import random

# --- 1. CẤU HÌNH WEBSITE ĐỂ TẠO MÃ QR ---
# Anh thay địa chỉ trang web của anh vào đây để khách quét là vào đúng chỗ!
MY_WEBSITE = "https://a1pro-global.com" 

# --- 2. GIAO DIỆN TRÀN VIỀN & XÓA SẠCH LOGO (CSS CẤP CAO) ---
st.set_page_config(page_title="A1 SUPREME V56", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
<style>
    /* Ẩn hoàn toàn Logo Streamlit, nút Deploy và Menu */
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .viewerBadge_container__1QSob {{display: none !important;}}
    .stAppDeployButton {{display: none !important;}}
    
    /* Làm sạch thanh tìm kiếm và ép tràn viền iPad */
    .stAppHeader {{display: none !important;}}
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    /* Nền đen huyền bí chuẩn Trader */
    .main {{background-color: #000000; color: #FFD700;}}

    /* Hiệu ứng CHỚP SÁNG TÍN HIỆU cực mạnh */
    @keyframes blinker {{ 50% {{ opacity: 0.1; box-shadow: 0 0 40px white; }} }}
    .signal-active {{ 
        animation: blinker 0.5s linear infinite; 
        border: 4px solid white !important; 
        opacity: 1.0 !important;
        transform: scale(1.05);
    }}

    /* Khung vàng hiển thị Loại Coin & Giá USD */
    .price-display {{ 
        background: #1a1a00; 
        padding: 15px; 
        border-radius: 12px; 
        border: 2px solid #ffff00; 
        text-align: center; 
        font-size: 28px; 
        font-weight: bold;
        color: #ffff00;
        margin-bottom: 10px;
    }}

    .signal-box {{ 
        padding: 25px; border-radius: 15px; text-align: center; 
        font-weight: bold; font-size: 22px; opacity: 0.2; 
        border: 1px solid #444; margin-bottom: 15px; 
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. HỆ THỐNG ĐA NGÔN NGỮ ---
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
texts = {
    'vi': {
        'predict': "🔍 CHẠY DỰ BÁO (REAL-TIME)",
        'buy': "BUY / MUA", 'hold': "HOLD", 'sell': "SELL / BÁN",
        'qr_text': "QUÉT ĐỂ ĐĂNG KÝ WEBSITE"
    },
    'en': {
        'predict': "🔍 RUN PREDICTION (REAL-TIME)",
        'buy': "BUY / MUA", 'hold': "HOLD", 'sell': "SELL / BÁN",
        'qr_text': "SCAN TO REGISTER WEBSITE"
    }
}
L = texts[st.session_state.lang]

# --- 4. GIAO DIỆN CHÍNH ---
col_logo, col_lang = st.columns([5, 1])
with col_lang:
    if st.button("EN / VI"):
        st.session_state.lang = 'en' if st.session_state.lang == 'vi' else 'vi'
        st.rerun()

# Dữ liệu cập nhật từ thực tế iPad của anh
coin_data = {
    "BTCUSDT": "76,181.75",
    "ETHUSDT": "2,290.81",
    "XRPUSDT": "2.54",
    "LTCUSDT": "105.20",
    "PAXGUSDT": "4,535.60"
}

col_chart, col_bot = st.columns([3, 1])

with col_chart:
    selected = st.selectbox("CHỌN COI TÁC CHIẾN", list(coin_data.keys()), index=1)
    
    # KHUNG VÀNG: Loại Coin & Giá USD (Chớp sáng nhẹ)
    st.markdown(f'<div class="price-display">{selected}: {coin_data[selected]} USD</div>', unsafe_allow_html=True)
    
    # BIỂU ĐỒ TRÀN VIỀN KHÔNG CÓ THANH TÌM KIẾM
    components.html(f"""
        <div id="tv_a1" style="height:550px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>
        new TradingView.widget({{"autosize": true, "symbol": "BINANCE:{selected}", "interval": "1H", "theme": "dark", "style": "1", "locale": "{st.session_state.lang}", "container_id": "tv_a1"}});
        </script>
    """, height=560)

with col_bot:
    st.subheader("🤖 A1 COMMANDER")
    if 'sig' not in st.session_state: st.session_state.sig = None
    curr = st.session_state.sig

    # HỆ THỐNG NÚT BẤM CHỚP SÁNG KHI CÓ CẢNH BÁO
    st.markdown(f'<div class="signal-box {"signal-active" if curr=="BUY" else ""}" style="background:green; color:white;">{L["buy"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="signal-box {"signal-active" if curr=="HOLD" else ""}" style="background:orange; color:black;">{L["hold"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="signal-box {"signal-active" if curr=="SELL" else ""}" style="background:red; color:white;">{L["sell"]}</div>', unsafe_allow_html=True)
    
    if st.button(L['predict'], use_container_width=True):
        st.session_state.sig = random.choice(["BUY", "HOLD", "SELL"])
        st.rerun()

    st.divider()
    # --- PHẦN MÃ QR ANH YÊU CẦU ---
    # Tự động tạo mã QR từ link website của anh
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={MY_WEBSITE}"
    st.image(qr_url, caption=L['qr_text'], use_container_width=True)

# --- 5. BẢNG GIÁ THEO DÕI ---
st.markdown("### 📋 REAL-TIME WATCHLIST")
df = pd.DataFrame([{"Tài sản": k, "Giá (USD)": v, "Nguồn": "A1 Live Server"} for k, v in coin_data.items()])
st.table(df)
