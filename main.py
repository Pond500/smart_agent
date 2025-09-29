# smart_agent/main.py

import os
import json
# Import การตั้งค่าและ Agent ของเรา
import config
from pipeline.extractor import extract_text_from_file
from pipeline.proofreader import proofread_text
from pipeline.librarian import generate_metadata
from pipeline.chunker import create_smart_chunks
# Import LLM
try:
    from llama_index.llms.openai_like import OpenAILike
except ImportError:
    print("คำเตือน: ไม่พบไลบรารี llama_index, สร้าง Class OpenAILike จำลอง")
    class OpenAILike:
        def __init__(self, **kwargs): self.kwargs = kwargs
        def complete(self, prompt):
            class MockResponse:
                def __init__(self): self.text = '{"document_type": "จำลอง", "main_topics": [], "summary": "", "target_audience": ""}'
            return MockResponse()

def run_pipeline():
    llm = OpenAILike(
        model=config.LLM_MODEL_NAME,
        api_base=config.LLM_API_BASE,
        api_key=config.LLM_API_KEY,
        temperature=0.1,
        is_chat_model=True,
    )

    all_processed_chunks = []
    root_folder_path = config.DATA_ROOT_FOLDER

    for dirpath, _, filenames in os.walk(root_folder_path):
        for filename in filenames:
            if filename.lower().endswith(('.txt', '.pdf', '.docx')):
                file_path = os.path.join(dirpath, filename)
                print(f"\n===== เริ่มไปป์ไลน์สำหรับไฟล์: {filename} =====")

                try:
                    content = extract_text_from_file(file_path)
                    if not content or not content.strip():
                        print(f"ข้ามไฟล์ {filename} เนื่องจากไม่มีเนื้อหา")
                        continue

                    proofread_content = proofread_text(content, llm)
                    if not proofread_content or not proofread_content.strip():
                         print(f"ข้ามไฟล์ {filename} เนื่องจากผลการพิสูจน์อักษรว่างเปล่า")
                         continue

                    # --- ส่วนที่เพิ่มเข้ามา ---
                    # สร้าง path สำหรับบันทึกไฟล์ .txt
                    txt_output_filename = os.path.splitext(filename)[0] + '.txt'
                    txt_output_path = os.path.join(config.TXT_OUTPUT_FOLDER, txt_output_filename)

                    # บันทึกเนื้อหาที่พิสูจน์อักษรแล้ว
                    with open(txt_output_path, 'w', encoding='utf-8') as f:
                        f.write(proofread_content)
                    print(f" -> บันทึกผลลัพธ์ Text ฉบับเต็มที่: {txt_output_path}")
                    # -----------------------

                    metadata = generate_metadata(proofread_content, llm)
                    if not metadata:
                        print(f"ข้ามไฟล์ {filename} เนื่องจากสร้าง Metadata ไม่สำเร็จ")
                        continue

                    chunks = create_smart_chunks(proofread_content, metadata, filename)
                    all_processed_chunks.extend(chunks)

                except Exception as e:
                    print(f"เกิดข้อผิดพลาดร้ายแรงกับไฟล์ {filename}: {e}")

    return all_processed_chunks

if __name__ == "__main__":
    # --- เพิ่มการตั้งค่า path สำหรับไฟล์ text ---
    # ต้องสร้างโฟลเดอร์สำหรับเก็บ text file ก่อน
    os.makedirs(config.TXT_OUTPUT_FOLDER, exist_ok=True)
    # ----------------------------------------

    if not os.path.isdir(config.DATA_ROOT_FOLDER):
        print(f"ไม่พบโฟลเดอร์ข้อมูล: {config.DATA_ROOT_FOLDER}")
    else:
        final_data = run_pipeline()

        if final_data:
            with open(config.JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)
            print(f"\n===== ไปป์ไลน์เสร็จสิ้น! =====")
            print(f"ผลลัพธ์ Chunks ทั้งหมดถูกบันทึกในไฟล์: {config.JSON_OUTPUT_FILE}")
            print(f"ผลลัพธ์ Text ของแต่ละไฟล์ถูกบันทึกในโฟลเดอร์: {config.TXT_OUTPUT_FOLDER}")
        else:
            print("\nไม่พบไฟล์ที่รองรับให้ประมวลผล")


