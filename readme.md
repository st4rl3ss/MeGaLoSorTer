# MeGaLoSorTer

MeGaLoSorTer generates MiSTer `.mgl` launcher files from a ROM directory and a PigSaint/GameDataBase CSV metadata file.

It scans ROM files, computes SHA1 hashes, matches them against the CSV, and writes a menu-browsable `_Organized` folder tree. Each generated `.mgl` launches a MiSTer core and points at the ROM via a path relative to the core’s games folder.

> **AI-assisted code note**: Large portions of this repository were generated with AI assistance and subsequently reviewed/edited by humans. To the extent copyright applies, the project is licensed under the MIT License.

---

## Supported systems (profiles)

MeGaLoSorTer uses **system profiles** to define:

- which MiSTer core (`<rbf>`) to launch
- which games folder (`<setname>`) the launcher targets
- which ROM extensions to scan
- how to build the `<file .../>` entries in the `.mgl`

Profiles currently include (not exhaustive): Genesis/Mega Drive, SNES/Super Famicom, NES, C64, Amiga/Minimig, many Atari cores, Coleco, SMS/Game Gear, TGFX16, PSX, Saturn, Neo Geo, WonderSwan, and more.

Run `python -m MeGaLoSorTer.cli --help` to see the available `--system` choices in your checkout.

---

## What it does

- Loads the CSV and indexes entries by SHA1.
- Scans a ROM directory for the extensions supported by the selected system profile.
- Computes SHA1 for each ROM (with an optional SQLite cache for faster re-runs).
- For matched ROMs, creates launchers organized by metadata facets:
  - `publisher`, `developer`, `genre`, `year`, `date`
- `genre` parsing supports PigSaint-style tokens such as:
  - `#genre:action:adventure`
  - `#genre:sim>building>train`
  - `#genre:action>platformer:parlor>pachinko`
- Optionally creates launchers for unmatched ROMs under `_Unmatched`.
- Prefixes output folders with `_` so they are visible in the MiSTer menu (“underscore jungle”).

---

## Key options

- `--system <profile>`  
  Select the system profile (sets core launch args + slot mapping + default extensions).

- `--rbf ...`, `--setname ...`, `--prefix-in-core ...`  
  Override profile defaults for:
  - the core path (`<rbf>`)
  - the games folder (`<setname>`)
  - the subfolder under that games folder (`prefix-in-core`, often `nointro/`)

- `--facets ...`  
  Choose which folder views to generate (e.g. `publisher developer genre date`).

- `--date-depth 1|2|3`  
  Controls date granularity for the `date` facet:
  - `1`: Year
  - `2`: Year / Month (as month name)
  - `3`: Year / Month / Day

- `--name-source rom|db`  
  Controls `.mgl` filenames:
  - `rom` (default): use the ROM filename stem
  - `db`: use CSV title/region/id

- `--on-collision skip-identical|suffix`  
  What to do if a target `.mgl` already exists:
  - `skip-identical` (default): skip if content matches, otherwise suffix
  - `suffix`: always write `__2`, `__3`, ...

- `--cache PATH`  
  SQLite cache path (default: `./hashcache.sqlite`).

- `--write-unmatched`  
  Also generate launchers for ROMs not found in the CSV.

- `--dry-run`  
  Do hashing/matching and print stats, but do not write output.

---

## Defaults

When run from a working directory, defaults are:

- CSV: a `*.csv` in `./` (or a conventional filename fallback)
- ROMs: `./ROMS`
- Output (default only): `./_Organized/_<setname>`
- Cache: `./hashcache.sqlite`

If `--outdir` is provided, it is used **as-is** (no auto-appended `_<setname>`).

---

## How MiSTer paths work (important)

The generated `.mgl` files include:

- `<rbf>`: core path (e.g. `_Console/MegaDrive`, `_Console/SNES`)
- `<setname>`: controls which `.../games/<setname>/...` folder the launcher targets
- `path="..."`: ROM path **relative to that games folder** (often prefixed by `nointro/`)

This means *you* control where the ROMs live on MiSTer by choosing:

- `--setname` (games folder name)
- `--prefix-in-core` (subfolder inside that games folder)

Example (Genesis):

- ROMs on MiSTer: `/media/usb0/games/Genesis/nointro/*.md`
- Launchers generated with: `--setname Genesis --prefix-in-core nointro`

---

## Multi-slot MGL support

Some cores need different MiSTer `<file>` mappings depending on ROM type (or multiple `<file>` entries).

MeGaLoSorTer supports this via **slots** defined in profiles:

- each slot matches one or more extensions
- each slot emits one or more `<file .../>` entries in the `.mgl`

`--ext` now **filters existing slot mappings only**. If you pass extensions that don’t exist in the selected profile’s slots, the program exits with an error instead of inventing a mapping.

> Note: slot extension normalization is not automatic yet. Prefer lower-case extensions with a leading dot in profiles and CLI inputs (e.g. `.sfc`, not `SFC`).

---

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
  --romdir ./ROMS/SNES \
  --csv ./console_nintendo_superfamicom_snes.csv \
  --facets publisher developer genre date \
  --date-depth 2 \
  --write-unmatched
```

Custom MiSTer placement example (change where the ROMs will live *on MiSTer*):

```bash
python -m MeGaLoSorTer.cli \
  --system snes \
  --setname SNES \
  --prefix-in-core MyRoms \
  --romdir ./ROMS/SNES \
  --csv ./console_nintendo_superfamicom_snes.csv
```

This will generate launchers pointing at `MyRoms/<romname>` under the MiSTer `games/SNES` folder.

---

## Output

The output is a tree of `.mgl` files under `_Organized/` with underscore-prefixed folders so the MiSTer menu will show them.

Typical copy targets on MiSTer:

- Copy the generated `_Organized` tree to `/media/fat/_Organized` (or another menu-visible folder).
- Keep your actual ROM set wherever you prefer (e.g. `/media/usb0/games/<setname>/<prefix>/...`).

---

## C64 `.d64` support

Launchers for `.d64` images use a multi-file MGL and reference `autorun.prg` as a second file entry.

You must place `autorun.prg` in the MiSTer games folder that matches your `<setname>` for C64 (for example: `/media/usb0/games/C64/autorun.prg`, if `setname=C64`).

MeGaLoSorTer does **not** copy this file automatically.

---

## Important changes so far (project notes)

Recent implementation decisions (the “why does it behave like this?” section):

- **Multi-console support via profiles**: systems are selected with `--system`.
- **Multi-slot MGL generation**: slots select `<file>` mappings per extension and can emit multiple entries.
- **`--ext` now filters only**: it no longer invents a default mapping for unknown extensions; it errors clearly.
- **`--outdir` behavior**: default output includes `./_Organized/_<setname>`, but user-supplied `--outdir` is used as-is.
- **Collision handling**: `skip-identical` avoids `__2` spam when content is the same.
- **ROM-filename naming**: default `.mgl` filename source is the curated ROM filename (`--name-source rom`).
- **Date facet depth**: `date` supports Year / Month-name / Day granularity.
- **Genre parsing fix**: supports colon-separated groups and `>` hierarchies as used in PigSaint tags.
- **Cache default location**: SQLite cache defaults to `./hashcache.sqlite` (override via `--cache`).

---

## License

MIT, where applicable. See `LICENSE`.

## Warranty

None. This software is provided “AS IS”, without warranty of any kind. See the LICENSE for details.
