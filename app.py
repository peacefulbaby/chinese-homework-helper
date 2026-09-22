import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import re

st.set_page_config(page_title="中文寫字小幫手", page_icon="✍️", layout="centered")

st.title("🇭🇰 寫字功課好幫手")
st.markdown("> **Helper Instructions:** Take a picture or upload an image from your device gallery.")

# 1. 快捷選擇常見生字（隨時可以直接點選）
st.markdown("### 📌 快捷選擇生字 (Quick Select)")
common_chars = ["學", "校", "我", "們", "老", "師", "早", "安", "爸", "媽", "家", "人", "功", "課", "中", "文"]
selected_quick = st.selectbox("如果認唔到，可直接喺呢度揀：", ["請選擇..."] + common_chars)

# 2. 上傳方式分頁（手機/iPad 介面最清晰）
tab1, tab2 = st.tabs(["📸 直接拍照 (Take Photo)", "📁 從相簿上傳 (Upload Image)"])

image_file = None

with tab1:
    camera_file = st.camera_input("請拍攝功課上的生字")
    if camera_file is not None:
        image_file = camera_file

with tab2:
    uploaded_file = st.file_uploader("請選擇手機相簿中的圖片檔案", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image_file = uploaded_file

detected_chars = []
if image_file is not None:
    image = Image.open(image_file)
    st.image(image, caption="已載入的功課相片", use_container_width=True)
    
    with st.spinner("🔍 正在進行影像優化與文字辨識..."):
        try:
            # 影像預處理：轉灰階 + 提高對比度
            gray_image = ImageOps.grayscale(image)
            enhancer = ImageEnhance.Contrast(gray_image)
            enhanced_image = enhancer.enhance(2.5)
            
            # 執行 Tesseract 繁體中文辨識
            raw_text = pytesseract.image_to_string(enhanced_image, lang='chi_tra')
            detected_chars = re.findall(r'[\u4e00-\u9fa5]', raw_text)
            detected_chars = list(dict.fromkeys(detected_chars)) # 去重
        except Exception as e:
            st.error(f"辨識發生錯誤：{e}")

# 組合所有可用的字（辨識到的字 + 快捷選到的字）
final_chars = detected_chars if detected_chars else []
if selected_quick != "請選擇..." and selected_quick not in final_chars:
    final_chars.insert(0, selected_quick)

if final_chars:
    st.success(f"✅ 可選字元：{' '.join(final_chars)}")
    selected_char = st.selectbox("請選擇需要教學的字 (Select Character):", final_chars)
else:
    if image_file is not None:
        st.warning("⚠️ 相片未能自動辨識出文字。")
    manual_input = st.text_input("或者直接手動輸入要查詢的字：")
    selected_char = manual_input if manual_input else None

# 3. 顯示教學與筆順區塊
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
