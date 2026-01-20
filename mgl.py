from __future__ import annotations

from xml.sax.saxutils import escape


def make_mgl(
    rbf: str,
    setname: str,
    delay: int,
    ftype: str,
    index: int,
    rel_path_from_core_games_folder: str,
) -> str:
    return (
        "<mistergamedescription>\n"
        f"  <rbf>{escape(rbf)}</rbf>\n"
        f"  <setname>{escape(setname)}</setname>\n"
        f'  <file delay="{delay}" type="{escape(ftype)}" '
        f'index="{index}" path="{escape(rel_path_from_core_games_folder)}"/>\n'
        "</mistergamedescription>\n"
    )


def make_mgl_c64_d64(
    rbf: str,
    setname: str,
    rel_path_from_core_games_folder: str,
) -> str:
    """
    Special MGL generator for C64 .d64 files.
    Creates an MGL with two file entries:
    - The .d64 disk image (delay=1, type=s, index=0)
    - autorun.prg (delay=0, type=f, index=1)
    """
    return (
        "<mistergamedescription>\n"
        f"  <rbf>{escape(rbf)}</rbf>\n"
        f"  <setname>{escape(setname)}</setname>\n"
        f'  <file delay="1" type="s" index="0" path="{escape(rel_path_from_core_games_folder)}"/>\n'
        f'  <file delay="0" type="f" index="1" path="autorun.prg"/>\n'
        "</mistergamedescription>\n"
    )
