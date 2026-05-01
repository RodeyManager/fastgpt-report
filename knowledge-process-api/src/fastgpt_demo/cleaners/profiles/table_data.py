from __future__ import annotations

from .base import CleanProfile
from .default import DEFAULT_RULES, DEFAULT_PARAMS


def create_profile() -> CleanProfile:
    rules = {**DEFAULT_RULES, "clean_table": True}
    return CleanProfile(name="table_data", description="表格数据（CSV/XLSX）", rules=rules, params=DEFAULT_PARAMS)
