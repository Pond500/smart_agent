# smart_agent/pipeline/librarian.py

import json
import re
from langchain.prompts import PromptTemplate

# --- อัปเกรด Prompt Template ให้ฉลาดและรัดกุมขึ้น ---
prompt_template_str = """คุณคือบรรณารักษ์ผู้เชี่ยวชาญด้านเอกสารราชการไทย หน้าที่ของคุณคืออ่านเนื้อหาของเอกสารต่อไปนี้ แล้วสร้าง Metadata ที่เป็นประโยชน์และครอบคลุมที่สุดในรูปแบบ JSON เท่านั้น

**เนื้อหาเอกสาร:**
"{document_text}"

**จงสร้างผลลัพธ์ในรูปแบบ JSON ที่มีโครงสร้างดังนี้เท่านั้น โดยปฏิบัติตามกฎอย่างเคร่งครัด:**
- "document_type": (เลือกจาก: "คู่มือ", "ระเบียบ", "แนวคำวินิจฉัย", "ประกาศ", "คำถาม-คำตอบ", "กฎหมาย", "อื่นๆ")
- "main_topics": (ลิสต์ของ Keyword ที่เป็นหัวใจของ "ทั้งเอกสาร" 3-5 คำ)
- "summary": (สรุปย่อภาพรวมของ "ทั้งเอกสาร" ความยาว 2-3 ประโยค)
- "target_audience": (เลือกจาก: "ประชาชน", "เจ้าหน้าที่", "นิติบุคคล", "ทั่วไป")
- "publication_date": (ค้นหา "วันที่ประกาศใช้เอกสาร" จากเนื้อหา แล้วตอบเป็นรูปแบบ "YYYY-MM-DD" เท่านั้น หากไม่พบจริงๆ ให้เป็น null)
- "references_docs": (ค้นหา "หนังสือที่อ้างถึง" หรือ "คำสั่งที่" จากเนื้อหา และดึงเฉพาะ "เลขที่หนังสือ" เช่น "นร ๑๐๐๔/ว ๒๔" หรือ "674/2490" มาเป็นลิสต์ของข้อความ **ห้ามนำปี พ.ศ. มาใส่เด็ดขาด** หากไม่พบให้ออกเป็นลิสต์ว่าง [])
"""
PROMPT = PromptTemplate.from_template(prompt_template_str)

def generate_metadata(document_content, llm):
    print("สถานีที่ 3: Agent บรรณารักษ์ (เวอร์ชันอัปเกรด) กำลังทำงาน...")
    formatted_prompt = PROMPT.format(document_text=document_content[:8000])
    response = llm.complete(formatted_prompt)
    raw_text = response.text
    try:
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            json_string = match.group(0)
            metadata = json.loads(json_string)
            print(" -> สร้าง Metadata ที่ทรงพลังสำเร็จ!")
            return metadata
        else:
            return json.loads(raw_text)
    except Exception as e:
        print(f" -> เกิดข้อผิดพลาดในการแปลง Metadata: {e}")
        return None