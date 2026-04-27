import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. CẤU HÌNH GIAO DIỆN CHUẨN A1 ---
st.set_page_config(page_title="Q68 MASTER V22", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background: #020617 !important; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 2px solid gold; min-width: 270px !important; }
    div.stButton > button { width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); color: black; font-weight: 900; border-radius: 12px; height: 50px; border: none; }
    .neon-card { display: flex; justify-content: space-around; padding: 18px; background: #1e293b; border-radius: 15px; border: 1px solid gold; margin-bottom: 20px; }
    .signal { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; opacity: 0.1; border: 1px solid rgba(255,255,255,0.2); }
    .buy-on { color: #22c55e; border-color: #22c55e; box-shadow: 0 0 15px #22c55e; opacity: 1; }
    .sell-on { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 15px #ef4444; opacity: 1; }
    .hold-on { color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 15px #f59e0b; opacity: 1; }
</style>
""", unsafe_allow_html=True)

# --- 2. XÁC THỰC & NGÔN NGỮ ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'lang' not in st.session_state: st.session_state['lang'] = 'Việt'

UI = {
    'Việt': {'t': 'HỆ THỐNG Q68 TOÀN CẦU', 'p': 'MÃ TRUY CẬP', 'b': 'KÍCH HOẠT', 'c': 'TÀI SẢN', 'f': 'KHUNG GIỜ', 's': 'BIỂU ĐỒ', 'err': 'Đang tải dữ liệu...'},
    'Eng': {'t': 'Q68 GLOBAL SYSTEM', 'p': 'ACCESS CODE', 'b': 'ACTIVATE', 'c': 'ASSETS', 'f': 'TIMEFRAME', 's': 'STYLE', 'err': 'Loading data...'}
}

if not st.session_state['auth']:
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=150)
        choice = st.radio("LANG", ["Tiếng Việt", "English"], horizontal=True, label_visibility="collapsed")
        st.session_state['lang'] = 'Việt' if "Việt" in choice else 'Eng'
        curr = UI[st.session_state['lang']]
        st.markdown(f"<h2 style='text-align: center; color: gold;'>{curr['t']}</h2>", unsafe_allow_html=True)
        pwd = st.text_input(curr['p'], type="password")
        if st.button(curr['b']):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

curr = UI[st.session_state['lang']]

# --- 3. ĐỘNG CƠ DỮ LIỆU CẢI TIẾN (FIX LỖI KẸT ĐỒNG BỘ) ---
def fetch_safe_data(symbol, interval):
    try:
        # Sử dụng headers để giả lập trình duyệt, tránh bị sàn chặn trên thiết bị di động
        h = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=150"
        response = requests.get(url, headers=h, timeout=15)
        if response.status_code != 200: return None
        raw = response.json()
        if not isinstance(raw, list) or len(raw) < 20: return None
        
        df = pd.DataFrame(raw, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
        # Chỉ báo A1 chuẩn
        df['EMA'] = df['C'].ewm(span=20, adjust=False).mean()
        change = df['C'].diff()
        gain = (change.where(change > 0, 0)).rolling(14).mean()
        loss = (-change.where(change < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        return df
    except: return None

# --- 4. SIDEBAR ĐIỀU KHIỂN ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=80)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    st.divider()
    coin = st.selectbox(curr['c'], ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"])
    tfs = {"30m":"30 Phút", "1h":"1 Giờ", "4h":"4 Giờ", "1d":"1 Ngày", "1w":"1 Tuần", "1M":"1 Tháng"}
    tf_k = st.selectbox(curr['f'], list(tfs.keys()), format_func=lambda x: tfs[x], index=1)
    chart = st.radio(curr['s'], ["Candles", "Line", "Area"], horizontal=True)
    st.divider()
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://nrynpp6caudetlbejh8appz.streamlit.app")
    if st.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHIẾN THUẬT ---
data = fetch_safe_data(coin, tf_k)

if data is not None:
    last = data.iloc[-1]
    p, r, e = last['C'], last['RSI'], last['EMA']
    
    # Logic đèn Neon A1 cực nhạy
    b_on = "buy-on" if (p > e and r < 65) else ""
    s_on = "sell-on" if (p < e and r > 35) else ""
    h_on = "hold-on" if not b_on and not s_on else ""
    
    st.markdown(f'<div class="neon-card"><div class="signal {b_on}">MUA</div><div class="signal {h_on}">CHỜ</div><div class="signal {s_on}">BÁN</div></div>', unsafe_allow_html=True)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    if chart == "Candles":
        fig.add_trace(go.Candlestick(x=data.index, open=data['O'], high=data['H'], low=data['L'], close=data['C'], name="Price"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(y=data['C'], fill='tozeroy' if chart=="Area" else None, line=dict(color='gold', width=2), name="Price"), row=1, col=1)
        fig.add_trace(go.Bar(x=data.index, y=data['V'], marker_color='rgba(128,128,128,0.4)', name="Vol"), row=2, col=1)
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.columns(3)[0].metric("PRICE", f"${p:,.1f}")
    st.columns(3)[1].metric("RSI", f"{r:.1f}")
    st.columns(3)[2].metric("EMA", f"{e:,.1f}")
else:
    # Nếu lỗi, tự động reset cache và thử lại sau 2 giây
    st.error(curr['err'])
    time.sleep(2)
    st.rerun()
