---
title: Script Assistant
emoji: 🎬
colorFrom: indigo
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# 剧本标注编辑器 - Script Assistant

基于本地微调的 MacBERT 模型，实现杂乱剧本的毫秒级标准自动化标注与 Fountain 格式化转换。

## 功能特性

- 🤖 **AI 自动标注**：本地 BERT 模型（MacBERT 微调）逐行识别剧本元素类型，毫秒级推理，无需联网调用 LLM API
- 📄 **Fountain 格式化**：标注结果自动转换为标准 Fountain 语法，右侧实时渲染成中文剧本书式（场景自动编号、角色名/对白缩进等）
- 📂 **多格式导入**：支持上传 `.docx` `.pdf` `.md` `.markdown` `.txt` `.fountain`，或直接 Ctrl+V 粘贴
- ✍️ **手动修正**：可对 AI 标注结果逐行手动调整类型标记
- 🖨️ **一键导出 PDF**：借助浏览器打印，内置 A4 打印样式

## 项目结构

```
├── backend/                        # FastAPI 后端
│   ├── model/best_script_bert_model/  # 本地微调 MacBERT 模型（config/tokenizer/权重）
│   ├── src/
│   │   ├── main.py                 # API 入口：/api/annotate /api/upload /api/health + 静态文件服务
│   │   ├── ai.py                   # BERT 推理（模型加载、上下文窗口、批量预测）
│   │   ├── formatter.py            # 标注 → Fountain 转换器（后端版）
│   │   └── launch.py               # 启动入口（8080 端口）
│   └── requirements.txt
├── frontend_render/
│   ├── index.html                  # 单页编辑器（HTML/CSS/JS 内联，含前端版标注→Fountain 转换）
│   ├── samples/                    # 示例 Fountain 剧本
│   └── src/js/                     # fountain.js 渲染引擎等
├── docker-compose.yml              # Docker 部署（8080 端口）
├── Dockerfile                      # 镜像（Hugging Face Spaces 兼容，7860 端口）
└── setup.sh                        # 一键启动脚本
```

## 快速开始

### 方式一：一键脚本

```bash
bash setup.sh
```

按提示选择：
- `1` Docker 启动（推荐）→ 访问 http://localhost:8080
- `2` 本地 Python 启动 → 访问 http://localhost:8080
- `3` 仅安装依赖

### 方式二：Docker Compose

```bash
docker compose up -d --build
# 访问 http://localhost:8080
# 停止：docker compose down
```

### 方式三：本地 Python

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/launch.py
```

### 端口说明

| 启动方式 | 端口 | 说明 |
| --- | --- | --- |
| `setup.sh`（本地 / Compose） | 8080 | `launch.py` 固定 8080；Compose 映射 `8080:8080` |
| Dockerfile 默认 CMD | 7860 | Hugging Face Spaces 要求；`docker run -p 7860:7860` 直接使用 |
| FastAPI 静态服务 | 同上 | 后端同时托管前端页面，前后端同源，无 CORS 问题 |

## 前端使用指南

启动后在浏览器打开对应地址，页面分左右两栏：**左栏编辑/标注，右栏格式化预览**。

### 1. 输入剧本

三种方式任选：

- **上传文件**：点击左栏顶部虚线区域或拖拽文件进去，支持 `.docx` `.pdf` `.md` `.markdown` `.txt` `.fountain`（由后端 `/api/upload` 解析提取文本）
- **直接粘贴**：在下方文本框 Ctrl+V 粘贴剧本文本
- **示例剧本**：页面加载时文本框内已有一段示例剧本，可直接体验

### 2. AI 标注

点击工具栏 **「🤖 AI 标注」** 按钮（或按 `Ctrl+Enter`）：

- 前端将文本 POST 到 `/api/annotate`，后端本地 BERT 模型逐行分类后以 SSE 流式返回
- 返回结果在每行行首自动加上 `[h]` `[a]` `[c]` `[d]` 等类型标记，并覆盖回左侧文本框

标记类型对照表：

| 标记 | 含义 | 标记 | 含义 |
| --- | --- | --- | --- |
| `[h]` | 场景标题 | `[l]` | 歌词 |
| `[a]` | 动作描述 | `[n]` | 居中 |
| `[c]` | 角色名 | `[s]` | 章节 |
| `[d]` | 对白 | `[y]` | 概要 |
| `[p]` | 旁白括号 | `[x]` | 注释 |
| `[t]` | 转场 | `[b]` | 废弃区 |
| `[g]` | 分页符 | | |

### 3. 手动修正标记

AI 结果不准确时可以手动改：

1. 在文本框中**选中要修改的行**（可多选）
2. 工具栏下拉框选择正确类型（如 `[h] 场景标题`）
3. 选中行行首标记自动替换；「清除标记」按钮可去掉全部行首标记

### 4. 格式化预览

点击 **「📄 格式化预览」**（或 `Ctrl+P`，AI 标注完成后也会自动触发）：

- **转换在前端浏览器本地完成**（`index.html` 中的 `annotatedToFountain` 函数，是后端 `formatter.py` 的 JS 等价实现）
- 右侧面板以 Fountain 引擎渲染为中文剧本书式：场景自动编号、宋体动作描述右缩进、角色名前短横线、对白左右缩进等

### 5. 导出 PDF

点击 **「🖨️ 导出 PDF」**，调用浏览器打印对话框；打印 CSS 已适配 A4 纸张，仅打印右侧预览内容。建议在浏览器打印设置中选择"保存为 PDF"。

### 6. 右上角 ⚙️ 设置

弹窗内可配置 API Key / Base URL / 模型名称，仅保存在浏览器 localStorage。

> ⚠️ **注意**：当前后端为**本地 BERT 模型推理**，`/api/annotate` 并不读取这些 API 配置。该设置项是早期 LLM 版本的遗留 UI，现阶段填写与否都不影响标注结果（"测试连接"按钮也只测试接口可达性）。

## BERT 模型更换指南

### 模型加载逻辑

- 模型在 `backend/src/ai.py` 中**懒加载单例**：第一次调用 `/api/annotate` 时载入显存/内存，之后复用
- 默认路径为 `backend/model/best_script_bert_model`，由环境变量 `SCRIPT_ASSISTANT_MODEL_PATH` 覆盖
- 加载方式：`AutoTokenizer.from_pretrained(路径)` + `AutoModelForSequenceClassification.from_pretrained(路径)`
- 设备自动选择：有 CUDA 用 GPU，否则 CPU

> 📦 **注意：仓库不包含模型权重文件**。`backend/model/` 已加入 `.gitignore`（`model.safetensors` 约 391MB，超过 GitHub 单文件 100MB 限制），克隆本仓库后需自行放置模型，见下方「模型权重从哪来」。

### 模型权重从哪来

仓库不随附权重文件，可任选其一获取：

1. **从 Hugging Face Space 下载**：项目此前托管在 [PctQrO/script-assistant](https://huggingface.co/spaces/PctQrO/script-assistant)，该 Space 仓库内带有训练好的模型文件，克隆后把 `backend/model/` 复制到本项目：

   ```bash
   git clone https://huggingface.co/spaces/PctQrO/script-assistant
   cp -r script-assistant/backend/model/* backend/model/
   ```

2. **自行训练/微调**：按上文「重新微调模型的注意事项」训练后，把产物放入 `backend/model/best_script_bert_model/`（或用 `SCRIPT_ASSISTANT_MODEL_PATH` 指向其他位置）

3. 放置完成后目录结构应为：

   ```
   backend/model/best_script_bert_model/
   ├── config.json
   ├── model.safetensors        # 或 pytorch_model.bin
   ├── tokenizer_config.json
   └── tokenizer.json
   ```

### 方法一：直接替换目录（最简单）

把新模型的全部文件放入 `backend/model/best_script_bert_model/`（保持目录名不变），重启服务即可。

### 方法二：通过环境变量指向新模型

在项目根目录 `.env` 中添加（Compose 会自动注入容器）：

```bash
SCRIPT_ASSISTANT_MODEL_PATH=/app/backend/model/my_new_model
```

本地启动则在 shell 中导出：

```bash
export SCRIPT_ASSISTANT_MODEL_PATH=/绝对路径/我的模型目录
```

> Docker 部署时注意：模型目录必须**挂载进容器**（或 COPY 进镜像），否则容器内读不到宿主机路径。可在 `docker-compose.yml` 的 `volumes` 中追加类似 `- ./backend/model/my_new_model:/app/backend/model/my_new_model`。

### 新模型必须满足的条件

1. **架构一致**：`config.json` 中 `architectures` 必须为 `["BertForSequenceClassification"]`（或你同步修改 `ai.py` 中的加载类与分词器类）
2. **标签编码一致**：必须是 **13 分类**，且 `config.json` 的 `id2label` 使用**单字母编码**：
   ```json
   {
     "0": "h", "1": "a", "2": "c", "3": "d", "4": "p", "5": "t",
     "6": "l", "7": "n", "8": "s", "9": "y", "10": "x", "11": "b", "12": "g"
   }
   ```
   原因：推理代码直接读 `model.config.id2label[预测id]`，且行合并与前端解析只认 `^\[([a-z])\]` 单字母格式；若 `id2label` 是完整单词（如 `"LABEL_0"` 或 `"scene_heading"`），输出标记将无法被识别
3. **分词器配套**：`tokenizer_config.json`、`tokenizer.json` 必须与新模型同源（部分 BERT 变体还需要 `vocab.txt`）；当前模型使用中文 BERT 词表（`vocab_size=21128`）
4. **预处理严格一致**：推理时每行的输入构造为
   ```
   前一行 [SEP] 当前行 [SEP] 后一行
   ```
   `max_length=128`（超长截断）。新模型**训练时的拼接逻辑必须与此完全相同**，否则准确率会大幅下降；若你训练时用了不同格式，需同步修改 `ai.py` 中 `annotate_stream` 的上下文拼接代码
5. **文件清单**：至少包含 `config.json`、`model.safetensors`（或 `pytorch_model.bin`）、`tokenizer_config.json`、`tokenizer.json`

### 重新微调模型的注意事项

- 推理管线还包括 `_split_scene_and_action`（拆分"场号+动作"混合行）与"合并相邻同标签行"两个步骤，均在 `ai.py` 中，换模型时无需改动，但训练数据应与之匹配
- `requirements.txt` 固定了 `transformers==4.38.2`；若新模型由更高版本 transformers 保存，可能需要同步升级该依赖
- 默认安装 CPU 版 PyTorch（`torch --index-url https://download.pytorch.org/whl/cpu`），本地推理足够快；如需 GPU 请自行替换为 CUDA 版

## 常见问题（FAQ）

| 问题 | 说明 |
| --- | --- |
| 第一次点"AI 标注"很慢 | 正常现象：首次请求会加载 BERT 模型（数百 MB），之后复用，毫秒级推理 |
| 填了 API Key 但标注结果没变化 | 当前版本用本地模型推理，不调用 LLM API，设置项为遗留 UI，见上文 |
| 8080 还是 7860？ | `setup.sh` / Compose 用 8080；直接 `docker run` 官方 Dockerfile 镜像用 7860（Hugging Face Spaces 要求） |
| 预览中文排版/字体不对 | 打印样式依赖系统字体（SimSun/宋体、KaiTi/楷体等），Linux 服务器或无中文字体环境会回落到浏览器默认字体 |
| 导出 PDF 内容不全或样式错 | PDF 导出走浏览器打印，请先点击"格式化预览"生成右侧内容；个别浏览器需在打印设置里勾选"背景图形" |
| PDF/DOCX 解析不理想 | 文本提取由 `pypdf` / `python-docx` 完成，扫描版 PDF（图片型）无法提取文字 |
| 某些行标注不准 | 可手动修正标记（选中行 → 下拉选择类型）；若整体偏差大，考虑按上文指南更换/重新微调模型 |
| 剧本超长行被截断 | 模型输入 `max_length=128` 截断是训练时就确定的，超长行会丢失尾部信息，建议提前分行 |
| 克隆仓库后启动报"找不到模型" | 仓库不包含模型权重（见「模型权重从哪来」），下载并放入 `backend/model/best_script_bert_model/` 即可 |