from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .profiles import Slot

@dataclass(frozen=True)
class SystemConfig:
    """
    Configuration for one MiSTer 'system' (e.g. Genesis/MegaDrive).
    """

    name: str  # e.g. "Genesis"
    csv_path: Path
    romdir: Path
    outdir: Path
    cache_path: Path

    rbf: str  # e.g. "_Console/MegaDrive"
    setname: str  # e.g. "Genesis"
    prefix_in_core: str  # e.g. "nointro"

    slots: List[Slot]
    facets: List[str]  # e.g. ["publisher","developer","genre","date"]

    genre_depth: int = 2  # 1 or 2
    date_depth: int = 2  # 1=Year, 2=Year/Month, 3=Year/Month/Day

    system: str = ""

    name_source: str = "rom"  # "rom" | "db"
    on_collision: str = "skip-identical"  # "suffix" | "skip-identical"
    write_unmatched: bool = False
    dry_run: bool = False
