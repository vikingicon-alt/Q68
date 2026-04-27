import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. GIAO DIỆN LUXURY ---
st.set_page_config(page_title="Q68 SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background: #020617; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #FFD700; }
    div.stButton > button {
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
        color: black; font-weight: bold; height: 50px; border-radius: 12px;
    }
    .neon-box { display: flex; justify-content: space-around; padding: 15px; background: #1e293b; border-radius: 15px; margin-bottom: 20px; }
    .neon-light { width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 900; opacity: 0.1; border: 2px solid rgba(255,255,255,0.1); }
    .neon-buy { color: #22c55e; border-color: #22c55e; box-shadow: 0 0 15px #22c55e; opacity: 1; }
    .neon-sell { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 15px #ef4444; opacity: 1; }
    .neon-hold { color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 15px #f59e0b; opacity: 1; }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ ĐĂNG NHẬP ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'lang' not in st.session_state: st.session_state['lang'] = 'vi'

L_DB = {
    'vi': {'title': 'HỆ THỐNG Q68 TOÀN CẦU', 'pwd': 'MÃ TRUY CẬP', 'btn': 'KÍCH HOẠT', 'buy': 'MUA', 'sell': 'BÁN', 'hold': 'CHỜ'},
    'en': {'title': 'Q68 GLOBAL SYSTEM', 'pwd': 'ACCESS KEY', 'btn': 'ACTIVATE', 'buy': 'BUY', 'sell': 'SELL', 'hold': 'HOLD'}
}

def login():
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown("<div style='text-align: center; margin-top: 50px;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='180'></div>", unsafe_allow_html=True)
        sel = st.radio("LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        st.session_state['lang'] = 'vi' if sel == "Tiếng Việt" else 'en'
        L = L_DB[st.session_state['lang']]
        st.markdown(f"<h1 style='text-align: center; color: gold;'>{L['title']}</h1>", unsafe_allow_html=True)
        pwd = st.text_input(L['pwd'], type="password")
        if st.button(L['btn']):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

if not st.session_state['auth']: login()
L = L_DB[st.session_state['lang']]

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=15)
def get_data(symbol, tf):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=100"
        data = requests.get(url, timeout=10).json()
        df = pd.DataFrame(data, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        return df
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='100'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    target = st.selectbox("TÀI SẢN", ["BTCUSDT", "PAXGUSDT", "ETHUSDT"])
    tf_val = st.selectbox("KHUNG GIỜ", ["15m", "30m", "1h", "4h", "1d", "1w", "1M"], index=2)
    style = st.radio("BIỂU ĐỒ", ["Candles", "Line", "Area"], horizontal=True)
    st.divider()
    st.markdown("<p style='text-align: center; font-size: 12px;'>SHARE SYSTEM</p>", unsafe_allow_html=True)
    qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app"
    st.image(qr_url, use_container_width=True)
    if st.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. MAIN ---
df = get_data(target, tf_val)
if df is not None:
    p, r, e, v = df['C'].iloc[-1], df['RSI'].iloc[-1], df['EMA20'].iloc[-1], df['V'].iloc[-1]
    b_c = "neon-buy" if (p > e and r < 65) else ""
    s_c = "neon-sell" if (p < e and r > 35) else ""
    h_c = "neon-hold" if (not b_c and not s_c) else ""
    st.markdown(f'<div class="neon-box"><div class="neon-light {b_c}">{L["buy"]}</div><div class="neon-light {h_c}">{L["hold"]}</div><div class="neon-light {s_c}">{L["sell"]}</div></div>', unsafe_allow_html=True)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.7, 0.3])
    if style == "Candles": fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C']), row=1, col=1)
    elif style == "Line": fig.add_trace(go.Scatter(y=df['C'], line=dict(color='#3b82f6')), row=1, col=1)
    else: fig.add_trace(go.Scatter(y=df['C'], fill='tozeroy', line=dict(color='gold')), row=1, col=1)
    
    fig.add_trace(go.Bar(x=df.index, y=df['V'], marker_color='gray'), row=2, col=1)
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("GIÁ", f"${p:,.2f}")
    c2.metric("RSI", f"{r:.2f}")
    c3.metric("VOL", f"{v:,.0f}")
else:
    st.warning("⚠️ Đang kết nối dữ liệu...")
    time.sleep(2)
    st.rerun()
