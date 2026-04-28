import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# --- 1. CẤU TRÚC GIAO DIỆN BỀN VỮNG (ANTI-CRASH) ---
st.set_page_config(page_title="A1 MASTER V36.0", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 2px solid gold; min-width: 300px !important; }
    div.stButton > button { width: 100%; background: gold; color: black; font-weight: bold; border-radius: 10px; height: 50px; border: none; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid gold; }
    .signal-card { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 24px; border: 2px solid gold; margin-bottom: 25px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG XÁC THỰC AN TOÀN (FIX 46cce953, 64886ad4) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=150)
        st.markdown("<h2 style='color: gold;'>A1 GLOBAL SYSTEM</h2>", unsafe_allow_html=True)
        
        # Dùng Selectbox để tránh bị "liệt" trên Safari iPad (Fix 64886ad4)
        lang = st.selectbox("NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"])
        label_pwd = "MẬT KHẨU (A1PRO)" if lang == "Tiếng Việt" else "PASSWORD (A1PRO)"
        btn_txt = "KÍCH HOẠT V36.0" if lang == "Tiếng Việt" else "ACTIVATE V36.0"
        
        pwd = st.text_input(label_pwd, type="password")
        if st.button(btn_txt):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Sai mật khẩu!")
    st.stop()

# --- 3. ĐỘNG CƠ DỮ LIỆU CÓ LỚP BẢO VỆ (FIX IndexError 7bb4d22f) ---
def get_a1_master_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=120"
        r = requests.get(url, timeout=10)
        if r.status_code != 200: return None
        
        data = r.json()
        if not data or len(data) < 50: return None # Bảo vệ nếu dữ liệu quá ít
        
        df = pd.DataFrame(data, columns=['time','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df['C'] = df['C'].astype(float)
        
        # Chỉ báo A1 (EMA20 & RSI)
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        u, d = (delta.where(delta > 0, 0)).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (u / (d + 1e-10))))
        return df
    except Exception:
        return None

# --- 4. THANH ĐIỀU KHIỂN & MÃ QR (FIX 6a03b831, 21b0263b) ---
with st.sidebar:
    st.markdown("<h2 style='color: gold; text-align: center;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray;'>Cập nhật: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    st.divider()
    
    coin = st.selectbox("TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    tf = st.selectbox("KHUNG GIỜ", ["15m", "1h", "4h", "1d", "1w"], index=1)
    view = st.radio("HIỂN THỊ", ["Nến & EMA20", "Đường Kẻ", "Vùng"])
    
    st.divider()
    # Mã QR - Mẫu Gà quản lý hệ thống (Fix 6a03b831)
    st.write("A1 GLOBAL QR")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=A1-GLOBAL-V36", caption="QUÉT ĐỂ TRUY CẬP")
    
    st.divider()
    if st.button("THOÁT HỆ THỐNG"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ KẾT QUẢ VÀ XỬ LÝ LỖI TRIỆT ĐỂ ---
data_df = get_a1_master_data(coin, tf)

if data_df is not None and not data_df.empty:
    # Lấy nến cuối cùng an toàn (Fix lỗi 7bb4d22f)
    curr = data_df.iloc[-1]
    p, r, e = curr['C'], curr['RSI'], curr['EMA20']
    
    # Tín hiệu A1
    if p > e and r < 70:
        st.markdown('<div class="signal-card" style="color:#10b981; background:#064e3b;">TÍN HIỆU: MUA (A1 UP)</div>', unsafe_allow_html=True)
    elif p < e and r > 30:
        st.markdown('<div class="signal-card" style="color:#ef4444; background:#450a0a;">TÍN HIỆU: BÁN (A1 DOWN)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-card" style="color:#f59e0b; background:#451a03;">TÍN HIỆU: CHỜ (A1 WAIT)</div>', unsafe_allow_html=True)

    # Biểu đồ (Fix b6c600f2)
    st.write(f"### BIỂU ĐỒ {coin} - {tf}")
    if view == "Nến & EMA20":
        st.line_chart(data_df[['C', 'EMA20']])
    elif view == "Đường Kẻ":
        st.line_chart(data_df['C'])
    else:
        st.area_chart(data_df['C'])
        
    st.write("### CHỈ SỐ RSI (14)")
    st.line_chart(data_df['RSI'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("GIÁ", f"${p:,.1f}")
    c2.metric("RSI", f"{r:.2f}")
    c3.metric("EMA20", f"{e:,.1f}")
else:
    # Thông báo thay thế thay vì hiện bảng lỗi (Fix 7bb4d22f, 21b0263b)
    st.warning("⚠️ Hệ thống đang kết nối lại với dữ liệu thị trường... Vui lòng chờ trong giây lát!")
    time.sleep(3)
    st.rerun()
