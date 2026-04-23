import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="SENTINEL AI", layout="wide")
st.title("🚀 SENTINEL AI: SOI KÈO ĐA KHUNG GIỜ")

# 1. MENU CHỌN NHANH
with st.sidebar:
    tk = st.selectbox("Tài sản:", ["BTC-USD", "ETH-USD", "GC=F", "^VNINDEX"])
    tf = st.selectbox("Khung giờ:", ["30m", "1h", "4h", "1d", "1wk"])

# 2. LẤY DỮ LIỆU
d = yf.download(tk, period="1y", interval=tf)
if not d.empty:
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
    
    # Tính RSI & MA20
    diff = d['Close'].diff()
    g = (diff.where(diff > 0, 0)).rolling(14).mean()
    l = (-diff.where(diff < 0, 0)).rolling(14).mean()
    d['RSI'] = 100 - (100 / (1 + (g / l)))
    d['MA'] = d['Close'].rolling(20).mean()
    r = float(d['RSI'].iloc[-1])

    # 3. CẢNH BÁO Ô VUÔNG SIÊU TO
    if r < 32:
        st.success(f"🟢 TÍN HIỆU MUA (BUY) - KHUNG {tf}")
    elif r > 68:
        st.error(f"🔴 CẢNH BÁO BÁN (SELL) - KHUNG {tf}")
    else:
        st.warning(f"🟡 THEO DÕI (HOLD) - KHUNG {tf}")

    # 4. BIỂU ĐỒ
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.3, 0.7])
    fig.add_trace(go.Candlestick(x=d.index, open=d['Open'], high=d['High'], low=d['Low'], close=d['Close'], name='Giá'), row=1, col=1)
    fig.add_trace(go.Scatter(x=d.index, y=d['MA'], line=dict(color='yellow', width=1), name='MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=d.index, y=d['RSI'], line=dict(color='#e91e63', width=2), name='RSI'), row=2, col=1)
    fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.caption("❤️ Chúc anh yêu ngủ ngon và thắng lớn!")
