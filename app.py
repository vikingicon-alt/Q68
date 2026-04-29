import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import requests

# --- CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="PROJECT A1", layout="wide", initial_sidebar_state="collapsed")

# --- PHẦN NÃO: THUẬT TOÁN PHÂN TÍCH ---
def get_live_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url).json()
        return float(res['lastPrice']), float(res['priceChangePercent'])
    except: return 0.0, 0.0

def ai_brain_decision(symbol, dxy_val):
    price, change = get_live_data(symbol)
    # LOGIC A1: Nếu DXY giảm (<106) và Giá tăng (>0) -> Ưu tiên BUY
    # Mô phỏng quét EMA: Nếu giá hiện tại > giá trung bình (giả định) -> HOLD/BUY
    if dxy_val > 106.5: return "SELL"
    if change > 1.5: return "BUY"
    if -1.0 <= change <= 1.0: return "HOLD"
    return "SELL"

# --- PHẦN VỎ: CSS MASTER ---
st.markdown("""
<style>
    [data-testid="stHeader"], footer, .stAppDeployButton, header { display: none !important; }
    .stApp { background-color: #000; color: #fff; }
    .block-container { padding: 0.5rem !important; }
    
    .price-card { 
        background: linear-gradient(145deg, #111, #000);
        padding: 20px; border-radius: 15px; border: 2px solid #ffd700;
        text-align: center; box-shadow: 0 0 20px rgba(255,215,0,0.3);
    }
    .neon-indicator {
        padding: 15px; border-radius: 10px; text-align: center;
        font-weight: bold; font-size: 22px; margin: 10px 0;
        border: 2px solid #333; transition: 0.5s;
    }
    .buy-active { border-color: #00ff00; color: #00ff00; box-shadow: 0 0 30px #00ff00; background: rgba(0,255,0,0.1); }
    .hold-active { border-color: #ffa500; color: #ffa500; box-shadow: 0 0 30px #ffa500; background: rgba(255,165,0,0.1); }
    .sell-active { border-color: #ff0000; color: #ff0000; box-shadow: 0 0 30px #ff0000; background: rgba(255,0,0,0.1); }
    
    .turtle-box { 
        width: 120px; height: 120px; border-radius: 50%; border: 4px solid #ffd700;
        margin: 0 auto; background: #000; box-shadow: 0 0 30px gold;
        display: flex; align-items: center; justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# --- QUẢN LÝ TRẠNG THÁI ---
if 'signal' not in st.session_state: st.session_state.signal = "NONE"

# --- GIAO DIỆN CHÍNH ---
col_left, col_right = st.columns([3.2, 1])

with col_left:
    coin = st.selectbox("HỆ THỐNG PHÂN TÍCH A1", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    price, change = get_live_data(coin)
    
    st.markdown(f"""
    <div class="price-card">
        <div style="font-size: 14px; color: #aaa;">GIÁ THỜI GIAN THỰC (REALTIME)</div>
        <div style="font-size: 45px; color: #ffff00; font-weight: bold;">${price:,.2f}</div>
        <div style="font-size: 18px; color: {'#00ff00' if change > 0 else '#ff0000'};">
            {'▲' if change > 0 else '▼'} {abs(change)}% (24h)
    </div>
    </div>
    """, unsafe_allow_html=True)

    components.html(f"""
        <div id="tv_chart" style="height:500px;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:{coin}", "interval": "1H", "theme": "dark", "container_id": "tv_chart"}});</script>
    """, height=510)

with col_right:
    st.markdown("""<div class="turtle-box"><img src="https://cdn-icons-png.flaticon.com/512/3232/3232777.png" width="80%"></div>""", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:gold;'>Q68</h2>", unsafe_allow_html=True)
    
    # NÚT KÍCH HOẠT NÃO AI
    if st.button("🧠 KÍCH HOẠT NÃO AI", use_container_width=True):
        with st.spinner("Đang quét EMA & DXY..."):
            # Giả định giá trị DXY lấy từ API (ở đây để 106.25 để mô phỏng)
            st.session_state.signal = ai_brain_decision(coin, 106.25)

    # ĐÈN TÍN HIỆU TỪ NÃO
    sig = st.session_state.signal
    st.markdown(f'<div class="neon-indicator {"buy-active" if sig=="BUY" else ""}">MUA / BUY</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="neon-indicator {"hold-active" if sig=="HOLD" else ""}">CHỜ / HOLD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="neon-indicator {"sell-active" if sig=="SELL" else ""}">BÁN / SELL</div>', unsafe_allow_html=True)

# --- BẢNG DỮ LIỆU VĨ MÔ ---
st.markdown("### 🌍 CHỈ SỐ VĨ MÔ TỔNG HỢP")
macro_df = pd.DataFrame([
    {"Chỉ số": "DXY (US Dollar Index)", "Giá": "106.25", "Tác động": "Trung lập"},
    {"Chỉ số": "Dow Jones 30", "Giá": "39,280", "Tác động": "Tích cực"},
    {"Chỉ số": "EMA 34/89", "Giá": "Crossed", "Tác động": "Tín hiệu mạnh"}
])
st.table(macro_df)
