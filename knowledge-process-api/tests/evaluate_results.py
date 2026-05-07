"""Evaluate existing parsed results using Kimi K2.6 LLM.

Reads parsed markdown files from E:\dify\RAG\FastgptReport subdirectories
and evaluates them using Kimi API.

Usage:
    python evaluate_results.py

Environment variables:
    LLM_API_KEY  - Kimi API key (required)
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(r"E:\dify\RAG\FastgptReport")
REPORT_DIR = Path(r"E:\dify\RAG\FastgptReport")

PARSERS = ["fastgpt", "mineru", "unstructured", "marker", "docling"]

LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-v4-pro"
LLM_API_KEY = "sk-aaffcda6bd1a426f9df20c344d3394f7"

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
解析工具: {parser}

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
    evaluations: dict[str, EvaluationResult] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# LLM Evaluation
# ---------------------------------------------------------------------------

def evaluate_with_llm(content: str, filename: str, parser: str) -> dict[str, Any]:
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
        parser=parser,
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
            timeout=60,
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
# Report Generation
# ---------------------------------------------------------------------------

def generate_comparison_report(results: list[FileComparisonResult]) -> str:
    """Generate markdown comparison report."""
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
                row.append("❌ 错误")
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

def run_evaluation() -> None:
    """Run evaluation on existing parsed results."""
    print("=" * 60)
    print("Document Parser Evaluation Tool (Kimi K2.6)")
    print("=" * 60)
    print()
    
    # Check API key
    if not LLM_API_KEY:
        print("[ERROR] LLM_API_KEY environment variable not set")
        print("Please set: set LLM_API_KEY=your_moonshot_api_key")
        return
    
    # Check base directory
    if not BASE_DIR.exists():
        print(f"[ERROR] Directory not found: {BASE_DIR}")
        return
    
    # Get all files from first parser directory as reference
    first_parser_dir = BASE_DIR / PARSERS[0]
    if not first_parser_dir.exists():
        print(f"[ERROR] Parser result directory not found: {first_parser_dir}")
        return
    
    # Get list of all filenames (without extension)
    all_files = [f for f in first_parser_dir.iterdir() if f.is_file() and f.suffix == ".md"]
    print(f"Found {len(all_files)} files to evaluate")
    print(f"Evaluating parsers: {', '.join(PARSERS)}")
    print()
    
    # Process each file
    all_results: list[FileComparisonResult] = []
    
    for file_idx, ref_file in enumerate(all_files, 1):
        filename = ref_file.name
        print(f"[{file_idx}/{len(all_files)}] Evaluating file: {filename}")
        
        file_result = FileComparisonResult(filename=filename)
        
        # Evaluate each parser
        for parser in PARSERS:
            parser_file = BASE_DIR / parser / filename
            
            if not parser_file.exists():
                print(f"  [SKIP] {parser}: file not found")
                file_result.evaluations[parser] = EvaluationResult(
                    parser=parser,
                    filename=filename,
                    error="File not found",
                )
                continue
            
            # Read content
            try:
                content = parser_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  [SKIP] {parser}: read failed - {e}")
                file_result.evaluations[parser] = EvaluationResult(
                    parser=parser,
                    filename=filename,
                    error=f"Read failed: {e}",
                )
                continue
            
            # Skip if content is too short or is an error message
            if len(content) < 50 or content.startswith("[Error]"):
                print(f"  [SKIP] {parser}: invalid content")
                file_result.evaluations[parser] = EvaluationResult(
                    parser=parser,
                    filename=filename,
                    error="Invalid content or parse failed",
                )
                continue
            
            # Evaluate with LLM
            print(f"  [EVAL] {parser}...", end=" ")
            eval_data = evaluate_with_llm(content, filename, parser)
            
            if "error" in eval_data:
                eval_result = EvaluationResult(
                    parser=parser,
                    filename=filename,
                    error=eval_data["error"],
                )
                print(f"FAILED: {eval_data['error']}")
            else:
                eval_result = EvaluationResult(
                    parser=parser,
                    filename=filename,
                    completeness=eval_data.get("completeness", 0),
                    formatting=eval_data.get("formatting", 0),
                    semantic_accuracy=eval_data.get("semantic_accuracy", 0),
                    structure=eval_data.get("structure", 0),
                    special_elements=eval_data.get("special_elements", 0),
                    overall_score=eval_data.get("overall_score", 0),
                    summary=eval_data.get("summary", ""),
                    issues=eval_data.get("issues", []),
                )
                print(f"Score: {eval_result.overall_score}")
            
            file_result.evaluations[parser] = eval_result
            
            # Delay to avoid rate limiting
            time.sleep(0.5)
        
        all_results.append(file_result)
        print()
    
    # Generate report
    print("Generating evaluation report...")
    report_content = generate_comparison_report(all_results)
    
    report_path = REPORT_DIR / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report_content, encoding="utf-8")
    print(f"Report saved: {report_path}")
    print()
    
    # Print summary
    print("=" * 60)
    print("Evaluation Complete!")
    print("=" * 60)
    print(f"Report location: {report_path}")
    print()
    
    print("Average Scores:")
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
    run_evaluation()
