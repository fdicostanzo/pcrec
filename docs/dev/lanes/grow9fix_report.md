# grow9fix report: review r89 applied to the growth sweep

Branch lane/grow9fix, cut from lane/grow9. Charter: docs/dev/reviews/2026-11-23-r89-grow9code.md (its RULED section). No src/ edit.

## Summary

- All six FIX-NOW items, the R89-11 tier ruling, the DOC items, two plan rows, K161 and K162 and the critics-guide block are in. The full uncapped sweep (1,600 cells, 107 of them the former occasional ones) is green: 1,588 passed, 0 failed, 12 known-red.
- The doubling gate in `run_growth.sh` was wrong in both directions (unsharded run died under `set -u`, every shard ran the report); fixed, with `tests/growth/gate_check.sh` running a stubbed copy over unset, 1/1, 1/76, 5/76 and 76/76 (the old script fails 3 of 5 cases, the new one passes all).
- The cloud run is dispatched as the last act (see STATE AT HANDOFF).

## Fixes

- R89-1: `run_growth.sh` gate is `gs=${GROWTH_SHARD:-1/1}; [ "${gs%%/*}" = "${gs##*/}" ]`. `tests/growth/gate_check.sh` (new) runs a copy under the script's own `set -u` with stubbed python3/make/gcc and checks the selftest, CLI, doubling, two library stages and the ASan build per case (`GATE_SCRIPT=` points it at another script: the pre-fix script fails unset, 5/76 and 1/76).
- R89-2: both pools. A worker exception becomes `FAIL: <cell>: worker died: <exc>` (sweep) or a failed point (doubling), counted in the failures; queued cells are skipped at once (a shared event) and never counted as passes; the work dir is removed by an `atexit` hook whatever ends the run. Drilled on a fake job raising on cell 2 of 7: cells 3 to 7 were skipped, the failure named.
- R89-3 (cheap form): the doubling report runs serial by default (`--jobs` / `DOUBLING_JOBS`; `run_growth.sh` no longer passes the sweep's `JOBS` to it); the basis comment names contention as the dominant noise. Serial run: 531 points, 0 failed, 42 REPORT lines (the -j8 run gave 52; 10 lines were contention, 1 new).
- R89-5: `growth_driver.c` wall guard = min(10 x bound, 2400 s) (`WALL_CAP`), under the 2700 s job kill; library mode streams `library mode: begin cell ID` lines so a cut job names its cell; BOUNDS_BASIS says a CLI hang names its cell only if it starts in the job's first ~1200 s.
- R89-7: matcher runs use `MATCHER_CPU_S 60` / `MATCHER_WALL_S 600` (10x). Basis: the full sweep's worst matcher run read 0.00 s CPU (under watchdog's 0.1 s sample) over every limit cell; the `CPU:` headroom line now reports `matcher run max`.
- R89-14: a REFUSED doubling point is a FAIL and resets the neighbour; a point with no CPU never pairs the next one. R89-15 folded in: ratios are per doubling (normalised by log2 of the size ratio when the step is >= x1.5; the nested-`+` level steps stay raw).
- R89-11: `Cell.occasional` is now `cid in OCCASIONAL_COSTLY` (empty frozenset), so the 107 cells run in the default tier again. Shard table re-folded (`make cloud-reweight KIND=growth` path): 96 shards (was 76), 1,600 cells once each (`--shard-check` PASS), predicted slowest 1,421 s (job limit 2,700 s), 25 cells keep an ESTIMATE (the `+` edge cells never measured on a runner), no shard predicted under the sum of its cells' measured costs (checked: 0 of 96).
- R89-12: 19 `measured-red-shard` rows that came from the cut shards 31 and 60 now carry basis `measured-red-shard-lower-bound` in `tests/ci/measured_growth.tsv` (with a header line).

## Doc items

R89-4 (load-resilient wording and the D45 derivation written out), R89-6 (`CPU:` headroom per bound; the gcc figure is watchdog's sampled sum), R89-9 (OCC bounds re-derived: tier empty, figure reserved), R89-10 (stale "CLI wall" wording in run_growth.sh and tests/growth/CLAUDE.md), R89-12, R89-13 doc half (axes stop at the largest doubling under the limit n), R89-15 (docs/testing.md and tests/growth/CLAUDE.md updated, tier text rewritten). Plan rows: [WATCHDOG-CPU-CLOCK] (R89-8, with R89-6's exact-clock half) and [GROWTH-AXES] (R89-13 design half) in the Candidates section; `make -s test-plan-lint` green.

## Filings

K161 (possessive/star depth nests, x10 to x14 per doubling, 26 s CPU serial / 45 s at -j8 at depth 250) and K162 (character spines quadratic to n=4000, a cliff at 8000), both with repro and measured numbers; the doubling report is their witness. critics.md: one dated r89 block with the six lessons and the top process change.

## Validation

All under `scripts/boxlock run --label grow9fix`; logs in `/var/tmp/pcrec-pcrec/scratch/grow9fix/` (v_j1.log, v_j8.log, v_dbl.log, v_full.log).
- Gate stub, five cases: PASS (`bash tests/growth/gate_check.sh`); old script FAILS 3 of 5.
- `run_growth.py --only depth,spine` at -j1 and -j8: both rc 0, 539 runs passed, 5 known-red (K148), verdict lines identical (diff of everything but the `CPU:` lines is empty).
- Doubling report, once (serial, 7.5 min): 531 points, 0 failed, 42 REPORT lines.
- Full uncapped sweep `--no-ladder -j8` (6 min): 1,588 passed, 0 failed, 12 known-red, 107 compile-only cells green; slowest `matrix/named.poss.last.lit@250` 37 s compile CPU (12% of the 300 s bound); gcc build max 3.9 s; matcher run max 0.00 s.
- `make -s strict` clean; `make -s test-plan-lint` green; `--shard-check` PASS; `--selftest` ok.
- Not run: the library stage (plain and ASan) and the ladder locally; the cloud run covers both.

## STATE AT HANDOFF

Rulings applied: none (grow9fix_rulings.md was empty at each re-read). Scratch: /var/tmp/pcrec-pcrec/scratch/grow9fix/.
OWED: none (box queue); cloud growth run cloud/main/growth/grow9fix dispatched, verdict read by the manager.
The first cloud run prints the `CPU:` headroom lines (re-derive CPU_S from them), the last shard prints the doubling report; the cut-job shape (shard 31) now names its cell through the streamed `begin` lines. Open: the 25 estimated `+` cells need a runner measurement; the owner is told the occasional-tier reading at landing.
