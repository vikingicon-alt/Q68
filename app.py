import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- 1. PREMIUM INTERFACE ---
st.set_page_config(page_title="Q68 GLOBAL SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #080a0c; }
    .stButton>button { width: 100%; border-radius: 12px; height: 4em; font-weight: 800; font-size: 18px; border: none; color: white; opacity: 0.15; transition: 0.5s; }
    @keyframes neon-glow { 0% { box-shadow: 0 0 5px; transform: scale(1); } 50% { box-shadow: 0 0 25px; transform: scale(1.02); } 100% { box-shadow: 0 0 5px; transform: scale(1); } }
    .active-buy { background-color: #00ff88 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .q68-footer { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 26px; opacity: 0.4; letter-spacing: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MULTI-LANGUAGE ---
with st.sidebar:
    st.markdown("# 🐢 Q68") 
    lang = st.radio("🌐 LANGUAGE / NGÔN NGỮ:", ["Tiếng Việt", "English"], horizontal=True)
    
    t = {
        "asset": "TÀI SẢN CHIẾN LƯỢC:" if lang == "Tiếng Việt" else "STRATEGIC ASSET:",
        "tf": "KHUNG THỜI GIAN (TF):" if lang == "Tiếng Việt" else "TIMEFRAME (TF):",
        "scan": "HỆ THỐNG QUẢN TRỊ A1:" if lang == "Tiếng Việt" else "A1 OPERATING SYSTEM:",
        "title": "DỰ BÁO XU HƯỚNG" if lang == "Tiếng Việt" else "TREND PREDICTION",
        "price": "GIÁ THỜI GIAN THỰC" if lang == "Tiếng Việt" else "REAL-TIME PRICE",
        "signal": "🐢 TÍN HIỆU CHIẾN THUẬT A1" if lang == "Tiếng Việt" else "🐢 A1 STRATEGIC SIGNALS",
        "buy_btn": "🔥 MUA NGAY" if lang == "Tiếng Việt" else "🔥 BUY NOW",
        "sell_btn": "❄️ BÁN NGAY" if lang == "Tiếng Việt" else "❄️ SELL NOW",
        "hold_btn": "⏳ CHỜ ĐỢI" if lang == "Tiếng Việt" else "⏳ WAIT / HOLD",
        "wait": "🔄 ĐANG KẾT NỐI DỮ LIỆU..." if lang == "Tiếng Việt" else "🔄 CONNECTING DATA..."
    }

    asset_choice = st.selectbox(t["asset"], ["BITCOIN (BTC)", "ETHEREUM (ETH)", "PAXG (VÀNG)"])
    tf_choice = st.select_slider(t["tf"], options=["5m", "15m", "30m", "1h", "4h", "1D"], value="1h")
    
    st.divider()
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://A1-PROJECT", width=120)

# --- 3. DATA ENGINE (EMA, RSI, VOLUME) ---
@st.cache_data(ttl=15)
def fetch_global_data(symbol, tf):
    mapping = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "PAXG (VÀNG)": "PAXG-USD"}
    ticker = mapping.get(symbol, "BTC-USD")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={tf}&range=5d"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read())['chart']['result'][0]
            df = pd.DataFrame({
                'Date': pd.to_datetime(res['timestamp'], unit='s'),
                'Close': res['indicators']['quote'][0]['close'],
                'Open': res['indicators']['quote'][0]['open'],
                'High': res['indicators']['quote'][0]['high'],
                'Low': res['indicators']['quote'][0]['low'],
                'Volume': res['indicators']['quote'][0]['volume']
            }).dropna()
            
            # --- CÁC CHỈ BÁO CHIẾN THUẬT A1 ---
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain/loss)))
            return df
    except: return None

# --- 4. MAIN DASHBOARD ---
st.title(f"🐢 {asset_choice.split(' ')[0]} - {t['title']}")
df = fetch_global_data(asset_choice, tf_choice)

if df is not None:
    # Biểu đồ 3 tầng đẳng cấp: Nến/EMA - Volume - RSI
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.15, 0.25])
    
    # Tầng 1: Price + EMA 20 (Đường màu vàng)
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA20'], line=dict(color='#FFD700', width=1.5), name="EMA 20"), row=1, col=1)
    
    # Tầng 2: Volume
    v_colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=v_colors, name="Volume"), row=2, col=1)
    
    # Tầng 3: RSI
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], line=dict(color='#00d1ff', width=2), fill='tozeroy', name="RSI"), row=3, col=1)
    
    fig.update_layout(height=650, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. TÍN HIỆU CHIẾN THUẬT A1 ---
    st.markdown(f"### {t['signal']}")
    rsi_now = df['RSI'].iloc[-1]
    price_now = df['Close'].iloc[-1]
    ema_now = df['EMA20'].iloc[-1]
    
    # Dựa trên lõi vĩ mô (DXY/Dow Jones) mà anh em mình tính ngầm:
    # Nếu giá trên EMA và RSI đang vùng thuận lợi -> MUA
    b_class = "active-buy" if (price_now > ema_now and rsi_now < 70) else ""
s_class = "active-sell" if (price_now < ema_now or rsi_now > 70) else ""
    h_class = "active-hold" if not b_class and not s_class else ""

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<button class="stButton {b_class}">{t["buy_btn"]}</button>', unsafe_allow_html=True)
    with c2: st.markdown(f'<button class="stButton {h_class}">{t["hold_btn"]}</button>', unsafe_allow_html=True)
    with c3: st.markdown(f'<button class="stButton {s_class}">{t["sell_btn"]}</button>', unsafe_allow_html=True)
else:
    st.warning(t["wait"])

st.markdown('<div class="q68-footer">Q68 - A1 SYSTEM</div>', unsafe_allow_html=True)    
