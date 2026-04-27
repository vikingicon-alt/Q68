import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. GIAO DIỆN & STYLE (TỐI ƯU NÚT ĐĂNG NHẬP) ---
st.set_page_config(page_title="Q68 GLOBAL SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
        header, footer, #MainMenu {visibility: hidden !important;}
        .main { background: radial-gradient(circle, #0f172a 0%, #020617 100%); color: #e2e8f0; }
        [data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1e293b; }
        
        /* Làm nổi bật nút Đăng nhập */
        div.stButton > button {
            width: 100% !important;
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: black !important;
            font-weight: bold !important;
            font-size: 18px !important;
            height: 55px !important;
            border-radius: 15px !important;
            border: 2px solid gold !important;
            box-shadow: 0 4px 15px rgba(218, 165, 32, 0.4);
        }
        
        /* Hiệu ứng Neon cho tín hiệu */
        .neon-box { display: flex; justify-content: space-around; padding: 20px; background: rgba(30, 41, 59, 0.5); border-radius: 20px; margin-bottom: 25px; }
        .neon-light { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; opacity: 0.1; border: 2px solid rgba(255,255,255,0.1); }
        .neon-buy { color: #22c55e; border-color: #22c55e; box-shadow: 0 0 20px #22c55e; opacity: 1; }
        .neon-sell { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 20px #ef4444; opacity: 1; }
        .neon-hold { color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 20px #f59e0b; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ TRẠNG THÁI & NGÔN NGỮ ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'lang' not in st.session_state: st.session_state['lang'] = 'vi'

L_DB = {
    'vi': {'title': 'HỆ THỐNG Q68 TOÀN CẦU', 'pwd': 'MÃ TRUY CẬP HỆ THỐNG', 'btn_act': 'KÍCH HOẠT HỆ THỐNG', 'asset': 'TÀI SẢN', 'tf': 'KHUNG GIỜ', 'style': 'BIỂU ĐỒ', 'buy': 'MUA', 'sell': 'BÁN', 'hold': 'CHỜ', 'price': 'GIÁ', 'vol': 'VOL'},
    'en': {'title': 'Q68 GLOBAL SYSTEM', 'pwd': 'SYSTEM ACCESS KEY', 'btn_act': 'ACTIVATE SYSTEM', 'asset': 'ASSET', 'tf': 'TIMEFRAME', 'style': 'CHART STYLE', 'buy': 'BUY', 'sell': 'SELL', 'hold': 'HOLD', 'price': 'PRICE', 'vol': 'VOL'}
}

# --- 3. MÀN HÌNH ĐĂNG NHẬP (CỐ ĐỊNH NÚT) ---
def login_screen():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("<div style='text-align: center; margin-top: 50px;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='150'></div>", unsafe_allow_html=True)
        lang_sel = st.radio("CHỌN NGÔN NGỮ / SELECT LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        st.session_state['lang'] = 'vi' if lang_sel == "Tiếng Việt" else 'en'
        L = L_DB[st.session_state['lang']]
        
        st.markdown(f"<h1 style='text-align: center; color: gold; margin-bottom: 20px;'>{L['title']}</h1>", unsafe_allow_html=True)
        
        access_key = st.text_input(L['pwd'], type="password", placeholder="Nhập mã A1...")
        
        # Nút đăng nhập luôn luôn hiển thị rõ ràng
        if st.button(L['btn_act'], use_container_width=True):
            if access_key == "A1PRO":
                st.session_state['auth'] = True
                st.success("Đang khởi động hệ thống...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Mã không chính xác, anh kiểm tra lại nha!")
    st.stop()

if not st.session_state['auth']:
    login_screen()

L = L_DB[st.session_state['lang']]

# --- 4. ENGINE DỮ LIỆU ---
@st.cache_data(ttl=15)
def fetch_data(symbol, tf):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=100"
        r = requests.get(url, timeout=10).json()
        if not isinstance(r, list) or len(r) < 35: return None
        df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 0.000001))))
        return df
    except: return None

# --- 5. SIDEBAR & GIAO DIỆN CHÍNH ---
with st.sidebar:
    st.markdown("<h2 style='color: gold; text-align: center;'>Q68 GLOBAL</h2>", unsafe_allow_html=True)
    target = st.selectbox(L['asset'], ["BTCUSDT", "PAXGUSDT", "ETHUSDT"])
    tf_val = st.selectbox(L['tf'], ["15m", "30m", "1h", "4h", "1d", "1w", "1M"], index=2)
    style = st.radio(L['style'], ["Candles", "Line", "Area"], horizontal=True)
    if st.button("THOÁT / LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

df = fetch_data(target, tf_val)
if df is not None:
    p, r, e, v = df['C'].iloc[-1], df['RSI'].iloc[-1], df['EMA20'].iloc[-1], df['V'].iloc[-1]
    
    # Đèn Neon dự đoán
    b_c = "neon-buy" if (p > e and r < 70) else ""
    s_c = "neon-sell" if (p < e and r > 30) else ""
    h_c = "neon-hold" if (not b_c and not s_c) else ""
    st.markdown(f'<div class="neon-box"><div class="neon-light {b_c}">{L["buy"]}</div><div class="neon-light {h_c}">{L["hold"]}</div><div class="neon-light {s_c}">{L["sell"]}</div></div>', unsafe_allow_html=True)
    
    # Biểu đồ Subplots: Giá & Volume
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
    if style == "Candles":
        fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Price"), row=1, col=1)
    elif style == "Line":
        fig.add_trace(go.Scatter(y=df['C'], line=dict(color='#3b82f6', width=2), name="Price"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(y=df['C'], fill='tozeroy', line=dict(color='gold'), name="Price"), row=1, col=1)
    
    fig.add_trace(go.Bar(x=df.index, y=df['V'], name="Volume", marker_color='gray'), row=2, col=1)
    fig.update_layout(height=550, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    m1.metric(L['price'], f"${p:,.2f}")
    m2.metric("RSI (14)", f"{r:.2f}")
    m3.metric(f"VOL ({tf_val})", f"{v:,.1f}")
else:
    st.warning("Đang đồng bộ dữ liệu thị trường...")
    time.sleep(2); st.rerun()
