from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.exception_handlers import http_exception_handler

from app.api import endpoints
from app.api import file_ops
from app.api import full_content   # ✅ 注意：把 full_content 也导入

app = FastAPI(title="AI Agent for Paper Analysis")

# ✅ 异常统一 JSON 处理
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )

@app.exception_handler(HTTPException)
async def http_exception_json_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "detail": str(exc)},
    )

# ✅ 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 注册路由
app.include_router(endpoints.router)
app.include_router(file_ops.router)
app.include_router(full_content.router)   # ✅ 正确注册 full_content

# ✅ 根路径测试
@app.get("/")
async def root():
    return {"message": "AI Agent backend is running"}
