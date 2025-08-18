"""Load special name mappings from packaged JSON (works after install)."""
from __future__ import annotations

import json
from typing import Dict, Union
import importlib.resources as resources

_JSON_PACKAGE = "baseball_data_lab"
_JSON_PATH = ("data", "special_name_mappings.json")

def _load_mappings() -> Dict[str, Dict[str, Union[int, str]]]:
    # Access the file from the installed package (zip-safe)
    path = resources.files(_JSON_PACKAGE).joinpath(*_JSON_PATH)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Missing package data file: {path}. "
            "Ensure it's included via setuptools package-data/MANIFEST.in."
        ) from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e

SpecialNameMappings: Dict[str, Dict[str, Union[int, str]]] = _load_mappings()

__all__ = ["SpecialNameMappings"]

