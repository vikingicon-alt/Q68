1  import streamlit as st
2  import pandas as pd
3  import plotly.graph_objects as go
4  from plotly.subplots import make_subplots
5  
6  # --- CONFIG ---
7  st.set_page_config(page_title="SENTINEL AI - PRO", layout="wide")
8  
9  # --- CUSTOM CSS ---
10 st.markdown("""
11     <style>
12     .main { background-color: #0e1117; }
13     .stButton>button {
14         width: 100%; border-radius: 12px; height: 3.5em;
15         font-weight: bold; font-size: 18px;
16     }
17     .buy-btn { background-color: #00ff88 !important; color: black !important; box-shadow: 0 0 20px #00ff88; }
18     .sell-btn { background-color: #ff4b4b !important; color: white !important; box-shadow: 0 0 20px #ff4b4b; }
19     .hold-btn { background-color: #ffaa00 !important; color: black !important; box-shadow: 0 0 20px #ffaa00; }
20     .q68-footer {
21         position: fixed; bottom: 15px; left: 50%; transform: translateX(-50%);
22         color: #ffffff; font-weight: 900; font-size: 24px; opacity: 0.8;
23     }
24     </style>
25 """, unsafe_allow_html=True)
26 
27 # --- SIDEBAR ---
28 with st.sidebar:
29     st.header("🎮 CONTROL PANEL")
30     asset = st.selectbox("ASSET:", ["BITCOIN (BTC)", "ETHEREUM (ETH)", "GOLD (PAXG)"])
31     tf = st.select_slider("TIMEFRAME:", options=["15m", "30m", "1h", "4h", "1D", "1W", "1M"], value="30m")
32     st.divider()
33     st.write("📲 **SCAN APP:**")
34     st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://A1-PROJECT-APP", width=150)
35 
36 # --- DYNAMIC TITLE ---
37 asset_name = asset.split(" ")[0]
38 st.title(f"🚀 {asset_name} - TREND PREDICTION")
39 
40 # --- DATA SIMULATION ---
41 data = pd.DataFrame({
42     'Open': [10, 12, 11, 14, 13] * 10,
43     'High': [15, 16, 14, 18, 17] * 10,
44     'Low': [8, 9, 10, 11, 12] * 10,
45     'Close': [12, 11, 14, 13, 16] * 10,
46     'Volume': [100, 200, 150, 300, 250] * 10,
47     'RSI': [40, 55, 60, 45, 75] * 10
48 })
49 
50 # --- CHARTS ---
51 fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])
52 fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close']), row=1, col=1)
53 vol_colors = ['#ff4b4b' if data['Open'][i] > data['Close'][i] else '#00ff88' for i in range(len(data))]
54 fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=vol_colors), row=2, col=1)
55 fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], fill='tozeroy', line=dict(color='#00d1ff'), fillcolor='rgba(0, 209, 255, 0.15)'), row=3, col=1)
56 fig.update_layout(height=650, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False)
57 st.plotly_chart(fig, use_container_width=True)
58 
59 # --- SIGNALS ---
60 st.markdown("### 🎯 STRATEGIC SIGNALS")
61 c1, c2, c3 = st.columns(3)
62 with c1:
63     st.markdown('<button class="stButton buy-btn">🔥 BUY NOW</button>', unsafe_allow_html=True)
64 with c2:
  65     st.markdown('<button class="stButton hold-btn">⏳ HOLD</button>', unsafe_allow_html=True)
66 with c3:
67     st.markdown('<button class="stButton sell-btn">❄️ SELL NOW</button>', unsafe_allow_html=True)
68 
69 # --- FOOTER ---
70 st.markdown('<div class="q68-footer">Q68</div>', unsafe_allow_html=True)
