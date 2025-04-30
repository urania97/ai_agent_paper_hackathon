# app/api/endpoints.py

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse,StreamingResponse
from pydantic import BaseModel
from app.services.ai_agent_paper_analysis import AgentModel
from app.utils.chunking_utils import split_text_into_chunks, ask_llm_in_batches


import os
import shutil
from uuid import uuid4

from app.services.pdf_parser import (
    extract_basic_info_from_pdf,
    increment_pdf_counter,
    get_pdf_upload_count,
    get_pdf_count_from_folder,
    list_uploaded_pdf_files,
    list_all_parsed_papers,
)

router = APIRouter()
agentmodel = AgentModel()
UPLOAD_DIR = "tmp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===================== Ping Test =====================

@router.get("/ping")
async def ping():
    return {"status": "pong"}

# ===================== PDF Upload + Parse =====================

@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            return JSONResponse(status_code=400, content={"error": "Only PDF files are supported."})

        file_id = str(uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_info = extract_basic_info_from_pdf(file_path)
        increment_pdf_counter()
        agentmodel.analysis_paper(extracted_info)
        return {
            "message": "PDF uploaded and parsed successfully.",
            "file_id": file_id,
            "original_filename": file.filename,
            "parsed_info": extracted_info
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ===================== Statistics Endpoints =====================

@router.get("/upload_count")
async def get_upload_count():
    return {"count": get_pdf_upload_count()}

@router.get("/upload_stats")
async def get_upload_stats():
    return {
        "current_file_count": get_pdf_count_from_folder(),
        "total_uploaded": get_pdf_upload_count()
    }

# ===================== PDF Listing =====================

@router.get("/list_uploaded_files")
async def list_uploaded_files():
    return {"files": list_uploaded_pdf_files()}

@router.get("/list_parsed_papers")
async def list_parsed_papers():
    return {"papers": list_all_parsed_papers()}

# ===================== Optional: Simple /chat using local LLM =====================

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    id: str
    content: str

# Replace below if you're using HuggingFace + Langchain
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline

hf_pipeline = pipeline("text2text-generation", model="google/flan-t5-base", max_new_tokens=200)
llm = HuggingFacePipeline(pipeline=hf_pipeline)

from app.utils.chunking_utils import split_text_into_chunks, ask_llm_in_batches

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_message = request.message.strip()

    if not user_message:
        return {"id": "empty", "content": "Please say something."}

    try:
        return StreamingResponse(agentmodel.find_paper(user_message), media_type="text/event-stream")

    except Exception as e:
        return {
            "id": "error",
            "content": f"Error generating reply: {str(e)}"
        }