from __future__ import annotations

from pathlib import PurePosixPath

from .base import CleanProfile

_PROFILE_REGISTRY: dict[str, CleanProfile] = {}

_EXT_PROFILE_MAP: dict[str, str] = {
    ".pdf": "pdf_academic",
    ".docx": "docx_report",
    ".doc": "docx_report",
    ".csv": "table_data",
    ".xlsx": "table_data",
    ".xls": "table_data",
    ".html": "web_content",
    ".htm": "web_content",
}


def register_profile(profile: CleanProfile) -> None:
    _PROFILE_REGISTRY[profile.name] = profile


def get_profile(name: str) -> CleanProfile | None:
    return _PROFILE_REGISTRY.get(name)


def get_profile_for_file(filename: str) -> CleanProfile | None:
    ext = PurePosixPath(filename).suffix.lower()
    profile_name = _EXT_PROFILE_MAP.get(ext)
    if profile_name:
        return get_profile(profile_name)
    return None


def get_all_profiles() -> list[CleanProfile]:
    return list(_PROFILE_REGISTRY.values())


def clear_profiles() -> None:
    _PROFILE_REGISTRY.clear()
