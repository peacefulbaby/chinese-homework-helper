import streamlit as st
from PIL import Image
import pytesseract
import re

st.set_page_config(page_title="中文寫字小幫手", page_icon="✍️", layout="centered")

st.title("🇭🇰 寫字功課好幫手")
st.markdown("> **Helper Instructions:** Take a picture of the homework, and the app will automatically detect the Chinese characters.")

# 手機端直接呼叫相機拍照
image_file = st.camera_input("📸 請拍攝功課上的生字 (Take a photo)")

if image_file is not None:
    image = Image.open(image_file)
    st.image(image, caption="已上傳的功課相片", use_container_width=True)
    
    with st.spinner("🔍 正在辨識相片中的中文字... (Recognizing characters...)"):
        try:
            # 使用 Tesseract 辨識繁體中文
            raw_text = pytesseract.image_to_string(image, lang='chi_tra')
            # 過濾出相片中的中文字符
            detected_chars = re.findall(r'[\u4e00-\u9fa5]', raw_text)
            # 去重但保持先後順序
            detected_chars = list(dict.fromkeys(detected_chars))
        except Exception as e:
            detected_chars = []
            st.error(f"辨識發生錯誤：{e}")

    # 如果成功認出字
    if detected_chars:
        st.success(f"✅ 成功辨識出以下字元：{' '.join(detected_chars)}")
        selected_char = st.selectbox("請選擇需要教學的字 (Select Character):", detected_chars)
    else:
        st.warning("⚠️ 未能自動辨識出清晰的中文字（手寫字有時較難辨認），請在下方手動輸入：")
        manual_input = st.text_input("手動輸入要查詢的字：")
        selected_char = manual_input if manual_input else None

    if selected_char:
        st.divider()
        st.subheader(f"📖 生字詳解：【 {selected_char} 】")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**香港小學習字表規範**")
            st.write("• 標準筆順與結構")
            st.markdown("[🔗 查閱《香港小學習字表》](https://www.edbchinese.hk/lexlist_ch/)")
            
        with col2:
            st.markdown("**外傭指導提示 (Helper Guide)**")
            st.write("🗣️ 請依照香港標準發音教導小朋友。")
            
        st.markdown("""
        > 💡 **Helper Tip for Child:**
        > 1. Look at the correct stroke order.
        > 2. Write slowly, one stroke at a time.
        """)
