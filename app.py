import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. CẤU HÌNH GIAO DIỆN & CSS TỐI ƯU ---
st.set_page_config(page_title="Q68 GLOBAL MASTER V21", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background: #020617 !important; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 2px solid gold; min-width: 280px !important; }
    div.stButton > button { width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); color: black; font-weight: 900; border-radius: 12px; height: 50px; }
    .neon-card { display: flex; justify-content: space-around; padding: 20px; background: #1e293b; border-radius: 15px; border: 1px solid gold; margin-bottom: 20px; }
    .signal { width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; opacity: 0.1; border: 1px solid rgba(255,255,255,0.2); }
    .buy-on { color: #22c55e; border-color: #22c55e; box-shadow: 0 0 15px #22c55e; opacity: 1; }
    .sell-on { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 15px #ef4444; opacity: 1; }
    .hold-on { color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 15px #f59e0b; opacity: 1; }
    .stMetric { background: #1e293b; padding: 15px; border-radius: 10px; border-bottom: 3px solid gold; }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ TRẠNG THÁI ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'lang' not in st.session_state: st.session_state['lang'] = 'Việt'

TXT = {
    'Việt': {'title': 'HỆ THỐNG Q68 TOÀN CẦU', 'pwd': 'MÃ TRUY CẬP', 'btn': 'KÍCH HOẠT', 'coin': 'TÀI SẢN', 'tf': 'KHUNG GIỜ', 'style': 'BIỂU ĐỒ', 'sync': 'Đang đồng bộ dữ liệu thị trường...'},
    'Eng': {'title': 'Q68 GLOBAL SYSTEM', 'pwd': 'ACCESS CODE', 'btn': 'ACTIVATE', 'coin': 'ASSETS', 'tf': 'TIMEFRAME', 'style': 'CHART STYLE', 'sync': 'Syncing data...'}
}

if not st.session_state['auth']:
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown("<div style='text-align: center; margin-top: 50px;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='160'></div>", unsafe_allow_html=True)
        choice = st.radio("NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        st.session_state['lang'] = 'Việt' if "Việt" in choice else 'Eng'
        ui = TXT[st.session_state['lang']]
        pwd = st.text_input(ui['pwd'], type="password")
        if st.button(ui['btn']):
            if pwd == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

ui = TXT[st.session_state['lang']]
# --- 3. ĐỘNG CƠ DỮ LIỆU TỐI ƯU (FIX LỖI ĐỒNG BỘ) ---
@st.cache_data(ttl=5)
def get_data(s, i):
    try:
        # Binance klines limit: 1M (Month) is the max for native candles
        url = f"https://api.binance.com/api/v3/klines?symbol={s}&interval={i}&limit=200"
        r = requests.get(url, timeout=10).json()
        if not isinstance(r, list) or len(r) < 10: return None
        df = pd.DataFrame(r, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
        df['EMA'] = df['C'].ewm(span=20, adjust=False).mean()
        diff = df['C'].diff()
        u = (diff.where(diff > 0, 0)).rolling(14).mean()
        d = (-diff.where(diff < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (u / (d + 1e-10))))
        return df
    except: return None

# --- 4. SIDEBAR (BỔ SUNG KHUNG GIỜ: 30m, 1w, 1M) ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='90'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    st.divider()
    coin = st.selectbox(ui['coin'], ["BTCUSDT", "ETHUSDT", "PAXGUSDT", "SOLUSDT", "BNBUSDT"])
    # Khôi phục đầy đủ khung giờ anh yêu cầu
    tf_options = {"30m":"30 Phút", "1h":"1 Giờ", "4h":"4 Giờ", "1d":"1 Ngày", "1w":"1 Tuần", "1M":"1 Tháng"}
    tf_key = st.selectbox(ui['tf'], list(tf_options.keys()), format_func=lambda x: tf_options[x], index=1)
    ctype = st.radio(ui['style'], ["Candles", "Line", "Area"], horizontal=True)
    st.divider()
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app", caption="SHARE A1 SYSTEM")
    if st.button("LOGOUT / THOÁT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHIẾN THUẬT ---
df = get_data(coin, tf_key)

if df is not None:
    now = df.iloc[-1]
    p, r, e, v = now['C'], now['RSI'], now['EMA'], now['V']
    
    b_style = "buy-on" if (p > e and r < 65) else ""
    s_style = "sell-on" if (p < e and r > 35) else ""
    h_style = "hold-on" if not b_style and not s_style else ""
    
    st.markdown(f'<div class="neon-card"><div class="signal {b_style}">MUA</div><div class="signal {h_style}">CHỜ</div><div class="signal {s_style}">BÁN</div></div>', unsafe_allow_html=True)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    if ctype == "Candles":
        fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Price"), row=1, col=1)
    elif ctype == "Line":
        fig.add_trace(go.Scatter(y=df['C'], line=dict(color='gold', width=2), name="Price"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(y=df['C'], fill='tozeroy', line=dict(color='gold'), name="Price"), row=1, col=1)
    
    fig.add_trace(go.Bar(x=df.index, y=df['V'], marker_color='rgba(128,128,128,0.5)', name="Vol"), row=2, col=1)
    fig.update_layout(height=550, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("GIÁ", f"${p:,.1f}")
    c2.metric("RSI", f"{r:.2f}")
    c3.metric("KHỐI LƯỢNG", f"{v:,.0f}")
else:
    st.error(ui['sync'])
    time.sleep(3)
    st.rerun()
