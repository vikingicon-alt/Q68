import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- 1. THIẾT LẬP GIAO DIỆN BINANCE PRO (ÉP KHUNG IPAD) ---
st.set_page_config(page_title="Q68 Premier Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    
    /* Header Giá: Chữ to, rõ, không lệch */
    .header-box { border-bottom: 1px solid #2b3139; padding-bottom: 10px; margin-bottom: 15px; }
    .symbol-txt { color: #848e9c; font-size: 14px; font-weight: 500; }
    .price-txt { font-size: 48px; font-weight: 700; color: #02c076; line-height: 1; }
    .down { color: #cf304a !important; }

    /* Hệ thống 3 Nút Lệnh: Dùng Flexbox để chống liệt và nhảy hàng */
    .btn-container { 
        display: flex; 
        gap: 10px; 
        width: 100%; 
        margin: 15px 0 25px 0; 
    }
    .status-btn { 
        flex: 1; 
        height: 55px; 
        border-radius: 4px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-weight: 700; 
        font-size: 18px;
        background: #2b3139; 
        color: #848e9c;
        border: 1px solid #474d57;
    }
    .buy-on { background: #02c076 !important; color: white !important; border: none; box-shadow: 0 4px 20px rgba(2,192,118,0.4); }
    .sell-on { background: #cf304a !important; color: white !important; border: none; box-shadow: 0 4px 20px rgba(207,48,74,0.4); }
    .hold-on { background: #f0b90b !important; color: #000 !important; border: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. BỘ NÃO DỮ LIỆU (PROJECT A1) ---
@st.cache_data(ttl=15)
def load_data_final(symbol, tf):
    mapping = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "PAXG": "PAXG-USD"}
    data = yf.download(mapping[symbol], period="3d", interval=tf, progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    df = data.reset_index()
    # Tính EMA 25 & MACD cho AI
    df['EMA25'] = df['Close'].ewm(span=25, adjust=False).mean()
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

# Sidebar
with st.sidebar:
    st.markdown("### 🐢 Q68 SYSTEM")
    s_sym = st.selectbox("Market", ["BTC", "ETH", "SOL", "PAXG"], index=0)
    s_tf = st.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)

df = load_data_final(s_sym, s_tf)
last = df.iloc[-1]
prev = df.iloc[-2]

# --- 3. AI DECISION ---
signal = "HOLD"
if last['Close'] > last['EMA25'] and last['MACD'] > last['Signal']:
    signal = "BUY"
elif last['Close'] < last['EMA25'] or last['MACD'] < last['Signal']:
    signal = "SELL"

# --- 4. HIỂN THỊ GIAO DIỆN ---
p_color = "down" if last['Close'] < prev['Close'] else ""
st.markdown(f"""
<div class="header-box">
    <div class="symbol-txt">{s_sym} / USDT • {s_tf}</div>
    <div class="price-txt {p_color}">${last['Close']:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# 3 Nút bấm chuẩn Binance (Không bao giờ lệch)
st.markdown(f"""
<div class="btn-container">
    <div class="status-btn {'buy-on' if signal == 'BUY' else ''}">BUY</div>
    <div class="status-btn {'hold-on' if signal == 'HOLD' else ''}">HOLD</div>
    <div class="status-btn {'sell-on' if signal == 'SELL' else ''}">SELL</div>
</div>
""", unsafe_allow_html=True)

# --- 5. BIỂU ĐỒ NẾN CHUẨN SÀN ---
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
t_axis = 'Date' if 'Date' in df.columns else 'Datetime'

# Tầng 1: Nến & EMA
fig.add_trace(go.Candlestick(
    x=df[t_axis], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    increasing_line_color='#02c076', decreasing_line_color='#cf304a',
    increasing_fillcolor='#02c076', decreasing_fillcolor='#cf304a'
), row=1, col=1)
fig.add_trace(go.Scatter(x=df[t_axis], y=df['EMA25'], line=dict(color='#f0b90b', width=1.5)), row=1, col=1)

# Tầng 2: MACD Histogram
m_diff = df['MACD'] - df['Signal']
m_colors = ['#02c076' if x >= 0 else '#cf304a' for x in m_diff]
fig.add_trace(go.Bar(x=df[t_axis], y=m_diff, marker_color=m_colors), row=2, col=1)

fig.update_layout(
    height=600, template="plotly_dark", xaxis_rangeslider_visible=False,
    margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False
)
fig.update_yaxes(side="right", gridcolor="#1e2329")
fig.update_xaxes(gridcolor="#1e2329")

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
