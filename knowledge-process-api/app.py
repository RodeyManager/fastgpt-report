"""Knowledge Process API — FastAPI REST server for document processing pipeline.

Endpoints:
  POST /api/parse       — Parse uploaded files (PDF, DOCX, CSV, XLSX, PPTX, TXT, MD, HTML)
  POST /api/convert     — Convert raw text to Markdown
  POST /api/clean       — Clean text with configurable options
  POST /api/chunk       — Split text into chunks
  POST /api/index-image — Image indexing with VLM description
  GET  /api/health      — Health check

Run:
  uvicorn app:app --reload --port 8000
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Ensure the local ``src`` package is importable
# ---------------------------------------------------------------------------
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from fastgpt_demo.parsers import ParseResult, parse_file  # noqa: E402
from fastgpt_demo.converters import convert_to_markdown, convert_to_markdown_multi  # noqa: E402
from fastgpt_demo.cleaners import clean_text  # noqa: E402
from fastgpt_demo.chunkers import split_text_2_chunks  # noqa: E402
from fastgpt_demo.indexers import ImageIndexer  # noqa: E402

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Knowledge Process API",
    version="1.0.0",
    description="FastGPT 知识库文档处理 REST API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


ALLOWED_MD_TOOLS = ["markdownify", "markitdown"]


class ToolResult(BaseModel):
    tool: str
    markdown: str
    note: str
    duration_ms: float


class ConvertRequest(BaseModel):
    raw_text: str
    format_text: str
    file_ext: str
    tools: list[str] = ["markitdown"]

    @field_validator("tools")
    @classmethod
    def validate_tools(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one tool must be selected")
        if len(v) > 2:
            raise ValueError("Maximum 2 tools can be selected")
        for tool in v:
            if tool not in ALLOWED_MD_TOOLS:
                raise ValueError(f"Unknown tool: {tool}. Allowed: {ALLOWED_MD_TOOLS}")
        return v


class ConvertResponse(BaseModel):
    results: list[ToolResult]


class CleanOptions(BaseModel):
    trim: bool = True
    normalize_unicode: bool = True
    remove_invisible_chars: bool = True
    remove_chinese_space: bool = True
    normalize_newline: bool = True
    fix_hyphenation: bool = True
    collapse_whitespace: bool = True
    remove_empty_lines: bool = True
    filter_watermark: bool = False
    watermark_keywords: list[str] = []
    watermark_min_repeat: int = 2
    watermark_max_line_length: int = 30
    deduplicate_paragraphs: bool = False
    dedup_fuzzy: bool = False
    dedup_fuzzy_threshold: float = 0.9
    clean_table: bool = False
    mask_sensitive: bool = False
    filter_special_chars: bool = False
    clean_markdown_links: bool = True
    remove_md_escapes: bool = True
    clean_md_structure: bool = True
    filter_toc: bool = False
    filter_page_numbers: bool = False
    process_footnotes: bool = False
    footnote_action: str = "remove"
    remove_html_comments: bool = False
    normalize_html_entities: bool = False
    filter_html_noise: bool = False
    html_noise_patterns: list[str] = []
    html_ad_keywords: list[str] = []


class CleanRequest(BaseModel):
    text: str
    options: CleanOptions = Field(default_factory=CleanOptions)
    profile: str = "default"


class CleanResponse(BaseModel):
    cleaned: str


class ChunkRequest(BaseModel):
    text: str
    chunk_size: int = 500
    overlap_ratio: float = 0.2
    paragraph_chunk_deep: int = 2


class ChunkResponse(BaseModel):
    chunks: list[str]
    chars: int


class ParseResponse(BaseModel):
    raw_text: str
    format_text: str
    html_preview: str
    image_list: list
    sheet_names: Optional[list[str]] = None


class ImageIndexResponse(BaseModel):
    description: str
    width: int
    height: int
    format: str
    size_bytes: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/parse", response_model=ParseResponse)
async def parse(
    file: UploadFile = File(...),
    method: str = Form("auto"),
    engine: str = Form("fastgpt"),
    header_footer_ratio: float = Form(0.05),
    remove_html_noise: bool = Form(True),
):
    """Parse an uploaded document and extract raw text, formatted text, etc.

    Args:
        header_footer_ratio: Fraction of page height to filter as header/footer
            (PDF only). Default 0.05 (5%). Set to 0 to disable.
        remove_html_noise: Remove noise tags (nav/footer/header/aside/etc.) from
            HTML files. Default True.
    """
    try:
        buffer = await file.read()
        result: ParseResult = parse_file(
            buffer, file.filename or "unknown.txt", method, engine,
            header_footer_ratio=header_footer_ratio,
            remove_html_noise=remove_html_noise,
        )
        return ParseResponse(
            raw_text=result.raw_text,
            format_text=result.format_text,
            html_preview=result.html_preview,
            image_list=result.image_list,
            sheet_names=result.sheet_names,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Parse failed: {exc}") from exc


@app.post("/api/convert", response_model=ConvertResponse)
async def convert(req: ConvertRequest):
    """Convert raw text to Markdown using selected tools."""
    try:
        results = convert_to_markdown_multi(
            req.raw_text, req.format_text, req.file_ext, req.tools
        )
        return ConvertResponse(results=[ToolResult(**r) for r in results])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Convert failed: {exc}") from exc


@app.post("/api/clean", response_model=CleanResponse)
async def clean(req: CleanRequest):
    """Clean text with configurable options."""
    try:
        from fastgpt_demo.cleaners.profiles import get_profile as _get_profile
        opts = req.options.model_dump()
        default_opts = CleanOptions().model_dump()
        if opts == default_opts and req.profile != "default":
            p = _get_profile(req.profile)
            if p:
                opts = p.to_options_dict()
        cleaned = clean_text(req.text, opts)
        return CleanResponse(cleaned=cleaned)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Clean failed: {exc}") from exc


@app.post("/api/chunk", response_model=ChunkResponse)
async def chunk(req: ChunkRequest):
    """Split text into chunks."""
    try:
        result = split_text_2_chunks(
            req.text,
            chunk_size=req.chunk_size,
            overlap_ratio=req.overlap_ratio,
            paragraph_chunk_deep=req.paragraph_chunk_deep,
        )
        return ChunkResponse(chunks=result["chunks"], chars=result["chars"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chunk failed: {exc}") from exc


@app.post("/api/index-image", response_model=ImageIndexResponse)
async def index_image(file: UploadFile = File(...)):
    """Index an uploaded image: extract metadata and generate VLM description."""
    try:
        buffer = await file.read()
        indexer = ImageIndexer()
        info = indexer.load_image(buffer, file.filename or "unknown.png")
        description = indexer.get_vlm_description()
        return ImageIndexResponse(
            description=description,
            width=info["width"],
            height=info["height"],
            format=info["format"] or "",
            size_bytes=info["size_bytes"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image index failed: {exc}") from exc
