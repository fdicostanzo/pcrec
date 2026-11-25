# arenafix report (r104 fixes for [ARENA-SCOPES] F1)

## Summary

Branch `lane/arenafix` (cut from lane/arenabuild 71c425b78). Every r104 FIX-NOW and DOC item is applied, except where a
note below says otherwise; no compiler behaviour changed (src/ edits are comments only). The three gate findings
(MEMGATE-1, MEMGATE-3, CHECKS-4) each have a control that failed on the unfixed code and passes after. Three PLAN rows
filed (plan lint 0 violations). Mech re-run of the scope rows and a memgate sample run are OWED (box held by
arenabuild's queue job 200-arenabuild-mech/-test).

## Fixes

| finding | commit | what |
|---|---|---|
| MEMGATE-1 | a172fa1ed | `rungs`: any ERR side (either or both) is a failing move; VERDICT MOVED |
| MEMGATE-3 | a172fa1ed | `rung_layout`: LAYOUT needs both thresholds found, else MOVED (delta printed, not gated) |
| MEMGATE-2 | a172fa1ed | every mode returns 1 after its full report on STOP/MOVED/ERR; `main` exits with it; `make memgate-locked` runs all three modes then exits 1 if any failed; `peak` without `--bound` exits 1 on an ERR side |
| MEMGATE-5 | a172fa1ed | `--jobs` default `os.cpu_count()`; pooling the layout pass filed as a PLAN row |
| MEMGATE-6 | a172fa1ed | mg_drv.c `slot()` aborts naming MG_NARENA after a full probe cycle |
| CHECKS-4 | e4ce04987 | scope_check.c defines `abort()` -> `_exit(77)`; REFUSES requires exit 77, so glibc's `free(): invalid pointer` abort (SIGABRT) no longer reads as a refusal. No src change |
| CHECKS-1 | e4ce04987 | scanner: SCOPE_STORE accepts a cast; new rule for a `Scope` handle copied into a field; 2 MUST_FAIL fixtures; through-a-local form listed under "does not see" |
| CHECKS-3 | e4ce04987 | CHAN_CALL tolerates a space or a line break after `(`; 3 fixtures (1 must-fail on a broken-line non-chan call, 2 must-pass) |
| CHECKS-2 | e4ce04987 | rule header lists the regex limits (parenthesised names, macros, .h, file scope, ...) |
| CHECKS-6 | 449ffc42f | S3598 deleted (duplicate of S3597: the core arm never passed ASan flags); design notes it |
| REGISTRY-1 | 449ffc42f | design "Deviations at build": sabotage (3) UNREACHED, trigger "first scope client reachable from the force loop" |
| MEMGATE-7 | 449ffc42f | comments on `pcrec_err_chan` (internal.h, arena.c) narrowed to arena.c/sb.c; the 16 vm_stmt.c/enc.c sites noted as an F4 input (also in design) |
| MEMGATE-9 | 449ffc42f | internal.h `pcrec_sb_adopt` contract: dst and src must be distinct buffers |

Not applied: nothing left. CHECKS-6 took the "drop" option (the manager's leaning). The unwind site comment in the
design's line for (4c) still reads "run with REACH_ONLY=1" and is correct as is.

PLAN rows filed (Backlog, `make -s test-plan-lint` 0 violations): [W7-SITE-TALLY] (CHECKS-7), [MEMGATE-FAILFAST]
(MEMGATE-4), [MEMGATE-LAYOUT-POOL] (MEMGATE-5, the pooling half).
NOTED, no row: CHECKS-5 (scope_check floor 16 vs 35 deterministic checks is D110's form; a unit-test count may want an
exact pin, the manager's call), CHECKS-8 (known_stranded "reached" is a global OR over witnesses, allowlist-level),
MEMGATE-8 (`pcrec_err_chan` is an F1 placeholder; F4 adds the unconditional calls and the scanner then requires them).

## Controls

1. MEMGATE-1/2/3: `tests/core/memgate/test_verdicts.py` (new, 12 checks, fake sides, <1 s; `make memgate` runs it
   first). BEFORE (commit 7056a0a6f added it against the unfixed memgate.py): `test_verdicts: 8 of 12 FAILED`, incl.
   "both sides ERR: got ('IDENTICAL', None)", "flip, no threshold on the refusing side: got ('LAYOUT', None)", both
   exit-status checks. AFTER (a172fa1ed): `test_verdicts: ok 12/12`. Before-log: scratch/arenafix/memgate_before.txt.
2. CHECKS-4: the S3601 plant (sb_adopt accepts arena storage) applied to the built library, the OLD scope_check (71c425b78)
   against the NEW scope_check:
   OLD: `PASS: D-6: pcrec_sb_adopt into arena storage (dst) REFUSED` (glibc's bogus-free abort read as the refusal), rc=1 only through the src check.
   NEW: `FAIL: D-6: ... (src) REFUSED` and `FAIL: D-6: ... (dst) REFUSED`, rc=1. Unplanted: `scope_check: checks passed: 35, failed: 0`.
   Method: libpcrec.a of this worktree with sb.o replaced by one built from the planted sb.c (same edit as S3601).
3. CHECKS-1/3: the scanner's own self-test fixtures (MUST_FAIL cast + handle-field + line-break; MUST_PASS space + line
   break) run inside `scratch_builder_check.py`; after: `PASS: scratch_builder_check: ... 1 scope sites under the scope rules`.

Other re-runs, all clean: `make strict` (clean), `scripts/m6read_check_sab_anchors.py` (all anchors and runner plants
apply), `make -s test-plan-lint`, scope_check standalone built with -Werror -Wall (35/35), scanner as above. alloc_check
untouched (not re-run). No sabotage id taken (S3598 removed; none added).

## STATE AT HANDOFF

Rulings file: empty at every boundary, no R-n applied.
OWED: 200-arenafix-mech 200-arenafix-mg (the mech REACH run and the memgate sample below; the box stayed held by arenabuild's suite for the whole lane)
- mech with REACH on the touched scope rows: queue job `200-arenafix-mech` (S3593-S3597, S3599-S3603; expect
  `== mech run COMPLETE: 10 rows`); read with `scripts/monread arenafix` or `scripts/verdict`.
- memgate sample (queue job `200-arenafix-mg`; prep + peak/rungs/instr, side vs itself, --limit 25): its job log, last line
  `== mg sample COMPLETE`; each mode line `== MODE exit 0` expected (the noise read).
Note: the mech job archives HEAD at its start; later commits to this branch change what it tests.
