from __future__ import annotations

from xml.sax.saxutils import escape


def make_mgl(
    rbf: str,
    setname: str,
    files: list[tuple[int, str, int, str]],
) -> str:
    out = [
        "<mistergamedescription>",
        f"  <rbf>{escape(rbf)}</rbf>",
        f"  <setname>{escape(setname)}</setname>",
    ]
    for delay, ftype, index, path in files:
        out.append(
            f'  <file delay="{delay}" type="{escape(ftype)}" '
            f'index="{index}" path="{escape(path)}"/>'
        )
    out.append("</mistergamedescription>")
    return "\n".join(out) + "\n"

