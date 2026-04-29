import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN (iPad Optimized) ---
st.set_page_config(page_title="Q68 AI SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #050708; }
    .price-container { display: flex; align-items: baseline; margin-bottom: 5px; }
    .price-tag { font-size: 42px; font-weight: 900; margin-left: 15px; }
    .up { color: #00ff88; text-shadow: 0 0 10px #00ff8844; }
    .down { color: #ff4b4b; text-shadow: 0 0 10px #ff4b4b44; }
    .indicator-lamp { 
        width: 100%; border-radius: 15px; height: 110px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 900; font-size: 20px; color: white;
        background-color: #1a1c1e; border: 1px solid #333; opacity: 0.2;
    }
    .advice-text { font-size: 13px; font-weight: 400; margin-top: 8px; text-align: center; color: white; padding: 0 10px; }
    @keyframes neon-pulse {
        0% { box-shadow: 0 0 5px; opacity: 0.8; }
        50% { box-shadow: 0 0 35px; opacity: 1; }
        100% { box-shadow: 0 0 5px; opacity: 0.8; }
    }
    .lamp-buy { background-color: #00ff88 !important; color: black !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; }
    .lamp-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; }
    .lamp-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-pulse 2s infinite !important; opacity: 1 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR ĐIỀU KHIỂN ---
with st.sidebar:
    st.markdown("# 🐢 Q68 SYSTEM")
    assets = {
        "BITCOIN (BTC)": "BTC-USD", 
        "ETHEREUM (ETH)": "ETH-USD", 
        "SOLANA (SOL)": "SOL-USD",
        "GOLD (VÀNG)": "PAXG-USD"
    }
    asset_label = st.selectbox("CHỌN TÀI SẢN:", list(assets.keys()))
    tf_choice = st.select_slider("KHUNG GIỜ:", options=["5m", "15m", "1h", "4h", "1D"], value="1h")
    st.divider()
    vol_style = st.radio("MẪU VOLUME:", ["Mặc định", "Volume + MA20", "Dòng tiền"])
    chart_style = st.radio("MẪU BIỂU ĐỒ:", ["Quốc tế (EMA)", "Phân tích RSI"])

# --- 3. BỘ NÃO XỬ LÝ DỮ LIỆU (CHỐNG LỖI 100%) ---
def get_safe_data(symbol_key, tf):
    try:
        # Tải dữ liệu và xử lý ngay lập tức để tránh lỗi định dạng
        raw_df = yf.download(assets[symbol_key], period="5d", interval=tf, progress=False)
        if raw_df.empty: return None
        
        # San phẳng cột nếu là MultiIndex (Sửa lỗi TypeError)
        df = raw_df.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.reset_index()
        # Tính toán chỉ báo kỹ thuật
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['VolMA'] = df['Volume'].rolling(window=20).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain/loss)))
        
        return df
    except Exception as e:
        return None

df = get_safe_data(asset_label, tf_choice)

if df is not None:
    # 4. HIỂN THỊ GIÁ USD TO RÕ (BỎ CHỮ Q68)
    last_p = float(df['Close'].iloc[-1])
    prev_p = float(df['Close'].iloc[-2])
    color_c = "up" if last_p >= prev_p else "down"
    
    st.markdown(f"""
        <div class="price-container">
            <h1 style="margin:0; color:#fff;">🐢 {asset_label.split(' ')[0]}</h1>
            <div class="price-tag {color_c}">${last_p:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    # 5. BIỂU ĐỒ VỚI TRỤC GIÁ BÊN PHẢI
    show_rsi = chart_style == "Phân tích RSI"
    rows = 2 + (1 if show_rsi else 0)
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2] + ([0.2] if show_rsi else []))

    # Nến & Trục giá phải
    time_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
    fig.add_trace(go.Candlestick(x=df[time_col], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Giá"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df[time_col], y=df['EMA20'], line=dict(color='#FFD700', width=2), name="EMA20"), row=1, col=1)
    fig.update_yaxes(side="right", row=1, col=1, gridcolor="#333")

    # Volume theo mẫu
    v_colors = ['#ff4b4b' if df['Open'].iloc[i] > df['Close'].iloc[i] else '#00ff88' for i in range(len(df))]
    if vol_style != "Dòng tiền":
        fig.add_trace(go.Bar(x=df[time_col], y=df['Volume'], marker_color=v_colors), row=2, col=1)
    else:
        fig.add_trace(go.Scatter(x=df[time_col], y=df['Volume'], fill='tozeroy', line=dict(color='#00ff88')), row=2, col=1)
    
    if vol_style == "Volume + MA20":
        fig.add_trace(go.Scatter(x=df[time_col], y=df['VolMA'], line=dict(color='white', width=1)), row=2, col=1)
    fig.update_yaxes(side="right", row=2, col=1, gridcolor="#333")

    if show_rsi:
        fig.add_trace(go.Scatter(x=df[time_col], y=df['RSI'], line=dict(color='#00d1ff')), row=rows, col=1)
        fig.update_yaxes(side="right", range=[0, 100], row=rows, col=1)

    fig.update_layout(height=650, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False, margin=dict(t=5, b=5))
    st.plotly_chart(fig, use_container_width=True)

    # 6. BỘ NÃO AI PHÂN TÍCH THỰC THẾ
    st.markdown("### 🧠 HỆ THỐNG PHÂN TÍCH A1")
    l_c = float(df['Close'].iloc[-1])
    l_e = float(df['EMA20'].iloc[-1])
    l_r = float(df['RSI'].iloc[-1])
    l_v = float(df['Volume'].iloc[-1])
    l_vm = float(df['VolMA'].iloc[-1])

    status = "HOLD"
    msg = "Thị trường đang nén giá. Đứng ngoài quan sát Volume."
    
    if l_c > l_e and l_r < 65 and l_v > l_vm:
        status = "BUY"; msg = "ƯU TIÊN MUA: Giá trên EMA20 + Volume bùng nổ xác nhận xu hướng."
    elif l_c < l_e or l_r > 75:
        status = "SELL"; msg = "CẢNH BÁO: Giá gãy EMA20 hoặc RSI quá mua. Nên cân nhắc thoát hàng."

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="indicator-lamp {"lamp-buy" if status=="BUY" else ""}">🔥 LỆNH MUA<div class="advice-text">{msg if status=="BUY" else ""}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="indicator-lamp {"lamp-hold" if status=="HOLD" else ""}">⏳ THEO DÕI<div class="advice-text">{msg if status=="HOLD" else ""}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="indicator-lamp {"lamp-sell" if status=="SELL" else ""}">❄️ LỆNH BÁN<div class="advice-text">{msg if status=="SELL" else ""}</div></div>', unsafe_allow_html=True)

else:
    st.info("🔄 Đang đồng bộ hóa dữ liệu từ thị trường quốc tế...")
