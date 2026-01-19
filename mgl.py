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
