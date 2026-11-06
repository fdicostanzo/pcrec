# mechfix2 report (2026-11-05): [MECH-NOCOMPILE] parts 1-3

Scope kept: tests/mech (runner, nocompile selftest, 8 sabotage rows, CLAUDE.md), docs/testing.md, the plan row note, this report.
No src/, cli/, lib/, memfn/ edit. STATE: validation OWED (see STATE AT HANDOFF); the code is written and syntax-checked only.

PREMISE (checked): build/full_suite/20261104_daf6f002b/mech.log in the main tree ends
`== mech run COMPLETE: 1102 rows (unexpected: 0, undetected: 18, unreached: 16, anomalies: 7, oracle-skipped: 0)`; its 7 ANOMALY rows
are exactly S07 S1112 S1242 S184 S272 S403 S989.

## 1. S86

`tests/mech/sabotages/S86_kreset_write_untrailed.sh`: marker `\x01` -> `\x02` in both pairs (same fix as S53/S57, lane mechfix1;
`\x01` is PCREC_PREFIX_LEAD). Runner verdict OWED (job 430).

## 2. Per-row declaration: `SAB_EXPECT=COMPILE-CATCH`

Least machinery: one more value of the existing SAB_EXPECT field (sibling of BUILD-REFUSED, which covers the compiler tree's own build).
In `tests/mech/run_sabotage_matrix.sh`:
- declared and some failing arm's log carries a compiler error (the existing `NOCOMPILE_ERE`): verdict `DETECTED-BUILD (the designed compile-time catch fired: ARM:file:L:C: error...)`.
- declared and NO arm's artifact failed to compile (the catch stopped firing, whatever else failed): `**UNDETECTED -- NO ARM'S ARTIFACT FAILED TO COMPILE (SAB_EXPECT=COMPILE-CATCH wanted one)** ***UNEXPECTED***`, counted as undetected and unexpected, exit 1.
- undeclared compile failure: unchanged, ANOMALY. A typo in SAB_EXPECT is FATAL (the case list names the new value).
- The words DETECTED-BUILD / the UNEXPECTED verdict match no vcount ERE except the intended one (`UNDETECTED` only in the mismatch case).

Declared rows (each header read first; all say the compile failure is the designed catch or its documented signature):
S07 (header: OS-0b compile check, errno undeclared), S1112 (artifact "no longer compiles", "can never be copied"), S1242 and S989
(ksrc_deps_check (b): compile with -Isrc alone fails, `pcrec.h: No such file`), S184 (`_Static_assert` on RX_RESUME_FRAME_SIZE),
S272 (see caveat), S403 ("names arrays it lacks and fails to compile").

CAVEAT S272: its header names the nfa.c "bad AST node" wall; the 2026-11-04 log shows gen.c `-Werror=unused-parameter 'vars'`
(mechfix1 also saw `too few arguments to function 'rx_prefilter'`). Same cause (a prefilter built for a var pattern breaks the artifact),
wording of the error drifted. Declared as the brief's list says; the header text is not re-aimed. A reader who wants the row to be
kind A (a warning-clean plant instead) can drop the declaration; the ceiling then needs 1.

Control independence (learnings §3): the declaration lives in the row file, the evidence is the arm's own compiler output in its log
(a different source); a declared row that stops failing to build goes red rather than green. Population: the declared rows are the
seven above; a full run's DETECTED-BUILD count should be 7 (`grep -c DETECTED-BUILD` over the rows).

## 3. Anomaly ceiling

`ANOMALY_CEILING_PIN=0` in the runner (env override `MECH_ANOMALY_CEILING`). After the trailer line, `anomalies > ceiling` prints
`*** mech: anomalies N exceed the ceiling C ... ***` and exits 1 (the unexpected-row exit is unchanged and comes first). `make mech`
and the full suite's mech stage call the same runner, so both go red. Measured value expected with 1-2 in place: 0 (7 declared).
Single-row runs of an undeclared-anomaly row now exit 1 as well (intended).

`tests/mech/nocompile_selftest.sh` extended (the proof, no permanent row): Run A (Sy1 undeclared non-compiling, Sy2 clean, Sy3 = Sy1
declared) at ceiling 0 must read exactly 1 anomaly, Sy3 DETECTED-BUILD, rc 1 with `unexpected: 0` (so the ceiling alone is red);
Run B (Sy4, clean plant declared) must read UNEXPECTED, rc 1. No new S-id used.

Docs updated: tests/mech/CLAUDE.md, docs/testing.md (field table), the runner's own header + `--help`, plan row note
(row stays STATE:not-started in Backlog: plan_lint forbids started there; flip to done when the verdicts read green).

## STATE AT HANDOFF

- Branch lane/mechfix2, all committed; rulings file: none existed (last entry applied: none). Queue jobs read worktrees/mechfix2 at HEAD: do not remove it, commit nothing to the branch before they finish.
- Queued (scripts/boxqueue add, ids 430-433, keys = names):
  - `430-mechfix2-mechA`: S86 S07 S184 S403. Read `== mech run COMPLETE: 4 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0 ...)`; S86 row `DETECTED`, S07 S184 S403 rows `DETECTED-BUILD`.
  - `431-mechfix2-mechB`: S1112 S1242 S272 S989. Same trailer with 4 rows; all four `DETECTED-BUILD`.
  - `432-mechfix2-selftest`: `nocompile_selftest: DONE rc=0` with seven `ok` lines (the ceiling-alone-red line and the Sy4 UNEXPECTED line are the ratchet proof).
  - `433-mechfix2-mechfull` (LAST, ~7 h, cap 36000): `== mech run COMPLETE: N rows (... anomalies: 0 ...)` and job rc 0; seven DETECTED-BUILD rows. The ratchet itself rode this run.
- If 430/431 show a declared row DETECTED (not -BUILD) or UNEXPECTED, that row's compile catch has stopped firing: read its log, do not re-declare blindly.
- After green: set the plan row STATE:done (move per plan policy), update S86's SAB_DOC_FIGURE from the measured cells, S272's header wording if wanted.

## Triage 432 (lane mechtri5, 2026-11-05)

Cause: a bug in the self-test, not the runner. Job 432 read 6 of 7 `ok`; the one FAIL was "Sy3 (declared) reads DETECTED-BUILD". The matrix output did show `Sy3-selftest ... DETECTED-BUILD (the designed compile-time catch fired: ...)`, but the check's grep required a literal TAB before `DETECTED-BUILD`, and the matrix table pads columns with spaces (the tab-separated form is only the per-script `-- running` echo). Runner (`run_sabotage_matrix.sh` COMPILE-CATCH declaration, anomaly ceiling) behaved as designed in both runs: run A anomalies 1 / unexpected 0 / ceiling exit 1; run B UNEXPECTED, exit 1.

Fix: commit e5b0a5d0a, `tests/mech/nocompile_selftest.sh` line 45 only (tab -> `.* ` space match). The runner is UNCHANGED, so job 433 (runs this worktree HEAD) needs no new pickup for runner reasons, and the 4-row re-checks (435/436) were NOT re-queued (430/431 stand).

Queued: 434-mechtri5-selftest (owner mechtri5). Read: the last line must be `nocompile_selftest: DONE rc=0` with seven `ok` lines and no `FAIL`; job rc 0.
