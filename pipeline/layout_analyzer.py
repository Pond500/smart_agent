# smart_agent/pipeline/layout_analyzer.py

from openai import OpenAI
from typhoon_ocr.ocr_utils import image_to_base64png
import time
import re

# --- การตั้งค่า OCR Service ---
API_BASE_URL = "http://3.113.24.61/typhoon-ocr-service/v1"
API_KEY = "EMPTY"

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL,
    timeout=-360.0,
    max_retries=2,
)

def ocr_image(image_object):
    """
    รับ Object รูปภาพ แล้วส่งไปให้ OCR service เพื่อสกัดข้อความ
    (เวอร์ชันนี้จะใช้ความสามารถ retry ของ library โดยตรง)
    """
    try:
        image_base64 = image_to_base64png(image_object)

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Return the markdown representation of this document."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
            ],
        }]

        response = client.chat.completions.create(
            model="typhoon-ocr-preview",
            messages=messages,
            max_tokens=4096,
        )

        raw_output = response.choices[0].message.content

        match = re.search(r'\{\s*"natural_text":\s*"(.*)"\s*\}', raw_output, re.DOTALL)
        if match:
            cleaned_text = match.group(1).encode('utf-8').decode('unicode_escape')
            return cleaned_text
        else:
            return raw_output

    except Exception as e:
        print(f" -> เกิดข้อผิดพลาดร้ายแรงในการเรียก OCR API หลังจากลองใหม่แล้ว: {e}")
        return "" # คืนค่าว่างถ้าล้มเหลวทุกครั้ง