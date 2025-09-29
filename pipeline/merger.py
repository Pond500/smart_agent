# smart_agent/pipeline/merger.py

import ftfy
from Levenshtein import ratio

def _is_quality_text(text: str) -> bool:
    """
    ประเมินคุณภาพของข้อความ: ถ้ามี "ภาษาต่างดาว" เยอะจะถือว่าคุณภาพต่ำ
    """
    if not text or len(text.strip()) < 20: # ถ้าสั้นไป ถือว่าไม่ดี
        return False
    # ลองซ่อม ถ้าซ่อมแล้วเปลี่ยนไปเยอะ แสดงว่าเดิมเป็นภาษาต่างดาว
    fixed_text = ftfy.fix_text(text)
    if ratio(text, fixed_text) < 0.8: # ถ้าความคล้ายคลึงน้อยกว่า 80%
        return False
    return True

def merge_texts(text_from_layer: str, text_from_ocr: str) -> str:
    """
    Agent บรรณาธิการใหญ่: ผสานข้อมูลจาก Text Layer และ OCR อย่างชาญฉลาด
    """
    print(" -> Agent บรรณาธิการใหญ่กำลังทำงาน...")
    
    # 1. ทำความสะอาดข้อมูลทั้งสองแหล่งก่อน
    clean_layer_text = ftfy.fix_text(text_from_layer)
    clean_ocr_text = ftfy.fix_text(text_from_ocr)

    # 2. ประเมินคุณภาพของ Text Layer
    if not _is_quality_text(clean_layer_text):
        print(" -> Text Layer คุณภาพต่ำ, เลือกใช้ OCR")
        return clean_ocr_text

    # 3. ถ้า Text Layer คุณภาพดี: ทำการผสานข้อมูลอัจฉริยะ
    print(" -> Text Layer คุณภาพดี, เริ่มการผสานข้อมูล...")
    
    # สร้าง set ของประโยคจาก OCR เพื่อการค้นหาที่รวดเร็ว
    ocr_sentences = set(sent.strip() for sent in clean_ocr_text.split('\n') if sent.strip())
    
    # วนลูปในประโยคของ Text Layer เพื่อหาประโยคที่หายไปใน OCR
    final_text_parts = []
    for layer_sent in clean_layer_text.split('\n'):
        layer_sent_strip = layer_sent.strip()
        if layer_sent_strip:
            # ถ้าประโยคจาก Text Layer ไม่ได้อยู่ใน OCR ให้เพิ่มเข้าไป
            if layer_sent_strip not in ocr_sentences:
                final_text_parts.append(layer_sent_strip)

    # นำข้อความทั้งหมดมารวมกัน (OCR เป็นฐาน + ส่วนที่ขาดจาก Text Layer)
    # และใช้ set เพื่อขจัดความซ้ำซ้อนสุดท้าย
    combined_text = clean_ocr_text + "\n" + "\n".join(final_text_parts)
    
    # ใช้ dictionary key เพื่อขจัดความซ้ำซ้อนและรักษลำดับ
    lines = combined_text.split('\n')
    unique_lines = list(dict.fromkeys(lines))
    
    return "\n".join(unique_lines)