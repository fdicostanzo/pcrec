# studies/rwsurvey — [REWRITE-ADJ] / [SCANEDGE-SET] survey probe (lane rwsurvey, 2026-10-26)

Survey instrument behind `docs/dev/lanes/rwsurvey_report.md`. Throwaway: nothing here is built by
`make`, linked into pcrec or merged into `src/`. Survey only (no build go).

## Files

- `probe_hooks.[ch]` — AST dumper + neighbour-shape detectors (A absorb-optional, B absorb-EOL,
  C redundancy, D context-implied-after-run) + DFA chain-member MODEL + before/after reader of the
  REAL scan-edge pass. Linked in place of `compile.o`.
- `mkprobe.sh [set]` — copies `src/core/compile.c`, injects the hook calls by anchored `sed`
  (each site checked), builds `build/probe/pcrec_probe`; `set` also swaps `scanedge.o` for the
  class-SET variant (`mkscanedge_set.py`) and builds `pcrec_probe_set` (artifacts INVALID, counts only).
- `mkscanedge_set.py` — derives the set-rule `scanedge.c` from `src/opt/scanedge.c`: `shaped()` takes
  a class set S, `same_shape()` also compares the sets; every other precondition is the real code.
- `run_survey.py` — `corpus` (tests/**/*.rxt pattern rows via `--list-source`, head options applied),
  `bench` (pcrec-bench `bench/*/patterns/*.rx`, READ-ONLY), `list`, `stamp-*` (the real artifact's
  `RX_DFA_SCAN_EDGE`). Sequential, one process per pattern; launch through `scripts/boxlock run`.
- `analyze.py` — `shapes`, `hits`, `created`, `dfa`, `se` (real pass vs set variant), `union`,
  `validate2` (control: base probe vs the artifact's stamp).

Dumps live in `build/probe/` (gitignored). Rebuild: `bash studies/rwsurvey/mkprobe.sh && bash studies/rwsurvey/mkprobe.sh set`.
