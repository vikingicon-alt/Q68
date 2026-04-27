import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# --- 1. CẤU HÌNH HỆ THỐNG & GIAO DIỆN ---
icon_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png"
st.set_page_config(page_title="Q68 SYSTEM GLOBAL", layout="wide", page_icon="🐢")

st.markdown(f"""
    <style>
        header, footer, #MainMenu {{visibility: hidden !important;}}
        .main {{background-color: #05070a; color: white;}}
        [data-testid="stSidebar"] {{background-color: #0c0f14; border-right: 1px solid #1e2229; min-width: 300px;}}
        .signal-box {{
            padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; font-size: 28px;
            margin-bottom: 20px; text-transform: uppercase;
        }}
        .buy-neon {{ border: 3px solid #00ffcc; color: #00ffcc; text-shadow: 0 0 20px #00ffcc; box-shadow: inset 0 0 10px #00ffcc; }}
        .sell-neon {{ border: 3px solid #ff3366; color: #ff3366; text-shadow: 0 0 20px #ff3366; box-shadow: inset 0 0 10px #ff3366; }}
        .hold-neon {{ border: 3px solid #ffcc00; color: #ffcc00; text-shadow: 0 0 20px #ffcc00; box-shadow: inset 0 0 10px #ffcc00; }}
        .stMetric {{ background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid #333; }}
        div.stButton > button {{ width: 100%; background-color: gold; color: black; font-weight: bold; border-radius: 10px; border: none; height: 50px; }}
    </style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG SONG NGỮ ---
if 'lang' not in st.session_state: st.session_state['lang'] = 'vi'
text = {
    'vi': {'title': 'Q68 SYSTEM GLOBAL', 'pwd': 'MÃ KÍCH HOẠT HỆ THỐNG:', 'btn': 'KÍCH HOẠT', 'asset': 'TÀI SẢN (VÀNG/COIN)', 'tf': 'KHUNG THỜI GIAN', 'style': 'MẪU ĐỒ THỊ', 'qr': 'QUÉT ĐỂ CHIA SẺ', 'buy': '🔥 LỆNH: MUA (BUY)', 'sell': '❄️ LỆNH: BÁN (SELL)', 'hold': '⚠️ LỆNH: GIỮ (HOLD)', 'price': 'GIÁ HIỆN TẠI', 'load': '🔄 Đang đồng bộ luồng dữ liệu...'},
    'en': {'title': 'Q68 GLOBAL SYSTEM', 'pwd': 'SYSTEM PASSWORD:', 'btn': 'ACTIVATE', 'asset': 'ASSET (GOLD/COIN)', 'tf': 'TIMEFRAME', 'style': 'CHART STYLE', 'qr': 'SCAN TO SHARE', 'buy': '🔥 SIGNAL: BUY', 'sell': '❄️ SIGNAL: SELL', 'hold': '⚠️ SIGNAL: HOLD', 'price': 'CURRENT PRICE', 'load': '🔄 Syncing live data flow...'}
}

# --- 3. KIỂM TRA ĐĂNG NHẬP ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown(f"<div style='text-align: center; margin-top: 40px;'><img src='{icon_url}' width='140'></div>", unsafe_allow_html=True)
    lang_init = st.radio("CHỌN NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
    st.session_state['lang'] = 'vi' if lang_init == "Tiếng Việt" else 'en'
    L = text[st.session_state['lang']]
    st.markdown(f"<h1 style='text-align: center; color: gold; font-size: 35px;'>{L['title']}</h1>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        pw = st.text_input(L['pwd'], type="password")
        if st.button(L['btn']):
            if pw == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

L = text[st.session_state['lang']]

# --- 4. ENGINE DỮ LIỆU ---
def fetch_market_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        r = requests.get(url, timeout=10).json()
        if not isinstance(r, list) or len(r) < 20: return None
        df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','NT','TB','TQ','I'])
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
    st.image(icon_url, width=90)
    st.markdown("<h2 style='color: gold; text-align: center; margin-top: -10px;'>Q68 SYSTEM</h2>", unsafe_allow_html=True)
    st.session_state['lang'] = 'vi' if st.radio("NGÔN NGỮ", ["Tiếng Việt", "English"], index=0 if st.session_state['lang']=='vi' else 1, horizontal=True) == "Tiếng Việt" else 'en'
    st.divider()
    target = st.selectbox(L['asset'], ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"])
    timeframe = st.selectbox(L['tf'], ["15m", "30m", "1h", "4h", "1d", "1w"], index=2)
    chart_type = st.radio(L['style'], ["Candles", "Line", "Area"])
    st.divider()
    st.write(f"📲 {L['qr']}:")
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://audetlbejh8appz.streamlit.app", width=140)
    if st.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 6. HIỂN THỊ CHIẾN THUẬT ---
data = fetch_market_data(target, timeframe)

if data is not None:
    curr_p, rsi_v, ema_v = data['C'].iloc[-1], data['RSI'].iloc[-1], data['EMA20'].iloc[-1]
    name = "VÀNG (GOLD)" if target == "PAXGUSDT" else target
    st.markdown(f"<h2 style='text-align: center; color: gold;'>🐢 Q68 | {name} ({timeframe})</h2>", unsafe_allow_html=True)
    
    fig = go.Figure()
    if chart_type == "Candles":
        fig.add_trace(go.Candlestick(x=data.index, open=data['O'], high=data['H'], low=data['L'], close=data['C']))
    elif chart_type == "Line":
        fig.add_trace(go.Scatter(y=data['C'], line=dict(color='#00ffcc', width=3)))
    else:
        fig.add_trace(go.Scatter(y=data['C'], fill='tozeroy', line=dict(color='gold')))
        fig.add_trace(go.Scatter(y=data['EMA20'], line=dict(color='white', width=1, dash='dot'), name='EMA20'))
    fig.update_layout(height=400, template="plotly_dark", paper_bgcolor="#05070a", plot_bgcolor="#05070a", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    if curr_p > ema_v and rsi_v < 70:
        st.markdown(f'<div class="signal-box buy-neon">{L["buy"]}</div>', unsafe_allow_html=True)
    elif curr_p < ema_v and rsi_v > 30:
        st.markdown(f'<div class="signal-box sell-neon">{L["sell"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-box hold-neon">{L["hold"]}</div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric(L['price'], f"${curr_p:,.2f}")
    m2.metric("RSI (14)", f"{rsi_v:.2f}")
    m3.metric("EMA 20", f"{ema_v:,.1f}")
else:
    st.info(L['load'])
    time.sleep(2)
    st.rerun()
