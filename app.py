import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- TỐI ƯU HÓA CẤP ĐỘ 1: GIAO DIỆN APP CHUYÊN NGHIỆP ---
st.set_page_config(
    page_title="Q68 - A1 SYSTEM", 
    layout="wide", 
    page_icon="🐢",
    initial_sidebar_state="collapsed" # Tự động thu gọn menu để nhìn giống app hơn
)

# Mã độc quyền để xóa các thành phần thừa của trình duyệt
st.markdown("""
<style>
    /* Ẩn thanh công cụ Streamlit để giống App thật */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #080a0c; }
    
    /* Tối ưu nút bấm cho màn hình cảm ứng điện thoại/iPad */
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 4.5em; 
        font-weight: 800; font-size: 20px; border: none; 
        color: white; opacity: 0.2; transition: 0.5s; 
    }
    @keyframes neon-glow { 0% { box-shadow: 0 0 5px; transform: scale(1); } 50% { box-shadow: 0 0 25px; transform: scale(1.02); } 100% { box-shadow: 0 0 5px; transform: scale(1); } }
    .active-buy { background-color: #00ff88 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    .active-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-glow 1.5s infinite !important; opacity: 1 !important; }
    
    /* Chữ ký dự án A1 */
    .q68-footer { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #ffffff; font-weight: 900; font-size: 20px; opacity: 0.3; letter-spacing: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG ĐA NGÔN NGỮ ---
with st.sidebar:
    st.markdown("## 🐢 Q68 SYSTEM - A1")
    lang = st.radio("🌐 NGÔN NGỮ:", ["Tiếng Việt", "English"], horizontal=True)
    t = {
        "asset": "TÀI SẢN:" if lang == "Tiếng Việt" else "ASSET:",
        "tf": "KHUNG GIỜ (TF):" if lang == "Tiếng Việt" else "TIMEFRAME:",
        "title": "DỰ BÁO XU HƯỚNG" if lang == "Tiếng Việt" else "TREND PREDICTION",
        "signal": "🐢 TÍN HIỆU CHIẾN THUẬT A1" if lang == "Tiếng Việt" else "🐢 A1 STRATEGIC SIGNALS",
        "buy_btn": "🔥 BUY" if lang == "Tiếng Việt" else "🔥 BUY",
        "sell_btn": "❄️ SELL" if lang == "Tiếng Việt" else "❄️ SELL",
        "hold_btn": "⏳ WAIT" if lang == "Tiếng Việt" else "⏳ WAIT"
    }
    asset_choice = st.selectbox(t["asset"], ["BITCOIN (BTC)", "ETHEREUM (ETH)", "PAXG (VÀNG)"])
    tf_choice = st.select_slider(t["tf"], options=["5m", "15m", "30m", "1h", "4h", "1D"], value="1h")

# --- 3. ĐỘNG CƠ DỮ LIỆU ---
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
                'Low': res['indicators']['quote'][0]['low']
            }).dropna()
            df['MA7'] = df['Close'].rolling(7).mean()
            df['MA25'] = df['Close'].rolling(25).mean()
            df['MA99'] = df['Close'].rolling(99).mean()
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain/loss)))
            return df
    except: return None

# --- 4. HIỂN THỊ CHÍNH ---
df = fetch_global_data(asset_choice, tf_choice)
if df is not None:
    current_price = df['Close'].iloc[-1]
    st.markdown(f"<h1 style='text-align: center; color: white;'>🐢 {asset_choice.split(' ')[0]} | ${current_price:,.2f}</h1>", unsafe_allow_html=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Nến"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA7'], line=dict(color='#FFD700', width=1.5), name="MA7"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA25'], line=dict(color='#FF69B4', width=1.5), name="MA25"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA99'], line=dict(color='#9370DB', width=1.5), name="MA99"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], line=dict(color='#00d1ff', width=2), fill='tozeroy', name="RSI"), row=2, col=1)
    fig.update_layout(height=500, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. TÍN HIỆU CHIẾN THUẬT A1 ---
    rsi_now = df['RSI'].iloc[-1]; price_now = df['Close'].iloc[-1]; ma25_now = df['MA25'].iloc[-1]
    b_class = "active-buy" if (price_now > ma25_now and rsi_now < 70) else ""
    s_class = "active-sell" if (price_now < ma25_now or rsi_now > 70) else ""
    h_class = "active-hold" if not b_class and not s_class else ""
    st.markdown(f"<h3 style='text-align: center; color: #888;'>{t['signal']}</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<button class="stButton {b_class}">{t["buy_btn"]}</button>', unsafe_allow_html=True)
    with c2: st.markdown(f'<button class="stButton {h_class}">{t["hold_btn"]}</button>', unsafe_allow_html=True)
    with c3: st.markdown(f'<button class="stButton {s_class}">{t["sell_btn"]}</button>', unsafe_allow_html=True)

st.markdown('<div class="q68-footer">Q68 - A1 SYSTEM</div>', unsafe_allow_html=True)
