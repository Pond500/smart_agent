import os
import json
import re
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
# ตรวจสอบและ import OpenAILike
try:
    from llama_index.llms.openai_like import OpenAILike
except ImportError:
    print("คำเตือน: ไม่พบไลบรารี llama_index, สร้าง Class OpenAILike จำลอง")
    class OpenAILike:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        def complete(self, prompt):
            class MockResponse:
                def __init__(self):
                    self.text = '```json\n{"document_type": "คู่มือ (จำลอง)", "main_topics": ["จำลอง"], "summary": "สรุปย่อจำลอง", "target_audience": "ทั่วไป (จำลอง)"}\n```'
            return MockResponse()

# --- 1. ตั้งค่า LLM ---
LLM_MODEL_NAME = "ptm-gpt-oss-120b"
LLM_API_BASE = "http://52.195.227.79/llm-large-inference/v1"
LLM_API_KEY = "not-used"

llm = OpenAILike(
    model=LLM_MODEL_NAME,
    api_base=LLM_API_BASE,
    api_key=LLM_API_KEY,
    temperature=0.1,
    is_chat_model=True,
)

# --- 2. Prompt Template ---
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


# --- 3. ฟังก์ชัน Agent บรรณารักษ์ ---
def generate_metadata(document_content):
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

# --- 4. ฟังก์ชัน Agent แบ่งข้อมูล ---
def create_smart_chunks(document_content, generated_metadata, document_title):
    print("สถานีที่ 4: Agent แบ่งข้อมูลกำลังทำงาน...")
    separators = ["\nบทที่ ", "\nส่วนที่ ", "\nข้อ ", "\n\n", "\n", " "]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=separators
    )
    chunks_text = text_splitter.split_text(document_content)
    
    final_chunks = []
    for i, chunk_content in enumerate(chunks_text):
        chunk_metadata = {
            "document_title": document_title,
            "chunk_number": i + 1,
            **generated_metadata
        }
        relevant_headers = re.findall(r'(บทที่ .*|ส่วนที่ .*|ข้อ .*)', document_content[:document_content.find(chunk_content)])
        context_path = " > ".join(relevant_headers[-2:]) if relevant_headers else "บทนำ"
        chunk_metadata["context_path"] = context_path
        final_chunks.append({"content": chunk_content, "metadata": chunk_metadata})
    print(f" -> แบ่งเอกสารออกเป็น {len(final_chunks)} ชิ้น (Chunks) สำเร็จ!")
    return final_chunks

# --- 5. ฟังก์ชันจัดการโฟลเดอร์ (เวอร์ชันอัปเกรด) ---
def process_folder_recursively(root_folder_path):
    all_processed_chunks = []
    
    # *** ใช้ os.walk เพื่อวนซ้ำในทุกโฟลเดอร์ย่อย ***
    for dirpath, _, filenames in os.walk(root_folder_path):
        for filename in filenames:
            if filename.endswith(".txt"):
                file_path = os.path.join(dirpath, filename)
                print(f"\n===== เริ่มประมวลผลไฟล์: {file_path} =====")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        full_content = f.read()
                    
                    metadata = generate_metadata(full_content)
                    if metadata:
                        chunks = create_smart_chunks(full_content, metadata, filename)
                        all_processed_chunks.extend(chunks)
                    else:
                        print(f"ข้ามไฟล์ {filename} เนื่องจากไม่สามารถสร้าง Metadata ได้")

                except Exception as e:
                    print(f"เกิดข้อผิดพลาดร้ายแรงกับไฟล์ {filename}: {e}")
    
    return all_processed_chunks

# --- 6. ส่วนที่เรียกใช้งานหลัก ---
if __name__ == "__main__":
    # !!! เปลี่ยน path ตรงนี้ให้เป็นโฟลเดอร์หลักของคุณ !!!
    target_root_folder = r"D:\smart_agent\ไฟล์ พ.ร.บ. 51 กฎหมาย และที่เกี่ยวข้องกับการแต่งตั้ง"
    
    if not os.path.isdir(target_root_folder):
        print(f"ไม่พบโฟลเดอร์: {target_root_folder}")
        print("กรุณาสร้างโฟลเดอร์และนำเอกสารไปใส่ หรือแก้ไข path ในโค้ดให้ถูกต้อง")
    else:
        final_data = process_folder_recursively(target_root_folder)
        
        if final_data:
            output_file = "processed_chunks.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)
            print(f"\n===== การประมวลผลเสร็จสิ้น! =====")
            print(f"ผลลัพธ์ทั้งหมดถูกบันทึกในไฟล์: {output_file}")
        else:
            print("\nไม่พบไฟล์ .txt ที่จะประมวลผลในโฟลเดอร์ที่ระบุ")