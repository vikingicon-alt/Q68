import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# --- 1. THIẾT LẬP THƯƠNG HIỆU & ICON Q68 ---
icon_q68 = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png"

st.set_page_config(page_title="Q68 SYSTEM GLOBAL", layout="wide", page_icon="🐢")

st.markdown(f"""
    <style>
        header, footer, #MainMenu {{visibility: hidden !important;}}
        .main {{background-color: #05070a; color: white;}}
        [data-testid="stSidebar"] {{background-color: #0c0f14; border-right: 1px solid #1e2229;}}
        .signal-box {{
            padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; font-size: 26px;
            box-shadow: 0 0 20px rgba(255,255,255,0.1); margin-bottom: 20px;
        }}
        .buy-neon {{ border: 3px solid #00ffcc; color: #00ffcc; text-shadow: 0 0 15px #00ffcc; }}
        .sell-neon {{ border: 3px solid #ff3366; color: #ff3366; text-shadow: 0 0 15px #ff3366; }}
        .hold-neon {{ border: 3px solid #ffcc00; color: #ffcc00; text-shadow: 0 0 15px #ffcc00; }}
        .stMetric {{ background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; border: 1px solid #333; }}
        .stButton>button {{width: 100%; border-radius: 8px; font-weight: bold; background-color: gold; color: black; border: none;}}
    </style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ NGÔN NGỮ ---
if 'lang' not in st.session_state: st.session_state['lang'] = 'vi'

with st.sidebar:
    st.image(icon_q68, width=100)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 SYSTEM</h3>", unsafe_allow_html=True)
    lang_choice = st.radio("NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
    st.session_state['lang'] = 'vi' if lang_choice == "Tiếng Việt" else 'en'

text = {
    'vi': {'title': 'Q68 SYSTEM GLOBAL', 'pwd': 'MÃ KÍCH HOẠT HỆ THỐNG:', 'btn': 'KÍCH HOẠT', 'asset': 'TÀI SẢN (VÀNG/COIN)', 'tf': 'KHUNG THỜI GIAN', 'style': 'MẪU ĐỒ THỊ', 'qr': 'QUÉT ĐỂ CHIA SẺ', 'buy': '🔥 LỆNH: MUA (BUY)', 'sell': '❄️ LỆNH: BÁN (SELL)', 'hold': '⚠️ LỆNH: GIỮ (HOLD)', 'price': 'GIÁ HIỆN TẠI', 'err': 'Đang kết nối luồng dữ liệu...'},
    'en': {'title': 'Q68 GLOBAL SYSTEM', 'pwd': 'SYSTEM PASSWORD:', 'btn': 'ACTIVATE', 'asset': 'ASSET (GOLD/COIN)', 'tf': 'TIMEFRAME', 'style': 'CHART STYLE', 'qr': 'SCAN TO SHARE', 'buy': '🔥 SIGNAL: BUY', 'sell': '❄️ SIGNAL: SELL', 'hold': '⚠️ SIGNAL: HOLD', 'price': 'CURRENT PRICE', 'err': 'Connecting to live data...'}
}
L = text[st.session_state['lang']]

# --- 3. BẢO MẬT ---
if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False
if not st.session_state['authenticated']:
    st.markdown(f"<div style='text-align: center; margin-top: 50px;'><img src='{icon_q68}' width='150'></div>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: gold;'>{L['title']}</h1>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1,2,1])
    with col_b:
        password = st.text_input(L['pwd'], type="password")
        if st.button(L['btn']):
            if password == "A1PRO":
                st.session_state['authenticated'] = True
                st.rerun()
    st.stop()

# --- 4. ENGINE DỮ LIỆU (CẢI TIẾN CHỐNG LỖI) ---
def get_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        res = requests.get(url, timeout=10).json()
        if not isinstance(res, list) or len(res) < 20: return None
        df = pd.DataFrame(res, columns=['Time','Open','High','Low','Close','Vol','CT','QV','T','TB','TQ','I'])
        for c in ['Open','High','Low','Close']: df[c] = df[c].astype(float)
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss + 0.000001))) # Tránh chia cho 0
        return df
    except: return None

# --- 5. SIDEBAR ---
with st.sidebar:
    st.divider()
    target = st.selectbox(L['asset'], ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"])
    timeframe = st.selectbox(L['tf'], ["15m", "30m", "1h", "4h", "1d", "1w", "1M"], index=2)
    chart_style = st.radio(L['style'], ["Candles", "Line", "Area"])
    st.divider()
    st.write(f"📲 {L['qr']}:")
    app_url = "https://audetlbejh8appz.streamlit.app"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={app_url}", width=150)
    if st.button("LOGOUT"):
        st.session_state['authenticated'] = False
        st.rerun()

# --- 6. GIAO DIỆN CHÍNH ---
df = get_data(target, timeframe)

# KIỂM TRA DỮ LIỆU TRƯỚC KHI HIỂN THỊ (SỬA LỖI INDEX)
if df is not None and not df.empty and len(df) > 0:
    price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    ema20 = df['EMA20'].iloc[-1]
    
    asset_display = "GOLD (PAXG)" if target == "PAXGUSDT" else target
    st.markdown(f"<h2 style='text-align: center; color: gold;'>🐢 Q68 | {asset_display} ({timeframe})</h2>", unsafe_allow_html=True)
    
    fig = go.Figure()
    if chart_style == "Candles":
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    elif chart_style == "Line":
        fig.add_trace(go.Scatter(y=df['Close'], line=dict(color='#00ffcc', width=3)))
    else:
        fig.add_trace(go.Scatter(y=df['Close'], fill='tozeroy', line=dict(color='gold')))
    
    fig.add_trace(go.Scatter(y=df['EMA20'], line=dict(color='white', width=1, dash='dot'), name='EMA20'))
    fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="#05070a", plot_bgcolor="#05070a", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # TÍN HIỆU NEON
    if price > ema20 and rsi < 70:
        st.markdown(f'<div class="signal-box buy-neon">{L["buy"]}</div>', unsafe_allow_html=True)
    elif price < ema20 and rsi > 30:
        st.markdown(f'<div class="signal-box sell-neon">{L["sell"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-box hold-neon">{L["hold"]}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric(L['price'], f"${price:,.2f}")
    c2.metric("RSI (14)", f"{rsi:.2f}")
    c3.metric("EMA 20", f"{ema20:,.1f}")
else:
    # Nếu chưa có dữ liệu, hiện thông báo chờ thay vì báo lỗi đỏ
    st.info(L['err'])
    time.sleep(2)
    st.rerun()

st.button("🔥 ACTIVATE GLOBAL STRATEGY", use_container_width=True)
