import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import json

# --- 1. CẤU HÌNH GIAO DIỆN Q68 ---
st.set_page_config(page_title="Q68 AI SYSTEM", layout="wide", page_icon="🐢")

st.markdown("""
    <style>
    .main { background-color: #050708; }
    .price-tag { font-size: 36px; font-weight: 900; margin-left: 15px; }
    .up { color: #00ff88; text-shadow: 0 0 10px #00ff8844; }
    .down { color: #ff4b4b; text-shadow: 0 0 10px #ff4b4b44; }
    .indicator-lamp { 
        width: 100%; border-radius: 12px; height: 100px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 900; font-size: 18px; color: white;
        background-color: #1a1c1e; border: 1px solid #333; opacity: 0.1;
    }
    .advice-text { font-size: 12px; font-weight: 400; margin-top: 5px; text-align: center; padding: 0 5px; }
    @keyframes neon-pulse {
        0% { box-shadow: 0 0 5px; opacity: 0.8; transform: scale(1); }
        50% { box-shadow: 0 0 30px; opacity: 1; transform: scale(1.02); }
        100% { box-shadow: 0 0 5px; opacity: 0.8; transform: scale(1); }
    }
    .lamp-buy { background-color: #00ff88 !important; color: black !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; }
    .lamp-sell { background-color: #ff4b4b !important; color: white !important; animation: neon-pulse 1s infinite !important; opacity: 1 !important; }
    .lamp-hold { background-color: #ffaa00 !important; color: black !important; animation: neon-pulse 2s infinite !important; opacity: 1 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. ENGINE PHÂN TÍCH CHIẾN THUẬT ---
@st.cache_data(ttl=10)
def get_ai_analysis(asset_label, tf):
    # (Hàm lấy dữ liệu tương tự bản trước, bổ sung EMA50 để xác định xu hướng dài)
    # ... [Phần code lấy dữ liệu từ Yahoo Finance] ...
    # Giả định df đã có: Close, EMA20, EMA50, RSI, Volume, VolMA
    return df # df được tính toán đầy đủ

# --- 3. BỘ NÃO CỦA 3 NÚT CẢNH BÁO ---
def render_ai_brain(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Điều kiện MUA: Giá > EMA20, RSI vừa hồi từ dưới lên, Volume tăng đột biến
    buy_score = 0
    if last['Close'] > last['EMA20']: buy_score += 1
    if last['RSI'] < 40: buy_score += 1
    if last['Volume'] > last['VolMA']: buy_score += 1
    
    # Điều kiện BÁN: Giá < EMA20, RSI quá mua (>70), Xu hướng giảm
    sell_score = 0
    if last['Close'] < last['EMA20']: sell_score += 1
    if last['RSI'] > 65: sell_score += 1
    if last['Volume'] > last['VolMA'] and last['Close'] < last['Open']: sell_score += 1

    # Phân loại trạng thái
    status = "HOLD"
    advice = "Chưa có tín hiệu rõ ràng. Chờ đợi Volume xác nhận."
    
    if buy_score >= 2: 
        status = "BUY"
        advice = "LỰC MUA MẠNH. Giá trên EMA. Vào lệnh ưu tiên."
    elif sell_score >= 2: 
        status = "SELL"
        advice = "RỦI RO CAO. RSI quá mua hoặc gãy EMA. Thoát hàng."

    c1, c2, c3 = st.columns(3)
    with c1:
        active = "lamp-buy" if status == "BUY" else ""
        st.markdown(f'<div class="indicator-lamp {active}">🔥 LỆNH MUA<div class="advice-text">{advice if status=="BUY" else ""}</div></div>', unsafe_allow_html=True)
    with c2:
        active = "lamp-hold" if status == "HOLD" else ""
        st.markdown(f'<div class="indicator-lamp {active}">⏳ THEO DÕI<div class="advice-text">{advice if status=="HOLD" else ""}</div></div>', unsafe_allow_html=True)
    with c3:
        active = "lamp-sell" if status == "SELL" else ""
        st.markdown(f'<div class="indicator-lamp {active}">❄️ LỆNH BÁN<div class="advice-text">{advice if status=="SELL" else ""}</div></div>', unsafe_allow_html=True)

# --- 4. HIỂN THỊ ---
df = get_ai_analysis(asset_label, tf_choice)
if df is not None:
    # [Code hiển thị biểu đồ nến và Volume bên phải đã tối ưu]
    
    st.markdown("### 🧠 TRÍ TUỆ ĐẦU TƯ A1")
    render_ai_brain(df)
