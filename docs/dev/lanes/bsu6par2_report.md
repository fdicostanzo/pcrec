# bsu6par2 report: review r87's FIX-NOW items on the parallel cards.py selftest

## STATE AT HANDOFF
Branch lane/bsu6par2 (cut from lane/bsu6par 2061e7e98), code and report committed; rulings file
`docs/dev/lanes/bsu6par2_rulings.md` was empty at the last re-read (no R-n applied). All five
FIX-NOW ids are built and run in-lane. No check's assertion, seed or printed text changed (the only changed printed
line is the `--units` summary, which is SUBSET-LABEL). No timing run, nothing under `memfn/src` or `src/`, c6_rule.md
untouched. OWED: job `759-kit-bsu6par2-selftest` (key kit-bsu6par2-selftest), queued, the full selftest at -j16 plus the
masked diff against 757's serial log; it prints its wall beside 758's 780 s. Log
`/var/tmp/pcrec-pcrec/scratch/bsu6par2/selftest_par.log`; the job's source is
`docs/dev/lanes/bsu6par2_evidence/jobs/kit-bsu6par2-selftest.job`; completion line `JOB: GREEN`, with
`IDENTITY: byte-identical to job 757's serial log`.

## FIXES BY ID
- DEADWORKER: `memfn/tests/parpool.py` `run` no longer uses multiprocessing.Pool (which never readies a dead worker's
  result). Each unit is its own forked process with a pipe; a child that closes the pipe without a result fails the run at
  once with `UnitError: unit N (name): its worker died without a result (exit code C)`, after writing the in-order
  outputs already complete; the live children are terminated and the scratch root removed.
- CLOSURE: `parpool.closure(units, want)` is the transitive closure of `needs`; `cards.py selftest --units` uses it
  (the old loop took one level).
- SUBSET-LABEL: a `--units` run prints `selftest (SUBSET k of 218 units): N checks, F failed`, never the full trailer.
- STATE-CONTROL: one fork per unit, by construction (the pool is gone; there is no worker to reuse).
- TAIL: ready units start longest-first by `Unit.cost`; `cards.py` reads the committed
  `memfn/tests/span_forms/selftest_unit_costs.tsv` (header names its source, job 758's PARPOOL_TIMES profile,
  2026-11-23, 218 units). A unit missing from the table sorts as 0 and prints a WARNING on stderr. Output stays in list
  order; `-j 1` is the serial path in list order, unchanged. `memfn/tests/CLAUDE.md` line updated (kept under 12 KB).

## DRILLS
`python3 -I memfn/tests/parpool.py selftest`: 0 failed, 11 rows (4 old + 4 new + 3 unchanged):
- a unit calling `os._exit(7)` with a 30 s unit alongside: the run fails in 0.0 s naming `dies`, "before" written,
  "never" not (DEADWORKER);
- six units mutating a global on two workers each see fresh state, parent's global untouched (STATE-CONTROL);
- five units with costs 0-4 start 4,3,2,1,0 on two workers while the output equals the serial list-order output (TAIL);
- a depth-3 `needs` chain, closure from its last unit is the whole chain, from an independent unit only itself, from the
  middle only its prefix (CLOSURE). The real unit list lists full closures, so the chain drill lives in parpool.
- the planted shared scratch still reads red as designed (6 of 8 race lines change).

## IN-LANE RUNS
All under `scripts/boxlock run --label bsu6par2` (script `docs/dev/lanes/bsu6par2_evidence/inlane.sh`, log
`docs/dev/lanes/bsu6par2_evidence/inlane.log`):
| run | result |
|---|---|
| parpool selftest | 0 failed |
| bsu6par's 59-check subset `-j 1` | rc 0, 153.5 s, `selftest (SUBSET 41 of 218 units): 59 checks, 0 failed` |
| same `-j 4` | rc 0, 40.2 s, same trailer |
| masked diff -j1 vs -j4 | byte-identical after masking the one (r44 E) draws line |
| the 59 rows vs job 757's serial log | 59 found, in order |
| `--units 168 -j 4` (units 164-167 needed) | rc 0, `SUBSET 5 of 218 units: 1 checks, 0 failed` |
| `--list-units` | 218 lines, needs columns as before |
| PARPOOL_PLANT=shared-scratch on the subset | identical (expected, as in bsu6par) |

## OWED RUNS
`759-kit-bsu6par2-selftest` (key kit-bsu6par2-selftest): full `cards.py selftest -j 16` on this worktree at the
committed tip, masked diff against `/var/tmp/pcrec-pcrec/scratch/bsu6fix3/selftest_full.log`; cap 1800, `--ready` rc 75
outside 01:00-17:45. Its log prints `SELFTEST rc=.. wall=N s ... job 758 ...: 780 s`; the verdict is `JOB: GREEN`
plus `IDENTITY: byte-identical`. Not yet run when this report was written.
