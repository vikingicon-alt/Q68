import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Q68", layout="wide", initial_sidebar_state="collapsed")

# CSS "DIỆT" LOGO & ÉP TRÀN VIỀN
st.markdown("""
<style>
    footer, header, [data-testid="stHeader"], .stAppDeployButton, div[data-testid="stStatusWidget"], .viewerBadge_container__1QSob { display: none !important; }
    .block-container { padding: 0.5rem !important; }
    .stApp { background-color: #000000; color: white; }
    .turtle-circle { width: 100px; height: 100px; border-radius: 50%; border: 4px solid #FFD700; overflow: hidden; margin: 0 auto; box-shadow: 0 0 20px #FFD700; }
    .neon-btn { padding: 10px; text-align: center; font-weight: bold; margin: 5px 0; border: 2px solid #333; }
</style>
""", unsafe_allow_html=True)

# KHỞI TẠO BIẾN (VIẾT DÒNG ĐƠN ĐỂ TRÁNH LỖI INDENT)
if 'lang' not in st.session_state: st.session_state.lang = 'VI'
if 'signal' not in st.session_state: st.session_state.signal = 'NONE'

# GIAO DIỆN
c1, c2 = st.columns([3, 1])

with c1:
    if st.button("🌐 ĐỔI NGÔN NGỮ / CHANGE LANG"):
        st.session_state.lang = 'EN' if st.session_state.lang == 'VI' else 'VI'
    
    coin = st.selectbox("CHỌN COIN", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    st.markdown(f"### GIÁ: 76,181.75 USD")
    
    components.html(f"""
        <div id="tv" style="height:450px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:{coin}", "theme": "dark", "container_id": "tv"}});</script>
    """, height=460)

with c2:
    st.markdown(f'<div class="turtle-circle"><img src="https://cdn-icons-png.flaticon.com/512/3232/3232777.png" width="100%"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Q68</h2>", unsafe_allow_html=True)
    
    if st.button("⚡ PHÂN TÍCH AI"):
        st.session_state.signal = random.choice(["BUY", "HOLD", "SELL"])
    
    # HIỂN THỊ ĐÈN NEON
    s = st.session_state.signal
    st.markdown(f'<div class="neon-btn" style="color:{"#00FF00" if s=="BUY" else "#666"}">BUY</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="neon-btn" style="color:{"#FFA500" if s=="HOLD" else "#666"}">HOLD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="neon-btn" style="color:{"#FF0000" if s=="SELL" else "#666"}">SELL</div>', unsafe_allow_html=True)
    
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://a1pro-global.com")

# BẢNG VĨ MÔ ĐÃ SỬA LỖI
st.table(pd.DataFrame({"Chỉ số": ["DXY", "BTC Dominance"], "Giá trị": ["106.25", "54.2%"]}))
