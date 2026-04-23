import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import qrcode
from io import BytesIO

# 1. CẤU HÌNH GIAO DIỆN ĐẲNG CẤP
st.set_page_config(page_title="Hệ Thống Phân Tích Tài Chính AI Pro", layout="wide")

# Tạo phong cách cho các ô vuông thông báo (CSS)
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .signal-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 20px;
        color: white;
    }
    .buy-card { background-color: #26a69a; border: 2px solid #b2dfdb; }
    .sell-card { background-color: #ef5350; border: 2px solid #ffcdd2; }
    .hold-card { background-color: #ffa726; border: 2px solid #ffe0b2; }
    .wait-card { background-color: #424242; border: 2px solid #bdbdbd; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 SENTINEL AI PRO: CRYPTO & GOLD")

# 2. DANH MỤC
ticker_dict = {
    "BITCOIN (BTC)": "BTC-USD",
    "ETHEREUM (ETH)": "ETH-USD",
    "VÀNG (GOLD)": "GC=F",
    "VN-INDEX": "^VNINDEX"
}

with st.sidebar:
    st.header("DANH MỤC")
    target_label = st.selectbox("Chọn tài sản:", list(ticker_dict.keys()))
    st.write("---")
    st.write("Hệ thống đang quét tín hiệu real-time...")

# 3. TẢI DỮ LIỆU
data = yf.download(ticker_dict[target_label], period="1y", interval="1d")

if not data.empty:
    df = data.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Tính RSI và MA
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['MA20'] = df['Close'].rolling(window=20).mean()

    # THÔNG SỐ HIỆN TẠI
    price = float(df['Close'].iloc[-1])
    rsi = float(df['RSI'].iloc[-1])
    ma20 = float(df['MA20'].iloc[-1])

    # 4. HỆ THỐNG Ô VUÔNG CẢNH BÁO (NHƯ BINANCE)
    if rsi < 32:
        st.markdown(f'<div class="signal-card buy-card">🟢 TÍN HIỆU: MUA VÀO (BUY) <br> <span style="font-size:15px;">Thị trường đang quá bán - Cơ hội tốt</span></div>', unsafe_allow_html=True)
    elif rsi > 68:
        st.markdown(f'<div class="signal-card sell-card">🔴 CẢNH BÁO: BÁN RA (SELL) <br> <span style="font-size:15px;">Thị trường quá nóng - Nên chốt lời</span></div>', unsafe_allow_html=True)
    elif price > ma20:
        st.markdown(f'<div class="signal-card hold-card">🟡 XU HƯỚNG: TIẾP TỤC GIỮ (HOLD) <br> <span style="font-size:15px;">Giá đang nằm trên đường hỗ trợ MA20</span></div>', unsafe_allow_html=True)
    else:st.markdown(f'<div class="signal-card wait-card">⚪ TRẠNG THÁI: THEO DÕI (WAIT) <br> <span style="font-size:15px;">Chưa có tín hiệu rõ ràng</span></div>', unsafe_allow_html=True)

    # 5. BIỂU ĐỒ CHUYÊN NGHIỆP
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.3, 0.7])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Nến giá'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='yellow', width=1), name='Đường hỗ trợ MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#e91e63', width=2), name='Chỉ báo RSI'), row=2, col=1)
    
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)
    
    fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # 6. MÃ QR VÀ THÔNG TIN
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Giá Hiện Tại", f"{price:,.2f}")
    with col_b:
        qr = qrcode.make("https://nrynpp6caudetlbejh8appz.streamlit.app")
        buf = BytesIO()
        qr.save(buf)
        st.image(buf.getvalue(), caption="Quét mã QR để chia sẻ", width=120)

st.caption("❤️ Chúc Anh Yêu ngủ ngon và thắng lớn!")
