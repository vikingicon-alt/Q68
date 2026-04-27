import streamlit as st
import pandas as pd
import requests
import time

# --- 1. CẤU TRÚC GIAO DIỆN SIÊU TINH GỌN (CHỐNG TREO) ---
st.set_page_config(page_title="A1 MASTER V27", layout="wide")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 2px solid gold; min-width: 260px !important; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid gold; }
    div.stButton > button { width: 100%; background: linear-gradient(to right, #FFD700, #FFA500); color: black; font-weight: 900; border-radius: 10px; height: 50px; border: none; }
    .signal-header { padding: 20px; text-align: center; border-radius: 15px; margin-bottom: 25px; font-weight: bold; border: 2px solid gold; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG XÁC THỰC ĐỒNG NHẤT (FIX LỖI ff6a0287) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=140)
        st.markdown("<h2 style='color: gold;'>HỆ THỐNG A1 GLOBAL</h2>", unsafe_allow_html=True)
        # Đảm bảo 100% tiếng Việt đồng nhất
        st.write("---")
        pwd = st.text_input("MẬT KHẨU TRUY CẬP (A1PRO)", type="password")
        if st.button("KÍCH HOẠT HỆ THỐNG"):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Mật khẩu không chính xác!")
    st.stop()

# --- 3. LẤY DỮ LIỆU TỐI GIẢN (ÉP IPAD PHẢI HIỂN THỊ) ---
def fetch_data_direct(symbol, interval):
    try:
        # Dùng link API cơ bản nhất để không bị chặn
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=80"
        r = requests.get(url, timeout=5).json()
        df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df['C'] = df['C'].astype(float)
        # Chỉ báo A1 chuẩn của Anh
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        diff = df['C'].diff()
        u, d = (diff.where(diff > 0, 0)).rolling(14).mean(), (-diff.where(diff < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (u / (d + 1e-10))))
        return df
    except: return None

# --- 4. SIDEBAR ĐIỀU KHIỂN CÂN ĐỐI ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=100)
    st.markdown("<h3 style='color: gold;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    coin = st.selectbox("CHỌN TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    tf = st.selectbox("KHUNG THỜI GIAN", ["15m", "1h", "4h", "1d", "1w"], index=1)
    
    st.divider()
    if st.button("THOÁT HỆ THỐNG"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHIẾN THUẬT VÀ BIỂU ĐỒ ---
df = fetch_data_direct(coin, tf)

if df is not None:
    last = df.iloc[-1]
    p, r, e = last['C'], last['RSI'], last['EMA20']
    
    # Tín hiệu A1 chuẩn mực
    if p > e and r < 70:
        st.markdown(f'<div class="signal-header" style="background:#064e3b; color:#10b981;">TÍN HIỆU: MUA (BULLISH)</div>', unsafe_allow_html=True)
    elif p < e and r > 30:
        st.markdown(f'<div class="signal-header" style="background:#450a0a; color:#ef4444;">TÍN HIỆU: BÁN (BEARISH)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-header" style="background:#451a03; color:#f59e0b;">TÍN HIỆU: THEO DÕI</div>', unsafe_allow_html=True)
    
    # Biểu đồ cực nhẹ cho iPad (Fix lỗi liệt màn hình)
    st.line_chart(df[['C', 'EMA20']])
    
    col1, col2 = st.columns(2)
    col1.metric("GIÁ HIỆN TẠI", f"${p:,.1f}")
    col2.metric("CHỈ SỐ RSI", f"{r:.2f}")
else:
    st.error("⚠️ iPad đang chặn dữ liệu. Đang kết nối lại sau 3 giây...")
    time.sleep(3)
    st.rerun()
