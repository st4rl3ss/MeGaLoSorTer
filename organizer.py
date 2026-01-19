from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from .config import SystemConfig
from .csvdb import GameMeta, load_db
from .hashing import HashCache, sha1_file
from .mgl import make_mgl
from .naming import make_display_name, write_mgl_file
from .util import menu_folder, safe_name

GENRE_RE = re.compile(r"#genre:([^\s>]+)(?:>([^\s]+))?")


MONTH_NAMES = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]


def date_parts(release_date: str, depth: int) -> List[str]:
    """
    release_date: YYYY or YYYY-MM or YYYY-MM-DD (or empty)
    depth: 1=Year, 2=Year/MonthName, 3=Year/MonthName/Day(01..31)
    Stops early if month/day missing.
    """
    s = (release_date or "").strip()
    if not s:
        return ["Unknown"]

    parts = s.split("-")
    year = parts[0].strip() if len(parts) >= 1 else ""
    if not year.isdigit() or len(year) != 4:
        return ["Unknown"]

    out = [year]

    if depth >= 2 and len(parts) >= 2 and parts[1].isdigit():
        m = int(parts[1])
        if 1 <= m <= 12:
            out.append(MONTH_NAMES[m - 1])

    if depth >= 3 and len(parts) >= 3 and parts[2].isdigit():
        d = int(parts[2])
        if 1 <= d <= 31:
            out.append(f"{d:02d}")

    return out


def iter_roms(root: Path, exts: set[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def genre_buckets(tags: str, depth: int) -> List[List[str]]:
    hits: List[List[str]] = []
    for tok in (tags or "").split():
        m = GENRE_RE.match(tok)
        if not m:
            continue
        a = safe_name(m.group(1))
        b = m.group(2)
        parts = [a]
        if depth >= 2 and b:
            parts.append(safe_name(b))
        hits.append(parts)
    return hits if hits else [["Unknown"]]


def buckets_for(meta: GameMeta, facet: str, genre_depth: int, date_depth: int) -> List[List[str]]:
    facet = facet.lower()

    if facet == "publisher":
        return [[safe_name(meta.publisher)]]

    if facet == "developer":
        return [[safe_name(meta.developer)]]

    if facet == "year":
        y = meta.release_date.split("-")[0].strip() if meta.release_date else "Unknown"
        return [[safe_name(y)]]

    if facet == "date":
        return [[safe_name(p) for p in date_parts(meta.release_date, date_depth)]]

    if facet == "genre":
        return genre_buckets(meta.tags, genre_depth)

    raise ValueError(f"Unknown facet: {facet}")


def run_system(cfg: SystemConfig) -> int:
    if not cfg.csv_path.exists():
        raise SystemExit(f"[ERR] CSV not found: {cfg.csv_path}")
    if not cfg.romdir.exists():
        raise SystemExit(f"[ERR] ROM dir not found: {cfg.romdir}")

    db = load_db(cfg.csv_path, verbose=True)

    all_files = list(cfg.romdir.rglob("*"))
    ext_counts = Counter(p.suffix.lower() for p in all_files if p.is_file())
    print(f"[ROMDIR] {cfg.romdir}  files={sum(ext_counts.values()):,}")
    print(f"[ROMDIR] top extensions: {ext_counts.most_common(8)}")

    exts = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in cfg.exts}
    roms = list(iter_roms(cfg.romdir, exts))
    print(f"[ROMDIR] ROM candidates={len(roms):,}  (exts={sorted(exts)})")
    if not roms:
        raise SystemExit("[ERR] No ROM candidates found. Adjust extensions or folder.")

    # Ensure output directory exists so SQLite can create/open the cache DB.
    cfg.outdir.mkdir(parents=True, exist_ok=True)
    cache = HashCache(cfg.outdir / "hashcache.sqlite")  # per-output cache by default


    matched = unmatched = written = 0
    try:
        for rom in roms:
            sha1 = cache.get_or_compute_sha1(rom)
            meta = db.get(sha1)

            rel_inside_romdir = rom.relative_to(cfg.romdir).as_posix()
            mgl_target_path = f"{cfg.prefix_in_core}/{rel_inside_romdir}"

            mgl_text = make_mgl(
                rbf=cfg.rbf,
                setname=cfg.setname,
                delay=cfg.file_delay,
                ftype=cfg.file_type,
                index=cfg.file_index,
                rel_path_from_core_games_folder=mgl_target_path,
            )

            if meta:
                matched += 1
                display = make_display_name(meta, rom, cfg.name_source)

                if not cfg.dry_run:
                    for facet in cfg.facets:
                        for parts in buckets_for(meta, facet, cfg.genre_depth, cfg.date_depth):
                            # underscore jungle: EVERY folder in path gets underscore
                            folder = cfg.outdir / menu_folder(facet.title()) / Path(*[menu_folder(p) for p in parts])
                            folder.mkdir(parents=True, exist_ok=True)

                            target = folder / f"{display}.mgl"
                            if write_mgl_file(target, mgl_text, cfg.on_collision):
                                written += 1
            else:
                unmatched += 1
                if cfg.write_unmatched and not cfg.dry_run:
                    display = make_display_name(None, rom, "rom")
                    folder = cfg.outdir / menu_folder("Unmatched")
                    folder.mkdir(parents=True, exist_ok=True)
                    target = folder / f"{display}.mgl"
                    if write_mgl_file(target, mgl_text, cfg.on_collision):
                        written += 1

    finally:
        cache.close()

    total = matched + unmatched
    print("\n[SUMMARY]")
    print(f"  total scanned: {total:,}")
    print(f"  matched:       {matched:,}")
    print(f"  unmatched:     {unmatched:,}")
    if total:
        print(f"  match rate:    {matched/total*100:.1f}%")
    if cfg.dry_run:
        print("\n(dry-run) No MGL files were written.")
    else:
        print(f"\nWrote MGL files: {written:,}")
        print(f"Output folder:   {cfg.outdir.resolve()}")

    return 0
