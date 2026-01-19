from __future__ import annotations

import argparse
from pathlib import Path

from .config import SystemConfig
from .organizer import run_system


def default_csv(root: Path) -> Path:
    """
    Default CSV selection strategy:
      1) If exactly one *.csv exists in root, use it.
      2) Else try a conventional filename.
      3) Else fall back to <root>/*.csv (first alphabetically) if any.
    """
    csvs = sorted(root.glob("*.csv"))
    if len(csvs) == 1:
        return csvs[0]

    conventional = root / "console_sega_megadrive_genesis.csv"
    if conventional.exists():
        return conventional

    return (
        csvs[0] if csvs else conventional
    )  # conventional may not exist, but it's a sensible default


def build_argparser() -> argparse.ArgumentParser:
    root = Path.cwd()

    ap = argparse.ArgumentParser(
        prog="MeGaLoSorTer",
        description="MeGaLoSorTer — generate MiSTer .mgl library views from PigSaint CSV + ROM sets.",
    )

    ap.add_argument(
        "--csv",
        type=Path,
        default=default_csv(root),
        help="Path to the PigSaint CSV. Defaults to a CSV in the current directory.",
    )
    ap.add_argument(
        "--romdir",
        type=Path,
        default=root / "ROMS",
        help="Folder containing ROMs. Defaults to ./ROMS",
    )
    ap.add_argument(
        "--outdir",
        type=Path,
        default=root / "_Organized" / "_Genesis",
        help="Output folder for generated .mgl tree. Defaults to ./_Organized/_Genesis",
    )

    ap.add_argument(
        "--rbf",
        default="_Console/MegaDrive",
        help="MiSTer core path without .rbf/.timestamp, e.g. _Console/MegaDrive",
    )
    ap.add_argument(
        "--setname",
        default="Genesis",
        help="MiSTer setname (controls config/games folder name), e.g. Genesis",
    )
    ap.add_argument(
        "--prefix-in-core",
        default="nointro",
        help="Subfolder under the core games folder, e.g. nointro",
    )

    ap.add_argument(
        "--ext",
        nargs="*",
        default=[".md", ".bin", ".gen", ".smd"],
        help="ROM extensions to scan",
    )
    ap.add_argument(
        "--facets",
        nargs="+",
        default=["publisher", "developer", "genre"],
        choices=["publisher", "developer", "genre", "year", "date"],
    )
    ap.add_argument("--genre-depth", type=int, default=2, choices=[1, 2])
    ap.add_argument("--date-depth", type=int, default=2, choices=[1, 2, 3])

    ap.add_argument(
        "--name-source",
        choices=["rom", "db"],
        default="rom",
        help="rom = use ROM filename for .mgl name; db = use DB title/region/id",
    )
    ap.add_argument(
        "--on-collision",
        choices=["suffix", "skip-identical"],
        default="skip-identical",
        help="suffix = write __2 etc; skip-identical = skip if same content else suffix",
    )

    ap.add_argument(
        "--write-unmatched",
        action="store_true",
        help="Also write launchers for ROMs not found in the CSV under _Unmatched/",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute matches and stats, but don’t write .mgl files",
    )

    return ap


def main() -> int:
    args = build_argparser().parse_args()

    # If user didn't override outdir, make it follow setname automatically:
    # ./_Organized/_<setname>
    root = Path.cwd()
    default_outdir = root / "_Organized" / f"_{args.setname}"
    if args.outdir == (root / "_Organized" / "_Genesis"):
        args.outdir = default_outdir

    cfg = SystemConfig(
        name=args.setname,
        csv_path=args.csv,
        romdir=args.romdir,
        outdir=args.outdir,
        rbf=args.rbf,
        setname=args.setname,
        prefix_in_core=args.prefix_in_core,
        exts=list(args.ext),
        facets=list(args.facets),
        genre_depth=args.genre_depth,
        date_depth=args.date_depth,
        file_delay=1,
        file_index=1,
        file_type="f",
        name_source=args.name_source,
        on_collision=args.on_collision,
        write_unmatched=args.write_unmatched,
        dry_run=args.dry_run,
    )

    return run_system(cfg)


if __name__ == "__main__":
    raise SystemExit(main())
