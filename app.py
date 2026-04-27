import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# --- 1. THIẾT KẾ GIAO DIỆN ĐẲNG CẤP (UI/UX LUXURY) ---
st.set_page_config(page_title="Q68 GLOBAL SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
        /* Tổng thể nền tối sâu và font chữ hiện đại */
        header, footer, #MainMenu {visibility: hidden !important;}
        .main { background: radial-gradient(circle, #0f172a 0%, #020617 100%); color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
        
        /* Sidebar chuyên nghiệp */
        [data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1e293b; min-width: 300px; }
        
        /* Cải thiện khung đăng nhập & Nút bấm */
        .stTextInput > div > div > input { background-color: #1e293b; color: gold; border: 1px solid #334155; border-radius: 8px; height: 45px; text-align: center; font-size: 18px; }
        div.stButton > button { 
            width: 100%; background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%); 
            color: black; font-weight: 900; border-radius: 12px; border: none; height: 55px; 
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3); transition: 0.3s;
        }
        div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5); }

        /* Khung thông số Metric */
        .stMetric { background: #1e293b; padding: 20px; border-radius: 15px; border-left: 5px solid gold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        
        /* Tín hiệu Signal Lux */
        .signal-card {
            padding: 30px; border-radius: 20px; text-align: center; font-weight: 800; font-size: 32px;
            margin-bottom: 25px; letter-spacing: 3px; border: 2px solid rgba(255,215,0,0.2);
            background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(10px);
        }
        .buy-txt { color: #22c55e; text-shadow: 0 0 15px rgba(34, 197, 94, 0.6); }
        .sell-txt { color: #ef4444; text-shadow: 0 0 15px rgba(239, 68, 68, 0.6); }
        .hold-txt { color: #f59e0b; text-shadow: 0 0 15px rgba(245, 158, 11, 0.6); }
    </style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG NGÔN NGỮ ĐỒNG BỘ ---
if 'lang' not in st.session_state: st.session_state['lang'] = 'vi'
L_DB = {
    'vi': {
        'title': 'HỆ THỐNG Q68 TOÀN CẦU', 'pwd': 'MÃ TRUY CẬP HỆ THỐNG', 'btn_act': 'KÍCH HOẠT NGAY',
        'asset': 'CHỌN TÀI SẢN', 'tf': 'KHUNG THỜI GIAN', 'style': 'LOẠI BIỂU ĐỒ', 'logout': 'THOÁT',
        'buy': '🔥 TÍN HIỆU: MUA (BUY)', 'sell': '❄️ TÍN HIỆU: BÁN (SELL)', 'hold': '⚠️ TÍN HIỆU: CHỜ (HOLD)',
        'price': 'GIÁ THỊ TRƯỜNG', 'rsi': 'CHỈ SỐ RSI', 'ema': 'ĐƯỜNG EMA 20'
    },
    'en': {
        'title': 'Q68 GLOBAL SYSTEM', 'pwd': 'SYSTEM ACCESS KEY', 'btn_act': 'ACTIVATE NOW',
        'asset': 'SELECT ASSET', 'tf': 'TIMEFRAME', 'style': 'CHART TYPE', 'logout': 'LOGOUT',
        'buy': '🔥 SIGNAL: BUY', 'sell': '❄️ SIGNAL: SELL', 'hold': '⚠️ SIGNAL: HOLD',
        'price': 'MARKET PRICE', 'rsi': 'RSI INDEX', 'ema': 'EMA 20 LINE'
    }
}

# --- 3. LOGIC ĐĂNG NHẬP (CĂN CHỈNH ĐẸP) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

def show_login():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(f"<div style='text-align: center; margin-top: 30px;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='160'></div>", unsafe_allow_html=True)
        lang_pick = st.radio(" ", ["Tiếng Việt", "English"], horizontal=True, label_visibility="collapsed")
        st.session_state['lang'] = 'vi' if lang_pick == "Tiếng Việt" else 'en'
        L = L_DB[st.session_state['lang']]
        
        st.markdown(f"<h1 style='text-align: center; color: gold; font-size: 42px; margin-bottom: 30px;'>{L['title']}</h1>", unsafe_allow_html=True)
        pwd = st.text_input(L['pwd'], type="password", placeholder="••••••••")
        st.write(" ")
        if st.button(L['btn_act']):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

if not st.session_state['auth']: show_login()
L = L_DB[st.session_state['lang']]

# --- 4. DATA ENGINE ---
@st.cache_data(ttl=10)
def fetch_global_data(symbol, tf):
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

# --- 5. SIDEBAR (BỐ CỤC CHẶT CHẼ) ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='100'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 GLOBAL ADVISOR</h3>", unsafe_allow_html=True)
    st.divider()
    target = st.selectbox(L['asset'], ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"])
    tf = st.selectbox(L['tf'], ["15m", "1h", "4h", "1d"], index=1)
    style = st.radio(L['style'], ["Candles", "Line"], horizontal=True)
    st.divider()
    st.write("📲 SHARE ACCESS:")
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://audetlbejh8appz.streamlit.app", width=140)if st.button(L['logout']):
        st.session_state['auth'] = False
        st.rerun()

# --- 6. MAIN DASHBOARD ---
df = fetch_global_data(target, tf)
if df is not None:
    p, r, e = df['C'].iloc[-1], df['RSI'].iloc[-1], df['EMA20'].iloc[-1]
    name = "GOLD / USD" if target == "PAXGUSDT" else f"{target[:-4]} / USDT"
    
    st.markdown(f"<h2 style='text-align: center; color: gold; letter-spacing: 2px;'>{name} ANALYTICS ({tf})</h2>", unsafe_allow_html=True)
    
    # Chart tinh chỉnh
    fig = go.Figure()
    if style == "Candles":
        fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Price"))
    else:
        fig.add_trace(go.Scatter(y=df['C'], line=dict(color='#3b82f6', width=3), fill='tozeroy', name="Price"))
    
    fig.add_trace(go.Scatter(y=df['EMA20'], line=dict(color='gold', width=1.5, dash='dot'), name="EMA 20"))
    fig.update_layout(height=480, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Signal Card Luxury
    if p > e and r < 70:
        st.markdown(f'<div class="signal-card buy-txt">{L["buy"]}</div>', unsafe_allow_html=True)
    elif p < e and r > 30:
        st.markdown(f'<div class="signal-card sell-txt">{L["sell"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-card hold-txt">{L["hold"]}</div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric(L['price'], f"${p:,.2f}")
    m2.metric(L['rsi'], f"{r:.2f}")
    m3.metric(L['ema'], f"{e:,.1f}")
else:
    st.warning("⚡ Connecting to Global Market... Please wait.")
    time.sleep(2)
    st.rerun()
