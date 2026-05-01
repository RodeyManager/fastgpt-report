from __future__ import annotations

import importlib

from .base import CleanProfile
from .registry import (
    register_profile, get_profile, get_profile_for_file,
    get_all_profiles, clear_profiles,
)

_LOADED = False

_PROFILE_MODULES = [
    "default", "pdf_academic", "pdf_business", "docx_report",
    "table_data", "legal", "web_content",
]


def _load_builtins() -> None:
    global _LOADED
    if _LOADED:
        return
    for mod_name in _PROFILE_MODULES:
        mod = importlib.import_module(f".{mod_name}", package=__package__)
        creator = getattr(mod, "create_profile", None)
        if creator:
            register_profile(creator())
    _LOADED = True


def _reset_loaded() -> None:
    global _LOADED
    _LOADED = False


_load_builtins()

__all__ = [
    "CleanProfile", "register_profile", "get_profile",
    "get_profile_for_file", "get_all_profiles", "clear_profiles",
    "_load_builtins", "_reset_loaded",
]
