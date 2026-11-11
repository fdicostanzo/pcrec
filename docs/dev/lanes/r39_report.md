# r39 report: a part-K-of-N selector for `memfn/tests/run_g2.sh` (R-39, [CLOUD-SUITE])

Branch `lane/memfn-r39` (cut from main 60bd68154). Files changed, all under `memfn/tests/`: `run_g2.sh`, new `g2_units.tsv`, `g2_parts.py`, `g2_parts_selftest.sh`, plus `CLAUDE.md` and `NOTES.md` ("The part selector").

## Summary

`run_g2.sh --quick --part K/N` runs part K of N of the quick tier. The unit of work is a block of the script that runs, judges and reports on its own (24 units: `gcc`, `asan`, `w1w3`, `w2-1`..`w2-16`, `k1`, `simd`, `win`, `any`, `rows`). A declared weight table and a deterministic greedy rule deal the units to the parts; the generator stage runs in every part. `g2_parts.py gather` takes the N part logs and checks (1) that every unit ran exactly once, (2) section 4b's row checks (a)-(e), which are counts over the whole population, and (3) the totals. Without the options the run is unchanged (same stdout, same exit codes; the structure is `want UNIT` guards that are always true). On a 6-unit slice, split 1/2 + 2/2 gathered to the same census lines, verdict lines and `checks passed: 863579` as the unsplit slice. By the table's weights N=4 is balanced to 250-253 of 1006. The full-size claim (wall per part) is OWED to job 591.

## Selector spelling

- Kit side: `bash memfn/tests/run_g2.sh --quick --part K/N` (1 <= K <= N; `--part` and `--units` need `--quick`, else exit 2). Also `--units a,b,..` (a diagnostic slice, judged like a part) and `--list-units`. `G2_JOBS=N` overrides build parallelism (default: online CPUs). `G2_UNITS_OUT=FILE` writes the unit manifest from any run, with no stdout change.
- A part reports on stdout in the unsplit shape for the units it ran, and adds `G2UNIT name seconds` (one per unit, printed when the unit's judge ran), `G2PART ...` lines (partial counts, below), and the usual `checks passed:` / `checks failed:` trailer; its exit code is its own verdict (a part is red when a unit in it is red). The row checks (a)-(e) print `rows: (a)-(e) over the whole population are judged by g2_parts.py gather`.
- Gather: `python3 -I memfn/tests/g2_parts.py gather --table memfn/tests/g2_units.tsv --row-floors tests/memfn/row_floors.tsv part1.log .. partN.log`. It prints PASS/FAIL lines, each part's wall and units, then `checks passed/failed` as an unsplit run would; exit 0 green, 1 red.
- Proposed pcrec side (NOT edited here; `Makefile` and `tests/ci/cloud_kinds.tsv` are pcrec's):

      test-memfn-g2: all $(BUILD_DIR)/libpcrec_mftrace.a
      	... touch the .ran trailer as today ...
      	G2_ROW_FLOORS=tests/memfn/row_floors.tsv bash memfn/tests/run_g2.sh --quick $(if $(G2_PART),--part $(G2_PART))
      test-memfn-g2-gather:
      	python3 -I memfn/tests/g2_parts.py gather --table memfn/tests/g2_units.tsv --row-floors tests/memfn/row_floors.tsv $(G2_PART_LOGS)

  A cloud shard runs `make test-memfn-g2 G2_PART=K/4` and keeps its stdout as the part log; one final job runs `make test-memfn-g2-gather G2_PART_LOGS="part1.log .. part4.log"`. With `G2_PART` unset the recipe is today's. Setting `G2_ROW_FLOORS` on a part is harmless (a part defers (e)).

## Unit and balance

- Unit: the 24 blocks above, from `memfn/tests/g2_units.tsv`. Dealt by `g2_parts.py assign`: units sorted by declared weight (heaviest first, table order on ties) go one at a time to the part with the least weight so far (lowest part number on ties). Nothing about a run enters it. Why this unit: the batch-level driver run (`gcc`) judges coverage cells and `*_min` census lines that are not additive across batch subsets, so batches are not the unit (below, OWED/limit).
- Weights are seconds ALONE on the dev box at `G2_JOBS=2`, `nice 10`, from `--units NAME` slice runs of this lane: `asan` 103, `win` 53, `w1w3` 50, `any` 23, `k1` 13, `rows` 7, `w2-1` 41, `w2-5` 36, `w2-8` 14, `w2-9` 2, `w2-12` 16 (logs `/var/tmp/pcrec-pcrec/scratch/memfn/r39/logs/m_*.units`). `gcc` (250) and `simd` (140) are the 2026-11-03 CI log's 351 s and 195 s divided by 1.4, the CI/box ratio of the units both measured. The other `w2-*` weights are estimates, marked ESTIMATED in the table's `weight_source` column.
- Balance by weight (total 1006): N=2 `504 / 502`; N=3 `335 / 336 / 335`; N=4 `252 / 253 / 250 / 251`; N=8 is bounded by `gcc` (250) alone. Units inside a part overlap in time (background legs), so a part's wall is not the sum; the measured per-part wall comes from job 591 (OWED) and re-weights the table. A wrong weight costs balance, never coverage.
- Limit: `gcc` (one single-threaded driver run, ~25% of the total) caps the shortest possible part. Splitting it by batch needs the driver's coverage cells and `*_min` lines made mergeable (raw counters, not printed minima): not done, not needed up to about N=4.

## Population check

- Each part prints `G2UNIT name seconds` when a unit's judge ran; a unit that died earlier is missing, not counted. The expected population is the table, `--units`, or an unsplit run's manifest (`G2_UNITS_OUT`, which `--unsplit-units` reads).
- `gather` fails on a unit run by no part ("run by no part"), by more than one ("more than one part"), or not in the expected population ("does not list"), and on a part that ran a different set than the rule deals it ("the rule deals it"). It prints `population: N parts, U units expected, C run exactly once`.
- Planted, all red (`memfn/tests/g2_parts_selftest.sh`, 15 cases, `checks failed: 0`): a missing unit; a duplicated unit; an extra unit; two parts swapping a unit; also the same plants on REAL part logs of the slice run (`any` line deleted from part 2: `FAIL: units run by no part: any`, rc 1; `win` line copied into part 2: `FAIL: units run by more than one part: win(parts 1,2)`, rc 1). Controls: the clean fixtures for N = 1, 2, 3, 4 gather green.
- The unit checks and the rule share the table; the independent control is the manifest the run itself printed (a unit is listed only if its judge ran) and the unsplit run's own manifest.

## Floors over a split run

Each floor in `run_g2.sh`, classified:

- Per-unit facts (hold inside the part that has the unit, same code, same literal): the gcc answer run's ~100 floors (`FAM_FLOORS`, `FORM_FLOORS`, `FLOOR_MT_*`, `FLOOR_RB_*`, `FLOOR_ST_*`, `FLOOR_MM_*`, PF cells, coverage), the ASan floor, W1/W2/W3 (including every `FLOOR_*MUT*`), K1, libc record, SIMD / window / find-any runners' own floors, and section 4b's (f)/(g) and the two controls ((d), (b)), which live in the `rows` unit.
- Prelude facts (generator stage: `FAM_FLOORS` rendered counts, `FLOOR_REFUSALS`, `cls_floor` populations, poison, user-refusal floors): the generator runs in every part, so they are judged in every part. The prelude's and section 5's tallies are replicated, not summed: a part prints `G2PART prelude_passed` and `G2PART replicated_failed`, and gather subtracts them (N-1) times.
- COUNTS over the population (`tests/memfn/row_floors.tsv` and its section-4b siblings): (a) REACH_DROPPED is 0, (b) every row chosen at least once, (c) distinct rows >= `FLOOR_ROWS`, (d) every kit process printed REACH lines, (e) `G2_ROW_FLOORS` per-row g2_floor. A part defers them and prints `G2PART rowchosen-prelude T R N` (its prelude generator's rows), `G2PART rowchosen-other T R N` (every other process in the part), `reach_procs`, `reach_dropped`, `floor_rows`, `reach_noreach`. `gather` sums them (the prelude counted once; it must agree between parts, else FAIL "prelude generator"), applies (a)-(e) with the unsplit run's own words, and reads `FLOOR_ROWS` from the parts rather than holding a literal of its own.
- Planted through the gather path (fixture logs shaped as the real `G2PART` lines, floors from the real `row_floors.tsv`): row `arms/ofsskip` one under its g2_floor (summed over 3 parts) goes red `(e)`; a floored row chosen by no part, red `(e)`; a row at 0, red `(b) rows never chosen`; REACH_DROPPED nonzero, red `(a)`; a process with no REACH line, red `(d)`; a red part, red; the prelude's rows differing between parts, red.
- Totals: gather's `checks passed` equals an unsplit run's by construction (sum of parts - (N-1) x replicated + its own (a)-(e) passes); checked on the slice (below).

## Checks

- `make strict` on this branch: clean (`/var/tmp/pcrec-pcrec/scratch/memfn/r39/strict.log`, rc=0). `make test-spec-history`, `test-endmark`, `test-claudemd-size`, `test-doc-lint`: all green.
- Slice `k1,win,any,rows,w2-9,w2-12` at `G2_JOBS=2`, niced, unsplit (`f_all`) vs `--part 1/2` + `--part 2/2` (`f_p1`, `f_p2`): the sorted union of the parts' 45 census and verdict lines equals the unsplit run's, each log ends `checks failed: 0` rc 0; `gather --unsplit-units` reports `population: 2 parts, 6 units expected, 6 run exactly once`, and its totals (`checks passed: 863579`) equal `gather` over the unsplit log alone. An earlier slice (`k1,win,any,rows`) gave the same.
- Plants: 15 cases in `g2_parts_selftest.sh`, all behaved (clean N=1..4 green; missing, duplicate, extra, misdealt, floor, absent, zero, dropped, noreach, partfail, prelude red). Two more on real part logs (above).
- Not run (by the lane's box rule): a full `--quick` run, split or unsplit, and `make test`. The unsplit-unchanged claim rests on the guards being always true and on reading the diff (the only removed lines are the moved generators and guarded calls); job 591's unsplit leg runs the unchanged path in full.
- Two self-inflicted slips, recorded: editing `run_g2.sh` while a measurement run was reading it corrupted that run (it printed a stray `w2-16` unit); those runs were discarded and redone with no edits during a run.

## Gate jobs

Prepared, dry-run clean, NOT queued, under `/var/tmp/pcrec-pcrec/scratch/memfn/r39/jobs/` (shape and keys from kclose2's set; `common.sh` points at `worktrees/r39`, branch `lane/memfn-r39`, the evening hold, and waits for main's battery):

- `590-kit-r39-strict` (key `kit-r39-strict`): `make -j16; make strict`.
- `591-kit-r39-g2split` (key `kit-r39-g2split`, after `kit-r39-strict`): the full `run_g2.sh --quick` unsplit (`G2_ROW_FLOORS` set, manifest written), then `--part 1/4 .. 4/4` in sequence, then `g2_parts.py gather` with the unsplit manifest and `row_floors.tsv`; compares the unsplit run's (a)-(e) lines and totals with gather's, and the sorted union of the parts' census lines with the unsplit run's; prints `g2split wall unsplit|partK Ns` for the unsplit run and each part. est 2400 s, cap 4800 s.
- `592-kit-r39-test` (key `kit-r39-test`, after `kit-r39-g2split`): `make test` on the branch via `scripts/perfrun`.
- `--dry-run` of all three passes.

## Charter-vs-committed checklist

- [x] A selector, spelling and unit chosen: `--part K/N`, units from `g2_units.tsv`.
- [x] Deterministic assignment by a declared rule over declared weights; no run-time state.
- [x] Exact-population check, counted and printed, planted missing and duplicated units red (fixture and real logs).
- [x] Each part prints the unsplit run's verdict shape plus a manifest; floors classified per unit / prelude / population COUNT; partial counts in a gatherable form; gather script in `memfn/tests/`; planted under-floor count red through gather.
- [x] Unselected behaviour unchanged by construction and by the slice runs' shared code path; full-size confirmation is job 591.
- [x] Checks: `make strict` clean; slice unsplit vs split identical; two population plants; floor plant.
- [x] Gate jobs 590/591/592 prepared, dry-run, not queued.
- [x] `Makefile` and `tests/ci/cloud_kinds.tsv` untouched; the Makefile spelling is proposed above.
- [x] memfn/tests/CLAUDE.md (Files entry) and NOTES.md ("The part selector") updated.
- [ ] Full-size wall per part, the re-weighting from it, and the unsplit-vs-split verdict comparison at full size: job 591.

OWED: jobs 590, 591, 592 (prepared, not queued; the kit manager queues them). The numbers owed are job 591's `g2split wall unsplit|part1..part4` lines and its `== g2split step same rc=0` / `r39-g2split: DONE rc=0` trailer, and 592's `== r39 step test rc=0`; results land under `/var/tmp/pcrec-pcrec/scratch/memfn/r39/g2split/` and `/test/`. After 591, re-weight `g2_units.tsv` from the `G2UNIT` seconds if a part's wall differs from the others.
