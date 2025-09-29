# smart_agent/pipeline/librarian.py

import json
import re
from langchain.prompts import PromptTemplate

prompt_template_str = """คุณคือบรรณารักษ์ผู้เชี่ยวชาญด้านเอกสารราชการไทย หน้าที่ของคุณคืออ่านเนื้อหาของเอกสารต่อไปนี้ แล้วสร้าง Metadata ที่เป็นประโยชน์ในรูปแบบ JSON เท่านั้น

**เนื้อหาเอกสาร:**
"{document_text}"

**จงสร้างผลลัพธ์ในรูปแบบ JSON โดยมีฟิลด์ดังต่อไปนี้:**
- "document_type": (เลือกจาก: "คู่มือ", "ระเบียบ", "แนวคำวินิจฉัย", "ประกาศ", "คำถาม-คำตอบ", "กฎหมาย", "อื่นๆ")
- "main_topics": (ลิสต์ของ Keyword ที่เป็นหัวใจของเรื่อง 3-5 คำ)
- "summary": (สรุปย่อความยาว 2-3 ประโยค)
- "target_audience": (เลือกจาก: "ประชาชน", "เจ้าหน้าที่", "นิติบุคคล", "ทั่วไป")
"""
PROMPT = PromptTemplate.from_template(prompt_template_str)

def generate_metadata(document_content, llm):
    print("สถานีที่ 3: Agent บรรณารักษ์กำลังทำงาน...")
    formatted_prompt = PROMPT.format(document_text=document_content[:8000])
    response = llm.complete(formatted_prompt)
    raw_text = response.text
    try:
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            json_string = match.group(0)
            metadata = json.loads(json_string)
            print(" -> สร้าง Metadata สำเร็จ!")
            return metadata
        else:
            return json.loads(raw_text)
    except Exception as e:
        print(f" -> เกิดข้อผิดพลาดในการแปลง Metadata: {e}")
        return None