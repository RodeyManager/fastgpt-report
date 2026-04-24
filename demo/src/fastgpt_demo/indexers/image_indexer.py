"""Image indexer: preview loading + VLM concept description."""

from __future__ import annotations

from io import BytesIO

from PIL import Image

# Supported image extensions (lowercase)
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}


class ImageIndexer:
    """Load images for preview and describe the VLM indexing pipeline."""

    def load_image(self, buffer: bytes, filename: str) -> dict:
        """Load an image from bytes.

        Args:
            buffer: Raw file bytes.
            filename: Original filename (used for extension check).

        Returns:
            Dict with preview, width, height, format, size_bytes, is_image.
        """
        result: dict = {
            "preview": None,
            "width": 0,
            "height": 0,
            "format": None,
            "size_bytes": len(buffer),
            "is_image": False,
        }

        ext = _get_extension(filename)
        if ext not in SUPPORTED_EXTENSIONS:
            return result

        # SVG cannot be opened by Pillow
        if ext == ".svg":
            result["format"] = "SVG"
            result["is_image"] = False
            return result

        try:
            img = Image.open(BytesIO(buffer))
            img.load()  # force full decode to catch corrupt files
        except Exception:
            return result

        result["preview"] = img
        result["width"] = img.width
        result["height"] = img.height
        result["format"] = (img.format or ext.lstrip(".")).upper()
        result["is_image"] = True
        return result

    @staticmethod
    def get_vlm_description() -> str:
        """Return a static description of the VLM indexing pipeline."""
        return (
            "图片通过视觉语言模型自动生成描述文本，支持：\n"
            "- 自动识别图中文字 (OCR)\n"
            "- 场景与物体描述\n"
            "- 图表数据解读\n"
            "- 生成可检索的语义向量\n"
            "\n"
            "流程：图片上传 → VLM 模型描述 → 文本向量化 → 存入向量数据库 → 支持语义检索"
        )


def _get_extension(filename: str) -> str:
    """Return lowercase extension including the dot, e.g. '.png'."""
    dot = filename.rfind(".")
    if dot == -1:
        return ""
    return filename[dot:].lower()
