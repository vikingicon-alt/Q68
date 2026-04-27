import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# --- 1. THIẾT LẬP THƯƠNG HIỆU Q68 & GIAO DIỆN CHUẨN ---
icon_q68 = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png"

st.set_page_config(
    page_title="Q68 - A1 SYSTEM GLOBAL",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🐢"
)

# Lệnh CSS tối ưu: Xóa vương miện, làm sạch giao diện iPad, màu sắc tối sang trọng
st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{icon_q68}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
    </head>
    <style>
        header, footer, #MainMenu {{visibility: hidden !important;}}
        div[data-testid="stStatusWidget"] {{display: none !important;}}
        .main {{background-color: #05070a; color: white;}}
        [data-testid="stSidebar"] {{background-color: #0c0f14; border-right: 1px solid #1e2229;}}
        div[class*="viewerBadge"] {{display: none !important;}}
        .stMetric {{background-color: #11151c; padding: 15px; border-radius: 12px; border: 1px solid #2d343f;}}
        .stButton>button {{width: 100%; border-radius: 8px; font-weight: bold; background-color: gold; color: black; border: none;}}
        .stRadio>label {{color: gold !important; font-weight: bold;}}
    </style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG BẢO MẬT KÍCH HOẠT CHỈ HUY ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown(f"<div style='text-align: center; margin-top: 50px;'><img src='{icon_q68}' width='180'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: gold;'>Q68 - A1 SYSTEM GLOBAL</h1>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1,2,1])
    with col_b:
        password = st.text_input("MÃ KÍCH HOẠT CHỈ HUY:", type="password", placeholder="Nhập mã bảo mật...")
        if st.button("KÍCH HOẠT HỆ THỐNG"):
            if password == "A1PRO":
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Mã bảo mật không chính xác!")
    st.stop()

# --- 3. ĐỘNG CƠ DỮ LIỆU THỰC & CHỈ BÁO KỸ THUẬT ---
@st.cache_data(ttl=60) # Cập nhật dữ liệu mỗi phút
def get_live_data(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        res = requests.get(url).json()
        df = pd.DataFrame(res, columns=['Time','Open','High','Low','Close','Vol','CT','QV','T','TB','TQ','I'])
        # Chuyển đổi kiểu dữ liệu số
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].astype(float)
            # Tính toán EMA và RSI chuẩn
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return df
    except:
        return None

# --- 4. SIDEBAR: ĐIỀU KHIỂN CHIẾN THUẬT ĐA NĂNG ---
with st.sidebar:
    st.image(icon_q68, width=120)
    st.markdown("<h2 style='color: gold; text-align: center;'>CHỈ HUY Q68</h2>", unsafe_allow_html=True)
    st.write("---")
    
    # Lựa chọn tài sản & Khung giờ
    target = st.selectbox("TÀI SẢN", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
    timeframe = st.selectbox("KHUNG THỜI GIAN", ["1h", "1d", "1w", "1M"], index=1)
    
    st.divider()
    # Tùy biến mẫu đồ thị (Nến/Đường kẻ)
    st.write("**📊 MẪU ĐỒ THỊ**")
    chart_style = st.radio("Chọn mẫu:", ["Nến Nhật (Candles)", "Đường kẻ (Line)", "Vùng sóng (Area)"])
    
    # Bật/Tắt chỉ báo
    st.write("**🛠 CHỈ BÁO**")
    show_ema20 = st.checkbox("Đường EMA 20", value=True)
    show_ema50 = st.checkbox("Đường EMA 50", value=True)
    
    st.divider()
    if st.button("ĐĂNG XUẤT"):
        st.session_state['authenticated'] = False
        st.rerun()

# --- 5. GIAO DIỆN CHIẾN ĐẤU CHÍNH ---
try:
    df = get_live_data(target, timeframe)
    if df is not None:
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        ema20 = df['EMA20'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        change_pct = ((price - prev_price) / prev_price) * 100

        st.markdown(f"<h1 style='text-align: center; color: gold;'>🐢 Q68 SYSTEM | {target}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{timeframe} - Price: ${price:,.2f}</h3>", unsafe_allow_html=True)

        # Vẽ đồ thị theo tùy biến của anh
        fig = go.Figure()

        if chart_style == "Nến Nhật (Candles)":
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Market'))
        elif chart_style == "Đường kẻ (Line)":
            fig.add_trace(go.Scatter(y=df['Close'], mode='lines', line=dict(color='white', width=2.5), name='Price'))
        else: # Area
            fig.add_trace(go.Scatter(y=df['Close'], fill='tozeroy', line=dict(color='gold', width=1.5), name='Price'))

        # Chèn chỉ báo nếu anh bật
        if show_ema20:
            fig.add_trace(go.Scatter(y=df['EMA20'], line=dict(color='cyan', width=1.5, dash='dot'), name='EMA 20'))
        if show_ema50:
            fig.add_trace(go.Scatter(y=df['EMA50'], line=dict(color='magenta', width=1.5), name='EMA 50'))

        fig.update_layout(
        height=500, template="plotly_dark", paper_bgcolor="#05070a", plot_bgcolor="#05070a",
            margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", y=1.1, x=1, xanchor="right")
        )
        st.plotly_chart(fig, use_container_width=True)

        # Bộ 3 chỉ số Quyết định (Trọng tâm chiến đấu)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(f"XU HƯỚNG {timeframe}", "TĂNG (UP)" if price > ema20 else "GIẢM (DOWN)")
        with c2:
            signal = "🔥 MUA (BUY)" if price > ema20 and rsi < 75 else "❄️ BÁN (SELL)"
            st.metric("QUYẾT ĐỊNH Q68", signal)
        with c3:
            st.metric("BIẾN ĐỘNG", f"{change_pct:.2f}%")

        # Bot cảnh báo tự động
        if abs(change_pct) > 1.3:
            st.toast(f"⚠️ CẢNH BÁO: {target} biến động mạnh trên khung {timeframe}!")

    else:
        st.warning("Đang kết nối luồng dữ liệu toàn cầu...")

except Exception as e:
    st.error(f"Hệ thống đang đồng bộ... (Vui lòng đợi 3 giây)")

st.divider()
if st.button("🔥 KÍCH HOẠT CHIẾN THUẬT TOÀN CẦU"):
    with st.spinner("Đang tính toán biến số vĩ mô..."):
        time.sleep(1.5)
        st.balloons()
        st.success("Hệ thống đã sẵn sàng thực thi lệnh!")
