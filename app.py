import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# --- 1. THIẾT KẾ GIAO DIỆN (UI/UX) ---
st.set_page_config(page_title="A1 SUPREME V44.1", layout="wide")

st.markdown("""
<style>
    header, footer, .stAppHeader {visibility: hidden !important; display: none !important;}
    .main { background: #000000 !important; color: #FFD700; }
    .stImage img { border-radius: 20px; border: 2px solid gold; box-shadow: 0 0 30px #FFD700; }
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728);
        color: black; font-weight: bold; border-radius: 12px; height: 50px; border: none;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [aria-selected="true"] { color: gold !important; border-bottom-color: gold !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG QUẢN TRỊ ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'db' not in st.session_state: st.session_state['db'] = {"admin": "A1PRO"}

# --- 3. KIỂM TRA ĐĂNG NHẬP & QR ---
if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=160)
        st.markdown("<h1 style='color: gold;'>A1 GLOBAL</h1>", unsafe_allow_html=True)
        
        lang = st.radio("NGÔN NGỮ / LANGUAGE", ["Tiếng Việt", "English"], horizontal=True)
        if lang == "Tiếng Việt":
            L = {"u": "Tài khoản", "p": "Mật khẩu", "b": "KÍCH HOẠT", "reg": "Đăng ký", "nu": "Tên mới", "np": "Mật khẩu mới", "qr": "QUÉT ĐỂ TRUY CẬP"}
        else:
            L = {"u": "Username", "p": "Password", "b": "LOGIN", "reg": "Register", "nu": "New User", "np": "New Pass", "qr": "SCAN TO ACCESS"}
        
        tab_login, tab_reg = st.tabs([L['u'].upper(), L['reg'].upper()])
        
        with tab_login:
            u_in = st.text_input(L['u'], key="l_user")
            p_in = st.text_input(L['p'], type="password", key="l_pass")
            if st.button(L['b']):
                if u_in in st.session_state['db'] and st.session_state['db'][u_in] == p_in:
                    st.session_state['auth'] = True
                    st.rerun()
                else: st.error("❌ Invalid")
        
        with tab_reg:
            nu = st.text_input(L['nu'], key="r_user")
            np = st.text_input(L['np'], type="password", key="r_pass")
            if st.button(L['reg'].upper()):
                if nu and np:
                    st.session_state['db'][nu] = np
                    st.success("✅ Success!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app")
        st.caption(L['qr'])
    st.stop()

# --- 4. ENGINE DỮ LIỆU SIÊU TỐC ---
@st.cache_data(ttl=15)
def fetch_fast(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
        df = pd.read_json(url).iloc[:, :6]
        df.columns = ['T', 'O', 'H', 'L', 'C', 'V']
        df[['O', 'H', 'L', 'C']] = df[['O', 'H', 'L', 'C']].astype(float)
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        return df
    except: return None

# --- 5. GIAO DIỆN THỊ TRƯỜNG ---
with st.sidebar:
    st.markdown("<h2 style='color: gold;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    pair = st.selectbox("ASSET", ["BTCUSDT", "ETHUSDT", "PAXGUSDT"])
    if st.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun()

data = fetch_fast(pair)
if data is not None:
    curr = data.iloc[-1]
    st.markdown(f"### 📊 MARKET: {pair}")
    
    fig = go.Figure(data=[
        go.Candlestick(x=data.index, open=data['O'], high=data['H'], low=data['L'], close=data['C'], name="Price"),
        go.Scatter(x=data.index, y=data['EMA20'], line=dict(color='gold', width=2), name="EMA20")
    ])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2 = st.columns(2)
    c1.metric("PRICE", f"${curr['C']:,.2f}")
    if curr['C'] > curr['EMA20']:
        c2.success("🚀 SIGNAL: BUY (A1 UP)")
    else:
        c2.error("📉 SIGNAL: SELL (A1 DOWN)")
else:
    st.warning("🔄 Connecting...")
    time.sleep(3)
    st.rerun()
