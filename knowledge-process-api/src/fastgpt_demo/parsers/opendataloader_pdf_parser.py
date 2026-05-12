"""
OpenDataLoader-PDF 解析器
使用本地 Docling Python 库直接解析 PDF（无需外部 HTTP 服务）
"""

from __future__ import annotations

import io
import traceback
from typing import Optional

from docling.datamodel.base_models import DocumentStream
from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter

from ._types import ParseResult

# 全局转换器实例（懒加载，首次使用时初始化）
_converter: Optional[DocumentConverter] = None


def _get_converter() -> DocumentConverter:
    """获取或初始化 DocumentConverter 实例。"""
    global _converter
    if _converter is None:
        _converter = DocumentConverter()
    return _converter


def _extract_text_from_result(result: ConversionResult) -> str:
    """从 Docling 转换结果中提取纯文本内容。"""
    doc = result.document
    if not doc:
        return ""
    
    # 使用 export_to_text 获取纯文本
    return doc.export_to_text()


def _extract_tables_as_markdown(result: ConversionResult) -> str:
    """从 Docling 转换结果中提取表格并转为 Markdown。"""
    doc = result.document
    if not doc or not doc.tables:
        return ""
    
    md_tables = []
    for table in doc.tables:
        try:
            # 尝试导出为 DataFrame，然后转为 Markdown
            import pandas as pd
            df = table.export_to_dataframe(doc=doc)
            if df is not None and not df.empty:
                md_table = df.to_markdown(index=False)
                md_tables.append(md_table)
        except Exception:
            # 如果表格导出失败，跳过
            continue
    
    return "\n\n".join(md_tables)


def parse_opendataloader_pdf(
    buffer: bytes,
    timeout: float = 120.0,
) -> ParseResult:
    """通过本地 Docling 库解析 PDF（同步版本）"""
    try:
        converter = _get_converter()
        
        # 将 bytes 包装为 DocumentStream
        buf = io.BytesIO(buffer)
        source = DocumentStream(name="input.pdf", stream=buf)
        
        # 执行转换
        result = converter.convert(source)
        
        # 检查转换状态
        if result.status.value != "success":
            errors = [str(e) for e in result.errors] if result.errors else ["未知错误"]
            raise RuntimeError(f"Docling 解析失败: {errors[0]}")
        
        # 提取文本和表格
        text_content = _extract_text_from_result(result)
        table_content = _extract_tables_as_markdown(result)
        
        # 组合格式文本
        if table_content:
            format_text = text_content + "\n\n" + table_content
        else:
            format_text = text_content
        
        return ParseResult(
            raw_text=text_content,
            format_text=format_text,
            html_preview="",
            image_list=[],
        )
    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"OpenDataLoader-PDF 解析失败: {e}") from e


async def parse_opendataloader_pdf_async(
    buffer: bytes,
    timeout: float = 120.0,
) -> ParseResult:
    """通过本地 Docling 库解析 PDF（异步版本，供 FastAPI 直接 await）
    
    注意：Docling 的转换器是同步的，我们在线程池中执行以避免阻塞事件循环。
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(
            pool, parse_opendataloader_pdf, buffer, timeout
        )
