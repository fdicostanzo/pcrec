# mfindg2 — triage and fix of the cloud G2 red on lane/memfn-mfind

STATE: delivered, validation complete.

## Summary

Cloud `make test` of lane/memfn-mfind @ c369bbfc6 (GitHub run 43680940102) failed one shard, 1/18:
`FAIL: (b) rows never chosen: fn/fn-mfind fn/mfind-w16 fn/mfind-w32` (`test-memfn-g2`). The cause is a test
wiring gap, not a kit bug: the mfind family's runner linked the PLAIN library, so its generator printed no
`MFTRACE REACH` lines, and the three rows (unpicked by default, reached only through the test-only lever
`mfind`) were never credited. Fixed the general way: the family's process now links the library of the run
(the MF_TRACE build under `--rows`) and writes its REACH lines to `reach/gen-mfind.err`, exactly as the SIMD
family's does. `FLOOR_ROWS` does not move.

## Cause

- `memfn/tests/run_g2.sh` section 4z passed `--lib "$plainlib"` to `run_g2_mfind.py` (the comment said "the
  form is no row of section 4b's registry"). That was wrong for this form: the three rows ARE registry rows
  (the REACH dump lists every row of every table, chosen=0 when never picked), so every other process
  reported them at 0 and no process reported them above 0. Row (b) reads the summed tally and found three zeros.
- Precedent that was missed: the SIMD family (section 4a) links `$lib`, passes `--reach-err`, and its
  `gen-simd.err` joins the sum (the FLOOR_ROWS comment records fn/vrun-w16/-w32 as reached "by the SIMD
  family's process").
- Why the lane's own runs did not show it: the lane ran the standalone runner (`run_g2_mfind.py`, which
  judges its own checks, not the row tally) and queued the whole-gate job (621 kit-mfind-g2) as OWED
  (mfind_report.md); (b) is judged only by a whole `run_g2.sh --quick` (unsplit) or by the gather of all parts,
  neither of which had run before the cloud. Not a shard-mode difference as far as read from the script: the unsplit run
  uses the same processes and the same tally, so it would fail the same way (not re-run against the unfixed script).

## Fix

- `memfn/tests/run_g2_mfind.py`: new `--reach-err FILE`; the stderr of every generator process (each
  target x lever) is written there, concatenated (REACH lines are summed per line downstream, so
  concatenation is the same as separate files).
- `memfn/tests/run_g2.sh` section 4z: the runner gets `--lib "$lib"` (the traced library under rows) and
  `--reach-err "$work/reach/gen-mfind.err"` when rows are on; the comment now says why. No row is exempted by name.
- `FLOOR_ROWS` stays 20: the distinct (table,row) count is the same before and after (the three rows were
  already counted, at zero); the measured count is 36 against the floor 20, a floor that is a lower bound
  ("distinct pairs >= floor"), so raising it is not owed by this change.
- No `memfn/tests/CLAUDE.md` role change beyond the runner now taking the traced library; its entry is
  updated to say so. No sabotage anchor moved.

## Validation

All runs on the lane worktree, nice, -j8, logs in /var/tmp/pcrec-pcrec/scratch/memfn/mfindg2/.

- `make test-memfn-g2` in full (`g2_full.log`): `checks passed: 70358672`, `checks failed: 0`, no
  `*** [... test-` line. Tally lines: `row-chosen fn fn-mfind 240`, `fn mfind-w16 160`, `fn mfind-w32 80`;
  `PASS: (b) every row chosen >= 1 over the tier`, `(c) 36 distinct ... >= floor 20`, `(d) all 22 G2 kit
  processes printed REACH lines`, `(a) every REACH_DROPPED is 0`, `(e)` PASS.
- Sharded form (`--quick --part K/4`, K=1..4, run in turn; then `g2_parts.py gather`): part1-4 rc=0
  (`part1-4.log`); `gather.log`: `the 4 parts ran all 29 units, each exactly once`, `(a)`-`(e)` PASS incl.
  `(b) every row chosen >= 1 over the tier` and `(c) 36 distinct ... >= floor 20`, `checks passed: 70358675`,
  `checks failed: 0`, gather rc=0. The mfind unit ran in part 2 (67 s). `g2_parts_selftest.sh`:
  `checks failed: 0`, rc=0 (`selftest.log`).
- `python3 -I scripts/m6read_check_sab_anchors.py`: `sabotages checked: 1300 (1354 anchor sites)`, `all anchors resolve`.
