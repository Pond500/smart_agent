# smart_agent/pipeline/extractor.py

import os
import docx
from pdf2image import convert_from_path
# Import Agent สถานีที่ 2 ของเรา
from .layout_analyzer import ocr_image
import ftfy

def _handle_ocr_only_pdf_extraction(file_path):
    """
    จัดการสกัดข้อความจาก PDF ด้วย OCR เพียงอย่างเดียว
    """
    print(" -> ตรวจพบ PDF, เริ่มกระบวนการสกัดแบบ OCR-Only...")
    full_content_from_ocr = []

    try:
        images = convert_from_path(file_path)
    except Exception as e:
        print(f" -> ไม่สามารถแปลง PDF เป็นรูปภาพได้: {e}")
        return ""

    for i, image in enumerate(images):
        print(f" -> กำลัง OCR หน้าที่ {i + 1}/{len(images)}...")
        text_from_ocr = ocr_image(image)
        full_content_from_ocr.append(text_from_ocr)

    return "\n\n--- PAGE BREAK ---\n\n".join(full_content_from_ocr)


def extract_text_from_file(file_path):
    """
    ตรวจสอบนามสกุลไฟล์และเลือกวิธีสกัดข้อความที่เหมาะสม (PDF จะใช้ OCR เสมอ)
    """
    print(f"สถานีที่ 1: Agent คัดกรองกำลังทำงานกับไฟล์ {os.path.basename(file_path)}...")
    _, file_extension = os.path.splitext(file_path)

    try:
        content = ""
        if file_extension.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = ftfy.fix_text(f.read())
        elif file_extension.lower() == '.pdf':
            # *** เปลี่ยนมาเรียกใช้ฟังก์ชัน OCR-Only ***
            content = _handle_ocr_only_pdf_extraction(file_path)
        elif file_extension.lower() == '.docx':
            doc = docx.Document(file_path)
            raw_text = "\n".join([para.text for para in doc.paragraphs])
            content = ftfy.fix_text(raw_text)
        else:
            print(f" -> ไม่รองรับนามสกุลไฟล์: {file_extension}")
            return None
        return content

    except Exception as e:
        print(f" -> เกิดข้อผิดพลาดในการสกัดข้อความ: {e}")
        return None