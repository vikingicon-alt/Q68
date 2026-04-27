import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time
from datetime import datetime

# --- 1. KIẾN TRÚC GIAO DIỆN CHUẨN IPAD (SIÊU CẤP BẢO MẬT & ĐẸP) ---
st.set_page_config(page_title="Q68 MASTER A1", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #020617 !important; }
    /* Fix Sidebar méo mó: Cố định độ rộng và font chữ */
    [data-testid="stSidebar"] { 
        background-color: #0d1117 !important; 
        border-right: 2px solid #FFD700; 
        min-width: 320px !important;
    }
    .st-emotion-cache-16idsys p { font-size: 16px; color: #FFD700; font-weight: bold; }
    /* Nút bấm hiệu ứng Neon Gold */
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); 
        color: black; font-weight: 900; border-radius: 12px; border: none; height: 50px;
        box-shadow: 0 4px 15px rgba(218, 165, 32, 0.4);
    }
    /* Khung hiển thị Tín hiệu A1 */
    .a1-status-box { 
        padding: 25px; background: #161b22; border: 2px solid #FFD700; 
        border-radius: 15px; text-align: center; margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(218, 165, 32, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG XÁC THỰC VÀ NGÔN NGỮ (FIX FF6A0287 & BC812BD3) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=160)
        st.markdown("<h1 style='color: #FFD700;'>A1 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
        st.write("---")
        # Fix lỗi mất ngôn ngữ: Dùng widget rõ ràng
        lang = st.radio("NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        label_pwd = "MẬT KHẨU TRUY CẬP" if lang == "Tiếng Việt" else "ACCESS PASSWORD"
        pwd = st.text_input(label_pwd, type="password")
        btn_text = "KÍCH HOẠT HỆ THỐNG" if lang == "Tiếng Việt" else "ACTIVATE SYSTEM"
        
        if st.button(btn_text):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Sai mật khẩu / Invalid Password")
    st.stop()

# --- 3. ĐỘNG CƠ DỮ LIỆU "ULTRA-SYNC" (CHỐNG TREO THANH VÀNG/ĐỎ) ---
@st.cache_data(ttl=10)
def get_master_data(symbol, interval):
    # Sử dụng 3 cổng kết nối dự phòng để ép iPad phải lấy được dữ liệu
    for base_url in ["https://api.binance.com", "https://api1.binance.com", "https://api3.binance.com"]:
        try:
            url = f"{base_url}/api/v3/klines?symbol={symbol}&interval={interval}&limit=150"
            res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}).json()
            if isinstance(res, list) and len(res) > 50:
                df = pd.DataFrame(res, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
                df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
                
                # --- CHỈ BÁO A1 SYSTEM CHUẨN ---
                df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
                delta = df['C'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
                return df
        except: continue
    return None

# --- 4. SIDEBAR ĐIỀU KHIỂN CÂN ĐỐI TUYỆT ĐỐI (FIX MÉO) ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=120)
    st.markdown("<h2 style='color: #FFD700; margin-top: -10px;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: gray;'>Update: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    coin = st.selectbox("TÀI SẢN", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT", "BNBUSDT"])
    tfs = {"15m":"15 Phút", "1h":"1 Giờ", "4h":"4 Giờ", "1d":"1 Ngày", "1w":"1 Tuần", "1M":"1 Tháng"}
    tf = st.selectbox("KHUNG GIỜ", list(tfs.keys()), format_func=lambda x: tfs[x], index=1)
    
    st.divider()
    # QR Code chuẩn cho dự án A1
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app", caption="A1 GLOBAL QR")
    
    if st.button("LOGOUT / THOÁT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHIẾN THUẬT VÀ BIỂU ĐỒ CHUYÊN NGHIỆP ---
df = get_master_data(coin, tf)

if df is not None:
    last = df.iloc[-1]
    p, r, e = last['C'], last['RSI'], last['EMA20']
    
    # Logic Đèn tín hiệu A1 (Chuẩn Macro)
    if p > e and r < 70:
        msg, color = "TÍN HIỆU: MUA (BULLISH)", "#22c55e"
    elif p < e and r > 30:
        msg, color = "TÍN HIỆU: BÁN (BEARISH)", "#ef4444"
    else:
        msg, color = "TÍN HIỆU: THEO DÕI (WAIT)", "#f59e0b"
        
    st.markdown(f'<div class="a1-status-box"><h1 style="color: {color}; margin:0;">{msg}</h1></div>', unsafe_allow_html=True)
    
    # Biểu đồ kỹ thuật Plotly (Đã được tối ưu cho iPad để không lag)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.7, 0.3])
    
    fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='#FFD700', width=1.5), name="EMA20"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['V'], marker_color='rgba(255,255,255,0.2)', name="Vol"), row=2, col=1)
    
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Chỉ số Master A1
    c1, c2, c3 = st.columns(3)
    c1.metric("GIÁ (PRICE)", f"${p:,.2f}")
    c2.metric("CHỈ SỐ RSI", f"{r:.2f}")
    c3.metric("EMA20", f"{e:,.2f}")
else:
    # Fix triệt để lỗi treo bằng cơ chế tự phục hồi
    st.error("⚠️ Hệ thống đang kết nối lại dữ liệu thị trường...")
    time.sleep(3)
    st.rerun()
