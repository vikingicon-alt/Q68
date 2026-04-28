import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time

# --- 1. GIAO DIỆN QUÝ TỘC (UI/UX) ---
st.set_page_config(page_title="A1 ETERNITY V45.1", layout="wide")
st.markdown("""
<style>
    header, footer, .stAppHeader {visibility: hidden; display: none;}
    .main { background: #000000 !important; color: #FFD700; }
    div.stButton > button { 
        width: 100%; background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728);
        color: black; font-weight: bold; border-radius: 12px; height: 50px; border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG TÀI KHOẢN (SONG NGỮ) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'db' not in st.session_state: st.session_state['db'] = {"admin": "A1PRO"}

if not st.session_state['auth']:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", width=160)
        st.markdown("<h1 style='color: gold;'>A1 GLOBAL</h1>", unsafe_allow_html=True)
        
        # Giữ nguyên lựa chọn ngôn ngữ theo ý anh
        lang = st.radio("SELECT LANGUAGE / CHỌN NGÔN NGỮ", ["English", "Tiếng Việt"], horizontal=True)
        if lang == "Tiếng Việt":
            L = {"u": "Tài khoản", "p": "Mật khẩu", "b": "KÍCH HOẠT", "reg": "ĐĂNG KÝ", "qr": "QUÉT ĐỂ TRUY CẬP"}
        else:
            L = {"u": "Username", "p": "Password", "b": "LOGIN", "reg": "REGISTER", "qr": "SCAN TO ACCESS"}
        
        t1, t2 = st.tabs([L['u'].upper(), L['reg'].upper()])
        with t1:
            u = st.text_input(L['u'], key="l_u")
            p = st.text_input(L['p'], type="password", key="l_p")
            if st.button(L['b']):
                if u in st.session_state['db'] and st.session_state['db'][u] == p:
                    st.session_state['auth'] = True
                    st.rerun()
        with t2:
            nu = st.text_input(f"New {L['u']}", key="r_u")
            np = st.text_input(f"New {L['p']}", type="password", key="r_p")
            if st.button(L['reg']):
                if nu and np:
                    st.session_state['db'][nu] = np
                    st.success("Success! Please Login.")
        
        # Phục hồi mã QR cho anh
        st.markdown("<br>", unsafe_allow_html=True)
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://nrynpp6caudetlbejh8appz.streamlit.app")
        st.caption(L['qr'])
    st.stop()

# --- 3. GIAO DIỆN CHÍNH: TÍCH HỢP TRADINGVIEW & BINANCE ---
with st.sidebar:
    st.markdown("<h2 style='color: gold;'>Q68 MASTER</h2>", unsafe_allow_html=True)
    mode = st.radio("VIEW MODE / CHẾ ĐỘ XEM", ["TradingView (Global Indicators)", "A1 Chart (Binance EMA)"])
    pair = st.selectbox("SYMBOL / CẶP", ["BTCUSDT", "ETHUSDT", "PAXGUSDT", "SOLUSDT"])
    if st.button("LOGOUT / THOÁT"):
        st.session_state['auth'] = False
        st.rerun()

if "TradingView" in mode:
    st.markdown(f"### 🌐 TRADINGVIEW TERMINAL: {pair}")
    # Nhúng TradingView Widget - Giải pháp siêu mượt cho iPad (975b97a2)
    tv_code = f"""
    <div class="tradingview-widget-container" style="height:550px;">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "BINANCE:{pair}", "interval": "60",
        "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "en",
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(tv_code, height=560)
    st.info("💡 Pro Tip: TradingView provides direct global data. Smooth on iPad!")

else:
    # BIỂU ĐỒ A1 EMA20 (DỮ LIỆU TỰ ĐỘNG THỬ LẠI)
    st.markdown(f"### 📊 A1 SYSTEM CHART: {pair}")
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval=1h&limit=100"
        df = pd.read_json(url).iloc[:, :6]
        df.columns = ['T','O','H','L','C','V']
        df[['O','H','L','C']] = df[['O','H','L','C']].astype(float)
        df['EMA20'] = df['C'].ewm(span=20, adjust=False).mean()
        
        import plotly.graph_objects as go
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['O'], high=df['H'], low=df['L'], close=df['C'], name="Candle"),
                              go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='gold', width=2), name="EMA20")])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        if df.iloc[-1]['C'] > df.iloc[-1]['EMA20']: st.success("🚀 SIGNAL: BUY (A1 UP)")
        else: st.error("📉 SIGNAL: SELL (A1 DOWN)")
    except:
        st.warning("🔄 Connecting... Try 'TradingView' mode if this takes too long.")
        time.sleep(3)
        st.rerun()
