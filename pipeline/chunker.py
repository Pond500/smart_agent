# smart_agent/pipeline/chunker.py

import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_smart_chunks(document_content, generated_metadata, document_title):
    print("สถานีที่ 4: Agent แบ่งข้อมูลกำลังทำงาน...")
    separators = ["\nบทที่ ", "\nส่วนที่ ", "\nข้อ ", "\n\n", "\n", " "]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, separators=separators)
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