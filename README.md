# 🎬 Script Assistant — 剧本标注编辑器

一个基于 AI 的剧本标注工具，自动识别剧本中的场景标题、动作、角色名、对白等元素，并转换为标准的 [Fountain](https://fountain.io/) 剧本格式。

![Tech Stack](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)

---

## ✨ 功能特性

- 🤖 **AI 智能标注** — 自动识别剧本要素（场景/动作/角色/对白/转场等 12 种类型）
- 📄 **多格式导入** — 支持 TXT、Markdown、Fountain、PDF、DOCX 文件上传
- 🔄 **实时流式输出** — SSE 流式推送，标注结果即时可见
- 🎭 **Fountain 转换** — 一键将标注结果转为标准 Fountain 剧本格式
- 🎨 **暗色主题编辑器** — 专业的剧本编辑界面，沉浸式体验
- ⚙️ **浏览器内配置** — 打开网页直接填 API Key，无需编辑任何文件
- 🐳 **Docker 一键部署** — 零依赖安装，开箱即用

---

## 🚀 快速开始

### 前提条件

- Python 3.11+（本地运行）或 Docker（推荐）
- 一个 OpenAI 兼容的 API Key（支持 OpenAI / DeepSeek / 其他兼容服务）

### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆或下载本项目
git clone <your-repo-url>
cd ScriptAssitant

# 2. 启动服务
docker compose up -d

# 3. 打开浏览器，访问 http://localhost:8080
#    首次打开会自动弹出设置面板，填入 API Key 即可使用
```

### 方式二：本地运行

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 启动服务
python src/launch.py

# 3. 打开浏览器，访问 http://localhost:8080
#    首次打开会自动弹出设置面板，填入 API Key 即可使用
```

> 💡 **不需要编辑 .env 文件！** 打开网页后点击右上角 ⚙️ 设置，直接填入 API Key、Base URL 和模型名称即可。配置保存在浏览器本地，安全便捷。

---

## 🔧 环境变量说明

在 `.env` 文件中配置（参考 `.env.example`）：

| 变量 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `OPENAI_API_KEY` | ✅ | API 密钥 | `sk-xxxx` |
| `OPENAI_BASE_URL` | ❌ | API 地址（留空即用 OpenAI 官方） | `https://api.deepseek.com` |
| `OPENAI_MODEL` | ❌ | 模型名称（默认 gpt-4o-mini） | `deepseek-v4-flash` |

---

## 📖 使用指南

1. **输入剧本** — 在左侧编辑器中粘贴或输入剧本内容，也可拖拽/点击上传文件
2. **AI 标注** — 点击「🤖 AI 标注」按钮，AI 将自动为每行添加类型标记
3. **手动调整** — 可在标注结果中手动修正 [h] / [a] / [c] / [d] 等标记
4. **导出 Fountain** — 点击「📄 导出 Fountain」按钮，获得标准剧本格式

### 支持的标记类型

| 标记 | 含义 | 示例 |
|------|------|------|
| `[h]` | 场景标题 | `[h] EXT. 码头 - 日` |
| `[a]` | 动作描述 | `[a] 阳光明媚。老王坐在长椅上。` |
| `[c]` | 角色名 | `[c] 老王` |
| `[d]` | 对白 | `[d] 这日子没法过了。` |
| `[p]` | 旁白 | `[p] (叹气)` |
| `[t]` | 转场 | `[t] CUT TO:` |
| `[l]` | 歌词 | `[l] ~ 月落乌啼霜满天` |
| `[s]` | 章节 | `[s] # 第一幕` |
| `[n]` | 居中文本 | `[n] 剧终` |
| `[y]` | 概要 | `[y] 本章讲述了...` |
| `[x]` | 注释 | `[x] 此处需要修改` |
| `[b]` | 废弃区 | `[b] 被删除的内容` |
| `[g]` | 分页符 | `[g]` |

---

## 📁 项目结构

```
ScriptAssitant/
├── backend/                    # Python 后端
│   ├── requirements.txt        # Python 依赖
│   └── src/
│       ├── main.py             # FastAPI 主入口 + API 路由
│       ├── ai.py               # AI 标注器（流式 SSE）
│       ├── formatter.py        # 标注 → Fountain 格式转换
│       └── launch.py           # 启动入口
├── frontend_render/            # 前端（纯 HTML/CSS/JS）
│   ├── index.html              # 主页面
│   └── src/
│       ├── css/                # 样式文件
│       └── js/                 # JS 脚本
├── .env.example                # 环境变量模板
├── Dockerfile                  # Docker 镜像构建
├── docker-compose.yml          # Docker 编排
└── .gitignore
```

---

## 🛠️ 技术栈

- **后端**: Python / FastAPI / OpenAI SDK / SSE
- **前端**: 原生 HTML/CSS/JS + Fountain.js
- **部署**: Docker / Docker Compose
- **AI**: 兼容 OpenAI API 格式的大语言模型

---

## 📝 License

MIT License