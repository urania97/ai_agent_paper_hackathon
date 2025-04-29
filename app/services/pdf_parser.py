# app/services/pdf_parser.py

import datetime
import pdfplumber
import os
import json
import re
from collections import Counter

PDF_COUNTER_PATH = "pdf_upload_count.json"
UPLOAD_DIR = "tmp_uploads"

# ===================== PDF 内容提取 =====================

def extract_basic_info_from_pdf(file_path: str) -> dict:
    result = {
        "title": None,
        "authors": None,
        "abstract": None,
        "year": None
    }

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()

            if not text:
                return {"error": "Could not extract text from the PDF"}

            lines = text.split('\n')
            result["title"] = lines[0].strip() if len(lines) > 0 else None
            result["authors"] = lines[1].strip() if len(lines) > 1 else None

            abstract_lines = []
            found_abstract = False
            for line in lines:
                if 'abstract' in line.lower():
                    found_abstract = True
                    abstract_lines.append(line)
                elif found_abstract:
                    if line.strip() == "":
                        break
                    abstract_lines.append(line)

            if abstract_lines:
                result["abstract"] = " ".join(abstract_lines).strip()

            # 自动提取年份
            current_year = datetime.datetime.now().year
            matches = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
            for y in matches:
                y = int(y)
                if 1900 <= y <= current_year:
                    result["year"] = y
                    break

    except Exception as e:
        return {"error": str(e)}

    return result

# ===================== 简单关键词提取 =====================

def extract_keywords(text: str, num_keywords: int = 3) -> list:
    if not text:
        return []

    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {
        "the", "and", "of", "in", "to", "a", "is", "for", "with",
        "on", "this", "that", "as", "by", "an", "are"
    }
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(num_keywords)]

# ===================== 上传统计逻辑 =====================

def increment_pdf_counter():
    if not os.path.exists(PDF_COUNTER_PATH):
        with open(PDF_COUNTER_PATH, "w") as f:
            json.dump({"count": 0}, f)

    with open(PDF_COUNTER_PATH, "r") as f:
        data = json.load(f)

    data["count"] += 1

    with open(PDF_COUNTER_PATH, "w") as f:
        json.dump(data, f)

def get_pdf_upload_count() -> int:
    if not os.path.exists(PDF_COUNTER_PATH):
        return 0
    with open(PDF_COUNTER_PATH, "r") as f:
        data = json.load(f)
    return data.get("count", 0)

# ===================== 文件夹操作 =====================

def get_pdf_count_from_folder() -> int:
    if not os.path.exists(UPLOAD_DIR):
        return 0
    return len([
        f for f in os.listdir(UPLOAD_DIR)
        if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(UPLOAD_DIR, f))
    ])

def list_uploaded_pdf_files() -> list:
    if not os.path.exists(UPLOAD_DIR):
        return []
    return [
        f for f in os.listdir(UPLOAD_DIR)
        if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(UPLOAD_DIR, f))
    ]

# ===================== 所有论文内容汇总 =====================

def list_all_parsed_papers() -> list:
    results = []
    if not os.path.exists(UPLOAD_DIR):
        return results

    for f in os.listdir(UPLOAD_DIR):
        if f.lower().endswith(".pdf"):
            path = os.path.join(UPLOAD_DIR, f)
            parsed = extract_basic_info_from_pdf(path)

            # 跳过解析失败的文件
            if "error" in parsed:
                continue

            parsed["file_id"] = f
            parsed["keywords"] = extract_keywords(parsed.get("abstract", ""))
            results.append(parsed)

    return results
