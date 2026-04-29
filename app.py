import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# --- 1. GIAO DIỆN HIỆN ĐẠI (AUTHENTIC UI) ---
st.set_page_config(page_title="Project A1 - Secure Login", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    /* Nút bấm lệnh lớn */
    .status-btn {
        flex: 1; height: 60px; border-radius: 8px; display: flex; 
        align-items: center; justify-content: center; font-weight: 900;
        background: #2b3139; color: #848e9c; font-size: 22px;
        border: 2px solid #474d57;
    }
    .buy-active { background: #02c076 !important; color: white !important; box-shadow: 0 0 25px #02c076; border: none; }
    .sell-active { background: #cf304a !important; color: white !important; box-shadow: 0 0 25px #cf304a; border: none; }
    .hold-active { background: #f0b90b !important; color: black !important; border: none; }
    
    .price-hero { font-size: 65px; font-weight: 900; color: #02c076; line-height: 1; margin-bottom: 5px; }
    .price-red { color: #cf304a !important; }
    
    /* Khung QR Đăng nhập Luxury */
    .qr-login-box { 
        background: white; padding: 15px; border-radius: 10px; 
        text-align: center; border: 3px solid #f0b90b; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG SIDEBAR & QR LOGIN ---
with st.sidebar:
    st.markdown("# 🔐 PROJECT A1")
    st.info("Hệ thống dự đoán thị trường toàn cầu")
    
    # MÃ QR ĐĂNG NHẬP (Theo yêu cầu mới)
    st.divider()
    st.markdown("### 📲 QR LOGIN / ĐĂNG NHẬP")
    # Link này có thể thay bằng token hoặc link xác thực của anh
    qr_login_url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=LOGIN_TOKEN_SECURE_A1"
    st.image(qr_login_url, caption="Quét mã để xác thực tài khoản")
    st.warning("Vui lòng không chia sẻ mã này.")
    
    st.divider()
    asset = st.selectbox("Tài sản (Assets)", ["BTC", "ETH", "PAXG", "SOL", "BNB"])
    tf = st.selectbox("Khung giờ", ["15m", "1h", "4h", "1d"], index=1)
    
    st.divider()
    show_ema = st.toggle("Đường EMA Tím/Đỏ", True)
    # Tăng 300% độ đậm Volume bằng mặc định max
    vol_opacity = st.slider("Độ rõ Volume", 0.5, 1.0, 1.0) 

# --- 3. XỬ LÝ DỮ LIỆU & CHỈ BÁO XU HƯỚNG ---
@st.cache_data(ttl=10)
def get_data(symbol, interval):
    m = {"BTC": "BTC-USD", "ETH": "ETH-USD", "PAXG": "PAXG-USD", "SOL": "SOL-USD", "BNB": "BNB-USD"}
    df = yf.download(m[symbol], period="5d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    
    # Hệ thống đường EMA anh yêu cầu
    df['EMA_RED'] = df['Close'].ewm(span=7).mean()    # Đường Đỏ
df['EMA_PURPLE'] = df['Close'].ewm(span=99).mean() # Đường Tím (Đường về)
    
    # MACD & RSI
    exp1 = df['Close'].ewm(span=12).mean(); exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2; df['Sig'] = df['MACD'].ewm(span=9).mean()
    delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + g/l))
    return df

df = get_data(asset, tf)
last, prev = df.iloc[-1], df.iloc[-2]

# Tín hiệu AI
signal = "HOLD"
if last['Close'] > last['EMA_PURPLE'] and last['MACD'] > last['Sig']: signal = "BUY"
elif last['Close'] < last['EMA_PURPLE']: signal = "SELL"

# --- 4. HIỂN THỊ GIÁ & NÚT LỆNH ---
p_color = "price-red" if last['Close'] < prev['Close'] else ""
st.markdown(f'<div style="color:#848e9c; font-size:14px;">{asset}/USDT • {tf} MARKET</div>', unsafe_allow_html=True)
st.markdown(f'<div class="price-hero {p_color}">${last["Close"]:,.2f}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="display: flex; gap: 12px; margin-bottom: 25px;">
    <div class="status-btn {'buy-active' if signal == 'BUY' else ''}">BUY</div>
    <div class="status-btn {'hold-active' if signal == 'HOLD' else ''}">HOLD</div>
    <div class="status-btn {'sell-active' if signal == 'SELL' else ''}">SELL</div>
</div>
""", unsafe_allow_html=True)

# --- 5. BIỂU ĐỒ NẾN ĐA MÔ HÌNH ---
fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02, 
                    row_heights=[0.55, 0.1, 0.15, 0.2])
t_ax = 'Date' if 'Date' in df.columns else 'Datetime'

# TẦNG 1: NẾN & ĐƯỜNG TÍM/ĐỎ
fig.add_trace(go.Candlestick(x=df[t_ax], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                             increasing_line_color='#02c076', decreasing_line_color='#cf304a'), row=1, col=1)
if show_ema:
    fig.add_trace(go.Scatter(x=df[t_ax], y=df['EMA_RED'], line=dict(color='#cf304a', width=1.8), name="Đường Đỏ"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df[t_ax], y=df['EMA_PURPLE'], line=dict(color='#9c27b0', width=2.5), name="Đường Tím"), row=1, col=1)

# TẦNG 2: VOLUME SIÊU NÉT (Fix mờ hoàn toàn)
v_colors = ['#02c076' if df['Open'].iloc[i] < df['Close'].iloc[i] else '#cf304a' for i in range(len(df))]
fig.add_trace(go.Bar(x=df[t_ax], y=df['Volume'], marker_color=v_colors, opacity=vol_opacity), row=2, col=1)

# TẦNG 3: MACD
fig.add_trace(go.Bar(x=df[t_ax], y=df['MACD']-df['Sig'], marker_color='#474d57'), row=3, col=1)
fig.add_trace(go.Scatter(x=df[t_ax], y=df['MACD'], line=dict(color='#2962FF', width=2)), row=3, col=1)

# TẦNG 4: RSI MÔ HÌNH VÙNG MÂY
fig.add_trace(go.Scatter(x=df[t_ax], y=df['RSI'], line=dict(color='#ffffff', width=2)), row=4, col=1)
fig.add_hrect(y0=30, y1=70, fillcolor="#7b3af5", opacity=0.15, line_width=0, row=4, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="#cf304a", row=4, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="#02c076", row=4, col=1)

fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, 
                  margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
fig.update_yaxes(side="right", gridcolor="#1e2329")
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
