import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- 1. CẤU HÌNH GIAO DIỆN & STYLE NEON ---
st.set_page_config(page_title="SENTINEL AI GLOBAL", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #080a0c; }
    .stButton>button { width: 100%; border-radius: 12px; height: 4em; font-weight: 800; font-size: 18px; border: none; color: white; opacity: 0.15; transition: 0.5s; }
    
    @keyframes neon-glow {
        0% { box-shadow: 0 0 5px; transform: scale(1); }
        50% { box-shadow: 0 0 25px; transform: scale(1.02); }
        100% { box-shadow: 0 0 5px; transform: scale(1); }
    }
    
    .active-buy { background-color: #00ff88 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    
    .q68-footer { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 26px; opacity: 0.4; letter-spacing: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG ĐA NGÔN NGỮ ---
with st.sidebar:
    st.markdown("# 🐢 SENTINEL AI")
    
    # Thêm lựa chọn ngôn ngữ ngay đầu tiên
    lang = st.radio("🌐 LANGUAGE / NGÔN NGỮ:", ["Tiếng Việt", "English"], horizontal=True)
    
    # Bộ từ điển ngôn ngữ
    t = {
        "asset": "TÀI SẢN CHIẾN LƯỢC:" if lang == "Tiếng Việt" else "STRATEGIC ASSET:",
        "tf": "KHUNG THỜI GIAN (TF):" if lang == "Tiếng Việt" else "TIMEFRAME (TF):",
        "scan": "HỆ THỐNG QUẢN TRỊ A1:" if lang == "Tiếng Việt" else "A1 OPERATING SYSTEM:",
        "title": "DỰ BÁO XU HƯỚNG" if lang == "Tiếng Việt" else "TREND PREDICTION",
        "price": "GIÁ USD THỜI GIAN THỰC" if lang == "Tiếng Việt" else "REAL-TIME USD PRICE",
        "signal": "🎯 TÍN HIỆU CHIẾN THUẬT A1" if lang == "Tiếng Việt" else "🎯 A1 STRATEGIC SIGNALS",
        "buy": "🔥 MUA NGAY", "sell": "❄️ BÁN NGAY", "hold": "⏳ CHỜ ĐỢI",
        "wait": "🔄 ĐANG ĐỒNG BỘ DỮ LIỆU VỆ TINH..." if lang == "Tiếng Việt" else "🔄 SYNCING SATELLITE DATA..."
    } if lang == "Tiếng Việt" else {
        "asset": "STRATEGIC ASSET:", "tf": "TIMEFRAME (TF):", "scan": "A1 OPERATING SYSTEM:",
        "title": "TREND PREDICTION", "price": "REAL-TIME USD PRICE", "signal": "🎯 A1 STRATEGIC SIGNALS",
        "buy": "🔥 BUY NOW", "sell": "❄️ SELL NOW", "hold": "⏳ HOLD",
        "wait": "🔄 SYNCING SATELLITE DATA..."
    }
    asset_choice = st.selectbox(t["asset"], ["BITCOIN (BTC)", "ETHEREUM (ETH)", "PAXG (VÀNG)"])
    tf_choice = st.select_slider(t["tf"], options=["5m", "15m", "30m", "1h", "4h", "1D", "1W", "1M"], value="1h")
    
    st.divider()
    st.write(f"📲 **{t['scan']}**")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://A1-PROJECT", width=150)

# --- 3. LOGIC DỮ LIỆU QUỐC TẾ ---
@st.cache_data(ttl=15)
def fetch_global_data(symbol, tf):
    mapping = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "PAXG (VÀNG)": "PAXG-USD"}
    tf_map = {"5m":"5m", "15m":"15m", "30m":"30m", "1h":"1h", "4h":"1h", "1D":"1d", "1W":"1wk", "1M":"1mo"}
    range_map = {"5m":"1d", "15m":"2d", "30m":"5d", "1h":"7d", "4h":"14d", "1D":"60d", "1W":"1y", "1M":"5y"}
    
    ticker = mapping.get(symbol, "BTC-USD")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={tf_map[tf]}&range={range_map[tf]}"
    
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
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain/loss)))
            return df
    except: return None

# --- 4. HIỂN THỊ ---
st.title(f"🐢 {asset_choice.split(' ')[0]} - {t['title']}")

df = fetch_global_data(asset_choice, tf_choice)

if df is not None:
    current_p = df['Close'].iloc[-1]
    st.metric(f"{t['price']} ({tf_choice})", f"${current_p:,.2f}")

    # BIỂU ĐỒ NẾN CHUẨN QUỐC TẾ
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.15, 0.25])
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    v_colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], marker_color=v_colors, name="Volume"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], fill='tozeroy', line=dict(color='#00d1ff', width=2), fillcolor='rgba(0, 209, 255, 0.1)', name="RSI"), row=3, col=1)
    fig.update_layout(height=650, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=5, b=5))
    fig.update_yaxes(tickprefix="$", tickformat=",", row=1, col=1)
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. TÍN HIỆU NEON ĐA NGÔN NGỮ ---
    st.markdown(f"### {t['signal']}")
    rsi_now = df['RSI'].iloc[-1]
    
    b_class = "active-buy" if rsi_now < 30 else ""
    s_class = "active-sell" if rsi_now > 70 else ""
    h_class = "active-hold" if (30 <= rsi_now <= 70) else ""

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<button class="stButton {b_class}">{t["buy"]}</button>', unsafe_allow_html=True)
    with c2: st.markdown(f'<button class="stButton {h_class}">{t["hold"]}</button>', unsafe_allow_html=True)
    with c3: st.markdown(f'<button class="stButton {s_class}">{t["sell"]}</button>', unsafe_allow_html=True)
else:
    st.warning(t["wait"])

st.markdown('<div class="q68-footer">Q68</div>', unsafe_allow_html=True)
