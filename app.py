import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import re
import fitz  # PyMuPDF 處理 PDF
from streamlit_drawable_canvas import st_canvas
import numpy as np

st.set_page_config(page_title="中文寫字小幫手", page_icon="✍️", layout="centered")

st.title("🇭🇰 寫字功課好幫手")
st.markdown("> **Helper Instructions:** Upload/draw a box to select a character, and the stroke animation and pronunciation will appear directly below.")

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
    
    display_w = 400
    if orig_w > display_w:
        ratio = display_w / orig_w
        display_h = int(orig_h * ratio)
        img_for_canvas = image.resize((display_w, display_h))
    else:
        display_w = orig_w
        display_h = orig_h
        img_for_canvas = image
        
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
    
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data.get("objects", [])
        if len(objects) > 0:
            obj = objects[-1]
            box_left = obj["left"]
            box_top = obj["top"]
            box_width = obj["width"]
            box_height = obj["height"]
            
            scale_x = orig_w / display_w
            scale_y = orig_h / display_h
            
            orig_left = int(box_left * scale_x)
            orig_top = int(box_top * scale_y)
            orig_right = int((box_left + box_width) * scale_x)
            orig_bottom = int((box_top + box_height) * scale_y)
            
            orig_left = max(0, orig_left)
            orig_top = max(0, orig_top)
            orig_right = min(orig_w, orig_right)
            orig_bottom = min(orig_h, orig_bottom)
            
            if orig_right > orig_left and orig_bottom > orig_top:
                cropped_img = image.crop((orig_left, orig_top, orig_right, orig_bottom))
                st.image(cropped_img, caption="🎯 已精準框選的目標區域", use_container_width=True)

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

# 3. 直接在同一個版面顯示「動態筆順動畫」與「發音按鈕」
if selected_char:
    st.divider()
    st.subheader(f"📖 生字教學：【 {selected_char} 】")
    
    # 利用 HTML + JavaScript 嵌入筆順動畫與語音合成
    stroke_html = f"""
    <div style="text-align: center; font-family: sans-serif; background: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <p style="color: #666; font-size: 14px; margin-bottom: 8px;"><b>Stroke Order Animation / 筆順動畫</b></p>
        
        <!-- 筆順畫布 -->
        <div id="character-target" style="width: 160px; height: 160px; margin: 0 auto; background: #fafafa; border: 2px dashed #ccc; border-radius: 10px;"></div>
        
        <div style="margin-top: 12px;">
            <button onclick="writer.animateCharacter()" style="padding: 8px 14px; background: #FF4B4B; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px;">▶️ 播放筆順</button>
            <button onclick="writer.loopCharacterSequence()" style="padding: 8px 14px; background: #4B79FF; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; margin-left: 6px;">🔁 循環播放</button>
        </div>
        
        <p style="color: #666; font-size: 14px; margin-top: 20px; margin-bottom: 8px;"><b>Pronunciation / 語音朗讀</b></p>
        <div>
            <button onclick="speakWord('{selected_char}', 'zh-HK')" style="padding: 8px 14px; background: #2e7d32; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px;">🔊 廣東話發音</button>
            <button onclick="speakWord('{selected_char}', 'zh-CN')" style="padding: 8px 14px; background: #1565c0; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; margin-left: 6px;">🔊 普通話發音</button>
        </div>
    </div>

    <!-- 載入開源筆順繪製庫 Hanzi Writer -->
    <script src="https://cdn.jsdelivr.net/npm/hanzi-writer@3.5/dist/hanzi-writer.min.js"></script>
    <script>
        var writer = HanziWriter.create('character-target', '{selected_char}', {{
            width: 160,
            height: 160,
            padding: 8,
            showOutline: true,
            strokeAnimationSpeed: 1,
            delayBetweenStrokes: 400,
            strokeColor: '#222222',
            radicalColor: '#168F16'
        }});
        
        function speakWord(text, lang) {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel(); // 停止先前的發音
                var utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = lang;
                utterance.rate = 0.8; // 稍微放慢速度，方便小朋友跟讀
                window.speechSynthesis.speak(utterance);
            }} else {{
                alert('抱歉，此瀏覽器不支援語音朗讀功能。');
            }}
        }}
    </script>
    """
    
    # 渲染至 Streamlit 畫面中
    components.html(stroke_html, height=350)
    
    st.markdown("""
    > 💡 **Helper Tip for Child:**
    > 1. Click **"播放筆順"** to watch how the character is written stroke by stroke.
    > 2. Click **"廣東話發音"** to listen to the correct Cantonese pronunciation and guide the child to read along.
    """)
