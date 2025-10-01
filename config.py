# smart_agent/config.py

# --- การตั้งค่า LLM ---
LLM_MODEL_NAME = "ptm-gpt-oss-120b"
LLM_API_BASE = "http://3.113.24.61/llm-large-inference/v1"
LLM_API_KEY = "EMPTY"

# --- การตั้งค่าอื่นๆ ---
# โฟลเดอร์ที่เก็บเอกสารทั้งหมด
DATA_ROOT_FOLDER = r"D:\smart_agent\data\รวมข้อมูล chatbot" 
# ไฟล์ผลลัพธ์
JSON_OUTPUT_FILE = "output/processed_chunks.json"
TXT_OUTPUT_FOLDER = "output/text_previews"