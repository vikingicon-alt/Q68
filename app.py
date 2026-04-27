import streamlit as st
import pandas as pd
import requests
import time

# --- 1. CẤU TRÚC GIAO DIỆN CHỐNG TRÀN BỘ NHỚ (FIX 21b0263b) ---
st.set_page_config(page_title="A1 MASTER V31.0", layout="wide")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 2px solid gold; min-width: 300px !important; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid gold; }
    div.stButton > button { width: 100%; background: linear-gradient(to right, gold, orange); color: black; font-weight: bold; border-radius: 10px; height: 50px; border: none; }
    .signal-banner { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 24px; border: 2px solid gold; margin-bottom: 25px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG XÁC THỰC VÀ NGÔN NGỮ ĐỒNG NHẤT (FIX ff6a0287 & bc812bd3) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=150)
        st.markdown("<h2 style='color: gold;'>HỆ THỐNG A1 GLOBAL</h2>", unsafe_allow_html=True)
        # Fix triệt để lỗi mất ngôn ngữ
        lang = st.radio("CHỌN NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"], horizontal=True, key="lang_v31")
        pwd = st.text_input("MẬT KHẨU TRUY CẬP", type="password")
        if st.button("KÍCH HOẠT V31.0"):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Mật khẩu không chính xác!")
    st.stop()

# --- 3. ĐỘNG CƠ DỮ LIỆU THỰC THỜI (ANTI-LAG) ---
def fetch_a1_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=120"
        res = requests.get(url, timeout=7).json()
        df = pd.DataFrame(res, columns=['time','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df['C'] = df['C'].astype(float)
        # Chỉ báo lõi của Anh
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        return df
    except: return None

# --- 4. SIDEBAR ĐIỀU KHIỂN CHUYÊN NGHIỆP (BỔ SUNG CHỈ BÁO) ---
with st.sidebar:
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    st.divider()
    coin = st.selectbox("CHỌN TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    tf = st.selectbox("KHUNG GIỜ", ["15m", "1h", "4h", "1d", "1w"], index=1)
    
    st.markdown("---")
    # Phải có nút đổi hiển thị như anh dặn
    view_mode = st.radio("CHỌN KIỂU BIỂU ĐỒ", ["Nến & EMA20", "Đường Kẻ (Line)", "Vùng (Area)"], key="view_v31")
    
    st.divider()
    if st.button("LOGOUT / THOÁT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHÍNH XÁC TUYỆT ĐỐI ---
data = fetch_a1_data(coin, tf)

if data is not None:
    last = data.iloc[-1]
    p, r, e = last['C'], last['RSI'], last['EMA20']
    
    # Tín hiệu Mua/Bán rực rỡ
    if p > e and r < 70:
        st.markdown(f'<div class="signal-banner" style="color: #10b981; background: #064e3b;">TÍN HIỆU: MUA (BULLISH)</div>', unsafe_allow_html=True)
    elif p < e and r > 30:
        st.markdown(f'<div class="signal-banner" style="color: #ef4444; background: #450a0a;">TÍN HIỆU: BÁN (BEARISH)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-banner" style="color: #f59e0b; background: #451a03;">TÍN HIỆU: THEO DÕI</div>', unsafe_allow_html=True)
    
    # Vẽ biểu đồ theo lựa chọn của Anh (Dùng engine gốc để không bị mất chỉ báo)
    if view_mode == "Nến & EMA20":
        st.write("### BIỂU ĐỒ GIÁ & ĐƯỜNG KẺ EMA20")
        st.line_chart(data[['C', 'EMA20']])
    elif view_mode == "Đường Kẻ (Line)":
        st.line_chart(data['C'])
    else:
        st.area_chart(data['C'])
    
    st.write("### CHỈ BÁO NỀN: RSI (14)")
    st.line_chart(data['RSI'])
    
    c1, c2 = st.columns(2)
    c1.metric("GIÁ HIỆN TẠI", f"${p:,.1f}")
    c2.metric("RSI", f"{r:.2f}")
else:
    st.error("⚠️ Hệ thống đang kết nối lại dữ liệu... Vui lòng chờ 3 giây.")
    time.sleep(3)
    st.rerun()
