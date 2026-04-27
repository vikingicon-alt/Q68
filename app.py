import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# --- 1. CẤU HÌNH GIAO DIỆN LUXURY ---
st.set_page_config(page_title="Q68 SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    header, footer, #MainMenu {visibility: hidden !important;}
    .main { background-color: #020617 !important; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 2px solid gold; min-width: 250px !important; }
    div.stButton > button {
        width: 100%; background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
        color: black; font-weight: bold; height: 50px; border-radius: 12px; border: none;
    }
    .neon-box { display: flex; justify-content: space-around; padding: 15px; background: #1e293b; border-radius: 15px; border: 1px solid rgba(255,215,0,0.3); margin-bottom: 20px; }
    .n-light { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900; opacity: 0.1; border: 1px solid rgba(255,255,255,0.2); }
    .n-buy { color: #22c55e; border-color: #22c55e; box-shadow: 0 0 15px #22c55e; opacity: 1; }
    .n-sell { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 15px #ef4444; opacity: 1; }
    .n-hold { color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 15px #f59e0b; opacity: 1; }
    .m-card { background: #1e293b; padding: 10px; border-radius: 10px; border-bottom: 3px solid gold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG ĐĂNG NHẬP (KHÔNG LỖI INDENT) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='text-align: center; margin-top: 50px;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='160'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: gold;'>HỆ THỐNG Q68</h2>", unsafe_allow_html=True)
        key = st.text_input("MÃ TRUY CẬP", type="password")
        if st.button("KÍCH HOẠT HỆ THỐNG"):
            if key == "A1PRO":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

# --- 3. CƠ CHẾ DỮ LIỆU AN TOÀN (FIX INDEX ERROR) ---
@st.cache_data(ttl=12)
def get_safe_data(symbol, tf):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=120"
        res = requests.get(url, timeout=5).json()
        if not isinstance(res, list) or len(res) < 50:
            return None
        df = pd.DataFrame(res, columns=['T','O','H','L','C','V','CT','QV','N','TB','TQ','I'])
        df[['O','H','L','C','V']] = df[['O','H','L','C','V']].astype(float)
        # Tính EMA & RSI
        df['EMA'] = df['C'].ewm(span=20, adjust=False).mean()
        delta = df['C'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        return df
    except:
        return None

# --- 4. SIDEBAR CỐ ĐỊNH ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' width='90'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: gold; text-align: center;'>Q68 MASTER</h3>", unsafe_allow_html=True)
    target = st.selectbox("TÀI SẢN", ["BTCUSDT", "PAXGUSDT", "ETHUSDT"])
    tf_val = st.selectbox("KHUNG GIỜ", ["1h", "4h", "1d", "1w"], index=0)
    st.divider()
    qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app"
    st.image(qr_url, use_container_width=True)
    if st.button("THOÁT"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. GIAO DIỆN CHÍNH ---
df = get_safe_data(target, tf_val)

if df is not None:
    # Lấy dữ liệu an toàn
    last_row = df.iloc[-1]
    p, r, e, v = last_row['C'], last_row['RSI'], last_row['EMA'], last_row['V']
    
    # Tín hiệu đèn Neon
    b_c = "n-buy" if (p > e and r < 65) else ""
    s_c = "n-sell" if (p < e and r > 35) else ""
    h_c = "n-hold" if not b_c and not s_c else ""
    
    st.markdown(f'<div class="neon-box"><div class="n-light {b_c}">MUA</div><div class="n-light {h_c}">CHỜ</div><div class="n-light {s_c}">BÁN</div></div>', unsafe_allow_html=True)
    
    # Biểu đồ chuyên sâu
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Nến"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['V'], marker_color='gray', name="Vol"), row=2, col=1)
    fig.update_layout(height=480, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Các thẻ thông số
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="m-card"><small>GIÁ</small><h4>${p:,.1f}</h4></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="m-card"><small>RSI</small><h4>{r:.2f}</h4></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="m-card"><small>VOL</small><h4>{v:,.0f}</h4></div>', unsafe_allow_html=True)
else:
    st.warning("⚠️ Đang đồng bộ dữ liệu thị trường...")
    time.sleep(3)
    st.rerun()
