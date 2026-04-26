import streamlit as st

# 1. CẤU HÌNH ICON Q68 VÀ CHẾ ĐỘ TRÀN VIỀN
icon_q68 = "https://i.imgur.com/83pZpGv.png"
st.set_page_config(page_title="Q68-A1", layout="wide", page_icon="🐢")

st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{icon_q68}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    </head>
    <style>
        /* Ẩn các thành phần thừa */
        header {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* LỆNH XÓA VƯƠNG MIỆN ĐỎ Ở GÓC DƯỚI */
        div[class*="viewerBadge"] {{display: none !important;}}
        button[title="View source on GitHub"] {{display: none !important;}}
        
        .main {{background-color: #080a0c;}}
    </style>
""", unsafe_allow_html=True)

# 2. HIỂN THỊ NỘI DUNG TẠM THỜI
st.markdown("<h1 style='text-align: center; color: gold;'>🐢 Q68 - A1 SYSTEM</h1>", unsafe_allow_html=True)
st.write("---")
st.success("GitHub đã ổn định! Anh hãy nhấn Chia sẻ -> Thêm vào MH chính để thấy Con Rùa Vàng.")
