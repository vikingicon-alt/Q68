import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# --- 1. THIẾT LẬP GIAO DIỆN CHUẨN QUỐC TẾ ---
st.set_page_config(page_title="Q68 SYSTEM GLOBAL", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
        header, footer, #MainMenu {visibility: hidden !important;}
        .main {background-color: #05070a; color: white; font-family: 'Inter', sans-serif;}
        [data-testid="stSidebar"] {background-color: #0c0f14; border-right: 1px solid #1e2229; min-width: 280px;}
        .stMetric { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; border: 1px solid #222; }
        .signal-box {
            padding: 25px; border-radius: 15px; text-align: center; font-weight: 800; font-size: 30px;
            margin-bottom: 25px; letter-spacing: 2px; text-transform: uppercase;
        }
        .buy-neon { border: 3px solid #00ffcc; color: #00ffcc; text-shadow: 0 0 20px #00ffcc; box-shadow: inset 0 0 15px #00ffcc; }
        .sell-neon { border: 3px solid #ff3366; color: #ff3366; text-shadow: 0 0 20px #ff3366; box-shadow: inset 0 0 15px #ff3366; }
        .hold-neon { border: 3px solid #ffcc00; color: #ffcc00; text-shadow: 0 0 20px #ffcc00; box-shadow: inset 0 0 15px #ffcc00; }
        div.stButton > button { width: 100%; background: linear-gradient(90deg, gold, #ffcc00); color: black; font-weight: bold; border-radius: 10px; border: none; height: 55px; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ NGÔN NGỮ & BẢO MẬT ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'lang' not in st.session_state: st.session_state['lang'] = 'vi'

icon_q68 = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png"

def login_screen():
    st.markdown(f"<div style='text-align: center; margin-top: 50px;'><img src='{icon_q68}' width='150'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: gold;'>Q68 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        lang = st.radio("LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        st.session_state['lang'] = 'vi' if lang == "Tiếng Việt" else 'en'
        pwd = st.text_input("ACCESS KEY", type="password")
        if st.button("ACTIVATE SYSTEM"):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

if not st.session_state['auth']: login_screen()

# --- 3. CƠ CHẾ LẤY DỮ LIỆU CHỐNG TREO ---
@st.cache_data(ttl=10)
def get_world_data(symbol, tf):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=100"
        r = requests.get(url, timeout=10).json()
        if not isinstance(r, list): return None
        df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C']] = df[['O','H','L','C']].astype(float)
        # Chỉ báo A1 Standard
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 0.000001))))
        return df
    except: return None

# --- 4. ĐIỀU HÀNH HỆ THỐNG (SIDEBAR) ---
L = {'vi': {'asset': 'TÀI SẢN', 'tf': 'KHUNG GIỜ', 'qr': 'CHIA SẺ', 'buy': '🔥 LỆNH: MUA (BUY)', 'sell': '❄️ LỆNH: BÁN (SELL)', 'hold': '⚠️ LỆNH: CHỜ (HOLD)'},
     'en': {'asset': 'ASSET', 'tf': 'TIMEFRAME', 'qr': 'SHARE', 'buy': '🔥 SIGNAL: BUY', 'sell': '❄️ SIGNAL: SELL', 'hold': '⚠️ SIGNAL: HOLD' }}[st.session_state['lang']]

with st.sidebar:
    st.image(icon_q68, width=100)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 OFFICE</h3>", unsafe_allow_html=True)
    target = st.selectbox(L['asset'], ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"])
    timeframe = st.selectbox(L['tf'], ["15m", "1h", "4h", "1d"], index=1)
    st.divider()
    st.write(f"📲 {L['qr']}:")
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://audetlbejh8appz.streamlit.app", width=150)
    if st.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ ĐẲNG CẤP THẾ GIỚI ---
df = get_world_data(target, timeframe)

if df is not None:
    curr_p, rsi_v, ema_v = df['C'].iloc[-1], df['RSI'].iloc[-1], df['EMA20'].iloc[-1]
    name = "GOLD (VÀNG)" if target == "PAXGUSDT" else target
    st.markdown(f"<h2 style='text-align: center; color: gold;'>🐢 {name} | GLOBAL ANALYTICS</h2>", unsafe_allow_html=True)
    
    # Biểu đồ chuẩn TradingView
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Price")])
    fig.add_trace(go.Scatter(y=df['EMA20'], line=dict(color='white', width=1.5, dash='dot'), name="EMA 20"))
    fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="#05070a", plot_bgcolor="#05070a", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Tín hiệu AI Q68
    if curr_p > ema_v and rsi_v < 70:
        st.markdown(f'<div class="signal-box buy-neon">{L["buy"]}</div>', unsafe_allow_html=True)
    elif curr_p < ema_v and rsi_v > 30:
        st.markdown(f'<div class="signal-box sell-neon">{L["sell"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-box hold-neon">{L["hold"]}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("PRICE", f"${curr_p:,.2f}")
    c2.metric("RSI (14)", f"{rsi_v:.2f}")
    c3.metric("EMA 20", f"{ema_v:,.1f}")
else:
    st.info("⚡ System is synchronizing with Global Data Flow... Please wait.")
    time.sleep(2)
    st.rerun()
