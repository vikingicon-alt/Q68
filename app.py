import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_lightweight_charts import renderLightweightCharts

# --- CẤU HÌNH GIAO DIỆN SIÊU CẤP (FULL DARK MODE) ---
st.set_page_config(page_title="Binance Pro Terminal", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    /* Nút bấm thiết kế lại theo Binance App */
    .btn-container { display: flex; gap: 10px; margin-bottom: 20px; }
    .nav-btn {
        flex: 1; height: 50px; border-radius: 4px; display: flex; 
        align-items: center; justify-content: center; font-weight: 700;
        background: #2b3139; color: #848e9c; border: none; font-size: 16px;
    }
    .buy-active { background: #02c076 !important; color: white !important; box-shadow: 0 4px 15px rgba(2, 192, 118, 0.3); }
    .sell-active { background: #cf304a !important; color: white !important; box-shadow: 0 4px 15px rgba(207, 48, 74, 0.3); }
    .hold-active { background: #f0b90b !important; color: black !important; }
    
    /* Header Giá mượt mà */
    .header-box { border-bottom: 1px solid #2b3139; padding-bottom: 15px; margin-bottom: 20px; }
    .price-text { font-size: 42px; font-weight: 700; color: #02c076; }
</style>
""", unsafe_allow_html=True)

# --- QUẢN LÝ DỮ LIỆU ---
@st.cache_data(ttl=15)
def get_pro_data(symbol, tf):
    assets = {"BTC": "BTC-USD", "ETH": "ETH-USD", "BNB": "BNB-USD", "PAXG": "PAXG-USD"}
    df = yf.download(assets[symbol], period="5d", interval=tf, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df.columns = ['time', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    df['time'] = df['time'].astype(str)
    # Indicators cho AI
    df['ema25'] = df['close'].ewm(span=25).mean()
    return df

# Sidebar gọn gàng
with st.sidebar:
    st.markdown("### 🛠 CONTROL PANEL")
    sym = st.selectbox("Market", ["BTC", "ETH", "BNB", "PAXG"])
    tf_choice = st.selectbox("Interval", ["15m", "1h", "4h", "1d"], index=1)

df = get_pro_data(sym, tf_choice)
last = df.iloc[-1]

# --- AI BRAIN: PROJECT A1 DECISION ---
signal = "HOLD"
if last['close'] > last['ema25']: signal = "BUY"
elif last['close'] < last['ema25']: signal = "SELL"

# --- UI HEADER & BUTTONS ---
st.markdown(f"""
<div class="header-box">
    <div style="color: #848e9c; font-size: 14px;">{sym} / USDT • {tf_choice}</div>
    <div class="price-text">${last['close']:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# Hiển thị nút bấm (Không bao giờ liệt)
c1, c2, c3 = st.columns(3)
with c1:
    style = "buy-active" if signal == "BUY" else ""
    st.markdown(f'<div class="nav-btn {style}">BUY</div>', unsafe_allow_html=True)
with c2:
    style = "hold-active" if signal == "HOLD" else ""
    st.markdown(f'<div class="nav-btn {style}">HOLD</div>', unsafe_allow_html=True)
with c3:
    style = "sell-active" if signal == "SELL" else ""
    st.markdown(f'<div class="nav-btn {style}">SELL</div>', unsafe_allow_html=True)

# --- BIỂU ĐỒ LIGHTWEIGHT (GIỐNG BINANCE 100%) ---
chart_data = df[['time', 'open', 'high', 'low', 'close']].to_dict('records')
volume_data = df[['time', 'volume', 'close', 'open']].copy()
volume_data['color'] = volume_data.apply(lambda x: '#02c076' if x['close'] >= x['open'] else '#cf304a', axis=1)
volume_data = volume_data[['time', 'volume', 'color']].rename(columns={'volume': 'value'}).to_dict('records')

chart_options = {
    "layout": {"background_color": "#0b0e11", "text_color": "#848e9c"},
    "grid": {"vertLines": {"color": "#1e2329"}, "horzLines": {"color": "#1e2329"}},
    "rightPriceScale": {"borderColor": "#2b3139"},
    "timeScale": {"borderColor": "#2b3139"},
}

# Render biểu đồ chính
renderLightweightCharts([
    {
        "type": "Candlestick",
        "data": chart_data,
        "options": {"upColor": "#02c076", "downColor": "#cf304a", "borderVisible": False, "wickUpColor": "#02c076", "wickDownColor": "#cf304a"}
    },
    {
        "type": "Histogram",
        "data": volume_data,
        "options": {"color": "#26a69a", "priceFormat": {"type": "volume"}, "priceScaleId": ""},
        "priceScale": {"scaleMargins": {"top": 0.8, "bottom": 0}}
    }
], chart_options)

st.markdown("---")
st.caption("Project A1 AI Core • Real-time Syncing")
