import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- 1. CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP ---
st.set_page_config(page_title="Q68 AI GLOBAL SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #050708; }
    .price-container { display: flex; align-items: baseline; margin-bottom: 5px; }
    .price-tag { font-size: 38px; font-weight: 900; margin-left: 15px; }
    .up { color: #00ff88; text-shadow: 0 0 10px #00ff8844; }
    .down { color: #ff4b4b; text-shadow: 0 0 10px #ff4b4b44; }
    .indicator-lamp { 
        width: 100%; border-radius: 12px; height: 110px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 900; font-size: 20px; color: white;
        background-color: #1a1c1e; border: 1px solid #333; opacity: 0.15;
        transition: 0.5s;
    }
    .advice-text { font-size: 13px; font-weight: 400; margin-top: 8px; text-align: center; color: inherit; padding: 0 10px; }
    @keyframes neon-pulse {
        0% { box-shadow: 0 0 5px; opacity: 0.8; transform: scale(1); }
        50% { box-shadow: 0 0 35px; opacity: 1; transform: scale(1.02); }
        100% { box-shadow: 0 0 5px; opacity: 0.8; transform: scale(1); }
    }
    .lamp-buy { background-color: #00ff88 !important; color: black !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; }
    .lamp-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; }
    .lamp-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-pulse 2s infinite !important; opacity: 1 !important; }
    .q68-footer { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 25px; opacity: 0.1; letter-spacing: 15px; pointer-events: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR - ĐIỀU KHIỂN HỆ THỐNG ---
asset_list = {
    "BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD",
    "SOLANA (SOL)": "SOL-USD", "BINANCE COIN (BNB)": "BNB-USD",
    "PAXG (GOLD)": "PAXG-USD"
}

with st.sidebar:
    st.markdown("# 🐢 Q68 SYSTEM")
    asset_label = st.selectbox("TÀI SẢN CHIẾN LƯỢC:", list(asset_list.keys()))
    tf_choice = st.select_slider("KHUNG THỜI GIAN:", options=["5m", "15m", "30m", "1h", "4h", "1D"], value="1h")
    st.divider()
    vol_style = st.radio("MẪU VOLUME:", ["Mặc định", "Volume + MA20", "Tối giản"])
    st.divider()
    chart_style = st.radio("MẪU BIỂU ĐỒ:", ["Tiêu chuẩn quốc tế", "Phân tích RSI"])

# --- 3. DỮ LIỆU & THUẬT TOÁN AI ---
@st.cache_data(ttl=10)
def fetch_and_analyze(symbol_key, tf):
    ticker = asset_list[symbol_key]
    tf_map = {"5m":"5m", "15m":"15m", "30m":"30m", "1h":"1h", "4h":"1h", "1D":"1d"}
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={tf_map[tf]}&range=5d"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read())['chart']['result'][0]
            df = pd.DataFrame({
                'Date': pd.to_datetime(res['timestamp'], unit='s'),
                'Open': res['indicators']['quote'][0]['open'], 'High': res['indicators']['quote'][0]['high'],
                'Low': res['indicators']['quote'][0]['low'], 'Close': res['indicators']['quote'][0]['close'],
                'Volume': res['indicators']['quote'][0]['volume']
            }).dropna()
            # Chỉ báo kỹ thuật cho Bộ não AI
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['VolMA'] = df['Volume'].rolling(window=20).mean()
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain/loss)))
            return df
    except: return None

df = fetch_and_analyze(asset_label, tf_choice)

if df is not None:
    # HIỂN THỊ GIÁ USD TRỰC TIẾP (BỎ CHỮ Q68 PHÍA SAU)
    last_p = df['Close'].iloc[-1]
    prev_p = df['Close'].iloc[-2]
    color_c = "up" if last_p >= prev_p else "down"
    
    st.markdown(f"""
        <div class="price-container">
            <h1 style="margin:0; color:#fff; font-size: 32px;">🐢 {asset_label.split(' ')[0]}</h1>
            <div class="price-tag {color_c}">${last_p:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 4. BIỂU ĐỒ VỚI CỘT GIÁ BÊN PHẢI ---
    show_rsi = chart_style == "Phân tích RSI"
    rows = 2 + (1 if show_rsi else 0)
    row_h = [0.6, 0.2] + ([0.2] if show_rsi else [])
    
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=row_h)

    # Nến & EMA
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Giá"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA20'], line=dict(color='#FFD700', width=2), name="EMA20"), row=1, col=1)
    fig.update_yaxes(side="right", row=1, col=1, gridcolor="#333")

    # Volume
    v_colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    if vol_style != "Tối giản":
        fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=v_colors, name="Vol"), row=2, col=1)
    else:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Volume'], fill='tozeroy', line=dict(color='#00ff88', width=1)), row=2, col=1)
    
    if vol_style == "Volume + MA20":
        fig.add_trace(go.Scatter(x=df['Date'], y=df['VolMA'], line=dict(color='white', width=1)), row=2, col=1)
