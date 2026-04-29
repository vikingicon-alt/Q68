import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime

# --- CONFIG CHUẨN SÀN BINANCE ---
st.set_page_config(page_title="Q68 Premier | Binance Style", layout="wide", page_icon="📈")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    .stApp { background-color: #0b0e11; color: #eaecef; font-family: 'Roboto Mono', monospace; }
    
    /* Header Giá & Tín hiệu */
    .price-card { background: #1e2329; padding: 20px; border-radius: 8px; border-left: 5px solid #f0b90b; }
    .live-price { font-size: 52px; font-weight: 700; color: #02c076; margin: 0; line-height: 1; }
    .price-red { color: #cf304a !important; }
    
    /* Nút Lệnh Binance Style */
    .order-btn {
        height: 60px; width: 100%; border-radius: 4px; border: none;
        font-size: 18px; font-weight: 700; color: #848e9c; background: #2b3139;
        display: flex; align-items: center; justify-content: center; transition: 0.3s;
    }
    .btn-buy.active { background: #02c076 !important; color: white !important; box-shadow: 0 0 15px #02c07688; }
    .btn-sell.active { background: #cf304a !important; color: white !important; box-shadow: 0 0 15px #cf304a88; }
    .btn-hold.active { background: #f0b90b !important; color: black !important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CẢI TIẾN ---
with st.sidebar:
    st.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png", width=50)
    st.title("Q68 PREMIER")
    
    asset_list = {"BTC": "BTC-USD", "ETH": "ETH-USD", "BNB": "BNB-USD", "PAXG": "PAXG-USD", "XRP": "XRP-USD"}
    symbol = st.selectbox("MARKET", list(asset_list.keys()))
    tf = st.select_slider("INTERVAL", options=["5m", "15m", "1h", "4h", "1d"], value="1h")
    
    st.divider()
    st.markdown("### INDICATORS")
    show_ema = st.toggle("EMA (7, 25, 99)", value=True)
    show_vol = st.toggle("VOLUME", value=True)
    show_macd = st.toggle("MACD / RSI", value=True)

# --- PHÂN TÍCH NÃO BỘ AI ---
@st.cache_data(ttl=10)
def fetch_binance_data(sym, interval):
    data = yf.download(asset_list[sym], period="5d", interval=interval, progress=False)
    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
    df = data.reset_index()
    # Tính toán EMA đa tầng
    df['EMA7'] = df['Close'].ewm(span=7).mean()
    df['EMA25'] = df['Close'].ewm(span=25).mean()
    df['EMA99'] = df['Close'].ewm(span=99).mean()
    # MACD & RSI
    exp1 = df['Close'].ewm(span=12).mean(); exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2; df['Sig'] = df['MACD'].ewm(span=9).mean()
    delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (g/l)))
    return df

df = fetch_binance_data(symbol, tf)
last = df.iloc[-1]
prev = df.iloc[-2]

# --- LOGIC QUYẾT ĐỊNH (THE BRAIN) ---
signal = "HOLD"
if last['Close'] > last['EMA25'] and last['MACD'] > last['Sig']: signal = "BUY"
elif last['Close'] < last['EMA25'] or last['RSI'] > 75: signal = "SELL"

# --- HIỂN THỊ HEADER GIÁ & NÚT LỆNH ---
c_price, c_buy, c_hold, c_sell = st.columns([2, 1, 1, 1])

with c_price:
    color_class = "" if last['Close'] >= prev['Close'] else "price-red"
    st.markdown(f"""
        <div class="price-card">
            <p style="color:#848e9c; margin:0; font-size:14px;">{symbol} / USDT</p>
            <p class="live-price {color_class}">${last['Close']:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

with c_buy:
    active = "active" if signal == "BUY" else ""
    st.markdown(f'<div class="order-btn btn-buy {active}">BUY</div>', unsafe_allow_html=True)
with c_hold:
    active = "active" if signal == "HOLD" else ""
    st.markdown(f'<div class="order-btn btn-hold {active}">HOLD</div>', unsafe_allow_html=True)
with c_sell:
    active = "active" if signal == "SELL" else ""
    st.markdown(f'<div class="order-btn btn-sell {active}">SELL</div>', unsafe_allow_html=True)

# --- BIỂU ĐỒ TRADINGVIEW STYLE ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, 
                    row_heights=[0.6, 0.15, 0.25] if show_macd else [0.8, 0.2, 0])

# 1. Main Chart (Candlestick)
fig.add_trace(go.Candlestick(x=df.iloc[:,0], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                             increasing_line_color='#02c076', decreasing_line_color='#cf304a'), row=1, col=1)
if show_ema:
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['EMA7'], line=dict(color='#f0b90b', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['EMA25'], line=dict(color='#e841de', width=1)), row=1, col=1)

# 2. Volume Chart
if show_vol:
    v_colors = ['#02c076' if df['Open'].iloc[i] < df['Close'].iloc[i] else '#cf304a' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.iloc[:,0], y=df['Volume'], marker_color=v_colors, opacity=0.5), row=2, col=1)

# 3. MACD & RSI
if show_macd:
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df['RSI'], line=dict(color='#ffffff', width=1.5)), row=3, col=1)
    fig.add_trace(go.Bar(x=df.iloc[:,0], y=df['MACD']-df['Sig'], marker_color='#474d57'), row=3, col=1)

fig.update_layout(height=750, template="plotly_dark", xaxis_rangeslider_visible=False,
                  margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig.update_yaxes(side="right", gridcolor="#1e2329")
fig.update_xaxes(gridcolor="#1e2329")

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
