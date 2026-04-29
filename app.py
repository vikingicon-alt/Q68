import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- 1. GIAO DIỆN DARK-MODE BINANCE PRO ---
st.set_page_config(page_title="Q68 Ultimate Terminal", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    /* Hệ thống nút lệnh Flexbox - Không bao giờ lệch */
    .btn-container { display: flex; gap: 8px; margin: 10px 0; }
    .nav-btn {
        flex: 1; height: 50px; border-radius: 4px; display: flex; 
        align-items: center; justify-content: center; font-weight: 700;
        background: #2b3139; color: #848e9c; font-size: 16px; border: 1px solid #474d57;
    }
    .active-buy { background: #02c076 !important; color: white !important; border: none; box-shadow: 0 4px 15px rgba(2,192,118,0.3); }
    .active-sell { background: #cf304a !important; color: white !important; border: none; box-shadow: 0 4px 15px rgba(207,48,74,0.3); }
    .active-hold { background: #f0b90b !important; color: black !important; border: none; }
    
    .price-large { font-size: 52px; font-weight: 700; color: #02c076; line-height: 1; margin: 10px 0; }
    .price-red { color: #cf304a !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. BỘ BA KHUNG ĐIỀU KHIỂN (SIDEBAR) ---
with st.sidebar:
    st.markdown("## ⚙️ HỆ THỐNG ĐIỀU KHIỂN")
    
    # KHUNG 1: NGÔN NGỮ (LANGUAGE)
    lang = st.radio("Ngôn ngữ / Language", ["Tiếng Việt", "English"], horizontal=True)
    t = {
        "Tiếng Việt": ["Tài sản", "Khung giờ", "Chỉ báo", "Kiểu biểu đồ", "Nến", "Đường", "Bật/Tắt"],
        "English": ["Asset", "Timeframe", "Indicators", "Chart Type", "Candle", "Line", "On/Off"]
    }[lang]
    
    st.divider()
    
    # KHUNG 2: CHỈ BÁO (INDICATORS)
    st.markdown(f"### 📊 {t[2]}")
    show_ema = st.toggle("EMA 25/99", value=True)
    show_vol = st.toggle("Volume", value=True)
    show_macd = st.toggle("MACD", value=True)
    show_rsi = st.toggle("RSI", value=False)
    
    st.divider()
    
    # KHUNG 3: BIỂU ĐỒ (CHART CONTROL)
    st.markdown(f"### 📈 {t[3]}")
    chart_style = st.selectbox(t[3], [t[4], t[5]]) # Nến hoặc Đường
    asset_key = st.selectbox(t[0], ["BTC", "ETH", "PAXG", "SOL", "BNB"])
    tf = st.selectbox(t[1], ["15m", "1h", "4h", "1d"], index=1)

# --- 3. XỬ LÝ DỮ LIỆU ---
@st.cache_data(ttl=10)
def get_ultimate_data(symbol, interval):
    mapping = {"BTC": "BTC-USD", "ETH": "ETH-USD", "PAXG": "PAXG-USD", "SOL": "SOL-USD", "BNB": "BNB-USD"}
    df = yf.download(mapping[symbol], period="5d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    # Tính toán EMA, MACD, RSI
    df['EMA25'] = df['Close'].ewm(span=25).mean()
    df['EMA99'] = df['Close'].ewm(span=99).mean()
    exp1 = df['Close'].ewm(span=12).mean(); exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2; df['Sig'] = df['MACD'].ewm(span=9).mean()
    delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (g/l)))
    return df

df = get_ultimate_data(asset_key, tf)
last = df.iloc[-1]
prev = df.iloc[-2]

# Logic Tín hiệu AI
signal = "HOLD"
if last['Close'] > last['EMA25'] and last['MACD'] > last['Sig']: signal = "BUY"
elif last['Close'] < last['EMA25'] or last['MACD'] < last['Sig']: signal = "SELL"

# --- 4. HIỂN THỊ GIAO DIỆN CHÍNH ---
p_color = "price-red" if last['Close'] < prev['Close'] else ""
st.markdown(f'<div style="color: #848e9c; font-size: 14px;">{asset_key} / USDT • {tf}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="price-large {p_color}">${last["Close"]:,.2f}</div>', unsafe_allow_html=True)

# Nút lệnh chuẩn Flexbox
st.markdown(f"""
<div class="btn-container">
    <div class="nav-btn {'active-buy' if signal == 'BUY' else ''}">BUY</div>
    <div class="nav-btn {'active-hold' if signal == 'HOLD' else ''}">HOLD</div>
    <div class="nav-btn {'active-sell' if signal == 'SELL' else ''}">SELL</div>
</div>
""", unsafe_allow_html=True)

# --- 5. BIỂU ĐỒ TÙY BIẾN ĐA TẦNG ---
rows_count = 1 + (1 if show_vol else 0) + (1 if (show_macd or show_rsi) else 0)
row_h = [0.6]
if show_vol: row_h.append(0.15)
if show_macd or show_rsi: row_h.append(0.25)

fig = make_subplots(rows=len(row_h), cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=row_h)
t_col = 'Date' if 'Date' in df.columns else 'Datetime'

# Tầng 1: Price
if chart_style == t[4]: # Candle
    fig.add_trace(go.Candlestick(x=df[t_col], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                 increasing_line_color='#02c076', decreasing_line_color='#cf304a'), row=1, col=1)
else: # Line
    fig.add_trace(go.Scatter(x=df[t_col], y=df['Close'], line=dict(color='#02c076', width=2)), row=1, col=1)

if show_ema:
    fig.add_trace(go.Scatter(x=df[t_col], y=df['EMA25'], line=dict(color='#f0b90b', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df[t_col], y=df['EMA99'], line=dict(color='#e841de', width=1)), row=1, col=1)

# Tầng 2: Volume
current_r = 2
if show_vol:
    v_colors = ['#02c076' if df['Open'].iloc[i] < df['Close'].iloc[i] else '#cf304a' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df[t_col], y=df['Volume'], marker_color=v_colors, opacity=0.4), row=current_r, col=1)
    current_r += 1

# Tầng 3: Indicators
if show_macd or show_rsi:
    if show_macd:
        fig.add_trace(go.Bar(x=df[t_col], y=df['MACD']-df['Sig'], marker_color='#474d57'), row=current_r, col=1)
        fig.add_trace(go.Scatter(x=df[t_col], y=df['MACD'], line=dict(color='#2962FF')), row=current_r, col=1)
    if show_rsi:
        fig.add_trace(go.Scatter(x=df[t_col], y=df['RSI'], line=dict(color='#ffffff', width=1)), row=current_r, col=1)

fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
fig.update_yaxes(side="right", gridcolor="#1e2329")
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
