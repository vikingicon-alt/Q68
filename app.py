import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- 1. CẤU HÌNH GIAO DIỆN Q68 ĐẲNG CẤP ---
st.set_page_config(page_title="Q68 GLOBAL SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #050708; }
    .indicator-lamp { 
        width: 100%; border-radius: 15px; height: 90px; 
        display: flex; align-items: center; justify-content: center;
        font-weight: 900; font-size: 24px; color: white;
        background-color: #1a1c1e; border: 1px solid #333;
        opacity: 0.1; transition: 0.5s;
    }
    @keyframes neon-pulse {
        0% { box-shadow: 0 0 10px; opacity: 0.7; transform: scale(1); }
        50% { box-shadow: 0 0 40px; opacity: 1; transform: scale(1.03); }
        100% { box-shadow: 0 0 10px; opacity: 0.7; transform: scale(1); }
    }
    .lamp-buy { background-color: #00ff88 !important; color: black !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; border: none; }
    .lamp-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; border: none; }
    .lamp-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-pulse 2s infinite !important; opacity: 1 !important; border: none; }
    .q68-footer { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 28px; opacity: 0.3; letter-spacing: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR TÀI SẢN CHIẾN LƯỢC ---
with st.sidebar:
    st.markdown("# 🐢 Q68") 
    lang = st.radio("🌐 NGÔN NGỮ:", ["Tiếng Việt", "English"], horizontal=True)
    
    t = {
        "asset": "TÀI SẢN CHIẾN LƯỢC:" if lang == "Tiếng Việt" else "STRATEGIC ASSET:",
        "tf": "KHUNG THỜI GIAN (TF):" if lang == "Tiếng Việt" else "TIMEFRAME (TF):",
        "signal": "🐢 HỆ THỐNG CẢNH BÁO A1" if lang == "Tiếng Việt" else "🐢 A1 ALERT SYSTEM",
        "buy": "🔥 LỆNH MUA", "sell": "❄️ LỆNH BÁN", "hold": "⏳ THEO DÕI"
    }

    asset_list = {
        "BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD",
        "LITECOIN (LTC)": "LTC-USD", "RIPPLE (XRP)": "XRP-USD",
        "TETHER (USDT)": "USDT-USD", "PAXG (VÀNG)": "PAXG-USD"
    }
    
    asset_label = st.selectbox(t["asset"], list(asset_list.keys()))
    tf_choice = st.select_slider(t["tf"], options=["5m", "15m", "30m", "1h", "4h", "1D", "1W", "1M"], value="1h")

# --- 3. DỮ LIỆU & CHỈ BÁO CHI TIẾT ---
@st.cache_data(ttl=10)
def get_data(symbol_key, tf):
    ticker = asset_list[symbol_key]
    tf_map = {"5m":"5m", "15m":"15m", "30m":"30m", "1h":"1h", "4h":"1h", "1D":"1d", "1W":"1wk", "1M":"1mo"}
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={tf_map[tf]}&range=5d"
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
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain/loss)))
            return df
    except: return None

# --- 4. BIỂU ĐỒ 3 TẦNG: NẾN/EMA - VOLUME - RSI ---
df = get_data(asset_label, tf_choice)

if df is not None:
    st.title(f"🐢 {asset_label.split(' ')[0]} - Q68")
    
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, 
                        row_heights=[0.5, 0.2, 0.3],
                        subplot_titles=("", "", ""))

    # Tầng 1: Nến + EMA Vàng Phóng Đại
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA20'], line=dict(color='#FFD700', width=3), name="EMA 20"), row=1, col=1)

    # Tầng 2: Cột Volume (Xanh/Đỏ rõ rệt)
    v_colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=v_colors, name="Volume"), row=2, col=1)

    # Tầng 3: RSI Phóng Đại với vạch 30/70
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], line=dict(color='#00d1ff', width=2), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    fig.update_layout(height=750, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. LOGIC CẢNH BÁO TỰ ĐỘNG ---
    st.markdown(f"### {t['signal']}")
    rsi = df['RSI'].iloc[-1]; price = df['Close'].iloc[-1]; ema = df['EMA20'].iloc[-1]
    
    # Logic nhận diện nhanh tại thời điểm
    buy_active = "lamp-buy" if (rsi < 35 and price > ema) else ""
    sell_active = "lamp-sell" if (rsi > 65 or price < ema) else ""
    hold_active = "lamp-hold" if (not buy_active and not sell_active) else ""

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="indicator-lamp {buy_active}">{t["buy"]}</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="indicator-lamp {hold_active}">{t["hold"]}</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="indicator-lamp {sell_active}">{t["sell"]}</div>', unsafe_allow_html=True)
else:
    st.error("Dữ liệu đang được làm mới...")

st.markdown('<div class="q68-footer">Q68</div>', unsafe_allow_html=True)
