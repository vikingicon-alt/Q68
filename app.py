import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. ĐỊNH DẠNG GIAO DIỆN CHUẨN IPAD (FIX MÉO VÀ LỆCH) ---
st.set_page_config(page_title="Q68 MASTER V25", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #020617 !important; }
    /* Cố định Sidebar: Chống méo rùa và lệch chữ Q68 Master */
    [data-testid="stSidebar"] { 
        background-color: #0d1117 !important; 
        border-right: 2px solid gold; 
        min-width: 300px !important;
    }
    .st-emotion-cache-16idsys p { font-size: 16px; color: gold; font-weight: bold; }
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); 
        color: black; font-weight: 900; border-radius: 10px; border: none; height: 48px;
    }
    .status-card { 
        padding: 20px; background: #161b22; border: 2px solid gold; 
        border-radius: 15px; text-align: center; margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(218, 165, 32, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG ĐĂNG NHẬP (FIX LỖI TRÀN MÃ LOG) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=180)
        st.markdown("<h2 style='color: gold;'>Q68 MASTER - A1</h2>", unsafe_allow_html=True)
        pwd = st.text_input("NHẬP MÃ KÍCH HOẠT", type="password", key="pwd_input")
        if st.button("XÁC NHẬN KÍCH HOẠT V25"):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

# --- 3. ĐỘNG CƠ DỮ LIỆU SIÊU TỐC (CHỐNG TREO MÀU VÀNG/ĐỎ) ---
@st.cache_data(ttl=5)
def get_a1_master_data(symbol, interval):
    try:
        # Giả lập trình duyệt để tránh bị sàn chặn trên thiết bị di động
        h = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X)'}
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=120"
        res = requests.get(url, headers=h, timeout=15).json()
        if not isinstance(res, list) or len(res) < 50: return None
        
        df = pd.DataFrame(res, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
        
        # Chỉ báo A1 chuẩn: EMA20 & RSI14
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        change = df['C'].diff()
        gain = (change.where(change > 0, 0)).rolling(14).mean()
        loss = (-change.where(change < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        return df
    except: return None

# --- 4. SIDEBAR CÂN ĐỐI TUYỆT ĐỐI (FIX MÉO) ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=120)
    st.markdown("<h2 style='color: gold; margin-top: -10px;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    coin = st.selectbox("CHỌN TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "PAXGUSDT"])
    # Đầy đủ khung giờ theo đúng dự án A1
    tfs = {"15m":"15 Phút", "30m":"30 Phút", "1h":"1 Giờ", "4h":"4 Giờ", "1d":"1 Ngày", "1w":"1 Tuần", "1M":"1 Tháng"}
    tf = st.selectbox("KHUNG THỜI GIAN", list(tfs.keys()), format_func=lambda x: tfs[x], index=2)
    style = st.radio("KIỂU HIỂN THỊ", ["Nến Nhật", "Dạng Đường"], horizontal=True)
    
    st.divider()
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app", caption="A1 GLOBAL SYSTEM")
    if st.button("THOÁT HỆ THỐNG"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHIẾN THUẬT & BIỂU ĐỒ ---
df = get_a1_master_data(coin, tf)

if df is not None:
    last = df.iloc[-1]
    p, r, e = last['C'], last['RSI'], last['EMA20']
    
    # Hệ thống Đèn tín hiệu A1 (Cực nhạy)
    if p > e and r < 68:
        msg, color = "TÍN HIỆU: MUA (BUY)", "#22c55e"
    elif p < e and r > 32:
        msg, color = "TÍN HIỆU: BÁN (SELL)", "#ef4444"
    else:
        msg, color = "TÍN HIỆU: CHỜ (WAIT)", "#f59e0b"
        
    st.markdown(f"""<div class="status-card"><h2 style='color: {color}; margin:0;'>{msg}</h2></div>""", unsafe_allow_html=True)
    
    # Biểu đồ kỹ thuật
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    if style == "Nến Nhật":
        fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Price"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(y=df['C'], fill='tozeroy', line=dict(color='gold', width=2), name="Price"), row=1, col=1)
        
    fig.add_trace(go.Bar(x=df.index, y=df['V'], marker_color='rgba(255,255,255,0.2)', name="Volume"), row=2, col=1)
    fig.update_layout(height=550, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Chỉ số Master
    c1, c2, c3 = st.columns(3)
    c1.metric("GIÁ HIỆN TẠI", f"${p:,.1f}")
    c2.metric("CHỈ SỐ RSI", f"{r:.2f}")
    c3.metric("ĐƯỜNG EMA20", f"{e:,.1f}")
else:
    # Fix lỗi kẹt bằng cách tự động làm mới sau 3 giây
    st.warning("Hệ thống đang đồng bộ dữ liệu thị trường... Vui lòng chờ trong giây lát!")
    time.sleep(3)
    st.rerun()
