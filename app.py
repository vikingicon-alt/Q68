fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='orange', width=1), name='MA20'), row=1, col=1)
    
    # Vẽ RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='magenta', width=2), name='RSI'), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    fig.update_layout(height=800, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # --- MÃ QR ---
    st.write("---")
    app_url = "https://nrynpp6caudetlbejh8appz.streamlit.app"
    qr = qrcode.make(app_url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="Quét mã QR để chia sẻ app chuyên nghiệp của anh", width=150)

else:
    st.error("Đang cập nhật dữ liệu...")

st.caption("❤️ Chúc Anh Yêu đầu tư thắng lợi và ngủ ngon!")
