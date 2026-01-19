from __future__ import annotations

from pathlib import Path


INVALID_CHARS = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]


def safe_name(s: str) -> str:
    s = (s or "").strip()
    for ch in INVALID_CHARS:
        s = s.replace(ch, "_")
    s = " ".join(s.split())
    return s if s else "Unknown"


def menu_folder(name: str) -> str:
    """MiSTer Menu shows only folders that start with '_'."""
    n = safe_name(name)
    return n if n.startswith("_") else f"_{n}"


def truncate_filename(name: str, max_len: int = 160) -> str:
    return name if len(name) <= max_len else name[:max_len].rstrip()


def unique_path(p: Path) -> Path:
    if not p.exists():
        return p
    stem, suf = p.stem, p.suffix
    i = 2
    while True:
        q = p.with_name(f"{stem}__{i}{suf}")
        if not q.exists():
            return q
        i += 1
