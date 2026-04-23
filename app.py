import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import qrcode
from io import BytesIO

# 1. CẤU HÌNH
st.set_page_config(page_title="SENTINEL AI", layout="wide")

st.markdown("""
    <style>
    .signal-card { padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 22px; color: white; margin-bottom: 20px; }
    .buy-card { background-color: #26a69a; }
    .sell-card { background-color: #ef5350; }
    .hold-card { background-color: #ffa726; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 SENTINEL AI: ĐA KHUNG GIỜ")

# 2. MENU
with st.sidebar:
    target_label = st.selectbox("Chọn tài sản:", ["BITCOIN (BTC)", "ETHEREUM (ETH)", "VÀNG (GOLD)", "VN-INDEX"])
    time_frame = st.selectbox("Chọn khung thời gian:", ["30 Phút", "1 Giờ", "4 Giờ", "1 Ngày", "1 Tuần"])

tf_map = {"30 Phút": ("30m", "1mo"), "1 Giờ": ("1h", "2mo"), "4 Giờ": ("4h", "3mo"), "1 Ngày": ("1d", "1y"), "1 Tuần": ("1wk", "2y")}
interval, period = tf_map[time_frame]
t_map = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "VÀNG (GOLD)": "GC=F", "VN-INDEX": "^VNINDEX"}

# 3. DỮ LIỆU
df = yf.download(t_map[target_label], period=period, interval=interval)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # Tính toán
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['MA20'] = df['Close'].rolling(20).mean()

    rsi = float(df['RSI'].iloc[-1])
    
    # 4. CẢNH BÁO
    if rsi < 32:
        st.markdown(f'<div class="signal-card buy-card">🟢 MUA (BUY) - KHUNG {time_frame}</div>', unsafe_allow_html=True)
    elif rsi > 68:
        st.markdown(f'<div class="signal-card sell-card">🔴 BÁN (SELL) - KHUNG {time_frame}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-card hold-card">🟡 THEO DÕI (HOLD) - KHUNG {time_frame}</div>', unsafe_allow_html=True)

    # 5. BIỂU ĐỒ
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.3, 0.7])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Giá'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='yellow', width=1), name='MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#e91e63', width=2), name='RSI'), row=2, col=1)
    fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # 6. QR
    qr = qrcode.make("https://nrynpp6caudetlbejh8appz.streamlit.app")
    buf = BytesIO()
    qr.save(buf)st.image(buf.getvalue(), caption="Quét mã QR của anh", width=120)

st.caption("❤️ Chúc anh yêu ngủ ngon!")
