"""
递归字符分块策略 —— FastGPT 原始递归多级分块器的策略封装。

将原 text_chunker.py 中的 common_split / markdown_table_split / split_text_2_chunks
整体迁移至此，并以 RecursiveChunkStrategy 类对外暴露统一的 split 接口。
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from .base import ChunkStrategy, SplitResponse

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CUSTOM_SPLIT_SIGN = "-----CUSTOM_SPLIT_SIGN-----"
DEFAULT_MAX_CHUNK_SIZE = 8000

# ---------------------------------------------------------------------------
# Types (plain dicts — mirrors JS SplitResponse / inner structures)
# ---------------------------------------------------------------------------

SplitItem = Dict  # {text: str, title: str, chunk_max_size: int}
StepReg = Dict  # {reg: re.Pattern|str, max_len: int}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_text_valid_length(text: str) -> int:
    """统计非空白字符数（与 JS getTextValidLength 等价）。"""
    return len(re.sub(r"[\s\n]", "", text))


def _simple_text(text: str = "") -> str:
    """
    FastGPT simpleText 的 Python 移植 —— 对每块最终结果做轻量规范化。
    """
    text = text.strip()
    # 去除 CJK 字符之间的空格（保留换行）
    text = re.sub(r"([\u4e00-\u9fa5])[^\S\n]+([\u4e00-\u9fa5])", r"\1\2", text)
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[^\S\n]{2,}", " ", text)
    text = re.sub(r"[\x00-\x08]", " ", text)
    return text


# ---------------------------------------------------------------------------
# Markdown-table helpers
# ---------------------------------------------------------------------------


def str_is_md_table(s: str) -> bool:
    """判断字符串是否为 Markdown 表格（与 JS strIsMdTable 等价）。"""
    if "|" not in s:
        return False
    lines = s.split("\n")
    if len(lines) < 2:
        return False
    header_line = lines[0].strip()
    if not header_line.startswith("|") or not header_line.endswith("|"):
        return False
    separator_line = lines[1].strip()
    if not re.match(r"^(\|[\s:]*-+[\s:]*)+\|$", separator_line):
        return False
    for i in range(2, len(lines)):
        data_line = lines[i].strip()
        if data_line and (not data_line.startswith("|") or not data_line.endswith("|")):
            return False
    return True


def markdown_table_split(
    text: str,
    chunk_size: int,
    max_size: int = DEFAULT_MAX_CHUNK_SIZE,
    **_kwargs,
) -> SplitResponse:
    """
    Markdown 表格分块 —— 每块重复表头。

    与 JS `markdownTableSplit` 行为一致。
    """
    text = text or ""

    # 按行拆分
    split_text_2_lines = [line for line in text.split("\n") if line.strip()]

    # 不足两行则直接返回
    if len(split_text_2_lines) < 2:
        return {"chunks": [text], "chars": len(text)}

    header = split_text_2_lines[0]
    header_size = len(header.split("|")) - 2

    md_split_string = "| " + " | ".join(
        ["---"] * (header_size if header_size > 0 else 1)
    ) + " |"

    chunks: List[str] = []
    default_chunk = f"{header}\n{md_split_string}\n"
    chunk = default_chunk

    for i in range(2, len(split_text_2_lines)):
        chunk_length = get_text_valid_length(chunk)
        next_line_length = get_text_valid_length(split_text_2_lines[i])

        # 超容
        if chunk_length + next_line_length > chunk_size:
            # 单行极长时，直接委托 common_split 进一步切分
            if chunk_length > max_size:
                new_chunks = common_split(
                    text=chunk.replace(default_chunk, "").strip(),
                    chunk_size=chunk_size,
                    max_size=max_size,
                )["chunks"]
                chunks.extend(new_chunks)
            else:
                chunks.append(chunk)

            chunk = default_chunk
        chunk += f"{split_text_2_lines[i]}\n"

    if chunk:
        chunks.append(chunk)

    return {
        "chunks": chunks,
        "chars": sum(len(c) for c in chunks),
    }


# ---------------------------------------------------------------------------
# Core recursive splitter
# ---------------------------------------------------------------------------


def common_split(
    text: str,
    chunk_size: int,
    paragraph_chunk_deep: int = 5,
    paragraph_chunk_min_size: int = 100,
    max_size: int = DEFAULT_MAX_CHUNK_SIZE,
    overlap_ratio: float = 0.15,
    custom_reg: Optional[List[str]] = None,
) -> SplitResponse:
    """
    递归多级分块核心 —— JS ``commonSplit`` 的精确移植。
    """
    if custom_reg is None:
        custom_reg = []

    SPLIT_MARKER = "SPLIT_HERE_SPLIT_HERE"
    CODE_BLOCK_MARKER = "CODE_BLOCK_LINE_MARKER"
    overlap_len = round(chunk_size * overlap_ratio)

    # --- 预处理 -----------------------------------------------------------
    # 1. 代码块保护：替换内部换行
    text = re.sub(
        r"(```[\s\S]*?```|~~~[\s\S]*?~~~)",
        lambda m: m.group().replace("\n", CODE_BLOCK_MARKER),
        text,
    )

    # 2. 规范化过多换行
    text = re.sub(r"(\r?\n|\r){3,}", "\n\n\n", text)

    # --- 构建 step-rules 优先级链 --------------------------------------
    custom_reg_len = len(custom_reg)
    markdown_index = paragraph_chunk_deep - 1
    forbid_overlap_index = custom_reg_len + markdown_index + 4

    # Markdown 标题规则（H1 ~ H{paragraphChunkDeep}，最大到 8）
    markdown_header_rules: List[StepReg] = []
    if paragraph_chunk_deep and paragraph_chunk_deep != 0:
        max_deep = min(paragraph_chunk_deep, 8)
        for i in range(1, max_deep + 1):
            hash_symbols = "#" * i
            markdown_header_rules.append(
                {
                    "reg": re.compile(
                        rf"^({hash_symbols}\s[^\n]+\n)", re.MULTILINE
                    ),
                    "max_len": chunk_size,
                }
            )

    step_reges: List[StepReg] = []

    # 1. 自定义正则
    for cr in custom_reg:
        step_reges.append({"reg": cr.replace("\\n", "\n"), "max_len": max_size})

    # 2. Markdown 标题规则
    step_reges.extend(markdown_header_rules)

    # 3. 代码块
    step_reges.append(
        {"reg": re.compile(r"([\n](```[\s\S]*?```|~~~[\s\S]*?~~~))"), "max_len": max_size}
    )

    # 4. Markdown 表格
    step_reges.append(
        {
            "reg": re.compile(
                r"(\n\|(?:[^\n|]*\|)+\n\|(?:[:\-\s]*\|)+\n(?:\|(?:[^\n|]*\|)*\n)*)"
            ),
            "max_len": chunk_size,
        }
    )

    # 5. 双换行
    step_reges.append({"reg": re.compile(r"(\n{2,})"), "max_len": chunk_size})

    # 6. 单换行
    step_reges.append({"reg": re.compile(r"([\n])"), "max_len": chunk_size})

    # ------ 上层规则不生成重叠 ------

    # 7. 中文句号 / 英文句号
    step_reges.append(
        {"reg": re.compile(r"([。]|([a-zA-Z])\.\s)"), "max_len": chunk_size}
    )
    # 8. 中文感叹号 / 英文
    step_reges.append({"reg": re.compile(r"([！]|!\s)"), "max_len": chunk_size})
    # 9. 中文问号 / 英文
    step_reges.append({"reg": re.compile(r"([？]|\?\s)"), "max_len": chunk_size})
    # 10. 中文分号 / 英文
    step_reges.append({"reg": re.compile(r"([；]|;\s)"), "max_len": chunk_size})
    # 11. 中文逗号 / 英文
    step_reges.append({"reg": re.compile(r"([，]|,\s)"), "max_len": chunk_size})

    # --- 闭包辅助函数 -----------------------------------------------

    def check_is_custom_step(step: int) -> bool:
        return step < custom_reg_len

    def check_is_markdown_split(step: int) -> bool:
        return custom_reg_len <= step <= markdown_index + custom_reg_len

    def check_forbid_overlap(step: int) -> bool:
        return step <= forbid_overlap_index

    # --- get_split_texts ---------------------------------------------------

    def get_split_texts(text: str, step: int) -> List[SplitItem]:
        if step >= len(step_reges):
            return [{"text": text, "title": "", "chunk_max_size": chunk_size}]

        is_custom_step = check_is_custom_step(step)
        is_markdown_split = check_is_markdown_split(step)

        reg_entry = step_reges[step]
        reg = reg_entry["reg"]
        max_len = reg_entry["max_len"]

        # 根据步骤类型构造替换字符串
        if isinstance(reg, str):
            tmp_text = text
            for item_reg in reg.split("|"):
                if is_custom_step:
                    replacement = SPLIT_MARKER
                elif is_markdown_split:
                    replacement = f"{SPLIT_MARKER}\\1"
                else:
                    replacement = f"\\1{SPLIT_MARKER}"
                tmp_text = tmp_text.replace(item_reg, replacement)
            replace_text = tmp_text
        else:
            if is_custom_step:
                replacement = SPLIT_MARKER
            elif is_markdown_split:
                replacement = f"{SPLIT_MARKER}\\1"
            else:
                replacement = f"\\1{SPLIT_MARKER}"
            replace_text = reg.sub(replacement, text)

        split_texts = [p for p in replace_text.split(SPLIT_MARKER) if p.strip()]

        results: List[SplitItem] = []
        for part in split_texts:
            # 提取标题（仅 Markdown 步骤）
            match_title = ""
            if is_markdown_split:
                m = re.search(reg, part) if isinstance(reg, re.Pattern) else None
                match_title = m.group(0) if m else ""

            # 确定 chunk_max_size
            if is_custom_step:
                chunk_max_size = max_len
            else:
                m2 = re.search(reg, part) if isinstance(reg, re.Pattern) else None
                chunk_max_size = chunk_size if m2 is None else max_len

            item_text = part.replace(match_title, "", 1) if is_markdown_split else part

            if match_title or (item_text and item_text.strip()):
                results.append(
                    {
                        "text": item_text,
                        "title": match_title,
                        "chunk_max_size": chunk_max_size,
                    }
                )

        return results

    # --- get_one_text_overlap_text -----------------------------------------

    def get_one_text_overlap_text(text: str, step: int) -> str:
        forbid_overlap = check_forbid_overlap(step)
        max_overlap_len = chunk_size * 0.4

        if forbid_overlap or overlap_len == 0 or step >= len(step_reges):
            return ""

        split_items = get_split_texts(text, step)
        overlay_text = ""

        for i in range(len(split_items) - 1, -1, -1):
            current_text = split_items[i]["text"]
            new_text = current_text + overlay_text
            new_text_len = get_text_valid_length(new_text)

            if new_text_len > overlap_len:
                if new_text_len > max_overlap_len:
                    deeper = get_one_text_overlap_text(new_text, step + 1)
                    return deeper or overlay_text
                return new_text

            overlay_text = new_text

        return overlay_text

    # --- split_text_recursively --------------------------------------------

    def split_text_recursively(
        text: str,
        step: int,
        last_text: str,
        parent_title: str = "",
    ) -> List[str]:
        is_markdown_step = check_is_markdown_split(step)
        is_custom_step = check_is_custom_step(step)
        forbid_concat = is_custom_step  # forbid=True 时 last_text 始终为空

        # 规则耗尽 —— 固定长度兜底
        if step >= len(step_reges):
            combined_text = last_text + text
            combined_length = get_text_valid_length(combined_text)

            if combined_length < max_size:
                return [combined_text]

            chunks: List[str] = []
            i = 0
            while i < len(combined_text):
                chunks.append(combined_text[i : i + chunk_size])
                i += chunk_size - overlap_len
            return chunks

        # 按当前规则拆分
        split_items = get_split_texts(text, step)

        chunks: List[str] = []

        for i, item in enumerate(split_items):
            max_len = item["chunk_max_size"]

            last_text_len = get_text_valid_length(last_text)
            current_text = item["text"]
            new_text = last_text + current_text
            new_text_len = get_text_valid_length(new_text)

            # Markdown 表格溢出 → 委托专用切分
            if str_is_md_table(current_text) and new_text_len > max_len:
                if last_text_len > 0:
                    chunks.append(last_text)
                    last_text = ""

                table_result = markdown_table_split(
                    text=current_text,
                    chunk_size=round(chunk_size * 1.2),
                )
                chunks.extend(table_result["chunks"])
                continue

            # Markdown 标题步骤 → 递归，并前置标题
            if is_markdown_step:
                inner_chunks = split_text_recursively(
                    text=new_text,
                    step=step + 1,
                    last_text="",
                    parent_title=parent_title + item["title"],
                )

                # 仅标题无内容
                if len(inner_chunks) == 0:
                    chunks.append(f"{parent_title}{item['title']}")
                    continue

                # 最深标题层级：前置所有标题
                if step == markdown_index + custom_reg_len:
                    chunks.extend(
                        f"{parent_title}{item['title']}{chunk}"
                        for chunk in inner_chunks
                    )
                else:
                    chunks.extend(inner_chunks)

                continue

            # new_text 过大
            if new_text_len > max_len:
                min_chunk_len = max_len * 0.8
                max_chunk_len = max_len * 1.2

                # 在 20% 容差范围内 → 直接接受
                if new_text_len < max_chunk_len:
                    chunks.append(new_text)
                    last_text = get_one_text_overlap_text(new_text, step)
                    continue

                # 前一块已足够大 → 输出前一块，回退索引重试当前块
                if last_text_len > min_chunk_len:
                    chunks.append(last_text)
                    last_text = get_one_text_overlap_text(last_text, step)
                    i -= 1
                    continue

                # 当前文本仍大 → 更深递归
                inner_chunks = split_text_recursively(
                    text=current_text,
                    step=step + 1,
                    last_text=last_text,
                    parent_title=parent_title + item["title"],
                )
                last_chunk = inner_chunks[-1] if inner_chunks else None

                if not last_chunk:
                    continue

                # 最后内层块太小 → 作为 last_text 继续携带
                if get_text_valid_length(last_chunk) < min_chunk_len:
                    chunks.extend(inner_chunks[:-1])
                    last_text = last_chunk
                    continue

                # 最后内层块足够大
                chunks.extend(inner_chunks)
                last_text = get_one_text_overlap_text(last_chunk, step)
                continue

            # new_text 较小
            if forbid_concat:
                chunks.append(current_text)
                continue

            last_text = new_text

        # --- 尾部碎片处理 -----------------------------------------------
        if last_text and chunks and not chunks[-1].endswith(last_text):
            if get_text_valid_length(last_text) < chunk_size * 0.4:
                chunks[-1] = chunks[-1] + last_text
            else:
                chunks.append(last_text)
        elif last_text and len(chunks) == 0:
            chunks.append(last_text)

        return chunks

    # --- 执行 -----------------------------------------------------------
    try:
        raw_chunks = split_text_recursively(
            text=text,
            step=0,
            last_text="",
            parent_title="",
        )

        # 还原代码块并去除首尾空白
        chunks = [
            c.replace(CODE_BLOCK_MARKER, "\n").strip() if c else ""
            for c in raw_chunks
        ]

        chars = sum(len(c) for c in chunks)
        return {"chunks": chunks, "chars": chars}

    except Exception as err:
        raise RuntimeError(str(err)) from err


# ---------------------------------------------------------------------------
# Public entry point (kept for internal reuse)
# ---------------------------------------------------------------------------


def split_text_2_chunks(
    text: str,
    chunk_size: int,
    overlap_ratio: float = 0.15,
    paragraph_chunk_deep: int = 5,
    paragraph_chunk_min_size: int = 100,
    max_size: int = DEFAULT_MAX_CHUNK_SIZE,
    custom_reg: Optional[List[str]] = None,
) -> SplitResponse:
    """
    将文本分块。

    1. 按 CUSTOM_SPLIT_SIGN 拆分。
    2. 每段分别委托 markdown_table_split 或 common_split。
    3. 扁平化 chunks，应用 _simple_text 规范化。
    """
    if custom_reg is None:
        custom_reg = []

    text = text or ""
    split_with_custom_sign = text.split(CUSTOM_SPLIT_SIGN)

    split_result: List[SplitResponse] = []
    for item in split_with_custom_sign:
        if str_is_md_table(item):
            split_result.append(
                markdown_table_split(
                    text=item,
                    chunk_size=chunk_size,
                    max_size=max_size,
                )
            )
        else:
            split_result.append(
                common_split(
                    text=item,
                    chunk_size=chunk_size,
                    paragraph_chunk_deep=paragraph_chunk_deep,
                    paragraph_chunk_min_size=paragraph_chunk_min_size,
                    max_size=max_size,
                    overlap_ratio=overlap_ratio,
                    custom_reg=custom_reg,
                )
            )

    # 扁平化并规范化
    flat_chunks: List[str] = []
    for res in split_result:
        flat_chunks.extend(res["chunks"])

    flat_chunks = [_simple_text(chunk) for chunk in flat_chunks]
    total_chars = sum(res["chars"] for res in split_result)

    return {"chunks": flat_chunks, "chars": total_chars}


# ---------------------------------------------------------------------------
# Strategy wrapper
# ---------------------------------------------------------------------------


class RecursiveChunkStrategy(ChunkStrategy):
    """
    递归字符分块策略 —— FastGPT 默认的多级递归分块器。

    按以下优先级链逐级尝试拆分：
    自定义正则 → Markdown 标题 → 代码块 → 表格 → 段落 → 换行 → 标点 → 固定长度。
    """

    def split(
        self,
        text: str,
        chunk_size: int = 500,
        overlap_ratio: float = 0.2,
        paragraph_chunk_deep: int = 2,
        **kwargs,
    ) -> SplitResponse:
        return split_text_2_chunks(
            text=text,
            chunk_size=chunk_size,
            overlap_ratio=overlap_ratio,
            paragraph_chunk_deep=paragraph_chunk_deep,
        )
