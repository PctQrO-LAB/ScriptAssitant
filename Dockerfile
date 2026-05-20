FROM python:3.11-slim

WORKDIR /app

# 1. 安装系统依赖（如需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/cache/*

# 2. 复制依赖文件并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 复制项目的所有代码和静态资源
COPY backend ./backend
COPY frontend_render ./frontend_render

# 4. 暴露 Hugging Face 指定的 7860 端口
EXPOSE 7860

# 5. 启动 FastAPI，强制指定端口为 7860
CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "7860"]