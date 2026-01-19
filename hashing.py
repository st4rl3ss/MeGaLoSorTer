from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path


def sha1_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest().lower()


class HashCache:
    """
    SQLite cache keyed by (path,size,mtime) -> sha1.
    Speeds up re-runs massively on big sets.
    """
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS filehash(
                path TEXT PRIMARY KEY,
                size INTEGER NOT NULL,
                mtime REAL NOT NULL,
                sha1 TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def get_or_compute_sha1(self, path: Path) -> str:
        st = path.stat()
        row = self.conn.execute(
            "SELECT size, mtime, sha1 FROM filehash WHERE path=?",
            (str(path),),
        ).fetchone()
        if row and int(row[0]) == st.st_size and float(row[1]) == st.st_mtime:
            return str(row[2])
        digest = sha1_file(path)
        self.conn.execute(
            "INSERT OR REPLACE INTO filehash(path,size,mtime,sha1) VALUES (?,?,?,?)",
            (str(path), st.st_size, st.st_mtime, digest),
        )
        self.conn.commit()
        return digest

    def close(self) -> None:
        self.conn.close()
