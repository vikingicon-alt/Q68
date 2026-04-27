import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# --- 1. THIẾT LẬP GIAO DIỆN CHUẨN QUỐC TẾ (UX/UI GLOBAL) ---
st.set_page_config(page_title="Q68 GLOBAL SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
        header, footer, #MainMenu {visibility: hidden !important;}
        .main { background: radial-gradient(circle, #0f172a 0%, #020617 100%); color: #e2e8f0; }
        [data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1e293b; min-width: 300px; }
        .stTextInput > div > div > input { background-color: #1e293b; color: gold; border: 1px solid #334155; border-radius: 8px; text-align: center; font-size: 18px; }
        div.stButton > button { 
            width: 100%; background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%); 
            color: black; font-weight: 900; border-radius: 12px; border: none; height: 50px; cursor: pointer;
        }
        .signal-card {
            padding: 25px; border-radius: 15px; text-align: center; font-weight: 800; font-size: 28px;
            margin-bottom: 20px; letter-spacing: 2px; border: 1px solid rgba(255,215,0,0.2);
            background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(5px);
        }
        .buy-txt { color: #22c55e; text-shadow: 0 0 10px rgba(34, 197, 94, 0.5); }
        .sell-txt { color: #ef4444; text-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }
        .hold-txt { color: #f59e0b; text-shadow: 0 0 10px rgba(245, 158, 11, 0.5); }
        .stMetric { background: #1e293b; padding: 15px; border-radius: 12px; border-left: 4px solid gold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG NGÔN NGỮ ĐỒNG BỘ TUYỆT ĐỐI ---
if 'lang' not in st.session_state: st.session_state['lang'] = 'vi'
if 'auth' not in st.session_state: st.session_state['auth'] = False

L_DB = {
    'vi': {
        'title': 'HỆ THỐNG Q68 TOÀN CẦU', 'pwd': 'MÃ TRUY CẬP HỆ THỐNG', 'btn_act': 'KÍCH HOẠT NGAY',
        'asset': 'CHỌN TÀI SẢN', 'tf': 'KHUNG THỜI GIAN', 'style': 'LOẠI BIỂU ĐỒ', 'logout': 'THOÁT',
        'buy': '🔥 TÍN HIỆU: MUA (BUY)', 'sell': '❄️ TÍN HIỆU: BÁN (SELL)', 'hold': '⚠️ TÍN HIỆU: CHỜ (HOLD)',
        'price': 'GIÁ HIỆN TẠI', 'sync': '🔄 Đang kết nối luồng dữ liệu...'
    },
    'en': {
        'title': 'Q68 GLOBAL SYSTEM', 'pwd': 'SYSTEM ACCESS KEY', 'btn_act': 'ACTIVATE NOW',
        'asset': 'SELECT ASSET', 'tf': 'TIMEFRAME', 'style': 'CHART TYPE', 'logout': 'LOGOUT',
        'buy': '🔥 SIGNAL: BUY', 'sell': '❄️ SIGNAL: SELL', 'hold': '⚠️ SIGNAL: HOLD',
        'price': 'CURRENT PRICE', 'sync': '🔄 Connecting to live data...'
    }
}

# --- 3. MÀN HÌNH ĐĂNG NHẬP (CĂN CHỈNH TỈ MỶ) ---
def show_login():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("<div style='text-align: center; margin-top: 50px;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='150'></div>", unsafe_allow_html=True)
        lang_pick = st.radio(" ", ["Tiếng Việt", "English"], horizontal=True, label_visibility="collapsed")
        st.session_state['lang'] = 'vi' if lang_pick == "Tiếng Việt" else 'en'
        L = L_DB[st.session_state['lang']]
        st.markdown(f"<h1 style='text-align: center; color: gold; margin-bottom: 20px;'>{L['title']}</h1>", unsafe_allow_html=True)
        pwd = st.text_input(L['pwd'], type="password", placeholder="••••••••")
        if st.button(L['btn_act']):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

if not st.session_state['auth']: show_login()
L = L_DB[st.session_state['lang']]

# --- 4. DATA ENGINE (CHỐNG LỖI KẾT NỐI) ---
@st.cache_data(ttl=10)
def get_world_data(symbol, tf):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=100"
        r = requests.get(url, timeout=10).json()
        if not isinstance(r, list) or len(r) < 20: return None
        df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C']] = df[['O','H','L','C']].astype(float)
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 0.000001))))
        return df
    except: return None

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='100'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 GLOBAL</h3>", unsafe_allow_html=True)
    st.divider()
    target = st.selectbox(L['asset'], ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"])
    tf = st.selectbox(L['tf'], ["15m", "1h", "4h", "1d"], index=1)
    style = st.radio(L['style'], ["Candles", "Line"], horizontal=True)
    st.divider()
    st.write("📲 SHARE:")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://audetlbejh8appz.streamlit.app"
    st.image(qr_url, width=140)
    if st.button(L['logout']):
        st.session_state['auth'] = False
        st.rerun()

# --- 6. HIỂN THỊ CHÍNH (KHÔNG SAI SÓT) ---
df = get_world_data(target, tf)
if df is not None:
    p, r, e = df['C'].iloc[-1], df['RSI'].iloc[-1], df['EMA20'].iloc[-1]
    name = "GOLD / USD" if target == "PAXGUSDT" else f"{target[:-4]} / USDT"
    st.markdown(f"<h2 style='text-align: center; color: gold;'>{name} ({tf})</h2>", unsafe_allow_html=True)
    fig = go.Figure()
    if style == "Candles":
        fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Price"))
    else:
        fig.add_trace(go.Scatter(y=df['C'], line=dict(color='#3b82f6', width=3), name="Price"))
    fig.add_trace(go.Scatter(y=df['EMA20'], line=dict(color='white', width=1, dash='dot'), name="EMA 20"))
    fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    if p > e and r < 70:
        st.markdown(f'<div class="signal-card buy-txt">{L["buy"]}</div>', unsafe_allow_html=True)
    elif p < e and r > 30:
        st.markdown(f'<div class="signal-card sell-txt">{L["sell"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-card hold-txt">{L["hold"]}</div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric(L['price'], f"${p:,.2f}")
    m2.metric("RSI (14)", f"{r:.2f}")
    m3.metric("EMA 20", f"{e:,.1f}")
else:
    st.warning(L['sync'])
    time.sleep(3)
    st.rerun()
