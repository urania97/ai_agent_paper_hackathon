# app/api/full_content.py

import os
import pdfplumber
import base64
from app.services.ai_agent_paper_analysis import AgentModel
from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import JSONResponse, StreamingResponse
from PyPDF2 import PdfReader

router = APIRouter()
agentmodel = AgentModel()

UPLOAD_DIR = "tmp_uploads"

# 权限校验
def check_permissions(request: Request, x_user_token: str):
    if x_user_token != "secret123":
        raise HTTPException(status_code=403, detail="Unauthorized access")

# 提取全文内容
# @router.get("/get_full_content/{file_id}")
# async def get_full_content(file_id: str, request: Request, x_user_token: str = Header(...)):
#     check_permissions(request, x_user_token)
    
#     file_path = os.path.join(UPLOAD_DIR, file_id)
#     print(file_path)
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")

#     try:
#         full_text = []
#         images = []
#         full_text_str = ""
#         with pdfplumber.open(file_path) as pdf:
#             for page_num, page in enumerate(pdf.pages):
#                 # 提取文本
#                 text = page.extract_text()
#                 if text:
#                     full_text.append({
#                         "page": page_num + 1,
#                         "text": text.strip()
#                     })
#                     full_text_str += text.strip()

#                 # 提取图片
#                 if page.images:
#                     for img in page.images:
#                         try:
#                             cropped_image = page.crop((img['x0'], img['top'], img['x1'], img['bottom'])).to_image()
#                             img_bytes = cropped_image.original.save_to_bytes(format="png")
#                             img_base64 = base64.b64encode(img_bytes).decode('utf-8')
#                             images.append({
#                                 "page": page_num + 1,
#                                 "image_base64": img_base64
#                             })
#                         except Exception as e:
#                             print(f"⚠️ Failed to extract image on page {page_num + 1}: {e}")
#                             continue
#         agentmodel.analysis_full_paper(full_text_str)
#         return {
#             "file_id": file_id,
#             "text_content": full_text,
#             "images": images
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")


# 提取全文内容
@router.get("/get_full_content/{file_id}")
async def get_full_content(file_id: str, request: Request, x_user_token: str = Header(...)):
    check_permissions(request, x_user_token)
    
    file_path = os.path.join(UPLOAD_DIR, file_id)
    print(file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        full_text = []
        # images = []
        full_text_str = ""
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # 提取文本
                text = page.extract_text()
                if text:
                    full_text.append({
                        "page": page_num + 1,
                        "text": text.strip()
                    })
                    full_text_str += text.strip()

                # 提取图片
                # if page.images:
                #     for img in page.images:
                #         try:
                #             cropped_image = page.crop((img['x0'], img['top'], img['x1'], img['bottom'])).to_image()
                #             img_bytes = cropped_image.original.save_to_bytes(format="png")
                #             img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                #             images.append({
                #                 "page": page_num + 1,
                #                 "image_base64": img_base64
                #             })
                #         except Exception as e:
                #             print(f"⚠️ Failed to extract image on page {page_num + 1}: {e}")
                #             continue
        # event = agentmodel.analysis_full_paper(full_text_str)
        # return {
        #     "file_id": file_id,
        #     "text_content": full_text,
        #     "images": images
        # }
        # async for chunk in response:
        #     if content := chunk.choices[0].delta.content:
        #         yield json.dumps({"content": content})
    
        return StreamingResponse(agentmodel.analysis_full_paper(full_text_str), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")



# 提取目录
@router.get("/get_pdf_outline/{file_id}")
async def get_pdf_outline(file_id: str, request: Request, x_user_token: str = Header(...)):
    check_permissions(request, x_user_token)

    file_path = os.path.join(UPLOAD_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        reader = PdfReader(file_path)
        outline = []

        if hasattr(reader, "outline") and reader.outline:
            def parse_outline(outline_items):
                for item in outline_items:
                    if isinstance(item, list):
                        parse_outline(item)
                    else:
                        outline.append({
                            "title": str(item.title).strip(),
                            "page_number": reader.get_destination_page_number(item) + 1,
                        })

            parse_outline(reader.outline)
        
        return {
            "file_id": file_id,
            "outline": outline
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting outline: {str(e)}")


# ✅ 提取表格数据
@router.get("/get_pdf_tables/{file_id}")
async def get_pdf_tables(file_id: str, request: Request, x_user_token: str = Header(...)):
    check_permissions(request, x_user_token)

    file_path = os.path.join(UPLOAD_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        tables_data = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    structured_table = []
                    for row in table:
                        structured_table.append(row)
                    
                    tables_data.append({
                        "page": page_num + 1,
                        "table_index": table_idx,
                        "table_data": structured_table
                    })

        return {
            "file_id": file_id,
            "tables": tables_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting tables: {str(e)}")


# ✅ 按章节提取内容
@router.get("/extract_section/{file_id}")
async def extract_section(file_id: str, section_title: str, request: Request, x_user_token: str = Header(...)):
    check_permissions(request, x_user_token)

    file_path = os.path.join(UPLOAD_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        reader = PdfReader(file_path)
        outlines = []

        if hasattr(reader, "outlines") and reader.outlines:
            def parse_outline(outline_items):
                for item in outline_items:
                    if isinstance(item, list):
                        parse_outline(item)
                    else:
                        outlines.append({
                            "title": str(item.title).strip(),
                            "page_number": reader.get_destination_page_number(item)
                        })

            parse_outline(reader.outlines)

        # 找到目标章节起始页
        start_page = None
        end_page = None

        for idx, item in enumerate(outlines):
            if item["title"].lower() == section_title.lower():
                start_page = item["page_number"]
                # 找下一个章节，作为终止页
                if idx + 1 < len(outlines):
                    end_page = outlines[idx + 1]["page_number"]
                else:
                    end_page = len(reader.pages)  # 最后章节到最后一页
                break

        if start_page is None:
            raise HTTPException(status_code=404, detail="Section not found")

        # 用 pdfplumber 读取文本
        full_text = []
        with pdfplumber.open(file_path) as pdf:
            for page_num in range(start_page, end_page):
                page = pdf.pages[page_num]
                text = page.extract_text()
                if text:
                    full_text.append(text.strip())

        return {
            "file_id": file_id,
            "section": section_title,
            "text": "\n\n".join(full_text)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting section: {str(e)}")

import re

# ✅ 智能基于文本识别章节
@router.get("/smart_extract_sections/{file_id}")
async def smart_extract_sections(file_id: str, request: Request, x_user_token: str = Header(...)):
    check_permissions(request, x_user_token)

    file_path = os.path.join(UPLOAD_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with pdfplumber.open(file_path) as pdf:
            full_text_pages = [page.extract_text() or "" for page in pdf.pages]

        combined_text = "\n\n".join(full_text_pages)

        # 使用正则识别章节标题： 1. Introduction / 2 Related Work / 3.1 Subsection
        section_pattern = re.compile(r'^\s*(\d+(\.\d+)*)\s+([A-Z][^\n]*)', re.MULTILINE)
        matches = list(section_pattern.finditer(combined_text))

        sections = []
        for idx, match in enumerate(matches):
            title = match.group(3).strip()
            start_pos = match.start()
            end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(combined_text)
            section_text = combined_text[start_pos:end_pos].strip()
            sections.append({
                "title": title,
                "text": section_text
            })

        return {
            "file_id": file_id,
            "sections": sections
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in smart section extraction: {str(e)}")


