# smart_agent/pipeline/proofreader.py
import re
import ftfy
from langchain.prompts import PromptTemplate
import pandas as pd
import io

# พิมพ์เขียว "Prompt" ที่รัดกุมที่สุดสำหรับ LLM
proofread_prompt_template = """คุณคือบรรณาธิการตรวจทานอักษรที่มีความแม่นยำสูงสุด ภารกิจของคุณมีเพียงหนึ่งเดียวคือการแก้ไขข้อความที่ผิดเพี้ยนจากการสแกน (OCR) หรือการสะกดผิดเล็กน้อย ให้กลับมาเป็นภาษาไทยที่ถูกต้อง

**กฎเหล็กที่คุณต้องปฏิบัติตาม:**
1.  **ห้ามสรุปความ:** ห้ามย่อหรือตัดทอนเนื้อหาใดๆ ทั้งสิ้น
2.  **ห้ามเพิ่มเติม:** ห้ามเพิ่มคำ, ประโยค, หรือข้อมูลที่ไม่มีอยู่ในต้นฉบับ
3.  **ห้ามลบเนื้อหา:** หากไม่แน่ใจ ให้คงข้อความเดิมไว้ ห้ามลบประโยคที่ไม่เข้าใจทิ้ง
4.  **แก้ไขเฉพาะที่ผิด:** จงแก้ไขเฉพาะคำที่สะกดผิด, สระหรือวรรณยุกต์เพี้ยน, หรือตัวอักษรที่ผิดพลาดจากการ OCR อย่างชัดเจนเท่านั้น (เช่น "ใu" แก้เป็น "ใน", "รัฐบาa" แก้เป็น "รัฐบาล")
5.  **รักษารูปแบบเดิม:** คงการขึ้นบรรทัดใหม่และย่อหน้าของเอกสารต้นฉบับไว้ให้เหมือนเดิมที่สุด

**จงส่งคืนเฉพาะข้อความที่พิสูจน์อักษรแล้วเท่านั้น โดยไม่มีคำอธิบายอื่นใดเพิ่มเติม**

**ข้อความต้นฉบับ:**
"{text_to_proofread}"
"""
PROMPT = PromptTemplate.from_template(proofread_prompt_template)

def convert_html_tables_to_markdown(text: str) -> str:
    """
    ค้นหาตาราง HTML ทั้งหมดในข้อความและแปลงเป็น Markdown
    """
    tables = list(re.finditer(r'(<table.*?>.*?</table>)', text, re.DOTALL))
    if not tables:
        return text

    print(f" -> ตรวจพบ {len(tables)} ตาราง, กำลังแปลงเป็น Markdown...")
    for table_match in reversed(tables):
        html_table_str = table_match.group(1)
        try:
            df_list = pd.read_html(io.StringIO(html_table_str))
            if df_list:
                df = df_list[0]
                markdown_table = df.to_markdown(index=False)
                start, end = table_match.span()
                text = text[:start] + "\n\n" + markdown_table + "\n\n" + text[end:]
        except Exception as e:
            print(f" -> ไม่สามารถแปลงตารางได้, ข้ามไป... Error: {e}")
            pass
    return text

def proofread_text(text: str, llm) -> str:
    """
    สถานีพิสูจน์อักษร: ทำความสะอาดและแก้ไขข้อความให้สมบูรณ์แบบ
    """
    print("สถานีสุดท้าย: Agent พิสูจน์อักษรกำลังทำงาน...")
    if not text or not text.strip():
        return ""

    # --- ขั้นตอนที่ 1: การซ่อมแซมและปรับมาตรฐาน ---
    # 1.1 ซ่อม "ภาษาต่างดาว" (Mojibake)
    cleaned_text = ftfy.fix_text(text)
    
    # --- ขั้นตอนใหม่: แปลงตาราง HTML เป็น Markdown ---
    cleaned_text = convert_html_tables_to_markdown(cleaned_text)

    # 1.2 จัดการสัญลักษณ์รูปภาพ
    cleaned_text = re.sub(r'!\[.*?\]\(https?://i\.imgur\.com/.*?\)', '[รูปภาพประกอบ]', cleaned_text)

    # 1.3 ลบสิ่งที่ไม่จำเป็น
    cleaned_text = cleaned_text.replace('--- PAGE BREAK ---', '')
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text) # ลดการขึ้นบรรทัดใหม่ที่มากเกินไป

    # --- ขั้นตอนที่ 3: การพิสูจน์อักษรด้วย LLM ---
    # (ส่วนนี้ยังคงเหมือนเดิม ไม่มีการเปลี่ยนแปลง)
    print(" -> กำลังส่งข้อความให้ LLM ช่วยพิสูจน์อักษร...")
    final_proofread_text = []
    text_parts = [cleaned_text[i:i+4000] for i in range(0, len(cleaned_text), 4000)]

    for part in text_parts:
        formatted_prompt = PROMPT.format(text_to_proofread=part)
        response = llm.complete(formatted_prompt)
        final_proofread_text.append(response.text)

    print(" -> พิสูจน์อักษรสำเร็จ!")
    return "".join(final_proofread_text)