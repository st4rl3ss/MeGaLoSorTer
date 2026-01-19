from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SystemProfile:
    system: str
    rbf: str
    setname: str
    file_delay: int
    file_index: int
    file_type: str
    exts: tuple[str, ...]
    prefix_in_core: str = "nointro"


PROFILES: dict[str, SystemProfile] = {
    # Your known-good Genesis/MegaDrive settings (keep as-is)
    "genesis": SystemProfile(
        system="genesis",
        rbf="_Console/MegaDrive",
        setname="Genesis",
        file_delay=1,
        file_index=1,
        file_type="f",
        exts=(".md", ".bin", ".gen", ".smd"),
        prefix_in_core="nointro",
    ),
    # SNES (from MiSTer docs: delay=2, index=0, type=f)
    "snes": SystemProfile(
        system="snes",
        rbf="_Console/SNES",
        setname="SNES",
        file_delay=2,
        file_index=0,
        file_type="f",
        exts=(".sfc", ".smc", ".zip"),
        prefix_in_core="nointro",
    ),
}
