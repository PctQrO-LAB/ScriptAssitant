"""
标注→Fountain 转换器 —— 严格遵循 Fountain 官方语法规范。
纯确定性逻辑，零 AI 参与。

Fountain 核心规则：
- 场景标题：INT/EXT 等开头，或 . 强制前缀。前后各一个空行。
- 角色名：全大写，前有空行，后无空行（紧跟对白）。
- 对话块内部：角色名\n(旁白)\n对白 —— 单换行附着，作为一个整体。
- 转场：大写 + TO: 结尾，或 > 强制前缀。
- 歌词：~ 前缀。
- 居中：> < 包裹。
- 章节：# 前缀。概要：= 前缀。
- 注释：[[ ]]。废弃区：/* */。分页符：===。
"""

import re
from .ai import TYPE_MAP


def annotated_to_fountain(annotated_text: str) -> str:
    """
    将标注文本转换为标准 Fountain 格式。
    标注格式：每行以 [类型] 开头，如 [h] EXT. 码头 - 日
    """
    lines = annotated_text.split("\n")

    # 第一步：解析所有行为 (type, text)，保留原始缩进
    parsed: list[tuple[str, str]] = []
    for line in lines:
        s = line.rstrip()  # 仅去行尾空白
        if not s:
            parsed.append(("blank", ""))
            continue
        m = re.match(r'^\[([a-z])\]\s?(.*)', s)
        if m:
            code = m.group(1)
            raw = m.group(2)
            if code == "a":
                # Action 保留原始缩进，只去掉 [a] 标记
                parsed.append(("a", raw))
            else:
                # 其他元素去除首尾空白
                parsed.append((code, raw.strip()))
        else:
            parsed.append(("a", s))

    # 第二步：合并连续空行为单个
    merged: list[tuple[str, str]] = []
    for t, txt in parsed:
        if t == "blank":
            if merged and merged[-1][0] != "blank":
                merged.append(("blank", ""))
        else:
            merged.append((t, txt))
    while merged and merged[0][0] == "blank":
        merged.pop(0)
    while merged and merged[-1][0] == "blank":
        merged.pop()

    # 第三步：构建输出列表（跳过 blank，join 自然产生空行）
    output: list[str] = []
    i, n = 0, len(merged)

    while i < n:
        t, txt = merged[i]

        if t == "blank":
            i += 1
            continue

        if t == "h":
            output.append(_scene(txt))

        elif t == "a":
            output.append(txt)

        elif t == "c":
            block, skip = _dialogue(merged, i)
            output.append(block)
            i += skip - 1

        elif t == "t":
            output.append(_trans(txt))

        elif t == "l":
            output.append(_lyric(txt))

        elif t == "n":
            output.append(f"> {txt} <")

        elif t == "s":
            output.append(txt if txt.startswith("#") else f"# {txt}")

        elif t == "y":
            output.append(f"= {txt}")

        elif t == "x":
            output.append(f"[[ {txt} ]]")

        elif t == "b":
            output.append(f"/* {txt} */")

        elif t == "g":
            output.append("===")

        else:
            output.append(txt)

        i += 1

    # 第四步：大元素之间用双换行连接
    return "\n\n".join(output)


# ── 各元素格式化 ────────────────────────────────────────────

def _scene(text: str) -> str:
    """场景标题：删除【】符号和开头的数字，标准格式直接保留，非标准加 . 前缀。"""
    # 暴力移除前缀：所有括号【】[]、所有数字、以及所有的 . 、顿号、空格
    # 例如： "【1. 内景. 地铁 - 下午】" -> "内景. 地铁 - 下午"
    #        "2、外景 街道" -> "外景 街道"
    
    # 1. 如果有包裹的括号，先去掉两端括号
    text = re.sub(r'^[【\[(（](.*?)[】\])）]$', r'\1', text.strip())
    
    # 2. 去掉开头所有的数字、点、顿号、空格
    text = re.sub(r'^[\d.、\s]+', '', text).strip()
    
    u = text.upper()
    prefixes = ("INT", "EXT", "EST", "I/E", "INT.", "EXT.", "EST.",
                "INT/EXT", "INT./EXT", "I./E")
    return text if any(u.startswith(p) for p in prefixes) else f".{text}"


def _trans(text: str) -> str:
    """转场：标准格式直接保留，非标准加 > 前缀。"""
    u = text.upper().rstrip(".")
    if u.endswith("TO:") or u in ("FADE IN", "FADE OUT", "FADE TO BLACK", "CUT TO BLACK"):
        return text
    return f"> {text}"


def _lyric(text: str) -> str:
    """歌词：每行加 ~ 前缀，行间单换行。"""
    return "\n".join(f"~ {l.strip()}" for l in text.split("\n") if l.strip())


# ── 对话块构建（核心） ──────────────────────────────────────

def _dialogue(parsed: list, start: int) -> tuple[str, int]:
    """
    构建完整对话块。
    Fountain 格式：角色名\n(旁白)\n对白  （单换行附着）
    返回 (块文本, 消费元素数)
    """
    _, char = parsed[start]
    char = _normalize(char)

    parts = [char]
    consumed = 1
    i = start + 1
    n = len(parsed)

    while i < n:
        t, txt = parsed[i]
        if t == "blank":
            break
        if t == "p":
            # 暴力清理原有的各种乱七八糟的括号，只套一层纯英文小括号
            clean_txt = re.sub(r'^[（(]*(.*?)[)）]*$', r'\1', txt.strip())
            parts.append(f"({clean_txt})")
            consumed += 1
            i += 1
        elif t == "d":
            parts.append(txt)
            consumed += 1
            i += 1
        else:
            break

    return "\n".join(parts), consumed


def _normalize(name: str) -> str:
    """
    规范化角色名。
    - 清除中文剧本常带的冒号（: 或 ：）和末尾空格，这是 Fountain.js 正则匹配的死穴
    - 纯英文 → 全大写（Fountain 规范）
    - 含中文 → 保持原样
    - 保留 (V.O.)/(O.S.)/(CONT'D) 等扩展
    """
    # 暴力清理末尾的冒号和空格
    name = re.sub(r'[:：\s]+$', '', name).strip()
    
    exts = ["(V.O.)", "(O.S.)", "(CONT'D)", "(VO)", "(OS)"]
    base, ext = name, ""
    for e in exts:
        if e.upper() in name.upper():
            base = name.upper().replace(e.upper(), "").strip()
            ext = e
            break
    if base.isascii():
        base = base.upper()
    return f"{base} {ext}" if ext else base
