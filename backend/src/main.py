"""
FastAPI 入口 —— 提供标注和格式化接口。
"""

import os
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from .ai import annotate_stream

app = FastAPI(title="Script Assistant", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 请求模型 ────────────────────────────────────────────────

class AnnotateRequest(BaseModel):
    script: str
    api_key: str = ""
    base_url: str = ""
    model: str = ""

# ── API 端点 ────────────────────────────────────────────────

@app.post("/api/annotate")
async def api_annotate(req: AnnotateRequest):
    """流式标注：AI 逐段在原文前加 [h][a][c] 等标记，SSE 推送。"""
    if not req.script or not req.script.strip():
        raise HTTPException(status_code=400, detail="剧本内容不能为空")

    return StreamingResponse(
        annotate_stream(req.script.strip()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """处理上传的文件并提取文本"""
    ext = os.path.splitext(file.filename)[1].lower()
    content = await file.read()
    
    text = ""
    try:
        if ext == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif ext == '.docx':
            from docx import Document
            doc = Document(io.BytesIO(content))
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext in ['.txt', '.md', '.markdown', '.fountain']:
            text = content.decode('utf-8', errors='ignore')
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")
        
    return {"text": text}

# ── 静态文件服务 ────────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend_render")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "src")), name="assets")
    app.mount("/samples", StaticFiles(directory=os.path.join(FRONTEND_DIR, "samples")), name="samples")

    @app.get("/")
    async def index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
