"""
启动入口 —— 供 Docker 和本地开发使用。

运行方式（在 backend/ 目录下）：
    python src/launch.py
"""
import sys
import os
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(dotenv_path)

# 确保 backend/ 在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=False)
