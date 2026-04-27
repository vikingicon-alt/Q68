import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Q68 SYSTEM GLOBAL", layout="wide", page_icon="🐢")

# Giao diện chuẩn quốc tế
st.markdown("""
    <style>
        header, footer, #MainMenu {visibility: hidden !important;}
        .main {background-color: #05070a; color: white;}
        [data-testid="stSidebar"] {background-color: #0c0f14; border-right: 1px solid #1e2229;}
        .signal-box {
            padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; font-size: 28px;
            margin-bottom: 20px; text-transform: uppercase;
        }
        .buy-neon { border: 3px solid #00ffcc; color: #00ffcc; text-shadow: 0 0 15px #00ffcc; }
        .sell-neon { border: 3px solid #ff3366; color: #ff3366; text-shadow: 0 0 15px #ff3366; }
        .hold-neon { border: 3px solid #ffcc00; color: #ffcc00; text-shadow: 0 0 15px #ffcc00; }
        div.stButton > button { width: 100%; background: gold; color: black; font-weight: bold; border-radius: 10px; height: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BỘ TỪ ĐIỂN SONG NGỮ (ĐỒNG BỘ 100%) ---
if 'lang' not in st.session_state: st.session_state['lang'] = 'vi'

translations = {
    'vi': {
        'title': 'HỆ THỐNG Q68 TOÀN CẦU', 'pwd': 'MÃ TRUY CẬP:', 'btn_act': 'KÍCH HOẠT HỆ THỐNG',
        'asset': 'TÀI SẢN', 'tf': 'KHUNG GIỜ', 'style': 'MẪU ĐỒ THỊ', 'logout': 'ĐĂNG XUẤT',
        'buy': '🔥 LỆNH: MUA (BUY)', 'sell': '❄️ LỆNH: BÁN (SELL)', 'hold': '⚠️ LỆNH: CHỜ (HOLD)',
        'price': 'GIÁ HIỆN TẠI', 'sync': '🔄 Đang đồng bộ dữ liệu thế giới...', 'share': 'QUÉT ĐỂ CHIA SẺ'
    },
    'en': {
        'title': 'Q68 GLOBAL SYSTEM', 'pwd': 'ACCESS KEY:', 'btn_act': 'ACTIVATE SYSTEM',
        'asset': 'ASSET', 'tf': 'TIMEFRAME', 'style': 'CHART STYLE', 'logout': 'LOGOUT',
        'buy': '🔥 SIGNAL: BUY', 'sell': '❄️ SIGNAL: SELL', 'hold': '⚠️ SIGNAL: HOLD',
        'price': 'CURRENT PRICE', 'sync': '🔄 Syncing global data...', 'share': 'SCAN TO SHARE'
    }
}

# --- 3. KIỂM TRA ĐĂNG NHẬP ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

def login():
    st.markdown("<div style='text-align: center; margin-top: 50px;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='140'></div>", unsafe_allow_html=True)
    # Chọn ngôn ngữ ngay tại màn hình chờ
    lang_select = st.radio("CHỌN NGÔN NGỮ / SELECT LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
    st.session_state['lang'] = 'vi' if lang_select == "Tiếng Việt" else 'en'
    L = translations[st.session_state['lang']]
    
    st.markdown(f"<h1 style='text-align: center; color: gold;'>{L['title']}</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        pwd = st.text_input(L['pwd'], type="password")
        if st.button(L['btn_act']):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

if not st.session_state['auth']: login()

L = translations[st.session_state['lang']]

# --- 4. ENGINE DỮ LIỆU ---
@st.cache_data(ttl=15)
def get_data(symbol, tf):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=100"
        r = requests.get(url, timeout=10).json()
        df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C']] = df[['O','H','L','C']].astype(float)
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 0.000001))))
        return df
    except: return None

# --- 5. SIDEBAR ĐIỀU HÀNH ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=90)
    # Nút chuyển ngôn ngữ trong Sidebar cũng đồng bộ
    new_lang = st.radio("LANGUAGE", ["Tiếng Việt", "English"], index=0 if st.session_state['lang'] == 'vi' else 1, horizontal=True)
    st.session_state['lang'] = 'vi' if new_lang == "Tiếng Việt" else 'en'
    L = translations[st.session_state['lang']] # Cập nhật từ điển ngay lập tức
    
    st.divider()
    target = st.selectbox(L['asset'], ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"])
    timeframe = st.selectbox(L['tf'], ["15m", "1h", "4h", "1d"], index=1)
    chart_style = st.radio(L['style'], ["Candles", "Line", "Area"])
    st.divider()
    st.write(f"📲 {L['share']}:")
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://audetlbejh8appz.streamlit.app", width=140)
    if st.button(L['logout']):
        st.session_state['auth'] = False
        st.rerun()

# --- 6. HIỂN THỊ CHÍNH ---
df = get_data(target, timeframe)

if df is not None:
    price, rsi, ema = df['C'].iloc[-1], df['RSI'].iloc[-1], df['EMA20'].iloc[-1]
    asset_name = "GOLD (VÀNG)" if target == "PAXGUSDT" else target
    st.markdown(f"<h2 style='text-align: center; color: gold;'>🐢 Q68 | {asset_name} ({timeframe})</h2>", unsafe_allow_html=True)
    
    fig = go.Figure()
    if chart_style == "Candles":
        fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C']))
    elif chart_style == "Line":
        fig.add_trace(go.Scatter(y=df['C'], line=dict(color='#00ffcc', width=3)))
    else:
        fig.add_trace(go.Scatter(y=df['C'], fill='tozeroy', line=dict(color='gold')))
        fig.add_trace(go.Scatter(y=df['EMA20'], line=dict(color='white', width=1, dash='dot'), name='EMA20'))
    fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="#05070a", plot_bgcolor="#05070a", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Tín hiệu NEON chuẩn xác
    if price > ema and rsi < 70:
        st.markdown(f'<div class="signal-box buy-neon">{L["buy"]}</div>', unsafe_allow_html=True)
    elif price < ema and rsi > 30:
        st.markdown(f'<div class="signal-box sell-neon">{L["sell"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-box hold-neon">{L["hold"]}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric(L['price'], f"${price:,.2f}")
    c2.metric("RSI (14)", f"{rsi:.2f}")
    c3.metric("EMA 20", f"{ema:,.1f}")
else:
    st.info(L['sync'])
    time.sleep(2)
    st.rerun()
