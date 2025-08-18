"""Top level package for :mod:`baseball_data_lab`.

This module exposes the core public classes and the package version.  The
``__version__`` attribute is populated from the installed package metadata and
falls back to the package's development version when the metadata is
unavailable (for example, when running directly from a source checkout).
"""

from importlib.metadata import PackageNotFoundError, version

try:  # pragma: no cover - version may not be available in development
    __version__ = version("baseball-data-lab")
except PackageNotFoundError:  # pragma: no cover - fallback for local usage
    __version__ = "0.1.0"

from .player.player import Player
from .summary_sheets.pitcher_summary_sheet import PitcherSummarySheet
from .summary_sheets.batter_summary_sheet import BatterSummarySheet
from .exceptions import (
    NoFangraphsIdError,
    PlayerNotFoundError,
    PositionMismatchError,
    NoStatsError,
    StatFetchError,
)

__all__ = [
    "Player",
    "PitcherSummarySheet",
    "BatterSummarySheet",
    "NoFangraphsIdError",
    "PlayerNotFoundError",
    "PositionMismatchError",
    "NoStatsError",
    "StatFetchError",
    "__version__",
]
