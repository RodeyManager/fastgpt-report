"""Document parsing accuracy comparison tool.

Compares 5 parsing methods (FastGPT, MinerU, Unstructured-API, Marker, Docling)
using LLM-based accuracy evaluation.

Usage:
    python parse_comparison.py

Environment variables:
    LLM_API_KEY      - API key for LLM evaluation (default: reads from env)
    LLM_BASE_URL     - LLM API base URL (default: https://api.openai.com/v1)
    LLM_MODEL        - Model name (default: gpt-4o)
    MINERU_API_URL   - MinerU service URL (default: http://127.0.0.1:8000/file_parse)
    UNSTRUCTURED_API_URL - Unstructured-API URL (default: http://localhost:9500/general/v0/general)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project src to path
_PROJECT_SRC = Path(__file__).resolve().parent / "src"
if str(_PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(_PROJECT_SRC))

from fastgpt_demo.parsers import parse_file, ParseResult


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SOURCE_DIR = Path(r"E:\dify\RAG文件\RAG文件 (2)")
OUTPUT_BASE_DIR = Path(r"E:\dify\RAG\FastgptReport")
REPORT_DIR = Path(r"E:\dify\RAG文件\FastgptReport")

PARSERS = ["fastgpt", "mineru", "unstructured", "marker", "docling"]

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.moonshot.cn/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "kimi-k2-6")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

# Evaluation prompt template
EVALUATION_PROMPT = """你是一位文档解析质量评估专家。请对以下文档解析结果进行质量评分。

## 评分维度（每个维度0-100分）

1. **文本完整性** (completeness): 文档内容是否被完整提取，有无遗漏段落、章节或重要信息
2. **格式保留度** (formatting): 标题层级、列表、表格、段落等格式结构是否被正确保留
3. **语义准确性** (semantic_accuracy): 文本内容是否保持原意，有无错字、乱码、语义断裂
4. **结构清晰度** (structure): 文档的逻辑结构（章节、段落、表格）是否清晰可辨
5. **特殊元素处理** (special_elements): 表格、公式、图片说明等特殊元素的处理质量

## 输入

原始文件名: {filename}

解析结果（Markdown格式）:
```markdown
{content}
```

## 输出要求

请严格按照以下JSON格式返回评分结果，不要添加任何其他内容：

```json
{{
  "completeness": 85,
  "formatting": 80,
  "semantic_accuracy": 90,
  "structure": 85,
  "special_elements": 75,
  "overall_score": 83,
  "summary": "简要评价该解析结果的质量，包括优点和不足之处",
  "issues": ["发现的具体问题1", "问题2"]
}}
```

注意：
- overall_score 是五个维度的加权平均分
- 评分标准：90-100优秀，80-89良好，70-79一般，60-69及格，<60不及格
- issues 数组列出发现的具体问题，如果没有重大问题可以留空
"""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class EvaluationResult:
    """LLM evaluation result for a single parser output."""
    parser: str
    filename: str
    completeness: int = 0
    formatting: int = 0
    semantic_accuracy: int = 0
    structure: int = 0
    special_elements: int = 0
    overall_score: int = 0
    summary: str = ""
    issues: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class FileComparisonResult:
    """Comparison results for a single file across all parsers."""
    filename: str
    file_size: int
    parser_results: dict[str, ParseResult] = field(default_factory=dict)
    evaluations: dict[str, EvaluationResult] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# LLM Evaluation
# ---------------------------------------------------------------------------

def evaluate_with_llm(content: str, filename: str) -> dict[str, Any]:
    """Use LLM to evaluate parsing quality.
    
    Returns parsed JSON dict with scores.
    """
    import openai
    
    client = openai.OpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
    )
    
    # Truncate content if too long (LLM context limit)
    max_chars = 8000
    truncated_content = content[:max_chars]
    if len(content) > max_chars:
        truncated_content += f"\n\n... [内容已截断，原长度: {len(content)} 字符]"
    
    prompt = EVALUATION_PROMPT.format(
        filename=filename,
        content=truncated_content,
    )
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是一个文档解析质量评估专家，请严格按照要求的JSON格式输出评分结果。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        
        result_text = response.choices[0].message.content or "{}"
        
        # Extract JSON from markdown code block if present
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
        elif "```" in result_text:
            json_start = result_text.find("```") + 3
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
        
        return json.loads(result_text)
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Document Parsing
# ---------------------------------------------------------------------------

def parse_document(file_path: Path, parser: str) -> ParseResult:
    """Parse a document using specified parser.
    
    Args:
        file_path: Path to the document file
        parser: Parser name (fastgpt, mineru, unstructured, marker, docling)
    
    Returns:
        ParseResult with parsed content
    """
    buffer = file_path.read_bytes()
    filename = file_path.name
    
    try:
        result = parse_file(buffer, filename, method="auto", engine=parser)
        return result
    except Exception as e:
        # Return error result
        return ParseResult(
            raw_text=f"[Error] {str(e)}",
            format_text=f"[Error] {str(e)}",
            html_preview=f"<div style='color:red'>Error: {str(e)}</div>",
            image_list=[],
        )


# ---------------------------------------------------------------------------
# File Operations
# ---------------------------------------------------------------------------

def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_markdown(content: str, output_path: Path) -> None:
    """Save markdown content to file."""
    output_path.write_text(content, encoding="utf-8")


def get_safe_filename(filename: str) -> str:
    """Convert filename to safe version for filesystem."""
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    safe = filename
    for char in invalid_chars:
        safe = safe.replace(char, '_')
    return safe


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def generate_comparison_report(results: list[FileComparisonResult]) -> str:
    """Generate markdown comparison report.
    
    Args:
        results: List of comparison results for each file
    
    Returns:
        Markdown formatted report string
    """
    lines = []
    
    # Header
    lines.append("# 文档解析准确度对比测试报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**测试文件数**: {len(results)}")
    lines.append(f"**测试解析器**: {', '.join(PARSERS)}")
    lines.append(f"**评估模型**: {LLM_MODEL}")
    lines.append("")
    
    # Summary table
    lines.append("## 总体评分汇总")
    lines.append("")
    lines.append("| 文件名 | " + " | ".join(PARSERS) + " |")
    lines.append("|" + "---|" * (len(PARSERS) + 1))
    
    for file_result in results:
        row = [file_result.filename]
        for parser in PARSERS:
            eval_result = file_result.evaluations.get(parser)
            if eval_result and eval_result.error:
                row.append(f"❌ 错误")
            elif eval_result:
                row.append(f"{eval_result.overall_score}")
            else:
                row.append("-")
        lines.append("| " + " | ".join(row) + " |")
    
    lines.append("")
    
    # Average scores
    lines.append("### 平均分统计")
    lines.append("")
    lines.append("| 解析器 | 平均分 | 最高分 | 最低分 |")
    lines.append("|--------|--------|--------|--------|")
    
    for parser in PARSERS:
        scores = [
            r.evaluations[parser].overall_score
            for r in results
            if parser in r.evaluations and r.evaluations[parser].error is None
        ]
        if scores:
            avg = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            lines.append(f"| {parser} | {avg:.1f} | {max_score} | {min_score} |")
        else:
            lines.append(f"| {parser} | - | - | - |")
    
    lines.append("")
    
    # Detailed results per file
    lines.append("## 详细评测结果")
    lines.append("")
    
    for file_result in results:
        lines.append(f"### {file_result.filename}")
        lines.append("")
        lines.append(f"**文件大小**: {file_result.file_size:,} bytes")
        lines.append("")
        
        for parser in PARSERS:
            eval_result = file_result.evaluations.get(parser)
            if not eval_result:
                continue
            
            lines.append(f"#### {parser}")
            lines.append("")
            
            if eval_result.error:
                lines.append(f"**状态**: ❌ 错误 - {eval_result.error}")
            else:
                lines.append(f"**总体评分**: {eval_result.overall_score}/100")
                lines.append("")
                lines.append("| 维度 | 分数 |")
                lines.append("|------|------|")
                lines.append(f"| 文本完整性 | {eval_result.completeness} |")
                lines.append(f"| 格式保留度 | {eval_result.formatting} |")
                lines.append(f"| 语义准确性 | {eval_result.semantic_accuracy} |")
                lines.append(f"| 结构清晰度 | {eval_result.structure} |")
                lines.append(f"| 特殊元素处理 | {eval_result.special_elements} |")
                lines.append("")
                lines.append(f"**评价摘要**: {eval_result.summary}")
                lines.append("")
                
                if eval_result.issues:
                    lines.append("**发现问题**:")
                    for issue in eval_result.issues:
                        lines.append(f"- {issue}")
                    lines.append("")
            
            lines.append("")
    
    # Conclusion
    lines.append("## 结论与建议")
    lines.append("")
    
    # Calculate overall rankings
    parser_avg_scores = {}
    for parser in PARSERS:
        scores = [
            r.evaluations[parser].overall_score
            for r in results
            if parser in r.evaluations and r.evaluations[parser].error is None
        ]
        if scores:
            parser_avg_scores[parser] = sum(scores) / len(scores)
    
    if parser_avg_scores:
        ranked = sorted(parser_avg_scores.items(), key=lambda x: x[1], reverse=True)
        lines.append("### 综合排名")
        lines.append("")
        for i, (parser, score) in enumerate(ranked, 1):
            lines.append(f"{i}. **{parser}**: {score:.1f}分")
        lines.append("")
    
    lines.append("### 各解析器特点分析")
    lines.append("")
    lines.append("- **FastGPT**: 项目内置解析器，基于 PyMuPDF/mammoth 等库，支持多种格式")
    lines.append("- **MinerU**: 高质量PDF解析，支持表格识别、公式提取、版面还原")
    lines.append("- **Unstructured-API**: 通用文档解析API，支持多种策略（hi_res/fast）")
    lines.append("- **Marker**: 专注PDF到Markdown转换，速度快，准确度高")
    lines.append("- **Docling**: IBM开源文档理解框架，支持多种格式和深度解析")
    lines.append("")
    
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main Workflow
# ---------------------------------------------------------------------------

def run_comparison() -> None:
    """Run the full comparison workflow."""
    print("=" * 60)
    print("文档解析准确度对比测试工具")
    print("=" * 60)
    print()
    
    # Check source directory
    if not SOURCE_DIR.exists():
        print(f"❌ 源目录不存在: {SOURCE_DIR}")
        return
    
    # Check LLM API key
    if not LLM_API_KEY:
        print("⚠️ 警告: 未设置 LLM_API_KEY 环境变量，将跳过LLM评估")
        print("请设置环境变量: LLM_API_KEY=your_api_key")
        print()
    
    # Create output directories
    print("📁 创建输出目录...")
    for parser in PARSERS:
        parser_dir = OUTPUT_BASE_DIR / parser
        ensure_dir(parser_dir)
        print(f"  ✓ {parser_dir}")
    ensure_dir(REPORT_DIR)
    print(f"  ✓ {REPORT_DIR}")
    print()
    
    # Get all files
    files = [f for f in SOURCE_DIR.iterdir() if f.is_file()]
    print(f"📄 发现 {len(files)} 个待测试文件")
    print()
    
    # Process each file
    all_results: list[FileComparisonResult] = []
    
    for file_idx, file_path in enumerate(files, 1):
        print(f"[{file_idx}/{len(files)}] 处理文件: {file_path.name}")
        
        file_result = FileComparisonResult(
            filename=file_path.name,
            file_size=file_path.stat().st_size,
        )
        
        # Parse with each parser (sequential to avoid resource conflicts)
        for parser in PARSERS:
            print(f"  🔍 使用 {parser} 解析...", end=" ")
            
            try:
                result = parse_document(file_path, parser)
                file_result.parser_results[parser] = result
                
                # Save markdown output
                safe_name = get_safe_filename(file_path.stem) + ".md"
                output_path = OUTPUT_BASE_DIR / parser / safe_name
                save_markdown(result.format_text or result.raw_text, output_path)
                print(f"✓ 已保存")
                
            except Exception as e:
                print(f"✗ 错误: {e}")
                file_result.parser_results[parser] = ParseResult(
                    raw_text=f"[Error] {str(e)}",
                    format_text=f"[Error] {str(e)}",
                    html_preview="",
                    image_list=[],
                )
        
        # Evaluate with LLM
        if LLM_API_KEY:
            print(f"  🤖 LLM评估中...")
            for parser in PARSERS:
                result = file_result.parser_results.get(parser)
                if not result:
                    continue
                
                content = result.format_text or result.raw_text
                if content.startswith("[Error]"):
                    eval_result = EvaluationResult(
                        parser=parser,
                        filename=file_path.name,
                        error=content,
                    )
                else:
                    print(f"    评估 {parser}...", end=" ")
                    eval_data = evaluate_with_llm(content, file_path.name)
                    
                    if "error" in eval_data:
                        eval_result = EvaluationResult(
                            parser=parser,
                            filename=file_path.name,
                            error=eval_data["error"],
                        )
                        print(f"✗ {eval_data['error']}")
                    else:
                        eval_result = EvaluationResult(
                            parser=parser,
                            filename=file_path.name,
                            completeness=eval_data.get("completeness", 0),
                            formatting=eval_data.get("formatting", 0),
                            semantic_accuracy=eval_data.get("semantic_accuracy", 0),
                            structure=eval_data.get("structure", 0),
                            special_elements=eval_data.get("special_elements", 0),
                            overall_score=eval_data.get("overall_score", 0),
                            summary=eval_data.get("summary", ""),
                            issues=eval_data.get("issues", []),
                        )
                        print(f"✓ 评分: {eval_result.overall_score}")
                
                file_result.evaluations[parser] = eval_result
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
        
        all_results.append(file_result)
        print()
    
    # Generate report
    print("📊 生成对比报告...")
    report_content = generate_comparison_report(all_results)
    
    report_path = REPORT_DIR / f"parse_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report_content, encoding="utf-8")
    print(f"✓ 报告已保存: {report_path}")
    print()
    
    # Print summary
    print("=" * 60)
    print("测试完成!")
    print("=" * 60)
    print(f"📁 解析结果保存位置: {OUTPUT_BASE_DIR}")
    print(f"📊 对比报告保存位置: {report_path}")
    print()
    
    if LLM_API_KEY:
        print("📈 平均分统计:")
        for parser in PARSERS:
            scores = [
                r.evaluations[parser].overall_score
                for r in all_results
                if parser in r.evaluations and r.evaluations[parser].error is None
            ]
            if scores:
                avg = sum(scores) / len(scores)
                print(f"  {parser:15s}: {avg:.1f}")


if __name__ == "__main__":
    run_comparison()
