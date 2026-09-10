# oracle_store/ — the committed reference-oracle answer store

`docs/design/oracle_interface.md`'s answer store (PROPOSED, PANELED at r56,
REVISED, VERIFIED — see that document's own header and
`docs/dev/reviews/2026-09-10-r56-oracle-interface.md`), first built by lane
`orstore`. Top-level, on `third_party/`'s own precedent (§7.2's own lean, and
r56's "Ratified as-is" list): this is external-derived data too, derived by
RUNNING a reference library rather than by vendoring a data file, and a
non-test consumer could read it just as `third_party/`'s UCD tables can be
read by anything, not only `tests/`.

## Layout

One directory per `OracleId` (`<oracle-name>-<version>[-<config-tag>]`), one
TSV file per question KIND inside it (`<kind>.tsv`) — `docs/design/
oracle_interface.md` §7.1. Every file is SELF-CHECKING: its own header names
`store_format_version`, the resolved `OracleId` fields, its own row count,
and capture provenance (host, date, exact command); a reader verifies a
looked-up row's stored `question` text against its own recomputed
serialization before trusting the answer. **Never hand-edit a file here** —
regenerate it with the producing tool (`tests/oracle/build_uprops_store.py`
for `membership`) and let the write path's own duplicate-hash detector and
sorted-by-hash discipline do their job (§7.1a: "a store file is not a log a
caller appends a line to").

Only the REFERENCE version (today: `libpcre2-10.46`, the project's pin) is
committed here. A LOCAL box's own resolved library (Homebrew 10.48 on the Mac
dev box) is a separate, gitignored cache under `build/oracle_cache/` — see
`tests/oracle/CLAUDE.md`.

## Contents

- `libpcre2-10.46/membership.tsv` — the `membership` kind, 387 properties (45
  general categories + 171 script values × 2 namespaces — bare and `sc=`),
  captured over ONE ssh round trip (chunked into seven ~60-property calls)
  against the true 10.46 reference box (`duxevents@100.69.121.107`, the
  travel-month tailnet address — `docs/dev/lanes/BOILERPLATE.md`). Discharges
  `docs/dev/wake.md`'s owed "STAGE-5 10.46 EXACT arm" — `S-U12`'s own
  neighborhood (the script-namespace `membership` differential currently
  measured against whichever local library darwin resolves) — without darwin
  ever owning the reference. 387 rows / ~136 KB, well under the low-single-
  digit-MB bound `docs/design/oracle_interface.md` §7.3/§13 left as an
  open question — now MEASURED rather than estimated, so plain committed
  text needs no revisiting.

  **Wiring this store as `tests/utf8/axis12_scripts.rxt`'s actual oracle is
  NOT this lane's build** (D77 / the design's own migration-ladder scoping,
  §9 Step 1's text) — that is a separate step for whichever lane owns that
  differential's regeneration; this directory only makes the captured
  answers available.

Maintenance: update this file when an `OracleId` directory or a kind file is
added, removed, or its capture population changes.
