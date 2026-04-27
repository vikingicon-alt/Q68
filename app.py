import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# --- 1. CẤU TRÚC GIAO DIỆN BẢO MẬT & TỐI ƯU HÓA CAO (FIX 64886ad4) ---
st.set_page_config(page_title="A1 MASTER V33.0", layout="wide", page_icon="🐢")

# Ép CSS để Sidebar không bao giờ méo và các widget không bị ẩn (Fix 7ef5b06e)
st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] { 
        background-color: #161b22 !important; 
        border-right: 2px solid #FFD700; 
        min-width: 320px !important;
    }
    /* Tối ưu hóa các nút bấm cho cảm ứng iPad */
    .stButton > button {
        width: 100%; height: 55px; border-radius: 12px;
        background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
        color: #000; font-weight: 900; font-size: 18px; border: none;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    .stMetric { 
        background-color: #1e293b; padding: 15px; border-radius: 12px; 
        border: 1px solid #FFD700; 
    }
    .status-box {
        padding: 25px; border-radius: 15px; text-align: center;
        font-weight: 900; font-size: 26px; border: 3px solid #FFD700;
        margin-bottom: 25px; box-shadow: 0 0 20px rgba(255, 215, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ TRẠNG THÁI HỆ THỐNG (STATE MANAGEMENT) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'lang' not in st.session_state: st.session_state['lang'] = "Tiếng Việt"

# --- 3. MÀN HÌNH XÁC THỰC ĐA NGÔN NGỮ (FIX TRIỆT ĐỂ LỖI LIỆT 64886ad4) ---
if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=160)
        
        # FIX: Dùng Radio nhưng có Callback để ép iPad cập nhật ngay lập tức
        def change_lang(): pass 
        
        st.session_state['lang'] = st.radio(
            "CHỌN NGÔN NGỮ / SELECT LANGUAGE", 
            ["Tiếng Việt", "English"], 
            horizontal=True, 
            key="lang_selector",
            on_change=change_lang
        )
        
        # Logic hiển thị nội dung theo ngôn ngữ đã chọn (Fix ff6a0287)
        if st.session_state['lang'] == "Tiếng Việt":
            st.markdown("<h1 style='color: #FFD700;'>HỆ THỐNG A1 GLOBAL</h1>", unsafe_allow_html=True)
            pwd = st.text_input("MẬT KHẨU TRUY CẬP (A1PRO)", type="password", key="pwd_vn")
            btn_txt = "KÍCH HOẠT HỆ THỐNG"
            err_txt = "Mật khẩu không chính xác!"
        else:
            st.markdown("<h1 style='color: #FFD700;'>A1 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
            pwd = st.text_input("ENTER PASSWORD (A1PRO)", type="password", key="pwd_en")
            btn_txt = "ACTIVATE SYSTEM"
            err_txt = "Incorrect Password!"

        if st.button(btn_txt):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error(err_txt)
    st.stop()

# --- 4. CƠ CHẾ LẤY DỮ LIỆU CHỐNG TREO "FAIL-SAFE" (FIX 21b0263b) ---
@st.cache_data(ttl=15)
def fetch_data_robust(symbol, interval):
    # Thử kết nối qua nhiều cổng khác nhau để tránh bị iPad chặn (Fix 6e6163db)
    endpoints = ["https://api.binance.com", "https://api1.binance.com", "https://api3.binance.com"]
    for url_base in endpoints:
        try:
            url = f"{url_base}/api/v3/klines?symbol={symbol}&interval={interval}&limit=150"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                df = pd.DataFrame(data, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
                df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
                
                # Tính toán các chỉ báo A1 chuyên sâu (Fix b1e208ca)
                df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
                delta = df['C'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
                return df
        except:
            continue
    return None

# --- 5. BẢNG ĐIỀU KHIỂN CHIẾN THUẬT (SIDEBAR) ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=110)
    st.markdown("<h2 style='color: #FFD700;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #888;'>Cập nhật: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    coin = st.selectbox("LỰA CHỌN TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT", "BNBUSDT"])
    tf = st.selectbox("KHUNG THỜI GIAN", ["15m", "1h", "4h", "1d", "1w"], index=1)
    
    st.markdown("---")
    # Lựa chọn hiển thị (Fix b6c600f2)
    view_type = st.radio("CHẾ ĐỘ BIỂU ĐỒ", ["Đầy đủ (Full)", "Đường kẻ (Line)", "Vùng (Area)"])
    
    st.divider()
    if st.button("THOÁT HỆ THỐNG"):
        st.session_state['auth'] = False
        st.rerun()

# --- 6. HIỂN THỊ KẾT QUẢ & CHỈ BÁO A1 ---
df_final = fetch_data_robust(coin, tf)

if df_final is not None:
    last_row = df_final.iloc[-1]
    price, rsi, ema = last_row['C'], last_row['RSI'], last_row['EMA20']
    # Hệ thống đèn tín hiệu A1 (Dựa trên EMA20 và RSI)
    if price > ema and rsi < 70:
        status, s_color, b_color = "TÍN HIỆU: MUA (A1 BULLISH)", "#10b981", "#064e3b"
    elif price < ema and rsi > 30:
        status, s_color, b_color = "TÍN HIỆU: BÁN (A1 BEARISH)", "#ef4444", "#450a0a"
    else:
        status, s_color, b_color = "TÍN HIỆU: CHỜ (A1 NEUTRAL)", "#f59e0b", "#451a03"
    
    st.markdown(f'<div class="status-box" style="color: {s_color}; background: {b_color};">{status}</div>', unsafe_allow_html=True)
    
    # Biểu đồ chính (Fix lỗi mất chỉ báo 21b0263b)
    st.subheader(f"Biểu đồ {coin} ({tf})")
    if view_type == "Đầy đủ (Full)":
        st.line_chart(df_final[['C', 'EMA20']])
    elif view_type == "Đường kẻ (Line)":
        st.line_chart(df_final['C'])
    else:
        st.area_chart(df_final['C'])
        
    # Chỉ báo RSI phụ
    st.subheader("Chỉ báo RSI (14)")
    st.line_chart(df_final['RSI'])
    
    # Thông số Metric
    m1, m2, m3 = st.columns(3)
    m1.metric("GIÁ HIỆN TẠI", f"${price:,.2f}")
    m2.metric("RSI (14)", f"{rsi:.2f}")
    m3.metric("EMA 20", f"{ema:,.2f}")
else:
    # Cơ chế tự phục hồi nếu mất kết nối (Fix 21b0263b)
    st.warning("⚠️ Đang thiết lập lại kết nối dữ liệu an toàn...")
    time.sleep(3)
    st.rerun()
