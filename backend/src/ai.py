"""
AI 标注器 —— 本地 BERT 模型推理版。
基于微调后的 MacBERT 进行序列标注，兼容前端 SSE 流式接口。
"""

import os
import torch
from typing import AsyncGenerator
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── 类型码映射 ──────────────────────────────────────────────
TYPE_MAP: dict[str, str] = {
    "h": "scene_heading", "a": "action", "c": "character", 
    "d": "dialogue", "p": "parenthetical", "t": "transition", 
    "l": "lyrics", "n": "centered", "s": "section", 
    "y": "synopsis", "x": "note", "b": "boneyard", "g": "page_break",
}

# 模型路径定位到 backend/model/best_script_bert_model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "best_script_bert_model")

# ── 模型加载器（单例模式，避免每次请求重复加载显存/内存） ─────────
class ScriptAnnotator:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        # 如果服务器有 GPU 则用 GPU，否则用 CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load(self):
        if self.model is None:
            print(f"正在加载本地 BERT 模型... ({self.device})")
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
            self.model.to(self.device)
            self.model.eval()
            print("模型加载完成！")

    def predict(self, texts: list[str]) -> list[str]:
        """批量推理，返回标签列表"""
        inputs = self.tokenizer(
            texts, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=128
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        preds = torch.argmax(outputs.logits, dim=1)
        return [self.model.config.id2label[p.item()] for p in preds]

# 实例化全局标注器
annotator = ScriptAnnotator()


async def annotate_stream(script_text: str) -> AsyncGenerator[str, None]:
    """
    为了兼容前端的 SSE 接收逻辑，依然保留 AsyncGenerator。
    本地模型处理极快，处理完后直接一次性推送给前端。
    """
    annotator.load()

    yield "data: {\"type\": \"start\", \"total\": 1}\n\n"
    yield "data: {\"type\": \"progress\", \"chunk\": 1, \"total\": 1}\n\n"

    try:
        lines = script_text.split('\n')
        
        # 1. 提取非空行并记录它们的原始索引，用于构建滑动窗口
        non_empty_lines = []
        non_empty_indices = []
        for i, line in enumerate(lines):
            if line.strip():
                non_empty_lines.append(line.strip())
                non_empty_indices.append(i)

        # 2. 构建带上下文的输入 (前一行 [SEP] 当前行 [SEP] 后一行)
        # 注意：这里的拼接逻辑必须与你训练时的预处理一模一样！
        context_texts = []
        for i in range(len(non_empty_lines)):
            prev_line = non_empty_lines[i-1] if i > 0 else ""
            curr_line = non_empty_lines[i]
            next_line = non_empty_lines[i+1] if i < len(non_empty_lines) - 1 else ""
            context_texts.append(f"{prev_line} [SEP] {curr_line} [SEP] {next_line}")

        # 3. 批量推理 (分批处理，避免剧本过长导致内存溢出)
        batch_size = 64
        labels = []
        for i in range(0, len(context_texts), batch_size):
            batch_texts = context_texts[i:i+batch_size]
            labels.extend(annotator.predict(batch_texts))

        # 4. 将预测的标签拼回原始文本的对应行
        result_lines = lines.copy()
        for idx, label in zip(non_empty_indices, labels):
            result_lines[idx] = f"[{label}] {result_lines[idx]}"

        # 5. 合并并发送给前端
        final_text = "\n".join(result_lines)
        escaped = final_text.replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\"")
        
        yield f"data: {{\"type\": \"text\", \"content\": \"{escaped}\"}}\n\n"

    except Exception as e:
        yield f"data: {{\"type\": \"error\", \"message\": \"{str(e)}\"}}\n\n"
        return

    yield "data: {\"type\": \"done\"}\n\n"