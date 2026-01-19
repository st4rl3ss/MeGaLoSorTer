from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

# Your CSV headers
CSV_SHA1 = "SHA1"
CSV_MD5 = "MD5"
CSV_TITLE = "Screen title @ Exact"
CSV_ID = "ID"
CSV_REGION = "Region"
CSV_DATE = "Release date"
CSV_DEV = "Developer"
CSV_PUB = "Publisher"
CSV_TAGS = "Tags"


@dataclass(frozen=True)
class GameMeta:
    title: str
    game_id: str
    region: str
    release_date: str
    developer: str
    publisher: str
    tags: str
    sha1: str
    md5: str


def detect_csv_dialect(csv_path: Path) -> csv.Dialect:
    sample = csv_path.read_text(encoding="utf-8", errors="replace")[:50_000]
    try:
        return csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
    except Exception:
        class Comma(csv.Dialect):
            delimiter = ","
            quotechar = '"'
            doublequote = True
            skipinitialspace = False
            lineterminator = "\n"
            quoting = csv.QUOTE_MINIMAL
        return Comma()


def load_db(csv_path: Path, verbose: bool = True) -> Dict[str, GameMeta]:
    dialect = detect_csv_dialect(csv_path)
    if verbose:
        print(f"[CSV] delimiter={repr(dialect.delimiter)}  file={csv_path}")

    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f, dialect=dialect)
        if not reader.fieldnames:
            raise SystemExit("[CSV] No headers found.")
        if verbose:
            print(f"[CSV] headers({len(reader.fieldnames)}): {reader.fieldnames}")

        missing = [h for h in [CSV_SHA1, CSV_TITLE, CSV_ID] if h not in reader.fieldnames]
        if missing:
            raise SystemExit(f"[CSV] Missing required headers: {missing}")

        by_sha1: Dict[str, GameMeta] = {}
        for row in reader:
            sha1 = (row.get(CSV_SHA1) or "").strip().lower()
            if not sha1:
                continue
            meta = GameMeta(
                title=(row.get(CSV_TITLE) or "").strip(),
                game_id=(row.get(CSV_ID) or "").strip(),
                region=(row.get(CSV_REGION) or "").strip(),
                release_date=(row.get(CSV_DATE) or "").strip(),
                developer=(row.get(CSV_DEV) or "").strip(),
                publisher=(row.get(CSV_PUB) or "").strip(),
                tags=(row.get(CSV_TAGS) or "").strip(),
                sha1=sha1,
                md5=(row.get(CSV_MD5) or "").strip().lower(),
            )
            by_sha1.setdefault(sha1, meta)

    if verbose:
        print(f"[DB] entries indexed by SHA1: {len(by_sha1):,}")
    return by_sha1
