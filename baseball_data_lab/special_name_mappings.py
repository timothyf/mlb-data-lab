"""Load special name mappings from JSON."""
from __future__ import annotations

import json
from pathlib import Path

_MAPPING_FILE = Path(__file__).parent / "data" / "special_name_mappings.json"

with _MAPPING_FILE.open(encoding="utf-8") as f:
    SpecialNameMappings: dict[str, dict[str, int | str]] = json.load(f)

__all__ = ["SpecialNameMappings"]
