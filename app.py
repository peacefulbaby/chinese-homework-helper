import streamlit as st
from PIL import Image

st.set_page_config(page_title="中文寫字小幫手", page_icon="✍️", layout="centered")

st.title("🇭🇰 寫字功課好幫手")
st.markdown("> **Helper Instructions:** Take a picture of the homework, select the character, and follow the stroke order.")

# 手機端直接呼叫相機
image_file = st.camera_input("📸 請拍攝功課上的生字 (Take a photo)")

if image_file is not None:
    st.success("相片已成功上傳！")
    
    # 模擬辨識出的生字
    chars = ["學", "校", "功", "課"]
    selected = st.selectbox("請選擇要學習的字 (Select character):", chars)
    
    if selected:
        st.divider()
        st.subheader(f"📖 學習字體：{selected}")
        
        # 模擬筆順與發音區塊
        st.markdown("### 1. 筆順動畫 (Stroke Order)")
        st.info("▶️ [點擊這裡觀看香港小學習字表標準筆順動畫]")
        
        st.markdown("### 2. 語音與詞語 (Pronunciation)")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔊 廣東話發音"):
                st.toast("播放廣東話：Hok6")
        with col2:
            if st.button("🔊 普通話發音"):
                st.toast("播放普通話：Xué")
                
        st.markdown("""
        > 💡 **Helper Tip for Child:**
        > 1. Watch the stroke order first.
        > 2. Write slowly and check pencil grip.
        """)
