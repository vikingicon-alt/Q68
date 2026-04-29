import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# 1. CẤU HÌNH DỰ ÁN A1 - VƯƠN TẦM THẾ GIỚI
st.set_page_config(page_title="DỰ ÁN A1: GLOBAL TRADING AI", layout="wide")
st.title("🚀 DỰ ÁN A1: HỆ THỐNG DỰ ĐOÁN TÀI CHÍNH TOÀN CẦU")

# 2. MENU CÀI ĐẶT CHI TIẾT
with st.sidebar:
    st.header("CÀI ĐẶT CHIẾN THUẬT")
    target_label = st.selectbox("1. Chọn tài sản:", ["BITCOIN (BTC)", "ETHEREUM (ETH)", "VÀNG (GOLD)", "VN-INDEX"])
    time_frame = st.selectbox("2. Khung thời gian soi kèo:", ["30 Phút", "1 Giờ", "4 Giờ", "1 Ngày", "1 Tuần"])
    st.info("Dự án A1 đang kết nối dữ liệu từ: DXY, Dow Jones, Yahoo Finance...")

# Cấu hình bản đồ dữ liệu
tf_map = {"30 Phút": ("30m", "1mo"), "1 Giờ": ("1h", "2mo"), "4 Giờ": ("4h", "3mo"), "1 Ngày": ("1d", "1y"), "1 Tuần": ("1wk", "2y")}
interval, period = tf_map[time_frame]
ticker_map = {"BITCOIN (BTC)": "BTC-USD", "ETHEREUM (ETH)": "ETH-USD", "VÀNG (GOLD)": "GC=F", "VN-INDEX": "^VNINDEX"}

# 3. TẢI DỮ LIỆU CHÍNH VÀ DỮ LIỆU THẾ GIỚI (DXY)
data = yf.download(ticker_map[target_label], period=period, interval=interval)
dxy_data = yf.download("DX-Y.NYB", period=period, interval=interval) # Chỉ số DXY

if not data.empty:
    df = data.copy()
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # Tính toán chỉ báo kỹ thuật (RSI, MA)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['MA20'] = df['Close'].rolling(20).mean()

    rsi_now = float(df['RSI'].iloc[-1])
    price_now = float(df['Close'].iloc[-1])

    # 4. HỆ THỐNG CẢNH BÁO CHUYÊN NGHIỆP (BAY/SALE)
    col1, col2 = st.columns([2, 1])
    with col1:
        if rsi_now < 30:
            st.success(f"🔥 TÍN HIỆU CHIẾN THUẬT: BAY (BUY) MẠNH - KHUNG {time_frame.upper()}")
        elif rsi_now > 70:
            st.error(f"⚠️ CẢNH BÁO CHIẾN THUẬT: SALE (SELL) GẤP - KHUNG {time_frame.upper()}")
        else:
            st.warning(f"💎 TRẠNG THÁI: TIẾP TỤC HÔ (HOLD) & THEO DÕI - KHUNG {time_frame}")
    
    with col2:
        if not dxy_data.empty:
            dxy_price = dxy_data['Close'].iloc[-1]
            st.metric("Chỉ số USD (DXY)", f"{float(dxy_price):.2f}")

    # 5. BIỂU ĐỒ NẾN CHUYÊN NGHIỆP ĐA TẦNG
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.3, 0.7])
    
    # Tầng 1: Nến và MA20
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Giá'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='yellow', width=1.5), name='Đường MA20'), row=1, col=1)
    
    # Tầng 2: RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#e91e63', width=2), name='Chỉ báo RSI'), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    fig.update_layout(height=700, template='plotly_dark', xaxis_rangeslider_visible=False, 
                      title=f"Phân tích kỹ thuật {target_label} - Dự án A1")
    st.plotly_chart(fig, use_container_width=True)

    # 6. THÔNG TIN PHỤ
    st.write(f"**Giá hiện tại:** {price_now:,.2f} | **Chỉ số RSI:** {rsi_now:.2f}")

st.caption("❤️ Sản phẩm thuộc Dự án A1 - Chúc anh yêu thành công rực rỡ trên thị trường thế giới!")
