"""FastGPT 知识库管理 - Demo演示  (Streamlit UI)

交互式文档处理流水线演示，复刻 Vue demo 的 5 步 pipeline:
  1. 文档解析
  2. Markdown 转换
  3. 数据清洗
  4. 文本分块
  5. 图片索引
"""

from __future__ import annotations

import sys
from pathlib import Path
from io import BytesIO

import streamlit as st

# ---------------------------------------------------------------------------
# Ensure the local ``src`` package is importable when running ``demo/`` directly
# ---------------------------------------------------------------------------
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from fastgpt_demo.parsers import parse_file, ParseResult  # noqa: E402
from fastgpt_demo.converters import convert_to_markdown  # noqa: E402

from fastgpt_demo.cleaners import clean_text
from fastgpt_demo.chunkers import split_text_2_chunks
from fastgpt_demo.indexers import ImageIndexer


# ===================================================================
# Constants & helpers
# ===================================================================

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"}

# Parse methods offered per file type
_PARSE_METHODS: dict[str, list[str]] = {
    ".pdf": ["文本提取"],
    ".docx": ["HTML转换", "纯文本提取"],
    ".csv": ["表格解析", "原始文本"],
    ".xlsx": ["表格解析"],
    ".txt": ["纯文本"],
    ".md": ["纯文本"],
    ".markdown": ["纯文本"],
    ".pptx": ["文本提取"],
}


def _file_ext(name: str) -> str:
    return Path(name).suffix.lower()


def _is_image(name: str) -> bool:
    return _file_ext(name) in _IMAGE_EXTENSIONS


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024  # type: ignore[assignment]
    return f"{n:.1f} TB"


def _init_state() -> None:
    """Ensure every session_state key exists."""
    defaults = dict(
        buffer=None,
        file_info=None,
        raw_text="",
        format_text="",
        markdown_text="",
        cleaned_text="",
        chunks=None,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ===================================================================
# Page config & state
# ===================================================================

st.set_page_config(page_title="FastGPT Demo", page_icon="📄", layout="wide")
_init_state()

st.title("FastGPT 知识库管理 - Demo演示")
st.caption("交互式文档处理流水线演示")

# ===================================================================
# File uploader
# ===================================================================

uploaded = st.file_uploader(
    "上传文件",
    type=None,  # accept all
    help="支持 PDF / DOCX / CSV / XLSX / TXT / MD / PPTX / 图片 等格式",
)

if uploaded is not None:
    buf = uploaded.read()
    st.session_state.buffer = buf
    st.session_state.file_info = {
        "name": uploaded.name,
        "size": len(buf),
        "type": uploaded.type or "未知",
    }
    # Reset downstream state on new upload
    for key in ("raw_text", "format_text", "markdown_text", "cleaned_text", "chunks"):
        st.session_state[key] = "" if key != "chunks" else None

# ===================================================================
# Sidebar
# ===================================================================

with st.sidebar:
    st.header("📁 文件信息")
    fi = st.session_state.file_info
    if fi:
        st.write(f"**文件名**: {fi['name']}")
        st.write(f"**大小**: {_fmt_size(fi['size'])}")
        st.write(f"**类型**: {fi['type']}")
    else:
        st.info("尚未上传文件")

    st.divider()
    st.header("📊 处理统计")
    if st.session_state.raw_text:
        st.metric("原始文本", f"{len(st.session_state.raw_text):,} 字符")
    if st.session_state.markdown_text:
        st.metric("Markdown", f"{len(st.session_state.markdown_text):,} 字符")
    if st.session_state.cleaned_text:
        st.metric("清洗后", f"{len(st.session_state.cleaned_text):,} 字符")
    if st.session_state.chunks:
        total = sum(len(c) for c in st.session_state.chunks)
        st.metric("分块数", f"{len(st.session_state.chunks)} 块 / {total:,} 字符")

# ===================================================================
# Main tabs
# ===================================================================

if st.session_state.file_info is None:
    st.warning("请先上传文件以开始演示。")
    st.stop()

file_name = st.session_state.file_info["name"]
ext = _file_ext(file_name)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📄 文档解析", "📝 Markdown转换", "🧹 数据清洗", "✂️ 文本分块", "🖼️ 图片索引"]
)

# -------------------------------------------------------------------
# Tab 1: 文档解析
# -------------------------------------------------------------------
with tab1:
    st.subheader("文档解析")

    methods = _PARSE_METHODS.get(ext, ["纯文本"])
    method = st.selectbox("解析方式", methods, key="parse_method")

    if st.button("开始解析", key="btn_parse"):
        try:
            with st.spinner("解析中..."):
                result: ParseResult = parse_file(
                    st.session_state.buffer, file_name, method="auto"
                )
            st.session_state.raw_text = result.raw_text
            st.session_state.format_text = result.format_text
            st.success(
                f"解析完成 — 原始文本 {len(result.raw_text):,} 字符，"
                f"格式化文本 {len(result.format_text):,} 字符"
            )
        except Exception as exc:
            st.error(f"解析失败: {exc}")

    if st.session_state.raw_text:
        st.text_area(
            "解析结果 (raw_text)",
            value=st.session_state.raw_text[:5000],
            height=300,
            disabled=True,
            key="ta_parse",
        )

# -------------------------------------------------------------------
# Tab 2: Markdown 转换
# -------------------------------------------------------------------
with tab2:
    st.subheader("Markdown 转换")

    conv_note = (
        "当前转换策略: "
        + ("DOCX → HTML → Markdown" if ext == ".docx" else "直接使用格式化文本" if ext in {".csv", ".xlsx"} else "纯文本 / 原始 Markdown")
    )
    st.info(conv_note)

    if st.button("转换为 Markdown", key="btn_convert"):
        try:
            with st.spinner("转换中..."):
                md_text, note = convert_to_markdown(
                    st.session_state.raw_text,
                    st.session_state.format_text,
                    ext,
                )
            st.session_state.markdown_text = md_text
            st.success(note)
        except Exception as exc:
            st.error(f"转换失败: {exc}")

    if st.session_state.markdown_text:
        col_before, col_after = st.columns(2)
        with col_before:
            st.markdown("**转换前**")
            st.text_area(
                "raw",
                value=st.session_state.raw_text[:3000],
                height=300,
                disabled=True,
                key="ta_conv_before",
            )
        with col_after:
            st.markdown("**转换后**")
            st.markdown(st.session_state.markdown_text[:3000], unsafe_allow_html=False)
        st.caption("⚠️ 以上预览最多展示 3000 字符")

# -------------------------------------------------------------------
# Tab 3: 数据清洗
# -------------------------------------------------------------------
with tab3:
    st.subheader("数据清洗")

    st.markdown("#### 清洗选项")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        opt_trim = st.checkbox("去除首尾空白", value=True, key="opt_trim")
    with c2:
        opt_chinese = st.checkbox("移除中文间空格", value=True, key="opt_chinese")
    with c3:
        opt_newline = st.checkbox("规范化换行符", value=True, key="opt_newline")
    with c4:
        opt_collapse = st.checkbox("合并连续空白", value=True, key="opt_collapse")
    with c5:
        opt_empty = st.checkbox("移除空行", value=True, key="opt_empty")

    source_text = st.session_state.markdown_text or st.session_state.raw_text

    if st.button("执行清洗", key="btn_clean"):
        if not source_text:
            st.warning("请先完成前面的步骤（解析 / 转换）。")
        else:
            try:
                with st.spinner("清洗中..."):
                    options = {
                        "trim": opt_trim,
                        "remove_chinese_space": opt_chinese,
                        "normalize_newline": opt_newline,
                        "collapse_whitespace": opt_collapse,
                        "remove_empty_lines": opt_empty,
                    }
                    cleaned = clean_text(source_text, options)
                st.session_state.cleaned_text = cleaned
                orig_len = len(source_text)
                clean_len = len(cleaned)
                reduction = (1 - clean_len / orig_len) * 100 if orig_len else 0
                st.success(
                    f"清洗完成 — 原始 {orig_len:,} 字符 → "
                    f"清洗后 {clean_len:,} 字符 (减少 {reduction:.1f}%)"
                )
            except Exception as exc:
                st.error(f"清洗失败: {exc}")

    if st.session_state.cleaned_text:
        col_b, col_a = st.columns(2)
        with col_b:
            st.markdown("**清洗前**")
            st.text_area(
                "before",
                value=source_text[:3000],
                height=300,
                disabled=True,
                key="ta_clean_before",
            )
        with col_a:
            st.markdown("**清洗后**")
            st.text_area(
                "after",
                value=st.session_state.cleaned_text[:3000],
                height=300,
                disabled=True,
                key="ta_clean_after",
            )
        orig = len(source_text)
        cln = len(st.session_state.cleaned_text)
        red = (1 - cln / orig) * 100 if orig else 0
        st.caption(f"原始: {orig:,} 字符 | 清洗后: {cln:,} 字符 | 减少: {red:.1f}%")

# -------------------------------------------------------------------
# Tab 4: 文本分块
# -------------------------------------------------------------------
with tab4:
    st.subheader("文本分块")

    chunk_size = st.slider("块大小 (chunkSize)", 100, 8000, 500, step=100, key="sl_chunk_size")
    overlap_ratio = st.slider("重叠率 (overlapRatio)", 0.0, 0.4, 0.2, step=0.05, key="sl_overlap")
    para_depth = st.slider("段落深度 (paragraphChunkDeep)", 1, 5, 2, step=1, key="sl_para_depth")

    text_to_chunk = st.session_state.cleaned_text or st.session_state.markdown_text or st.session_state.raw_text

    if st.button("执行分块", key="btn_chunk"):
        if not text_to_chunk:
            st.warning("请先完成前面的步骤。")
        else:
            try:
                with st.spinner("分块中..."):
                    result = split_text_2_chunks(
                        text_to_chunk,
                        chunk_size=chunk_size,
                        overlap_ratio=overlap_ratio,
                        paragraph_chunk_deep=para_depth,
                    )
                    chunks = result["chunks"]
                st.session_state.chunks = chunks
                total_chars = sum(len(c) for c in chunks)
                avg_size = total_chars / len(chunks) if chunks else 0
                st.success(
                    f"分块完成 — {len(chunks)} 块 | "
                    f"平均 {avg_size:.0f} 字符/块 | 共 {total_chars:,} 字符"
                )
            except Exception as exc:
                st.error(f"分块失败: {exc}")

    if st.session_state.chunks:
        chunks = st.session_state.chunks
        total_chars = sum(len(c) for c in chunks)
        avg_size = total_chars / len(chunks) if chunks else 0
        st.info(
            f"📊 统计: {len(chunks)} 块 | 平均 {avg_size:.0f} 字符/块 | 共 {total_chars:,} 字符"
        )
        for i, chunk in enumerate(chunks):
            with st.expander(f"Chunk #{i + 1} ({len(chunk)} 字符)"):
                st.text(chunk[:2000])
                if len(chunk) > 2000:
                    st.caption(f"... 仅展示前 2000 字符（共 {len(chunk):,}）")

# -------------------------------------------------------------------
# Tab 5: 图片索引
# -------------------------------------------------------------------
with tab5:
    st.subheader("图片索引")

    if _is_image(file_name):
        st.image(st.session_state.buffer, caption=file_name)

        st.markdown("#### VLM 处理流水线")
        st.markdown(
            """
            1. **图片预处理** — 调整尺寸、格式标准化
            2. **VLM 模型推理** — 使用视觉语言模型生成图片描述
            3. **文本后处理** — 清洗 VLM 输出，结构化存储
            4. **向量索引** — 将描述文本转为向量，写入知识库
            """
        )

        if st.button("生成图片描述", key="btn_index"):
            with st.spinner("VLM 推理中（模拟）..."):
                try:
                    indexer = ImageIndexer()
                    info = indexer.load_image(st.session_state.buffer, file_name)
                    desc = indexer.get_vlm_description()
                    st.success("描述生成完成")
                    st.markdown(desc)
                    if info["is_image"]:
                        st.caption(
                            f"图片信息: {info['width']}×{info['height']} {info['format']} "
                            f"({info['size_bytes']:,} bytes)"
                        )
                except Exception as exc:
                    st.error(f"索引失败: {exc}")
    else:
        st.info("当前文件非图片格式。上传图片文件（PNG / JPG / GIF / BMP / WebP）后可使用此功能。")

        st.markdown("#### VLM 处理流水线（说明）")
        st.markdown(
            """
            图片索引功能支持以下流程：

            1. **图片预处理** — 调整尺寸、格式标准化
            2. **VLM 模型推理** — 使用视觉语言模型生成图片描述
            3. **文本后处理** — 清洗 VLM 输出，结构化存储
            4. **向量索引** — 将描述文本转为向量，写入知识库

            > 📌 请上传图片文件以体验完整的图片索引流程。
            """
        )


