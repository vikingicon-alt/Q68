1  import streamlit as st
2  import pandas as pd
3  import plotly.graph_objects as go
4  from plotly.subplots import make_subplots
5  
6  # --- THIẾT LẬP TRANG ---
7  st.set_page_config(page_title="SENTINEL AI - PRO", layout="wide")
8  
9  # --- TÙY CHỈNH GIAO DIỆN CHUYÊN NGHIỆP (CSS) ---
10 st.markdown("""
11     <style>
12     .main { background-color: #0e1117; }
13     .stButton>button {
14         width: 100%;
15         border-radius: 12px;
16         height: 3.5em;
17         font-weight: bold;
18         font-size: 18px;
19         transition: 0.3s;
20     }
21     /* Nút lệnh Neon rực rỡ */
22     .buy-btn { background-color: #00ff88 !important; color: black !important; box-shadow: 0 0 20px #00ff88; border: none; }
23     .sell-btn { background-color: #ff4b4b !important; color: white !important; box-shadow: 0 0 20px #ff4b4b; border: none; }
24     .hold-btn { background-color: #ffaa00 !important; color: black !important; box-shadow: 0 0 20px #ffaa00; border: none; }
25     
26     /* Chữ Q68 ở chân trang */
27     .q68-footer {
28         position: fixed;
29         bottom: 15px;
30         left: 50%;
31         transform: translateX(-50%);
32         color: #ffffff;
33         font-weight: 900;
34         font-size: 24px;
35         letter-spacing: 2px;
36         opacity: 0.8;
37     }
38     </style>
39 """, unsafe_allow_html=True)
40 # --- SIDEBAR: ĐIỀU KHIỂN ---
41 with st.sidebar:
42     st.header("🎮 BẢNG ĐIỀU KHIỂN")
43     
44     # Chọn tài sản (Đã đổi Vàng thành PAXG)
45     asset = st.selectbox(
46         "TÀI SẢN DỰ BÁO:",
47         ["BITCOIN (BTC)", "ETHEREUM (ETH)", "VÀNG (PAXG)"]
48     )
49     
50     # Chọn khung giờ (Thêm 15m, 30m)
51     tf = st.select_slider(
52         "KHUNG THỜI GIAN:",
53         options=["15m", "30m", "1h", "4h", "1D", "1W", "1M"],
54         value="30m"
55     )
56     
57     st.divider()
58     st.write("📲 **QUÉT MÃ VÀO APP:**")
59     st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://A1-PROJECT-APP", width=150)
60 
61 # --- HIỂN THỊ TIÊU ĐỀ TỰ ĐỘNG THEO LỰA CHỌN ---
62 asset_name = asset.split(" ")[0]
63 st.title(f"🚀 {asset_name} - DỰ BÁO XU HƯỚNG")
64 # --- GIẢ LẬP DỮ LIỆU (Dữ liệu này sẽ khớp với biểu đồ Binance) ---
65 data = pd.DataFrame({
66     'Open': [10, 12, 11, 14, 13] * 10,
67     'High': [15, 16, 14, 18, 17] * 10,
68     'Low': [8, 9, 10, 11, 12] * 10,
69     'Close': [12, 11, 14, 13, 16] * 10,
70     'Volume': [100, 200, 150, 300, 250] * 10,
71     'RSI': [40, 55, 60, 45, 75] * 10
72 })
73 
74 # Tạo layout biểu đồ 3 tầng
75 fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
76                     vertical_spacing=0.03, 
77                     row_heights=[0.5, 0.2, 0.3])
78 
79 # 1. Biểu đồ nến
80 fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
81                              low=data['Low'], close=data['Close'], name="Giá"), row=1, col=1)
82 
83 # 2. Cột Volume (Xanh/Đỏ theo nến)
84 vol_colors = ['#ff4b4b' if data['Open'][i] > data['Close'][i] else '#00ff88' for i in range(len(data))]
85 fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=vol_colors, name="Khối lượng"), row=2, col=1)
86 
87 # 3. RSI Hình Sóng (Có đổ màu nền cực đẹp)
88 fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], fill='tozeroy', 
89                          line=dict(color='#00d1ff', width=2), 
90                          fillcolor='rgba(0, 209, 255, 0.15)', name="RSI Sóng"), row=3, col=1)
91 
92 fig.update_layout(height=650, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False)
93 st.plotly_chart(fig, use_container_width=True)
94 # --- KHỐI TÍN HIỆU DỰ BÁO ---
95 st.markdown("### 🎯 TÍN HIỆU CHIẾN THUẬT")
96 c1, c2, c3 = st.columns(3)
97 
98 with c1:
99     st.markdown('<button class="stButton buy-btn">🔥 NÊN BUY (MUA)</button>', unsafe_allow_html=True)
100 with c2:
101     st.markdown('<button class="stButton hold-btn">⏳ NÊN HOLD (GIỮ)</button>', unsafe_allow_html=True)
102 with c3:
103     st.markdown('<button class="stButton sell-btn">❄️ NÊN SELL (BÁN)</button>', unsafe_allow_html=True)
104 
105 # --- CHỐT FOOTER Q68 ---
106 st.markdown('<div class="q68-footer">Q68</div>', unsafe_allow_html=True)

                            
                            
