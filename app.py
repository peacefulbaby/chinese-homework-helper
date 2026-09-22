import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import re
import fitz  # PyMuPDF 處理 PDF
from streamlit_drawable_canvas import st_canvas
import numpy as np

st.set_page_config(page_title="中文寫字小幫手", page_icon="✍️", layout="centered")

st.title("🇭🇰 寫字功課好幫手")
st.markdown("> **Helper Instructions:** Upload an image or PDF, then **draw a red box** around the target character on the canvas below.")

# 1. 常用生字快捷選單（雙重保險）
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
cropped_img = None

if image is not None:
    image = image.convert("RGB")
    orig_w, orig_h = image.size
    
    st.markdown("### ✍️ 請在下方圖片用手指畫框框住要學的字")
    st.markdown("*(Draw a rectangle box around the character)*")
    
    # 為了適應手機/iPad 畫面，將顯示寬度設定為 400 像素
    display_w = 400
    if orig_w > display_w:
        ratio = display_w / orig_w
        display_h = int(orig_h * ratio)
        img_for_canvas = image.resize((display_w, display_h))
    else:
        display_w = orig_w
        display_h = orig_h
        img_for_canvas = image
        
    # 建立互動畫布
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.2)",
        stroke_width=2,
        stroke_color="#FF0000",
        background_image=img_for_canvas,
        update_streamlit=True,
        height=display_h,
        width=display_w,
        drawing_mode="rect",
        key="canvas",
    )
    
    # 如果外傭在畫布上畫了方框
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data.get("objects", [])
        if len(objects) > 0:
            # 取得最後一個畫的方框座標
            obj = objects[-1]
            box_left = obj["left"]
            box_top = obj["top"]
            box_width = obj["width"]
            box_height = obj["height"]
            
            # 將畫布座標還原對應到原圖的高解像度座標
            scale_x = orig_w / display_w
            scale_y = orig_h / display_h
            
            orig_left = int(box_left * scale_x)
            orig_top = int(box_top * scale_y)
            orig_right = int((box_left + box_width) * scale_x)
            orig_bottom = int((box_top + box_height) * scale_y)
            
            # 限制邊界在圖片範圍內
            orig_left = max(0, orig_left)
            orig_top = max(0, orig_top)
            orig_right = min(orig_w, orig_right)
            orig_bottom = min(orig_h, orig_bottom)
            
            if orig_right > orig_left and orig_bottom > orig_top:
                cropped_img = image.crop((orig_left, orig_top, orig_right, orig_bottom))
                st.image(cropped_img, caption="🎯 已精準框選的目標區域", use_container_width=True)

# 進行 OCR 辨識
target_image = cropped_img if cropped_img is not None else image

if target_image is not None:
    with st.spinner("🔍 正在辨識文字中..."):
        try:
            gray_image = ImageOps.grayscale(target_image)
            enhancer = ImageEnhance.Contrast(gray_image)
            enhanced_image = enhancer.enhance(2.5)
            
            raw_text = pytesseract.image_to_string(enhanced_image, lang='chi_tra')
            detected_chars = re.findall(r'[\u4e00-\u9fa5]', raw_text)
            detected_chars = list(dict.fromkeys(detected_chars))
        except Exception as e:
            pass

# 結合辨識出的字與快捷選單
final_chars = detected_chars if detected_chars else []
if selected_quick != "請選擇..." and selected_quick not in final_chars:
    final_chars.insert(0, selected_quick)

if final_chars:
    st.success(f"✅ 可選字元：{' '.join(final_chars)}")
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
