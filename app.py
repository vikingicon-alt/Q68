import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf # Sử dụng thư viện chuẩn để đảm bảo ổn định 100%

# --- 1. CẤU HÌNH GIAO DIỆN HÀN LÂM ---
st.set_page_config(page_title="Q68 AI GLOBAL SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #050708; }
    .price-container { display: flex; align-items: baseline; margin-bottom: 5px; }
    .price-tag { font-size: 42px; font-weight: 900; margin-left: 20px; }
    .up { color: #00ff88; text-shadow: 0 0 15px #00ff8866; }
    .down { color: #ff4b4b; text-shadow: 0 0 15px #ff4b4b66; }
    .indicator-lamp { 
        width: 100%; border-radius: 15px; height: 120px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 900; font-size: 22px; color: white;
        background-color: #1a1c1e; border: 1px solid #333; opacity: 0.2;
    }
    .advice-text { font-size: 14px; font-weight: 400; margin-top: 10px; text-align: center; color: white; padding: 0 15px; }
    @keyframes neon-pulse {
        0% { box-shadow: 0 0 5px; opacity: 0.8; }
        50% { box-shadow: 0 0 40px; opacity: 1; }
        100% { box-shadow: 0 0 5px; opacity: 0.8; }
    }
    .lamp-buy { background-color: #00ff88 !important; color: black !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; }
    .lamp-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; }
    .lamp-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-pulse 2s infinite !important; opacity: 1 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR ĐIỀU KHIỂN ---
with st.sidebar:
    st.markdown("# 🐢 Q68 SYSTEM")
    asset_list = {
        "BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD",
        "SOLANA (SOL)": "SOL-USD", "GOLD (VÀNG)": "PAXG-USD"
    }
    asset_label = st.selectbox("TÀI SẢN CHIẾN LƯỢC:", list(asset_list.keys()))
    tf_choice = st.select_slider("KHUNG THỜI GIAN:", options=["5m", "15m", "30m", "1h", "4h", "1D"], value="1h")
    st.divider()
    vol_style = st.radio("MẪU VOLUME:", ["Mặc định", "Volume + MA20", "Dòng tiền Tối giản"])
    chart_style = st.radio("MẪU BIỂU ĐỒ:", ["Tiêu chuẩn quốc tế", "Phân tích RSI Chuyên sâu"])

# --- 3. BỘ NÃO XỬ LÝ DỮ LIỆU ---
def get_clean_data(symbol, tf):
    tf_map = {"5m":"5m", "15m":"15m", "30m":"30m", "1h":"1h", "4h":"1h", "1D":"1d"}
    try:
        data = yf.download(asset_list[symbol], period="5d", interval=tf_map[tf])
        if data.empty: return None
        df = data.copy()
        # Tính toán chỉ báo kỹ thuật
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['VolMA'] = df['Volume'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain/loss)))
        return df
    except: return None

df = get_clean_data(asset_label, tf_choice)

if df is not None:
    # HIỂN THỊ GIÁ USD TO RÕ (BỎ Q68 PHÍA SAU)
    last_p = float(df['Close'].iloc[-1])
    prev_p = float(df['Close'].iloc[-2])
    color_c = "up" if last_p >= prev_p else "down"
    
    st.markdown(f"""
        <div class="price-container">
            <h1 style="margin:0; color:#fff; font-size: 36px;">🐢 {asset_label.split(' ')[0]}</h1>
            <div class="price-tag {color_c}">${last_p:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 4. BIỂU ĐỒ VỚI CỘT GIÁ BÊN PHẢI ---
    show_rsi = chart_style == "Phân tích RSI Chuyên sâu"
    rows = 2 + (1 if show_rsi else 0)
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.2] + ([0.2] if show_rsi else []))

    # Nến và Trục giá PHẢI
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Giá"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='#FFD700', width=2), name="EMA20"), row=1, col=1)
    fig.update_yaxes(side="right", row=1, col=1, gridcolor="#333")

    # Volume
    colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    if vol_style != "Dòng tiền Tối giản":
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Vol"), row=2, col=1)
    else:
        fig.add_trace(go.Scatter(x=df.index, y=df['Volume'], fill='tozeroy', line=dict(color='#00ff88', width=1)), row=2, col=1)
    
    if vol_style == "Volume + MA20":
        fig.add_trace(go.Scatter(x=df.index, y=df['VolMA'], line=dict(color='white', width=1.5)), row=2, col=1)
    fig.update_yaxes(side="right", row=2, col=1, gridcolor="#333")

    # RSI
    if show_rsi:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#00d1ff', width=2)), row=rows, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=rows, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=rows, col=1)
        fig.update_yaxes(side="right", range=[0, 100], row=rows, col=1)

    fig.update_layout(height=650, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. BỘ NÃO AI ĐẦU TƯ (3 NÚT CÓ NÃO) ---
    st.markdown("### 🧠 CHIẾN THUẬT ĐẦU TƯ A1")
    
    last = df.iloc[-1]
    rsi_val = last['RSI']
    price_val = last['Close']
    ema_val = last['EMA20']
    vol_val = last['Volume']
    v_ma = last['VolMA']

    status = "HOLD"
    msg = "Thị trường đang nén giá. Đứng ngoài quan sát Volume xác nhận."

    if price_val > ema_val and rsi_val < 65 and vol_val > v_ma:
        status = "BUY"
        msg = "XU HƯỚNG TĂNG: Giá trên EMA + Volume bùng nổ. Ưu tiên vị thế MUA."
    elif price_val < ema_val and rsi_val > 35:
        status = "SELL"
        msg = "CẢNH BÁO RỦI RO: Giá gãy EMA20. Áp lực bán mạnh, nên thoát vị thế."
    elif rsi_val > 75:
        status = "SELL"
        msg = "QUÁ MUA: Chỉ số RSI quá cao. Nguy cơ đảo chiều giảm đột ngột."

    c1, c2, c3 = st.columns(3)
    with c1:
        active = "lamp-buy" if status == "BUY" else ""
        st.markdown(f'<div class="indicator-lamp {active}">🔥 LỆNH MUA<div class="advice-text">{msg if status=="BUY" else ""}</div></div>', unsafe_allow_html=True)
    with c2:
        active = "lamp-hold" if status == "HOLD" else ""
        st.markdown(f'<div class="indicator-lamp {active}">⏳ THEO DÕI<div class="advice-text">{msg if status=="HOLD" else ""}</div></div>', unsafe_allow_html=True)
    with c3:
        active = "lamp-sell" if status == "SELL" else ""
        st.markdown(f'<div class="indicator-lamp {active}">❄️ LỆNH BÁN<div class="advice-text">{msg if status=="SELL" else ""}</div></div>', unsafe_allow_html=True)

else:
    st.error("⚠️ Hệ thống đang kết nối lại dữ liệu Binance/Yahoo. Anh vui lòng đợi 5 giây...")

st.markdown('<div class="q68-footer">Q68 GLOBAL SYSTEM</div>', unsafe_allow_html=True)
