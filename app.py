import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# 1. Cấu hình hệ thống (iPad Optimization)
st.set_page_config(page_title="Project A1 Master", layout="wide")
st.markdown("<style>.stApp { background-color: #0b0e11; color: #eaecef; }</style>", unsafe_allow_html=True)

# 2. Sidebar - Chỉ giữ lại những thứ cốt lõi nhất
with st.sidebar:
    st.markdown("### 🔐 A1 AUTH")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=A1_MASTER_V24", width=100)
    asset = st.selectbox("Tài sản", ["BTC", "ETH", "PAXG", "LTC", "XRP", "BNB"], index=1)
    tf = st.selectbox("Khung giờ", ["15m", "1h", "4h", "1d"], index=1)
    st.write("🟣 EMA99 | 🔴 EMA7")

# 3. Xử lý dữ liệu (Cấu trúc phẳng, không lùi dòng sai)
m = {"BTC":"BTC-USD", "ETH":"ETH-USD", "PAXG":"PAXG-USD", "LTC":"LTC-USD", "XRP":"XRP-USD", "BNB":"BNB-USD"}
df = yf.download(m[asset], period="5d", interval=tf, progress=False)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df = df.reset_index()

# Tính chỉ báo
df['RED'] = df['Close'].ewm(span=7, adjust=False).mean()
df['PURPLE'] = df['Close'].ewm(span=99, adjust=False).mean()
e12 = df['Close'].ewm(span=12, adjust=False).mean()
e26 = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = e12 - e26
df['Sig'] = df['MACD'].ewm(span=9, adjust=False).mean()
delta = df['Close'].diff()
g = delta.where(delta > 0, 0).rolling(14).mean()
l = -delta.where(delta < 0, 0).rolling(14).mean()
df['RSI'] = 100 - (100 / (1 + g/l))

last = df.iloc[-1]
prev = df.iloc[-2]

# 4. Hiển thị giá & Tín hiệu (Bố cục dọc chống tràn)
price_color = "#02c076" if last['Close'] > prev['Close'] else "#cf304a"
st.markdown(f"<h1 style='color:{price_color}; font-size:45px; margin-bottom:0;'>${last['Close']:,.2f}</h1>", unsafe_allow_html=True)

# Logic tín hiệu thẳng hàng
ai_sig = "HOLD"
if last['Close'] > last['PURPLE'] and last['MACD'] > last['Sig']: ai_sig = "BUY"
elif last['Close'] < last['PURPLE']: ai_sig = "SELL"
st.markdown(f"### 🚦 TÍN HIỆU: {ai_sig}")

# 5. Biểu đồ 3 tầng (Nến - Vol - RSI)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])
t = 'Date' if 'Date' in df.columns else 'Datetime'

# Tầng 1: Nến + EMA
fig.add_trace(go.Candlestick(x=df[t], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Nến"), row=1, col=1)
fig.add_trace(go.Scatter(x=df[t], y=df['RED'], line=dict(color='#cf304a', width=2), name="EMA7"), row=1, col=1)
fig.add_trace(go.Scatter(x=df[t], y=df['PURPLE'], line=dict(color='#9c27b0', width=3), name="EMA99"), row=1, col=1)

# Tầng 2: Volume đậm
colors = ['#02c076' if df['Open'].iloc[i] < df['Close'].iloc[i] else '#cf304a' for i in range(len(df))]
fig.add_trace(go.Bar(x=df[t], y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

# Tầng 3: RSI hiện rõ
fig.add_trace(go.Scatter(x=df[t], y=df['RSI'], line=dict(color='#ffffff', width=2), name="RSI"), row=3, col=1)
fig.add_hrect(y0=30, y1=70, fillcolor="#7b3af5", opacity=0.1, row=3, col=1)

# Cấu hình hiển thị (Ép cột giá bên phải)
fig.update_layout(height=750, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=60, t=10, b=10), showlegend=False)
fig.update_yaxes(side="right", showgrid=True, gridcolor="#1e2329")

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
