# third_party/ — vendored outside data

**Read `README.md` first**: it is the index (one row per source), the general
rule this directory exists to make general (*a data source compiles to
generated tables*), and the two structural properties every source directory
must have. This file is the maintenance note beside it.

Chartered 2026-09-06 by [M5.0] stage 3, on Frank's ruling on
`docs/design/utf8_design.md` §14 ASK 2 (*"agreed, reluctantly"*) plus its
§3.3.2 extension. **Nothing here reaches a generated artifact** — the data
compiles to tables inside `libpcrec.a`; a user's matcher is an automaton over
bytes and holds none of it.

## Contents

- `README.md` — the index and the shape. Update the table in the same change
  that adds or removes a source directory.
- `ucd-16.0.0/` — the Unicode Character Database, pinned at 16.0.0. Holds
  `PROVENANCE.md` (source URL, version, checksums, licence, and **what derives
  from it**), `LICENSE.txt`, `generate.py` and the vendored `.txt` files
  unmodified. Derives `src/parse/uprops_tables.inc`.

## Adding a source

Four things, and the first two are the whole of `README.md`'s requirement:

1. A directory named `<source>-<version>`.
2. A `PROVENANCE.md` naming where the data came from, its licence, and —
   the direction a maintainer and a licence audit both actually need —
   **which generated artifacts derive from it**.
3. A `generate.py` beside the data, supporting a bare run (write) and
   `--check` (exit 1 if the committed output is stale). It is picked up by
   `make gen-tables` and by `tests/uprops/run_uprops_tests.sh` §1 with no
   edit to either, because both iterate `third_party/*/generate.py`.
4. The generated file added to `GEN_TABLES` in the Makefile. **Do not skip
   this**: it is the object-build prerequisite, and omitting it means editing
   the source rebuilds NOTHING — the same defect the Makefile's own comment
   records for `cls_bits.inc` (MOD-0.3e) and twice for `limits.def`, and
   which happened a third time here within minutes of this directory landing.

## Maintenance

Bumping a source's version is a DELIBERATE act with a deliberate diff (D26's
"a version bump is a re-measurement event"): add the new directory beside the
old one, regenerate, read the movement, then remove the old one. The
version-in-the-name rule exists so those two can coexist while you do.

Update this file and `README.md`'s table when a source is added, removed or
re-versioned.
