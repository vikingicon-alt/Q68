import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. KHỞI TẠO CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Q68 GLOBAL MASTER", layout="wide", page_icon="🐢")

# Quản lý Ngôn ngữ (Fix lỗi mất lựa chọn ngoại ngữ)
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'Việt'

# CSS Luxury & Tối ưu iPad (Fix lỗi hiển thị)
st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background: #020617 !important; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 2px solid #FFD700; min-width: 270px !important; }
    div.stButton > button {
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
        color: black; font-weight: 1000; height: 48px; border-radius: 12px; border: none;
    }
    .neon-box { display: flex; justify-content: space-around; padding: 15px; background: #1e293b; border-radius: 15px; border: 1px solid gold; margin-bottom: 20px; }
    .n-light { width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900; opacity: 0.1; border: 1px solid rgba(255,255,255,0.2); }
    .n-buy { color: #22c55e; border-color: #22c55e; box-shadow: 0 0 15px #22c55e; opacity: 1; }
    .n-sell { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 15px #ef4444; opacity: 1; }
    .n-hold { color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 15px #f59e0b; opacity: 1; }
    .metric-ui { background: #1e293b; padding: 12px; border-radius: 10px; border-left: 4px solid gold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Bộ từ điển ngôn ngữ
UI = {
    'Việt': {'t': 'HỆ THỐNG Q68 TOÀN CẦU', 'p': 'MÃ TRUY CẬP', 'b': 'KÍCH HOẠT', 'c': 'TÀI SẢN', 'f': 'KHUNG GIỜ', 's': 'BIỂU ĐỒ', 'sync': 'Đang đồng bộ dữ liệu...'},
    'Eng': {'t': 'Q68 GLOBAL SYSTEM', 'p': 'ACCESS CODE', 'b': 'ACTIVATE', 'c': 'ASSETS', 'f': 'TIMEFRAME', 's': 'CHART', 'sync': 'Syncing data...'}
}

# --- 2. XÁC THỰC VÀ NGÔN NGỮ ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=160)
        sel_lang = st.radio("", ["Tiếng Việt", "English"], horizontal=True)
        st.session_state['lang'] = 'Việt' if "Việt" in sel_lang else 'Eng'
        curr_ui = UI[st.session_state['lang']]
        
        st.markdown(f"<h2 style='text-align: center; color: gold;'>{curr_ui['t']}</h2>", unsafe_allow_html=True)
        pwd = st.text_input(curr_ui['p'], type="password")
        if st.button(curr_ui['b']):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

curr_ui = UI[st.session_state['lang']]

# --- 3. ĐỘNG CƠ DỮ LIỆU A1 (CHỐNG LỖI INDEX/INDENT) ---
@st.cache_data(ttl=12)
def get_a1_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=120"
        res = requests.get(url, timeout=5).json()
        if not isinstance(res, list) or len(res) < 50:
            return None
        df = pd.DataFrame(res, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
        # Chỉ báo lõi A1
        df['EMA'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        return df
    except:
        return None

# --- 4. SIDEBAR ĐIỀU KHIỂN (KHÔI PHỤC ĐẦY ĐỦ) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=100)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    st.divider()
    coin = st.selectbox(curr_ui['c'], ["BTCUSDT", "ETHUSDT", "PAXGUSDT", "SOLUSDT"])
    tf = st.selectbox(curr_ui['f'], ["15m", "1h", "4h", "1d", "1w"], index=1)
    chart_type = st.radio(curr_ui['s'], ["Candles", "Line", "Area"], horizontal=True)
    st.divider()
    # Fix lỗi Syntax QR ở các bản trước
    qr_link = "https://nrynpp6caudetlbejh8appz.streamlit.app"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}", caption="SHARE SYSTEM")
    if st.button("THOÁT / LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHIẾN THUẬT ---
data = get_a1_data(coin, tf)

if data is not None:
    last = data.iloc[-1]
    price, rsi, ema, vol = last['C'], last['RSI'], last['EMA'], last['V']
    
    # Hệ thống Đèn Neon A1
    buy_on = "n-buy" if (price > ema and rsi < 65) else ""
    sell_on = "n-sell" if (price < ema and rsi > 35) else ""
    hold_on = "n-hold" if not buy_on and not sell_on else ""
    
    st.markdown(f"""
    <div class="neon-box">
        <div class="n-light {buy_on}">MUA</div>
        <div class="n-light {hold_on}">CHỜ</div>
        <div class="n-light {sell_on}">BÁN</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Biểu đồ kỹ thuật
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    if chart_type == "Candles":
        fig.add_trace(go.Candlestick(x=data.index, open=data['O'], high=data['H'], low=data['L'], close=data['C'], name="Price"), row=1, col=1)
    elif chart_type == "Line":
        fig.add_trace(go.Scatter(y=data['C'], line=dict(color='gold', width=2), name="Price"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(y=data['C'], fill='tozeroy', line=dict(color='gold'), name="Price"), row=1, col=1)
    
    fig.add_trace(go.Bar(x=data.index, y=data['V'], marker_color='rgba(128,128,128,0.5)', name="Vol"), row=2, col=1)
    fig.update_layout(height=480, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Chỉ số Metric Luxury
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-ui"><small>PRICE</small><h4>${price:,.1f}</h4></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-ui"><small>RSI</small><h4>{rsi:.2f}</h4></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-ui"><small>VOLUME</small><h4>{vol:,.0f}</h4></div>', unsafe_allow_html=True)
else:
    st.warning(curr_ui['sync'])
    time.sleep(2)
    st.rerun()
