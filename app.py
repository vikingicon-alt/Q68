import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- 1. CẤU HÌNH GIAO DIỆN & HIỆU ỨNG NEON ---
st.set_page_config(page_title="SENTINEL PRO - A1", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8em; font-weight: bold; font-size: 18px; border: none; color: white; opacity: 0.15; transition: 0.5s; }
    
    /* Hiệu ứng nhịp thở cho đèn dự báo */
    @keyframes breathing {
        0% { box-shadow: 0 0 5px; transform: scale(1); }
        50% { box-shadow: 0 0 25px; transform: scale(1.02); }
        100% { box-shadow: 0 0 5px; transform: scale(1); }
    }
    
    .active-buy { opacity: 1 !important; background-color: #00ff88 !important; color: black !important; animation: breathing 1.5s infinite; }
    .active-sell { opacity: 1 !important; background-color: #ff4b4b !important; color: white !important; animation: breathing 1.5s infinite; }
    .active-hold { opacity: 1 !important; background-color: #ffaa00 !important; color: black !important; animation: breathing 1.5s infinite; }
    
    .q68-footer { position: fixed; bottom: 15px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 24px; opacity: 0.8; }
    </style>
""", unsafe_allow_html=True)

# --- 2. THANH ĐIỀU KHIỂN BÊN TRÁI ---
with st.sidebar:
    st.header("🐢 CONTROL PANEL")
    asset_choice = st.selectbox("CHỌN TÀI SẢN:", ["BITCOIN (BTC)", "ETHEREUM (ETH)", "PAXG (VÀNG)"])
    
    # Soạn khung thời gian dạng trượt cho iPad
    tf_display = st.select_slider(
        "KHUNG THỜI GIAN:",
        options=["15m", "30m", "1h", "4h", "1D"],
        value="30m"
    )
    
    st.divider()
    st.write("📲 **QUÉT MÃ APP:**")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://A1-PROJECT-APP", width=150)

# --- 3. LẤY DỮ LIỆU THỰC ---
@st.cache_data(ttl=20)
def get_data(symbol, tf):
    mapping = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "VÀNG (PAXG)": "PAXG-USD"}
    tf_map = {"15m": "15m", "30m": "30m", "1h": "1h", "4h": "1h", "1D": "1d"}
    ticker = mapping.get(symbol, "BTC-USD")
    interval = tf_map.get(tf, "30m")
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={interval}&range=5d"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read())['chart']['result'][0]
            df = pd.DataFrame({
                'Date': pd.to_datetime(res['timestamp'], unit='s'),
                'Open': res['indicators']['quote'][0]['open'],
                'High': res['indicators']['quote'][0]['high'],
                'Low': res['indicators']['quote'][0]['low'],
            'Close': res['indicators']['quote'][0]['close'],
                'Volume': res['indicators']['quote'][0]['volume']
            }).dropna()
            # Tính RSI dự báo
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain/loss)))
            return df
    except: return None

st.title(f"🐢 {asset_choice.split(' ')[0]} - TREND PREDICTION")

df = get_data(asset_choice, tf_display)

if df is not None:
    current_p = df['Close'].iloc[-1]
    st.metric(f"GIÁ USD ({tf_display})", f"${current_p:,.2f}")

    # --- 4. BIỂU ĐỒ NẾN & VOLUME & RSI ---
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
    
    vol_colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=vol_colors), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], fill='tozeroy', line=dict(color='#00d1ff'), fillcolor='rgba(0, 209, 255, 0.1)'), row=3, col=1)
    
    fig.update_layout(height=600, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=10, b=10))
    fig.update_yaxes(tickprefix="$", tickformat=",", row=1, col=1)
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. HỆ THỐNG DỰ BÁO THÔNG MINH ---
    st.markdown("### 🎯 CHIẾN THUẬT DỰ BÁO")
    rsi_val = df['RSI'].iloc[-1]
    
    # Xác định đèn Neon nào sáng
    buy_class = "active-buy" if rsi_val < 35 else ""
    sell_class = "active-sell" if rsi_val > 65 else ""
    hold_class = "active-hold" if (35 <= rsi_val <= 65) else ""

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<button class="stButton {buy_class}">🔥 BUY NOW</button>', unsafe_allow_html=True)
    with c2: st.markdown(f'<button class="stButton {hold_class}">⏳ HOLD</button>', unsafe_allow_html=True)
    with c3: st.markdown(f'<button class="stButton {sell_class}">❄️ SELL NOW</button>', unsafe_allow_html=True)

# --- 6. CHÂN TRANG Q68 ---
st.markdown('<div class="q68-footer">Q68</div>', unsafe_allow_html=True)
