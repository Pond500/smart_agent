# smart_agent/pipeline/chunker.py

import re
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def _size_based_split_with_metadata(text_piece: str, full_document_text: str, generated_metadata: dict, document_title: str, start_chunk_number: int) -> List[dict]:
    print(f" -> (ด่านสุดท้าย) กำลังแบ่งตามขนาด (เริ่มนับจาก Chunk ที่ {start_chunk_number})...")
    separators = ["\n\n", "\n", " ", ""]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, separators=separators)
    chunks_text = text_splitter.split_text(text_piece)
    
    final_chunks = []
    for i, chunk_content in enumerate(chunks_text):
        chunk_metadata = {
            "document_title": document_title,
            "chunk_number": start_chunk_number + i,
            **generated_metadata
        }
        
        # <--- บรรทัดที่แก้ไข
        # ใช้ re.MULTILINE เพื่อให้ ^ ตรวจจับต้นบรรทัดของทุกบรรทัด
        relevant_headers = re.findall(r'^(ส่วนที่\s[\d\w].{1,100}|บทที่\s[\d\w].{1,100}|ข้อ\s\d+.{1,100}|^\d+\.\s+.{1,150})', full_document_text[:full_document_text.find(chunk_content)], re.MULTILINE)
        
        context_path = " > ".join(relevant_headers[-2:]) if relevant_headers else "บทนำ"
        chunk_metadata["context_path"] = context_path
        final_chunks.append({"content": chunk_content, "metadata": chunk_metadata})
    
    return final_chunks

def structural_split(text: str) -> List[str]:
    print(" -> (ด่าน 1) กำลังวิเคราะห์โครงสร้างเอกสาร...")
    specific_patterns = [
        (r'(\nมาตรา\s+\d+)', "Legal Section (มาตรา)"),
        (r'(\nบทที่\s+\d+)', "Chapter (บทที่)"),
        (r'(\nคำถาม:)', "Q&A Document"),
    ]
    generic_patterns = [
        (r'(\n[A-Zก-๙\s]{5,}\n)', "All-Caps Heading"),
        (r'(\n[ก-ฮa-zA-Z0-9]+\s*[\.\)])', "Generic List Item"),
    ]

    for pattern_set, set_name in [(specific_patterns, "Specific"), (generic_patterns, "Generic")]:
        for pattern, pattern_name in pattern_set:
            if re.search(pattern, text):
                print(f" -> ตรวจพบโครงสร้าง! (ประเภท: {set_name}, รูปแบบ: {pattern_name})")
                split_text = re.split(pattern, text)
                chunks = []
                for i in range(1, len(split_text), 2):
                    combined_chunk = split_text[i] + split_text[i+1]
                    chunks.append(combined_chunk.strip())
                if split_text[0] and split_text[0].strip():
                    chunks.insert(0, split_text[0].strip())
                return chunks

    print(" -> ไม่พบโครงสร้างที่สามารถแบ่งได้")
    return []

def hybrid_chunker_agent(document_content: str, generated_metadata: dict, document_title: str) -> List[dict]:
    print("สถานีที่ 4: Hybrid Chunker Agent กำลังทำงาน...")
    final_chunks = []
    structural_chunks = structural_split(document_content)
    process_queue = structural_chunks if structural_chunks else [document_content]
    global_chunk_counter = 1
    
    for chunk_part in process_queue:
        chunks = _size_based_split_with_metadata(
            text_piece=chunk_part, 
            full_document_text=document_content, 
            generated_metadata=generated_metadata, 
            document_title=document_title, 
            start_chunk_number=global_chunk_counter
        )
        if chunks:
            final_chunks.extend(chunks)
            global_chunk_counter += len(chunks)
    
    print(f" -> แบ่งเอกสารออกเป็น {len(final_chunks)} ชิ้น (Chunks) สำเร็จ!")
    return final_chunks