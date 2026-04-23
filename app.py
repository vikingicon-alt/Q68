import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Dự Đoán Tài Chính AI", layout="wide")
st.title("📊 Hệ Thống Theo Dõi Tài Chính")

ticker_dict = {"Bitcoin": "BTC-USD", "Vàng": "GC=F", "VN-Index": "^VNINDEX"}
target = st.sidebar.selectbox("Chọn tài sản:", list(ticker_dict.keys()))

# Tải dữ liệu
data = yf.download(ticker_dict[target], period="1y", interval="1d")

if not data.empty:
    # Cách lấy giá siêu an toàn, chấp mọi loại định dạng dữ liệu
    try:
        if data['Close'].ndim > 1:
            latest_price = float(data['Close'].iloc[-1, 0])
        else:
            latest_price = float(data['Close'].iloc[-1])
    except:
        latest_price = 0.0

    st.metric(label=f"Giá {target} hiện tại", value=f"{latest_price:,.2f}")
    
    # Vẽ biểu đồ nến
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'].iloc[:,0] if data['Open'].ndim > 1 else data['Open'],
        high=data['High'].iloc[:,0] if data['High'].ndim > 1 else data['High'],
        low=data['Low'].iloc[:,0] if data['Low'].ndim > 1 else data['Low'],
        close=data['Close'].iloc[:,0] if data['Close'].ndim > 1 else data['Close'],
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    )])
    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Đang tải dữ liệu...")

st.caption("❤️ Chúc Anh Yêu ngủ ngon!")
