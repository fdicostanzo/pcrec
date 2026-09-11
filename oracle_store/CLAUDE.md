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

- `libpcre2-10.48/{match-at,captures}.tsv` — the C3 THREE-WAY VERDICT's
  own store instance (`docs/design/c3_three_way.md`, lane `pyrole`,
  2026-09-10/11; built by `tests/rxtsource/build_c3_store.py`). **A
  deliberate DEVIATION from this file's own "only the reference version is
  committed" rule above, directed by this lane's brief, not a mistake**:
  the LOCAL Homebrew 10.48 answers to exactly seven `.rxt`-corpus-derived
  questions (one `match-at`, six `captures` — `tests/harness/
  verify_rxt.py`'s C3 tier's own known python-vs-expectation
  divergences, cited file:line in `build_c3_store.py`'s own `QUESTIONS`
  dict), captured over one local ctypes call (no ssh round trip — no
  general remote match-at/captures adapter exists yet). Safe under the
  design's own staleness-impossibility argument (`oracle_interface.md`
  §8 Claim 2): `OracleId` carries `version`, so a box whose resolved
  libpcre2 is NOT literally `10.48` gets a clean miss on every row here,
  never a false confirmation — the same property that makes a version
  BUMP safe protects a version MISMATCH across boxes identically. See
  `c3_three_way.md` §4 for the full argument and §9 for what migrating to
  a real 10.46 capture would need.

Maintenance: update this file when an `OracleId` directory or a kind file is
added, removed, or its capture population changes.
