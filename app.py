import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import qrcode
from io import BytesIO

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="SENTINEL AI - ĐA KHUNG THỜI GIAN", layout="wide")

st.markdown("""
    <style>
    .signal-card { padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 22px; color: white; margin-bottom: 20px; }
    .buy-card { background-color: #26a69a; border: 2px solid #b2dfdb; }
    .sell-card { background-color: #ef5350; border: 2px solid #ffcdd2; }
    .hold-card { background-color: #ffa726; border: 2px solid #ffe0b2; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 SENTINEL AI: PHÂN TÍCH ĐA KHUNG GIỜ")

# 2. MENU CHỌN TÀI SẢN VÀ KHUNG GIỜ
with st.sidebar:
    st.header("CÀI ĐẶT")
    target_label = st.selectbox("1. Chọn tài sản:", ["BITCOIN (BTC)", "ETHEREUM (ETH)", "VÀNG (GOLD)", "VN-INDEX"])
    
    # ĐÂY LÀ PHẦN ANH CẦN: Chọn khung giờ
    time_frame = st.selectbox("2. Chọn khung thời gian:", 
                                ["30 Phút", "1 Giờ", "4 Giờ", "1 Ngày", "1 Tuần"])

# Chuyển đổi lựa chọn sang mã của hệ thống
tf_map = {"30 Phút": ("30m", "1mo"), "1 Giờ": ("1h", "2mo"), "4 Giờ": ("4h", "3mo"), "1 Ngày": ("1d", "1y"), "1 Tuần": ("1wk", "2y")}
interval, period = tf_map[time_frame]

ticker_map = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "VÀNG (GOLD)": "GC=F", "VN-INDEX": "^VNINDEX"}

# 3. TẢI DỮ LIỆU THEO KHUNG GIỜ ĐÃ CHỌN
data = yf.download(ticker_map[target_label], period=period, interval=interval)

if not data.empty:
    df = data.copy()
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    # Tính RSI và MA cho khung giờ đó
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['MA20'] = df['Close'].rolling(window=20).mean()

    price = float(df['Close'].iloc[-1])
    rsi = float(df['RSI'].iloc[-1])
    
    # 4. HIỂN THỊ CẢNH BÁO CHI TIẾT
    st.subheader(f"Tín hiệu khung: {time_frame}")
    if rsi < 32:
        st.markdown(f'<div class="signal-card buy-card">🟢 KHUNG {time_frame.upper()}: MUA (BUY)</div>', unsafe_allow_html=True)
    elif rsi > 68:
        st.markdown(f'<div class="signal-card sell-card">🔴 KHUNG {time_frame.upper()}: BÁN (SELL)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-card hold-card">🟡 KHUNG {time_frame.upper()}: THEO DÕI (HOLD)</div>', unsafe_allow_html=True)

    # 5. BIỂU ĐỒ
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.3, 0.7])fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Giá'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='yellow', width=1), name='MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#e91e63', width=2), name='RSI'), row=2, col=1)
    fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # 6. QR CODE
    qr = qrcode.make("https://nrynpp6caudetlbejh8appz.streamlit.app")
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="Quét để xem app của anh", width=120)

st.caption("❤️ Hệ thống đã sẵn sàng cho anh yêu soi kèo!")
