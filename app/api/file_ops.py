# app/api/file_ops.py

import os
import shutil
import zipfile
from io import BytesIO
from typing import List

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime
from pydantic import BaseModel

from app.services.pdf_parser import extract_basic_info_from_pdf

router = APIRouter()

UPLOAD_DIR = "tmp_uploads"
TRASH_DIR = "trash_uploads"
os.makedirs(TRASH_DIR, exist_ok=True)

# ✅ 请求体模型
class FileIdsRequest(BaseModel):
    file_ids: List[str]

# ✅ 权限校验
def check_permissions(request: Request):
    token = request.headers.get("X-User-Token")
    if token != "secret123":
        raise HTTPException(status_code=403, detail="Unauthorized access")

# ✅ 日志记录
def log_action(action: str, file_id: str, request: Request):
    user = request.headers.get("X-User-Token", "anonymous")
    print(f"[{datetime.now()}] User:{user} - {action} {file_id}")

# ✅ 批量删除（软删除 -> 回收站）
@router.post("/delete_pdfs")
async def delete_pdfs(req: FileIdsRequest, request: Request):
    check_permissions(request)
    deleted = []
    for file_id in req.file_ids:
        src = os.path.join(UPLOAD_DIR, file_id)
        dst = os.path.join(TRASH_DIR, file_id)
        if os.path.exists(src):
            shutil.move(src, dst)
            log_action("delete", file_id, request)
            deleted.append(file_id)
    return {"deleted": deleted}

# ✅ 列出回收站文件
@router.get("/list_trash_files")
async def list_trash_files(request: Request):
    check_permissions(request)
    trash_files = []
    for file_id in os.listdir(TRASH_DIR):
        path = os.path.join(TRASH_DIR, file_id)
        info = extract_basic_info_from_pdf(path)
        title = info.get("title") or file_id
        trash_files.append({"file_id": file_id, "title": title})
    return {"trash": trash_files}

# ✅ 批量恢复
@router.post("/restore_pdfs")
async def restore_pdfs(req: FileIdsRequest, request: Request):
    check_permissions(request)
    restored = []
    for file_id in req.file_ids:
        src = os.path.join(TRASH_DIR, file_id)
        dst = os.path.join(UPLOAD_DIR, file_id)
        if os.path.exists(src):
            shutil.move(src, dst)
            log_action("restore", file_id, request)
            restored.append(file_id)
    return {"restored": restored}

# ✅ 批量彻底删除
@router.delete("/purge_pdfs")
async def purge_pdfs(req: FileIdsRequest, request: Request):
    check_permissions(request)
    purged = []
    for file_id in req.file_ids:
        path = os.path.join(TRASH_DIR, file_id)
        if os.path.exists(path):
            os.remove(path)
            log_action("purge", file_id, request)
            purged.append(file_id)
    return {"purged": purged}

# ✅ 批量打包下载
@router.post("/download_pdfs_zip")
async def download_pdfs_zip(req: FileIdsRequest, request: Request):
    check_permissions(request)
    file_ids = req.file_ids

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zf:
        for file_id in file_ids:
            path = os.path.join(UPLOAD_DIR, file_id)
            if os.path.exists(path):
                zf.write(path, arcname=file_id)
    memory_file.seek(0)

    return StreamingResponse(memory_file, media_type="application/zip", headers={
        "Content-Disposition": "attachment; filename=selected_papers.zip"
    })
