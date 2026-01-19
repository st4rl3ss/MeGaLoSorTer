# MeGaLoSorTer

MeGaLoSorTer generates MiSTer `.mgl` launcher files from a ROM directory and a CSV metadata database (PigSaint/GameDataBase format).

It scans ROM files, computes SHA1 hashes, matches them against the CSV, and writes a menu-browsable `_Organized` folder tree on disk. Each generated `.mgl` launches a chosen MiSTer core and points at the ROM via a path relative to the core’s games folder.

## What it does

- Reads the CSV and indexes entries by SHA1.
- Scans a ROM directory for configured extensions.
- Hashes each ROM (with an optional SQLite cache for faster re-runs).
- For matched ROMs, creates launchers organized by metadata facets:
  - `publisher`, `developer`, `genre`, `year`, `date`
- For unmatched ROMs, can optionally still create launchers under `_Unmatched`.
- Prefixes output folders with `_` so MiSTer’s menu will display them.

## Key options

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

- CSV: a `*.csv` in `./` (or `console_sega_megadrive_genesis.csv`)
- ROMs: `./ROMS`
- Output: `./_Organized/_<setname>`

## Example

```bash
python -m MeGaLoSorTer.cli --dry-run

python -m MeGaLoSorTer.cli \
  --facets publisher developer genre date \
  --date-depth 2 \
  --write-unmatched

