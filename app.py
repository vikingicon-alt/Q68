import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- 1. CẤU HÌNH HỆ THỐNG CAO CẤP (ẨN THANH TÌM KIẾM & TRÀN VIỀN) ---
st.set_page_config(page_title="Q68 - A1 SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
<style>
    .main { background-color: #080a0c; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 4em; 
        font-weight: 800; font-size: 18px; border: none; 
        color: white; opacity: 0.15; transition: 0.5s; 
    }
    @keyframes neon-glow { 0% { box-shadow: 0 0 5px; transform: scale(1); } 50% { box-shadow: 0 0 25px; transform: scale(1.02); } 100% { box-shadow: 0 0 5px; transform: scale(1); } }
    .active-buy { background-color: #00ff88 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .q68-footer { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 20px; opacity: 0.3; letter-spacing: 5px; }
</style>
<head>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
</head>
""", unsafe_allow_html=True)

# --- 2. MENU ĐIỀU KHIỂN CHIẾN THUẬT ---
with st.sidebar:
    st.markdown("# 🐢 Q68 SYSTEM") 
    lang = st.radio("🌐 NGÔN NGỮ / LANGUAGE:", ["Tiếng Việt", "English"], horizontal=True)
    t = {
        "asset": "TÀI SẢN CHIẾN LƯỢC:" if lang == "Tiếng Việt" else "STRATEGIC ASSET:",
        "tf": "KHUNG GIỜ (TF):" if lang == "Tiếng Việt" else "TIMEFRAME (TF):",
        "scan": "QUÉT MÃ A1 SYSTEM:" if lang == "Tiếng Việt" else "SCAN A1 SYSTEM:",
        "signal": "🐢 TÍN HIỆU CHIẾN THUẬT A1" if lang == "Tiếng Việt" else "🐢 A1 STRATEGIC SIGNALS",
        "buy_btn": "🔥 BUY" if lang == "English" else "🔥 MUA",
        "sell_btn": "❄️ SELL" if lang == "English" else "❄️ BÁN",
        "hold_btn": "⏳ WAIT" if lang == "English" else "⏳ CHỜ",
    }
    asset_choice = st.selectbox(t["asset"], ["BITCOIN (BTC)", "ETHEREUM (ETH)", "PAXG (VÀNG)"])
    tf_choice = st.select_slider(t["tf"], options=["5m", "15m", "30m", "1h", "4h", "1D"], value="1h")
    st.divider()
    st.write(f"📲 **{t['scan']}**")
    qr_link = "https://nrynpp6caudetlbejh8appz.streamlit.app"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}", width=150)
    # --- 3. ĐỘNG CƠ DỮ LIỆU TÀI CHÍNH ---
@st.cache_data(ttl=15)
def fetch_global_data(symbol, tf):
    mapping = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "PAXG (VÀNG)": "PAXG-USD"}
    ticker = mapping.get(symbol, "BTC-USD")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={tf}&range=5d"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())['chart']['result'][0]
            df = pd.DataFrame({
                'Date': pd.to_datetime(data['timestamp'], unit='s'),
                'Close': data['indicators']['quote'][0]['close'],
                'Open': data['indicators']['quote'][0]['open'],
                'High': data['indicators']['quote'][0]['high'],
                'Low': data['indicators']['quote'][0]['low'],
                'Volume': data['indicators']['quote'][0]['volume']
            }).dropna()
            # Tính toán các chỉ báo kỹ thuật
            df['MA7'] = df['Close'].rolling(7).mean()
            df['MA25'] = df['Close'].rolling(25).mean()
            df['MA99'] = df['Close'].rolling(99).mean()
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain/loss)))
            return df
    except: return None

# --- 4. BIỂU ĐỒ TẦM CỠ THẾ GIỚI (CÓ VOLUME) ---
df = fetch_global_data(asset_choice, tf_choice)
if df is not None:
    current_price = df['Close'].iloc[-1]
    st.markdown(f"<h1 style='text-align: center; color: white;'>🐢 {asset_choice.split(' ')[0]} | ${current_price:,.2f} USD</h1>", unsafe_allow_html=True)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.15, 0.25])
    
    # Tầng 1: Price & MAs
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA7'], line=dict(color='#FFD700', width=1.5), name="MA7"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA25'], line=dict(color='#FF69B4', width=1.5), name="MA25"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA99'], line=dict(color='#9370DB', width=1.5), name="MA99"), row=1, col=1)
    
    # Tầng 2: VOLUME CHI TIẾT
    v_colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=v_colors, name="Volume"), row=2, col=1)
    
    # Tầng 3: RSI CHUYÊN SÂU
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], line=dict(color='#00d1ff', width=2), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.3, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.3, row=3, col=1)

    fig.update_layout(height=650, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. TÍN HIỆU CHIẾN THUẬT A1 (HIỆU ỨNG NEON) ---
    rsi_now = df['RSI'].iloc[-1]; price_now = df['Close'].iloc[-1]; ma25_now = df['MA25'].iloc[-1]
    b_class = "active-buy" if (price_now > ma25_now and rsi_now < 70) else ""
    s_class = "active-sell" if (price_now < ma25_now or rsi_now > 70) else ""
    h_class = "active-hold" if not b_class and not s_class else ""

    st.markdown(f"<h3 style='text-align: center; color: #888;'>{t['signal']}</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<button class="stButton {b_class}">{t["buy_btn"]}</button>', unsafe_allow_html=True)
    with c2: st.markdown(f'<button class="stButton {h_class}">{t["hold_btn"]}</button>', unsafe_allow_html=True)
    with c3: st.markdown(f'<button class="stButton {s_class}">{t["sell_btn"]}</button>', unsafe_allow_html=True)
else:
    st.error("🔄 LỖI KẾT NỐI DỮ LIỆU / CONNECTION ERROR")

st.markdown('<div class="q68-footer">Q68 - A1 SYSTEM</div>', unsafe_allow_html=True)
