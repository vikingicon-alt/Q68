import streamlit as st
import pandas as pd
import requests
import time

# --- 1. GIAO DIỆN TỐI ƯU (ĐÃ FIX LỖI MẤT BIỂU ĐỒ 6a03b831) ---
st.set_page_config(page_title="A1 MASTER V35.0", layout="wide")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 2px solid gold; min-width: 300px !important; }
    div.stButton > button { width: 100%; background: gold; color: black; font-weight: bold; border-radius: 8px; height: 45px; }
    .stMetric { background-color: #1e293b; padding: 10px; border-radius: 10px; border: 1px solid gold; }
    .signal-status { padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 20px; border: 2px solid gold; margin-bottom: 20px; }
    .qr-container { background: white; padding: 10px; border-radius: 10px; text-align: center; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. XÁC THỰC (FIX LỖI LIỆT NGÔN NGỮ 64886ad4) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=120)
        st.markdown("<h2 style='color: gold;'>A1 GLOBAL SYSTEM</h2>", unsafe_allow_html=True)
        lang = st.selectbox("CHỌN NGÔN NGỮ", ["Tiếng Việt", "English"])
        pwd = st.text_input("MẬT KHẨU (A1PRO)", type="password")
        if st.button("KÍCH HOẠT HỆ THỐNG"):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

# --- 3. DỮ LIỆU THỊ TRƯỜNG ---
def get_a1_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        res = requests.get(url, timeout=5).json()
        df = pd.DataFrame(res, columns=['time','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df['C'] = df['C'].astype(float)
        # Chỉ báo lõi
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        u, d = (delta.where(delta > 0, 0)).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (u / (d + 1e-10))))
        return df
    except: return None

# --- 4. THANH ĐIỀU KHIỂN (CÓ MÃ QR NHƯ TRONG HÌNH 21b0263b) ---
with st.sidebar:
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    st.divider()
    coin = st.selectbox("TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    tf = st.selectbox("KHUNG GIỜ", ["15m", "1h", "4h", "1d", "1w"], index=1)
    mode = st.radio("CHẾ ĐỘ HIỂN THỊ", ["Nến & EMA20", "Đường Kẻ", "Vùng"])
    
    st.divider()
    # MÃ QR ĐÃ QUAY TRỞ LẠI (FIX 21b0263b, 4dbcb21d)
    st.write("A1 GLOBAL QR")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=A1-GLOBAL-SYSTEM", caption="QUÉT ĐỂ TRUY CẬP")
    
    st.divider()
    if st.button("THOÁT / LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ ---
data = get_a1_data(coin, tf)

if data is not None:
    curr = data.iloc[-1]
    p, r, e = curr['C'], curr['RSI'], curr['EMA20']
    
    if p > e and r < 70:
        st.markdown('<div class="signal-status" style="color:#10b981; background:#064e3b;">TÍN HIỆU: MUA</div>', unsafe_allow_html=True)
    elif p < e and r > 30:
        st.markdown('<div class="signal-status" style="color:#ef4444; background:#450a0a;">TÍN HIỆU: BÁN</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-status" style="color:#f59e0b; background:#451a03;">TÍN HIỆU: CHỜ</div>', unsafe_allow_html=True)

    st.write(f"### DỮ LIỆU {coin}")
    if mode == "Nến & EMA20":
        st.line_chart(data[['C', 'EMA20']])
    elif mode == "Đường Kẻ":
        st.line_chart(data['C'])
    else:
        st.area_chart(data['C'])
    
    st.write("### CHỈ SỐ RSI (14)")
    st.line_chart(data['RSI'])
    
    c1, c2 = st.columns(2)
    c1.metric("GIÁ", f"${p:,.1f}")
    c2.metric("RSI", f"{r:.2f}")
else:
    st.error("⚠️ Lỗi kết nối. Đang thử lại...")
    time.sleep(2)
    st.rerun()
