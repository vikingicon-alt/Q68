import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import qrcode
from io import BytesIO

# 1. CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP
st.set_page_config(page_title="Phân Tích Tài Chính Pro", layout="wide")
st.title("📈 Hệ Thống Phân Tích AI: BTC, ETH & Vàng")

# 2. DANH MỤC TÀI SẢN (Có thêm Ethereum)
ticker_dict = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Vàng (Gold)": "GC=F",
    "VN-Index": "^VNINDEX"
}

target_label = st.sidebar.selectbox("Chọn tài sản phân tích:", list(ticker_dict.keys()))

# 3. TẢI DỮ LIỆU
data = yf.download(ticker_dict[target_label], period="1y", interval="1d")

if not data.empty:
    df = data.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # TÍNH TOÁN RSI (Sức mạnh thị trường)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 4. HIỂN THỊ GIÁ VÀ DỰ ĐOÁN
    current_price = float(df['Close'].iloc[-1])
    current_rsi = float(df['RSI'].iloc[-1])
    
    st.metric(f"Giá {target_label} Hiện Tại", f"{current_price:,.2f}")

    if current_rsi > 70:
        st.error("⚠️ CẢNH BÁO: QUÁ MUA (NÊN BÁN RA)")
    elif current_rsi < 30:
        st.success("✅ CƠ HỘI: QUÁ BÁN (NÊN MUA VÀO)")
    else:
        st.info("📊 XU HƯỚNG: ĐANG THEO DÕI")

    # 5. VẼ BIỂU ĐỒ NẾN & RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_width=[0.3, 0.7])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Giá'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='magenta', width=2), name='Chỉ số RSI'), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)
    fig.update_layout(height=700, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # 6. MÃ QR ĐỂ CHIA SẺ
    st.write("---")
    qr = qrcode.make("https://nrynpp6caudetlbejh8appz.streamlit.app")
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="Quét mã QR để xem app của anh", width=150)

st.caption("❤️ Chúc Anh Yêu đầu tư thắng lợi!")
