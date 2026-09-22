import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import re
import fitz  # PyMuPDF 處理 PDF
from streamlit_cropper import st_cropper

st.set_page_config(page_title="中文寫字小幫手", page_icon="✍️", layout="centered")

st.title("🇭🇰 寫字功課好幫手")
st.markdown("> **Helper Instructions:** Upload an image or PDF, crop the target character to avoid noise, and get the stroke order.")

# 1. 快捷選擇常見生字（雙重保險）
common_chars = ["學", "校", "我", "們", "老", "師", "早", "安", "爸", "媽", "家", "人", "功", "課", "中", "文"]
selected_quick = st.selectbox("📌 快捷選擇生字 (Quick Select):", ["請選擇..."] + common_chars)

# 2. 檔案上傳（支援圖片 JPG/PNG 及 PDF）
uploaded_file = st.file_uploader("📁 上傳功課圖片或 PDF 檔案 (Upload Image or PDF)", type=["jpg", "jpeg", "png", "pdf"])

image = None

if uploaded_file is not None:
    file_type = uploaded_file.type
    try:
        if "pdf" in file_type:
            with st.spinner("📄 正在讀取 PDF 檔案..."):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                if len(doc) > 0:
                    page = doc[0]
                    pix = page.get_pixmap(dpi=200)
                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    st.success(f"✅ 成功載入 PDF（共 {len(doc)} 頁，現顯示第 1 頁）")
        else:
            image = Image.open(uploaded_file)
    except Exception as e:
        st.error(f"檔案讀取發生錯誤：{e}")

detected_chars = []

if image is not None:
    image = image.convert("RGB")
    st.markdown("### ✂️ 裁剪需要識別的文字區域 (Crop Target Character)")
    st.markdown("請在下方圖片調整框選範圍，**只框出要學的那一個字**：")
    
    try:
        # 互動式裁剪工具
        cropped_img = st_cropper(image, real_time=True, box_color='#FF4B4B', aspect_ratio=None, key="cropper")
        
        if cropped_img is not None:
            st.image(cropped_img, caption="已裁剪的目標區域", use_container_width=True)
            
            with st.spinner("🔍 正在辨識裁剪區內的文字..."):
                # 影像預處理：轉灰階 + 提高對比度
                gray_image = ImageOps.grayscale(cropped_img)
                enhancer = ImageEnhance.Contrast(gray_image)
                enhanced_image = enhancer.enhance(2.5)
                
                # 執行 Tesseract 繁體中文辨識
                raw_text = pytesseract.image_to_string(enhanced_image, lang='chi_tra')
                detected_chars = re.findall(r'[\u4e00-\u9fa5]', raw_text)
                detected_chars = list(dict.fromkeys(detected_chars)) # 去重
    except Exception as e:
        st.warning(f"⚠️ 裁剪工具載入中或發生小錯誤，您可以直接使用下方快捷選單或手動輸入。")

# 結合辨識出的字與快捷選單
final_chars = detected_chars if detected_chars else []
if selected_quick != "請選擇..." and selected_quick not in final_chars:
    final_chars.insert(0, selected_quick)

if final_chars:
    st.success(f"✅ 成功鎖定字元：{' '.join(final_chars)}")
    selected_char = st.selectbox("請選擇需要教學的字 (Select Character):", final_chars)
else:
    if uploaded_file is not None:
        st.info("💡 如果未自動認出，請直接在下方手動輸入要查的字：")
    manual_input = st.text_input("手動輸入要查詢的字：")
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
