import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import qrcode
from io import BytesIO

st.set_page_config(page_title="Dự Đoán Tài Chính AI", layout="wide")
st.title("📊 Hệ Thống Dự Đoán: BTC, Vàng & Chứng Khoán")

asset_dict = {"Bitcoin": "BTC-USD", "Vàng Thế Giới": "GC=F", "Cổ Phiếu PVF": "PVF.VN", "Ethereum": "ETH-USD"}
target = st.sidebar.selectbox("Chọn tài sản:", list(asset_dict.keys()))

data = yf.download(asset_dict[target], period="1y", interval="1d")

if not data.empty:
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🤖 Phân Tích AI")
    price_now = data['Close'].iloc[-1]
    st.metric("Giá hiện tại", f"{price_now:,.2f}")
    st.success("Tín hiệu AI: Đang phân tích xu hướng... Hãy giữ vững mục tiêu!")

    st.sidebar.write("📲 Mã QR Truy Cập:")
    qr = qrcode.make(f"https://finance.yahoo.com/quote/{asset_dict[target]}")
    buf = BytesIO()
    qr.save(buf, format="PNG")
    st.sidebar.image(buf.getvalue())
