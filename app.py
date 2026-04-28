import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# --- 1. CẤU TRÚC GIAO DIỆN SIÊU CẤP (FIX 6a03b831, 7bb4d22f) ---
st.set_page_config(page_title="A1 SUPREME V37", layout="wide")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #0d1117 !important; color: white; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 2px solid #FFD700; min-width: 320px !important; }
    /* Nút bấm lớn cho iPad */
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); 
        color: black; font-weight: 900; border-radius: 12px; height: 55px; border: none;
    }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #FFD700; }
    .login-card { 
        background: #161b22; padding: 30px; border-radius: 20px; 
        border: 2px solid #FFD700; text-align: center; box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. MÀN HÌNH ĐĂNG NHẬP HOÀN CHỈNH (CÓ MÃ QR BÊN NGOÀI - FIX THEO Ý ANH) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=180)
        st.markdown("<h1 style='color: #FFD700;'>A1 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
        
        # Bố cục 2 cột cho Mật khẩu và Mã QR hỗ trợ (Fix yêu cầu đưa QR ra ngoài)
        c1, c2 = st.columns([1.5, 1])
        with c1:
            lang = st.selectbox("NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"])
            pwd = st.text_input("MẬT KHẨU (A1PRO)", type="password", help="Nhập mật khẩu để kích hoạt hệ thống")
        with c2:
            st.markdown("<p style='font-size: 12px; color: gold;'>QUÉT TRUY CẬP</p>", unsafe_allow_html=True)
            st.image("https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=A1-PRO-ACCESS")
            
        if st.button("KÍCH HOẠT HỆ THỐNG V37.0"):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("❌ Mật khẩu chưa chính xác! Vui lòng kiểm tra lại.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. CƠ CHẾ LẤY DỮ LIỆU "FAST-TRACK" (KHÔNG TREO - FIX 21b0263b, dabfe0a4) ---
@st.cache_data(ttl=10) # Tự động làm mới mỗi 10 giây
def fetch_market_data(symbol, tf):
    try:
        # Sử dụng API tối giản để iPad không bị quá tải
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=100"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            df = pd.DataFrame(r.json(), columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
            df['C'] = df['C'].astype(float)
            # Chỉ báo A1 Master
            df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
            delta = df['C'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            return df
    except: return None
    return None

# --- 4. GIAO DIỆN QUẢN LÝ (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='color: #FFD700; text-align: center;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    st.divider()
    
    coin = st.selectbox("CHỌN TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT", "BNBUSDT"])
    tf_choice = st.selectbox("KHUNG THỜI GIAN", ["15m", "1h", "4h", "1d"], index=1)
    view_mode = st.radio("KIỂU HIỂN THỊ", ["Nến & EMA20", "Đường Kẻ (Line)", "Vùng (Area)"])
    
    st.divider()
    st.write("DỰ ÁN A1 - QR HỖ TRỢ")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=A1-SUPPORT-V37", caption="QR HỆ THỐNG")
    
    if st.button("THOÁT HỆ THỐNG"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHÍNH (FIX LỖI Index 7bb4d22f & TREO dabfe0a4) ---
df_core = fetch_market_data(coin, tf_choice)

if df_core is not None and not df_core.empty:
    last = df_core.iloc[-1]
    curr_p, curr_r, curr_e = last['C'], last['RSI'], last['EMA20']
    
    # Tín hiệu đèn giao thông A1
    if curr_p > curr_e and curr_r < 70:
        st.success(f"🚀 TÍN HIỆU A1: MUA (Giá {curr_p:,.1f} nằm trên EMA20)")
    elif curr_p < curr_e and curr_r > 30:
        st.error(f"📉 TÍN HIỆU A1: BÁN (Giá {curr_p:,.1f} nằm dưới EMA20)")
    else:
        st.warning("⚖️ TÍN HIỆU A1: CHỜ (Thị trường đang tích lũy)")

    # Biểu đồ chính
    st.subheader(f"Biểu đồ phân tích {coin}")
    if view_mode == "Nến & EMA20":
        st.line_chart(df_core[['C', 'EMA20']])
    elif view_mode == "Đường Kẻ (Line)":
        st.line_chart(df_core['C'])
    else:
        st.area_chart(df_core['C'])

    # Thông số Metric
    col1, col2 = st.columns(2)
    col1.metric("GIÁ HIỆN TẠI", f"${curr_p:,.2f}")
    col2.metric("CHỈ SỐ RSI", f"{curr_r:.2f}")
else:
    # Fix lỗi treo dabfe0a4: Thêm nút tải lại thủ công nếu API bị nghẽn
    st.info("🔄 Đang đợi dữ liệu từ sàn Binance... Nếu quá 10 giây không thấy biểu đồ, anh hãy bấm nút bên dưới.")
    if st.button("TẢI LẠI DỮ LIỆU NGAY"):
        st.rerun()
