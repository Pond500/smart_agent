# smart_agent/test_ocr.py
import os
from openai import OpenAI
from typhoon_ocr.ocr_utils import image_to_base64png, get_anchor_text_from_image

# --- ตั้งค่า ---
API_BASE_URL = "http://3.113.24.61/typhoon-ocr-service/v1"
API_KEY = "not-used"
IMAGE_PATH = "D:\smart_agent\Screenshot 2025-09-18 110646.png"

def final_ocr_test():
    print(f"กำลังทดสอบด้วยวิธีที่ถูกต้องตามสคริปต์ของคุณ...")
    print(f"Base URL: {API_BASE_URL}")

    try:
        # 1. สร้าง Client แบบเดียวกับโค้ดของคุณ
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE_URL,
            timeout=60.0,
        )

        # 2. เตรียมข้อมูลรูปภาพ
        from PIL import Image
        image = Image.open(IMAGE_PATH)
        image_base64 = image_to_base64png(image)

        # 3. สร้าง Payload แบบเดียวกับโค้ดของคุณ
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Return the full text exactly as it appears."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
            ],
        }]

        # 4. เรียก API ไปยัง /chat/completions
        print("กำลังส่งคำขอไปยัง /chat/completions...")
        response = client.chat.completions.create(
            model="typhoon-ocr-preview",
            messages=messages,
            max_tokens=4096,
        )

        raw_output = response.choices[0].message.content

        print("\n--- ผลการทดสอบ ---")
        print("✅✅✅ สำเร็จ! ✅✅✅")
        print("\nข้อความที่สกัดได้:")
        print(raw_output)

    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์รูปภาพ '{IMAGE_PATH}'")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    # ติดตั้ง typhoon-ocr-utils ก่อน ถ้ายังไม่มี
    try:
        import typhoon_ocr
    except ImportError:
        print("กำลังติดตั้ง typhoon_ocr_utils ที่จำเป็น...")
        os.system('pip install typhoon-ocr-utils')
        from typhoon_ocr.ocr_utils import image_to_base64png, get_anchor_text_from_image

    if not os.path.exists(IMAGE_PATH):
         print(f"ไม่พบไฟล์รูปภาพ '{IMAGE_PATH}' กรุณาถ่ายภาพหน้าจอ PDF แล้วบันทึกเป็นชื่อนี้ก่อนรัน")
    else:
        final_ocr_test()