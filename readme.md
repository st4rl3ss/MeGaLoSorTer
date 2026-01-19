# MeGaLoSorTer

MeGaLoSorTer generates MiSTer `.mgl` launcher files from a ROM directory and a PigSaint/GameDataBase CSV metadata file.

It scans ROM files, computes SHA1 hashes, matches them against the CSV, and writes a menu-browsable `_Organized` folder tree. Each generated `.mgl` launches a MiSTer core and points at the ROM via a path relative to the core’s games folder.

## Supported systems (profiles)

- Genesis / Mega Drive
- SNES / Super Famicom

(Additional systems can be added via profiles.)

## What it does

- Loads the CSV and indexes entries by SHA1.
- Scans a ROM directory for configured extensions.
- Computes SHA1 for each ROM (with an optional SQLite cache for faster re-runs).
- For matched ROMs, creates launchers organized by metadata facets:
  - `publisher`, `developer`, `genre`, `year`, `date`
- `genre` parsing supports PigSaint-style tokens such as:
  - `#genre:action:adventure`
  - `#genre:sim>building>train`
  - `#genre:action>platformer:parlor>pachinko`
- Optionally creates launchers for unmatched ROMs under `_Unmatched`.
- Prefixes output folders with `_` so they are visible in the MiSTer menu.

## Key options

- `--system genesis|snes`  
  Select the system profile (sets core launch args + default extensions).

- `--facets ...`  
  Choose which folder views to generate (e.g. `publisher developer genre date`).

- `--date-depth 1|2|3`  
  Controls date granularity for the `date` facet:
  - `1`: Year
  - `2`: Year / Month
  - `3`: Year / Month / Day

- `--name-source rom|db`  
  Controls `.mgl` filenames:
  - `rom` (default): use the ROM filename stem
  - `db`: use CSV title/region/id

- `--on-collision skip-identical|suffix`  
  What to do if a target `.mgl` already exists:
  - `skip-identical` (default): skip if content matches, otherwise suffix
  - `suffix`: always write `__2`, `__3`, ...

- `--write-unmatched`  
  Also generate launchers for ROMs not found in the CSV.

- `--dry-run`  
  Do hashing/matching and print stats, but do not write output.

## Defaults

When run from a working directory, defaults are:

- CSV: a `*.csv` in `./` (or a conventional filename)
- ROMs: `./ROMS`
- Output: `./_Organized/_<setname>`

## Usage

Dry run:

```bash
python -m MeGaLoSorTer.cli --dry-run
```

Genesis example:

```bash
python -m MeGaLoSorTer.cli \
  --system genesis \
  --facets publisher developer genre date \
  --date-depth 2 \
  --write-unmatched
```

SNES example:

```bash
python -m MeGaLoSorTer.cli \
  --system snes \
  --romdir ./ROMS_SNES \
  --csv ./console_nintendo_snes.csv \
  --facets publisher developer genre date \
  --date-depth 2 \
  --write-unmatched
```

## Output

The output is a tree of `.mgl` files under `_Organized/` with underscore-prefixed folders so the MiSTer menu will show them.

Copy the generated `_Organized` tree to the MiSTer SD card (commonly `/media/fat/_Organized`) and browse it from the MiSTer main menu.

## MiSTer notes

The generated `.mgl` files include:

- `<rbf>`: core path (e.g. `_Console/MegaDrive`, `_Console/SNES`)
- `<setname>`: controls which `/media/usb0/games/<setname>/...` folder the launcher targets
- `path="..."`: ROM path relative to that games folder (often prefixed by `nointro/`)
