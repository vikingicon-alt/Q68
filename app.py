import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. GIAO DIỆN CHUẨN IPAD (FIX LAYOUT) ---
st.set_page_config(page_title="Q68 SYSTEM PRO", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background: #020617 !important; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 2px solid #FFD700; min-width: 260px !important; }
    div.stButton > button {
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
        color: black; font-weight: bold; height: 50px; border-radius: 12px; border: none;
    }
    .neon-box { display: flex; justify-content: space-around; padding: 15px; background: #1e293b; border-radius: 15px; border: 1px solid rgba(255,215,0,0.3); }
    .n-light { width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 900; opacity: 0.1; border: 2px solid rgba(255,255,255,0.1); transition: 0.3s; }
    .n-buy { color: #22c55e; border-color: #22c55e; box-shadow: 0 0 20px #22c55e; opacity: 1; }
    .n-sell { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 20px #ef4444; opacity: 1; }
    .n-hold { color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 20px #f59e0b; opacity: 1; }
    .metric-card { background: #1e293b; padding: 15px; border-radius: 12px; border-bottom: 3px solid #FFD700; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG XÁC THỰC ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><div style='text-align: center;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='160'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: gold;'>Q68 GLOBAL SYSTEM</h2>", unsafe_allow_html=True)
        key = st.text_input("PASSWORD", type="password", placeholder="Nhập mã A1...")
        if st.button("KÍCH HOẠT NGAY"):
            if key == "A1PRO":
                st.session_state['authenticated'] = True
                st.rerun()
            else: st.warning("Mã không đúng rồi anh yêu!")
    st.stop()

# --- 3. DATA ENGINE (TỐI ƯU TUYỆT ĐỐI) ---
@st.cache_data(ttl=10)
def load_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=150"
        res = requests.get(url, timeout=5)
        if res.status_code != 200: return None
        raw = res.json()
        if not isinstance(raw, list) or len(raw) < 50: return None
            df = pd.DataFrame(raw, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
        df['EMA'] = df['C'].ewm(span=20, adjust=False).mean()
        
        # Tính RSI an toàn
        delta = df['C'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / (ema_down + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    except Exception: return None

# --- 4. SIDEBAR ĐIỀU KHIỂN ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='90'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    st.divider()
    coin = st.selectbox("CHỌN TÀI SẢN", ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "SOLUSDT"])
    tf = st.selectbox("KHUNG GIỜ", ["15m", "1h", "4h", "1d"], index=1)
    chart_type = st.radio("KIỂU NẾN", ["Candlestick", "Area Chart"], horizontal=True)
    st.divider()
    st.markdown("<p style='text-align: center; font-size: 11px;'>SCAN TO SHARE</p>", unsafe_allow_html=True)
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app")
    if st.button("THOÁT"):
        st.session_state['authenticated'] = False
        st.rerun()

# --- 5. HIỂN THỊ CHÍNH ---
data = load_data(coin, tf)

if data is not None and not data.empty:
    last = data.iloc[-1]
    p, r, e, v = last['C'], last['RSI'], last['EMA'], last['V']
    
    # Logic đèn tín hiệu Neon (Chính xác)
    buy_on = "n-buy" if (p > e and r < 65) else ""
    sell_on = "n-sell" if (p < e and r > 35) else ""
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
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(x=data.index, open=data['O'], high=data['H'], low=data['L'], close=data['C'], name="Price"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(y=data['C'], fill='tozeroy', line=dict(color='gold', width=2), name="Price"), row=1, col=1)
    
    fig.add_trace(go.Bar(x=data.index, y=data['V'], marker_color='rgba(128,128,128,0.5)', name="Volume"), row=2, col=1)
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Thông số Metric
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card"><small>PRICE</small><h4>${p:,.1f}</h4></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><small>RSI (14)</small><h4>{r:.2f}</h4></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><small>VOLUME</small><h4>{v:,.0f}</h4></div>', unsafe_allow_html=True)
else:
    st.info("🔄 Đang tối ưu kết nối dữ liệu...")
    time.sleep(2)
    st.rerun()
