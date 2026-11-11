# r39b report: rebalance R-39's g2 split

Branch `lane/memfn-r39b` (cut from `lane/memfn-r39`). Files changed, all under `memfn/tests/`: `run_g2.sh`, `run_g2_simd.py`, `g2_units.tsv`, `g2_parts.py`, `CLAUDE.md`, `NOTES.md`.

## Summary

Job 561 balanced badly (92 / 267 / 87 / 107 s) because the `simd` unit alone took 221 s of ~822 s of unit walls and was under-weighted (140 against gcc's 250, which actually took 81 s). Fixes: (1) `simd` is now five units, one per ARM of `run_g2_simd.py` (`--arms`): `simd-facts`, `simd-answers`, `simd-paths`, `simd-plants-a`, `simd-plants-b`; (2) `g2_units.tsv` is re-weighted from measured walls, largest unit 81 s (total/8 = 103); (3) `g2_parts.py` gained `reweight` and `predict`. By the new table N=4 deals 205 / 206 / 205 / 206 and N=8 deals 101..104. The real N=4 wall check is gate job 564, which now fails if max > 1.5 x min part wall. OWED: job 564 (full-size part walls, unsplit-vs-split diffs) and job 565 (`make test`); nothing of them was run here.

## Measured walls

Job 561 (whole `--quick` g2 as N=4 on the 16-core dev box, unniced, box loaded; `/var/tmp/pcrec-pcrec/scratch/memfn/r39/g2split/gather.log`), unit walls inside their part: gcc 81, simd 221, asan 46, win 54, w1w3 41, any 22, k1 6, rows 5, w2-1..16 = 34 35 30 40 37 30 16 11 3 4 2 20 26 15 20 23. Sum 822 s; part walls 92 / 267 / 87 / 107.

Own single-unit runs of the new simd arms (`run_g2.sh --quick --units NAME`, `G2_JOBS=2`, nice 10, one at a time, box load 7-10): simd-facts 51 s, simd-answers 48, simd-paths 17, simd-plants-a 68, simd-plants-b 67; sum 251 s (logs `/var/tmp/pcrec-pcrec/scratch/memfn/r39b/logs/simd-*.out`). They are scaled by 221/251 so the five sum to job 561's 221 s for unsplit simd.

## Unit split

`run_g2_simd.py --arms A[,B..]` (default all five, so the script run alone is unchanged). Every arm renders the space, runs the generator and the fact checks (sections 0-2) quietly (stdout and counters restored; `FACT_FAIL`, `HELPER_TEXT`, `SITE_RUN` kept because they gate and feed the compiles), then judges only its own section: `facts` = sections 0-2 and 6 (targets, headers, consumer TU, classes, ranking, verify, bounds, instruction classes), `answers` = 3 (six builds + two ASan), `paths` = 4, `plants-a` = the first three PLANTS (final-guard, lane-mask, lane-order), `plants-b` = no-verify, reach-short, pad-margin. `run_g2.sh` loops the five arms as units `simd-ARM` (`want`/`ustart`/`udone`); an unsplit run runs them in turn. The REACH stderr of the generator is kept only from `facts`, so the per-row sums see one simd process as before. Cost: the space is rendered 5 times (replicated, uncounted).

Proof the unsplit output equals the union of the sub-units: `run_g2_simd.py --quick` with no `--arms` (`logs/eq/all.out`) against the five `--arms` runs (`logs/eq/{facts,answers,paths,plants-a,plants-b}.out`), all `G2V_JOBS=2` niced, one at a time: the sorted non-trailer lines (105) are identical (`diff` empty); `checks passed` 1638 unsplit = 1638 summed over the arms; `checks failed: 0` in all six; `skipped arms: 0`. Each arm also ran through `run_g2.sh --quick --units simd-ARM` (rc 0, a `G2UNIT` line each).

## New weights and balance

Table `memfn/tests/g2_units.tsv` (header comment names the source, box, 16 cores, G2_JOBS, the scale): gcc 81, simd-facts 45, simd-answers 42, simd-paths 15, simd-plants-a 60, simd-plants-b 59, asan 46, win 54, w1w3 41, any 22, rows 5, k1 6, w2-* as above. Total 822. Prediction (`g2_parts.py predict`, sums of weights): N=4 `205 / 206 / 205 / 206` (max/min 1.00); N=8 `103 / 101 / 104 / 104 / 102 / 103 / 102 / 103` (1.03). Units overlap in time inside a part, so the real wall is below the sum (job 561: part sums 83 / 298 / 178 / 263 against walls 92 / 267 / 87 / 107; the sum is only an estimate of the ordering).

4-CORE RUNNER RATIOS MAY DIFFER from these 16-core ratios: the build and driver legs overlap here, the single-threaded gcc driver and the sequential legs do not shrink. The table is re-measured from any split run: `python3 -I memfn/tests/g2_parts.py reweight --table memfn/tests/g2_units.tsv --source 'TEXT' gather.log` (reads `G2UNIT name seconds` lines or gather's `units a:1s` lines), then `g2_parts.py predict --table ... 4 8`. The rule written in the header: no unit above total/N.

## Checks

- `g2_parts_selftest.sh`: 15 PASS lines, `checks failed: 0` (all plants red, clean N=1..4 green), run after the final table.
- `make strict` (`-j4`, niced): clean, rc 0 (`logs/strict.log`).
- `bash -n run_g2.sh`; `--units simd-*` runs; `assign` N=4 gives four non-empty parts (gcc w1w3 k1 ...; simd-answers simd-plants-a ...; simd-facts simd-plants-b rows ...; simd-paths asan win any ...).
- `make test-claudemd-size` through the pre-commit hook: within limits. Not run: a whole g2 (box rule), `make test`.

## Gate jobs

Prepared, `--dry-run` rc 0 for all three, NOT queued, in `/var/tmp/pcrec-pcrec/scratch/memfn/r39b/jobs/` (copied from r39's; tree `worktrees/r39b`, branch `lane/memfn-r39b`, keys `kit-r39b-*`): `563-kit-r39b-strict` (key `kit-r39b-strict`), `564-kit-r39b-g2split` (key `kit-r39b-g2split`, after strict; unsplit run, N=4 parts, gather, same-verdict diff, and NOW prints `g2split balance max Ns min Ns ratio R limit 1.5 ok|FAIL` and fails if max > 1.5 x min), `565-kit-r39b-test` (key `kit-r39b-test`, after g2split; `make test` via perfrun).

OWED: jobs 564 and 565 (full-size part walls vs the prediction, the unsplit-vs-split diffs at full size, `make test`); the lane ran no whole g2.

## Charter-vs-committed checklist

- [x] simd split at a natural boundary (arms), exact-population check covers each sub-unit once (they are table units; gather unchanged).
- [x] Unsplit simd equals the union of its sub-units (diff empty, 1638 = 1638).
- [x] Weights re-set from measured walls; header names source, box, cores, G2_JOBS; 4-core caveat stated; `reweight` subcommand documented.
- [x] Predicted N=4 and N=8 part walls from the table.
- [x] Selftest all plants red; `make strict` clean.
- [x] Gate jobs 563/564/565 prepared, dry-run, not queued; 564 checks max <= 1.5 x min.
- [ ] Real N=4 balance at full size: job 564.

## STATE AT HANDOFF

committed on `lane/memfn-r39b`; nothing running; scratch `/var/tmp/pcrec-pcrec/scratch/memfn/r39b/`.
