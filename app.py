import streamlit as st

# 1. ÉP HỆ THỐNG HIỆN ICON CON RÙA VÀ TRÀN VIỀN
icon_q68 = "https://i.imgur.com/83pZpGv.png"

st.set_page_config(page_title="A1 SYSTEM", layout="wide", page_icon="🐢")

st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{icon_q68}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    </head>
    <style>
        header {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .main {{background-color: #080a0c;}}
    </style>
""", unsafe_allow_html=True)

# 2. NỘI DUNG HIỂN THỊ CHÍNH
st.markdown("<h1 style='text-align: center; color: gold;'>🐢 Q68 - A1 SYSTEM</h1>", unsafe_allow_html=True)
st.write("---")
st.success("Hệ thống A1 đã sẵn sàng. Anh hãy thử thêm vào Màn hình chính ngay nhé!")
