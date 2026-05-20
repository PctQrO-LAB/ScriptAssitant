#!/usr/bin/env bash
# =============================================
# Script Assistant — 一键启动脚本
# =============================================
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║   🎬 Script Assistant 启动脚本      ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# ── 检查 .env（可选，服务端兜底用） ────
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[!] 未找到 .env 文件，正在从 .env.example 创建...${NC}"
    cp .env.example .env
fi

echo -e "${GREEN}[✓] 准备就绪${NC}"
echo -e "${YELLOW}💡 提示：打开网页后点击右上角 ⚙️ 设置，填入 API Key 即可使用${NC}"
echo ""

# ── 选择运行方式 ──────────────────────
echo -e "${CYAN}请选择启动方式:${NC}"
echo "  [1] Docker 启动（推荐）"
echo "  [2] 本地 Python 启动"
echo "  [3] 仅安装本地依赖"
echo ""
read -rp "请输入选项 [1/2/3]: " mode

case "$mode" in
    1)
        echo ""
        echo -e "${CYAN}[→] 正在使用 Docker Compose 启动...${NC}"
        
        # 检查 docker 是否可用
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}[✗] 未找到 Docker，请先安装 Docker。${NC}"
            exit 1
        fi
        
        docker compose up -d --build
        echo ""
        echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  🎉 启动成功！                      ║${NC}"
        echo -e "${GREEN}║  访问: http://localhost:8080         ║${NC}"
        echo -e "${GREEN}║  点击右上角 ⚙️ 设置填入 API Key    ║${NC}"
        echo -e "${GREEN}║  停止: docker compose down           ║${NC}"
        echo -e "${GREEN}║  日志: docker compose logs -f        ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
        ;;
    2)
        echo ""
        echo -e "${CYAN}[→] 正在安装依赖并启动本地服务...${NC}"
        
        cd "$PROJECT_DIR/backend"
        
        # 创建虚拟环境（如果不存在）
        if [ ! -d ".venv" ]; then
            echo -e "${YELLOW}[→] 创建 Python 虚拟环境...${NC}"
            python3 -m venv .venv
        fi
        
        source .venv/bin/activate
        pip install -q -r requirements.txt
        
        echo -e "${GREEN}[✓] 依赖安装完成${NC}"
        echo ""
        echo -e "${CYAN}[→] 正在启动服务...${NC}"
        python src/launch.py
        ;;
    3)
        echo ""
        echo -e "${CYAN}[→] 正在安装本地依赖...${NC}"
        
        cd "$PROJECT_DIR/backend"
        
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
        fi
        
        source .venv/bin/activate
        pip install -r requirements.txt
        
        echo ""
        echo -e "${GREEN}[✓] 依赖安装完成！${NC}"
        echo -e "${YELLOW}  后续启动命令:${NC}"
        echo "    cd backend && source .venv/bin/activate"
        echo "    python src/launch.py"
        ;;
    *)
        echo -e "${RED}[✗] 无效选项${NC}"
        exit 1
        ;;
esac