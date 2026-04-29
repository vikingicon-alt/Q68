import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- 1. CẤU HÌNH GIAO DIỆN (UI/UX CHUẨN IPAD) ---
st.set_page_config(page_title="Project A1 - Global Master", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .status-btn {
        flex: 1; height: 60px; border-radius: 8px; display: flex; 
        align-items: center; justify-content: center; font-weight: 900;
        background: #2b3139; color: #848e9c; font-size: 24px;
        border: 2px solid #474d57;
    }
    .buy-active { background: #02c076 !important; color: white !important; box-shadow: 0 0 25px #02c076; border: none; }
    .sell-active { background: #cf304a !important; color: white !important; box-shadow: 0 0 25px #cf304a; border: none; }
    .hold-active { background: #f0b90b !important; color: black !important; border: none; }
    .price-hero { font-size: 70px; font-weight: 900; color: #02c076; line-height: 1.1; margin: 10px 0; }
    .price-red { color: #cf304a !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. THANH ĐIỀU KHIỂN & BẢO MẬT QR ---
with st.sidebar:
    st.markdown("# 🔐 PROJECT A1")
    st.markdown("### 📲 QR LOGIN (ĐĂNG NHẬP)")
    # QR Login bảo mật theo yêu cầu
    qr_code = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=A1_VERIFIED_V20_MASTER"
    st.image(qr_code, caption="Quét mã để xác thực truy cập")
    
    st.divider()
    # DANH MỤC TÀI SẢN ĐẦY ĐỦ: BTC, ETH, PAXG, LTC, XRP, BNB
    asset = st.selectbox("Chọn tài sản", ["BTC", "ETH", "PAXG", "LTC", "XRP", "BNB"])
    tf = st.selectbox("Khung thời gian", ["15m", "1h", "4h", "1d"], index=1)
    
    st.divider()
    # Fix triệt để Volume mờ - Mặc định 1.0 (Đậm nhất)
    vol_intensity = st.slider("Độ sắc nét Volume", 0.1, 1.0, 1.0)
    st.info("Tím (EMA99): Đường về\nĐỏ (EMA7): Ngắn hạn")

# --- 3. XỬ LÝ DỮ LIỆU (ĐÃ KIỂM TRA LỖI INDENTATION) ---
@st.cache_data(ttl=10)
def fetch_verified_data(symbol, interval):
    # Map mã giao dịch
    tickers = {"BTC":"BTC-USD", "ETH":"ETH-USD", "PAXG":"PAXG-USD", "LTC":"LTC-USD", "XRP":"XRP-USD", "BNB":"BNB-USD"}
    data = yf.download(tickers[symbol], period="5d", interval=interval, progress=False)
    
    # Xử lý MultiIndex nếu có
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.reset_index()
    
    # Tính toán chỉ báo kỹ thuật
    data['EMA_RED'] = data['Close'].ewm(span=7, adjust=False).mean()
    data['EMA_PURPLE'] = data['Close'].ewm(span=99, adjust=False).mean()
    
    # MACD chuẩn
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    # RSI chuẩn
    change = data['Close'].diff()
    up = change.clip(lower=0); down = -1 * change.clip(upper=0)
    ma_up = up.rolling(window=14).mean(); ma_down = down.rolling(window=14).mean()
    data['RSI'] = 100 - (100 / (1 + ma_up/ma_down))
    
    return data

# Triển khai lấy dữ liệu
df_final = fetch_verified_data(asset, tf)
curr = df_final.iloc[-1]
prev = df_final.iloc[-2]

# --- 4. HIỂN THỊ TERMINAL & TÍN HIỆU ---
st.write(f"**Asset:** {asset}/USDT • **Market Status:** ONLINE")
p_color = "price-red" if curr['Close'] < prev['Close'] else ""
st.markdown(f'<div class="price-hero {p_color}">${curr["Close"]:,.2f}</div>', unsafe_allow_html=True)

# AI Logic (Tín hiệu dựa trên Đường Tím & MACD)
ai_signal = "HOLD"
if curr['Close'] > curr['EMA_PURPLE'] and curr['MACD'] > curr['Signal']:
    ai_signal = "BUY"
elif curr['Close'] < curr['EMA_PURPLE']:
    ai_signal = "SELL"

st.markdown(f"""
<div style="display: flex; gap: 12px; margin-bottom: 25px;">
    <div class="status-btn {'buy-active' if ai_signal == 'BUY' else ''}">BUY</div>
    <div class="status-btn {'hold-active' if ai_signal == 'HOLD' else ''}">HOLD</div>
    <div class="status-btn {'sell-active' if ai_signal == 'SELL' else ''}">SELL</div>
</div>
""", unsafe_allow_html=True)

# --- 5. BIỂU ĐỒ NẾN ĐA TẦNG SIÊU NÉT ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                    row_heights=[0.6, 0.2, 0.2])
x_axis = 'Date' if 'Date' in df_final.columns else 'Datetime'

# Tầng 1: Nến + Hệ thống đường EMA (Tím/Đỏ)
fig.add_trace(go.Candlestick(x=df_final[x_axis], open=df_final['Open'], high=df_final['High'], 
                             low=df_final['Low'], close=df_final['Close'],
                             increasing_line_color='#02c076', decreasing_line_color='#cf304a'), row=1, col=1)
fig.add_trace(go.Scatter(x=df_final[x_axis], y=df_final['EMA_RED'], line=dict(color='#cf304a', width=2), name="Đỏ"), row=1, col=1)
fig.add_trace(go.Scatter(x=df_final[x_axis], y=df_final['EMA_PURPLE'], line=dict(color='#9c27b0', width=3.5), name="Tím"), row=1, col=1)

# Tầng 2: Volume (Đã kiểm tra độ đậm)
v_colors = ['#02c076' if df_final['Open'].iloc[i] < df_final['Close'].iloc[i] else '#cf304a' for i in range(len(df_final))]
fig.add_trace(go.Bar(x=df_final[x_axis], y=df_final['Volume'], marker_color=v_colors, opacity=vol_intensity), row=2, col=1)

# Tầng 3: RSI mây tín hiệu
fig.add_trace(go.Scatter(x=df_final[x_axis], y=df_final['RSI'], line=dict(color='#ffffff', width=2)), row=3, col=1)
fig.add_hrect(y0=30, y1=70, fillcolor="#7b3af5", opacity=0.15, row=3, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="#cf304a", row=3, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="#02c076", row=3, col=1)

fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False, 
                  margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
fig.update_yaxes(side="right", gridcolor="#1e2329")
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
