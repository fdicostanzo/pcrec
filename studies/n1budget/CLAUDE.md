# studies/n1budget — [LIM-2] N1's default-sizing measurement

Never built or run by pcrec's top-level `make`/`make test` (studies/CLAUDE.md's
standing rule). Links the repo root's `build/libpcrec.a`.

## Files

- **n1_measure.c** — the measuring instrument. Drives the same internal
  pipeline `src/core/compile.c`'s D7 fast path calls (modelled directly on
  `studies/lim2_census/lim2_census.c`'s own precedent), and reports the
  finished `Ctx.subset_elems` — K7's already-counted subset-construction
  element total — per pattern, over every `.rxt`/`.rx` file given on argv.
  Builds the mandatory forward+reverse machines for every DFA-route
  pattern and, for a DFA-CHOSEN artifact, the [ENG-ABS] optional third
  machine too (mirrored inline; `build_anchored_dfa` itself is `static` to
  compile.c and not exported), so its reported MAX is the real total spend
  a corpus artifact pays today rather than an under-count. See its own
  header for the full methodology and why this is not a "control shares a
  source with what it controls" instrument (docs/dev/learnings.md S3):
  the verdict — where `PCREC_MAX_AUTO_DFA_ELEMS`'s default sits — is
  written in the report this data feeds, not here.
- **Makefile** — `make` builds `n1_measure` against `../../build/libpcrec.a`
  (build the repo root first); `make sweep` re-runs the full sweep via
  `run_sweep.sh` and regenerates `n1_data.tsv`/`n1_summary.txt` IN PLACE
  (does not commit them — re-measurement is a deliberate act,
  `studies/CLAUDE.md`'s own rule).
- **run_sweep.sh** — finds pcrec's `.rxt` corpus and (read-only, skipped
  loudly if absent) pcrec-bench's `bench/altwide/patterns/*.rx`, runs the
  binary over the union, writes `n1_data.tsv`/`n1_summary.txt`.

## Finding

MEASURED 2026-09-04: 3,386 pattern blocks (193 `.rxt` files + 33 altwide
patterns), 390 refused (any `ctx_fail`, including K7's own hard cap), 2,157
`route=unanch` + 433 `route=attempt`, both not refused. **MAX
`subset_elems` over non-refused rows: 24,050,003**
(`tests/counterk/counterk.rxt:1845`, `((a)|bc){0,4000}d` — one of three
near-identical 8,002-raw-state exact-repeat witnesses in that file, at
1,725/1,807/1,845). This is the derivation behind `src/core/limits.def`'s
`PCREC_MAX_AUTO_DFA_ELEMS` default (30,000,000): comfortably above the
measured maximum, confirmed by a before/after engine-stamp census over the
corpus (docs/dev/lanes/n1budget_report.md).

Maintenance: update this file when files are added/removed or their roles
change.
