from __future__ import annotations

from pathlib import Path
from typing import Optional

from .csvdb import GameMeta
from .util import safe_name, truncate_filename, unique_path


def make_display_name(meta: Optional[GameMeta], rom: Path, name_source: str) -> str:
    """
    name_source:
      - "rom": use curated ROM filename
      - "db":  use PigSaint title + region + id
    """
    if name_source == "rom" or meta is None:
        return truncate_filename(safe_name(rom.stem))

    display = meta.title or rom.stem
    if meta.region:
        display = f"{display} ({meta.region})"
    if meta.game_id:
        display = f"{display} [{meta.game_id}]"
    return truncate_filename(safe_name(display))


def write_mgl_file(target: Path, content: str, on_collision: str) -> bool:
    """
    Returns True if wrote a new file, False if skipped (already identical).
    on_collision:
      - "suffix": always create __2, __3... if target exists
      - "skip-identical": if target exists and content identical, skip; otherwise suffix
    """
    if not target.exists():
        target.write_text(content, encoding="utf-8")
        return True

    if on_collision == "skip-identical":
        try:
            existing = target.read_text(encoding="utf-8")
            if existing == content:
                return False
        except Exception:
            pass

    p2 = unique_path(target)
    p2.write_text(content, encoding="utf-8")
    return True
