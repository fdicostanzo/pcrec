# s3012fix report: S3012 re-homed to the window runner; the twin check now covers the DETECTOR

Lane s3012fix (opus), 2026-11-24. Branch lane/s3012fix, cut from lane/memfn-plantcheck @ 63e474123.
D203 bug fix, test side only. I edited nothing under src/, cli/, lib/ or memfn/src, so kit bytes are unchanged.
Inputs: s3012tri_report.md (the triage), plantfix2_report.md, review r94, and the mutant harness
`docs/dev/lanes/plantfix2_evidence/harness.py`.

## Summary

- **S3012 moved.** It is out of `memfn/tests/run_g2_pres.sh` (PLANTS, `plant_spec`, `plant_expect`,
  the `--reach` comment, the header) and in `memfn/tests/run_g2_win.sh`. Its edit is unchanged.
  The win runner now asserts a reason: `plant_expect S3012` = `^FAIL: site inrun#[0-9]+ DECIDE: `,
  so a plant that is red only for some other reason reads `RED BUT NOT BY ITS DETECTOR` and exits 1.
  It is a DECLARED twin of mech S3012 (`PLANT_TWINS="S3012"`). The mech row's arm is g2win, so the
  runner is now the row's own detector as well as its own edit.
- **Proved on this Mac.** `bash memfn/tests/run_g2_win.sh --plant S3012` printed
  `PLANT S3012 RED   (driver passed failed: 6897 43): FAIL: site inrun#2602 DECIDE: stop 1@7, the reference 1@1`
  with rc 0. The 43 failures are the 43 filter-decisive in-run sites that s3012tri measured.
- **Pins.** PLANT_PINS: win 39 (was 38), pres 34 (was 35), proof 6, wreply 2, 81 in total.
  Twins compared: 39 (pres 34 + proof 4 + win 1).
- **GF-1's hole is closed, as a class fix** (`scripts/m6read_check_sab_anchors.py`):
  - (a) The twin check reads the row's SAB_SUITES, through `read_row`, the same reader as the rest
    of the check. A declared twin is valid only if an arm among those suites runs the twin's runner
    in its DEFAULT mode. Otherwise the check reports `TWIN DETECTOR MOVED`.
    - The arm-to-runner map is READ from `tests/mech/run_sabotage_matrix.sh`'s arm table, not
      hand-copied. That table is each `NAME)` block that calls `score_arm`, and the map takes that
      block's `bash "$tree/X"` calls that pass no argument.
    - The map is closed over the scripts those runners call (`bash "$ROOT/X"`, no argument). That
      gives memfnfinder -> run_finder.sh -> run_proof.sh.
    - An arm that passes a mode does not count: g2v runs `run_g2_win.sh --v`, a different detector.
    - If the table yields no arm, the check reports `ARM TABLE UNREADABLE`.
  - (b) `PLANT_TWINS` must be ONE literal assignment of ids, and the dump's declared twins must be
    exactly that literal's ids. `PLANT_TWINS="$PLANTS"`, a second assignment, or a mode that passes
    anything other than the literal each read `TWINS NOT EXPLICIT`. The pres runner's blanket
    declaration is now a literal of its 34 ids.
  - (c) The standing `--selftest` has 12 new cases, which brings it to 68 cases and 11 unit rows.
    All three drills the brief names go red: S3044's suites set to g2win, a blanket PLANT_TWINS, and
    S3012 restored to pres.
- **Mutants.** I added 15 T mutants on the new clauses to the harness. All 15 are killed. The whole harness has 80 mutants: 78 killed, plus P15 and N15, the two that plantfix2 already argued equivalent.
- **Pass form documented.** All 4 runner headers now state their `--plant` pass form exactly. A
  detected plant prints `PLANT <id> RED ...` (run_wreply.sh: `PLANT <id>: RED (...)`) and the run
  exits 0. GREEN means NOT DETECTED and exits 1.
- **PLAN item for main**, not closed here: runner plants are checked to APPLY and never to DETECT.
  See "STATE AT HANDOFF".

## Changes

| file | change |
|---|---|
| `memfn/tests/run_g2_win.sh` | S3012 `plant_spec` case (the mech row's edit, `win` dialect) with its provenance; a new `plant_expect` (patterns `;`-separated, each required; empty = any FAIL, so the other 38 plants behave as before) and the `RED BUT NOT BY ITS DETECTOR` branch in `--plant`; `S3012` in PLANTS; `PLANT_TWINS="S3012"` with the explicit-literal rule stated; the header's PASS FORM |
| `memfn/tests/run_g2_pres.sh` | S3012 removed (case, `plant_expect`, PLANTS, the `--reach` "S3012's in-run stop" note); the plant-table header says where it went and why; `PLANT_TWINS` is now the literal 34-id list, with why a blanket is refused; the header's PASS FORM (RED / GREEN / RED BUT NOT BY ITS DETECTOR / OWED / MOVED A PASS) |
| `tests/memfn/run_proof.sh`, `tests/memfn/run_wreply.sh` | the header's PASS FORM (wreply's own colon spelling and its setup exit 2) |
| `scripts/m6read_check_sab_anchors.py` | `read_row` also returns SAB_SUITES; `arm_runners()` (the matrix arm table, default-mode calls, the closure); `explicit_twins()`; `twin_check` holds `TWIN DETECTOR MOVED`; `plant_pass` records `ARM TABLE UNREADABLE`; PLANT_PINS win 39 / pres 34; the matrix joins SELFTEST_TREE; 12 new CASES (below); the header documents both clauses |
| `docs/dev/lanes/plantfix2_evidence/harness.py` | T1-T15, the mutants on the new clauses |
| `tests/mech/sabotages/S3012_in_run_stop_filter_deleted.sh` | comment only: the runner twin is run_g2_win.sh's S3012 (no SAB_* value moved; the anchor check reads it unchanged) |
| `memfn/tests/CLAUDE.md`, `memfn/tests/NOTES.md`, `tests/mech/CLAUDE.md`, `tests/memfn/CLAUDE.md` | the plant lists follow the move; the twin rule restated (each CLAUDE.md within its 12 KB limit, `check_claudemd_size.sh --all` clean) |

Other statements of the pass form, found by grep (`PLANT <id> RED|GREEN`, and `--plant(s)` with
green/red/detected/pass across `*.md`, leaving out reports, history, reviews and journals): no
committed orientation or spec file states it. The one wrong statement was the kit journal's account
of the form the kit manager gave main (memfn/docs/journal.md, 2026-11-24), which is append-only
history and already says it was wrong. I left it as it is.

## Drills and mutants

**Self-test cases added** (`--selftest`, each in its own hardlinked copy):

| case | rc | words required |
|---|---|---|
| S3012 restored to pres (out of win: case, PLANTS, PLANT_TWINS; into pres, the edit unchanged) | 1 | S3012, TWIN DETECTOR MOVED, run_g2_pres.sh |
| S3044's row re-aimed to g2win, the runner not | 1 | S3044, TWIN DETECTOR MOVED, g2win |
| S3044's row to g2pres-asan (the same runner: the CONTROL) | 0 | all runner plants apply |
| S3012's row to g2v (a MODE of its runner) | 1 | S3012, TWIN DETECTOR MOVED, g2v |
| S1221's row with no SAB_SUITES | 1 | S1221, TWIN DETECTOR MOVED, none |
| run_finder.sh runs run_proof.sh in a mode (the closure) | 1 | S1221, TWIN DETECTOR MOVED, run_proof.sh |
| the arm table gone | 1 | ARM TABLE UNREADABLE, MISSING |
| the arm table yields no arm | 1 | ARM TABLE UNREADABLE, NO ARM READ |
| blanket `PLANT_TWINS="$PLANTS"` (pres) | 1 | TWINS NOT EXPLICIT, run_g2_pres.sh, 0 literal |
| a second, blanket PLANT_TWINS after the literal (pres) | 1 | TWINS NOT EXPLICIT, run_g2_pres.sh, 2 assignment |
| the mode passes `$PLANTS`, not the literal (win) | 1 | TWINS NOT EXPLICIT, run_g2_win.sh, does not pass |
| a non-arm block (one that scores no arm) running run_proof.sh, with S1221's suites set to it | 1 | S1221, TWIN DETECTOR MOVED, zzfake |

The clean-copy case now also requires `runner plant twins checked: 39 `.

**The live instance.** The S3012-restored case is today's base exactly: S3012 back in pres and its
row unchanged. It goes red as `TWIN DETECTOR MOVED`. The plantfix2 check was green on that base
(39 twins, rc 0, per s3012tri).

**Mutants** (harness T1-T15; KILLED = the live run or the self-test exits non-zero):

| id | mutant (clause broken) | verdict | killed by |
|---|---|---|---|
| T1 | the twin's suites never compared to the runner's arms | KILLED | S3012-restored, S3044-to-g2win, S3012-to-g2v, no-SAB_SUITES and closure cases |
| T2 | the row's SAB_SUITES never read (the runner's own arms used instead) | KILLED | the same cases |
| T3 | read_row's SAB_SUITES replaced by every runner's arm | KILLED | S3012-restored, S3044-to-g2win, S3012-to-g2v |
| T4 | any arm counts, not the arms that run THIS runner | KILLED | S3012-restored, S3044-to-g2win, closure |
| T5 | the DEFAULT-mode rule dropped (an arm that passes a mode counts) | KILLED | S3012-to-g2v, closure |
| T6 | the closure dropped | KILLED | the LIVE run (proof's 4 twins red) and the clean copy |
| T7 | blocks that score no arm read as arms | SURVIVED run 1, then KILLED | I added the selftest case "a non-arm block (scores no arm) running the runner". On today's table T7 was equivalent: the one non-arm 12-space block runs no runner. A table edit could change that, so the case now pins it. |
| T8 | a table that yields no arm is not unreadable | KILLED | no-arm case |
| T9 | a missing table is not unreadable | KILLED | table-gone case |
| T10 | an unreadable table is not recorded | KILLED | both table cases |
| T11 | the ONE-assignment rule dropped | KILLED | second-blanket case (the pres literal equals its PLANTS, so only this rule sees it) |
| T12 | the LITERAL rule dropped | KILLED | blanket case |
| T13 | the dump's twins not held to the literal | KILLED | mode-passes-$PLANTS case |
| T14 | explicit_twins never called | KILLED | the three explicit cases |
| T15 | harness self-check: a syntax error | KILLED | live and selftest (a positive control on the harness itself) |

**T tally:** 15 mutants, 15 killed. T7 survived the first run and was killed after I added its case.
Evidence: `docs/dev/lanes/s3012fix_evidence/mutants_T_run1.out` (the first run) and
`mutants_all.out` (the final run).

**The whole harness on the final code** (`mutants_all.out`), 80 mutants: the 65 that plantfix2
ran plus T1-T15.
- 78 KILLED.
- 2 SURVIVED: **P15** (nplants taken from the rows, not the summary) and **N15** (a per-runner
  timeout instead of the shared deadline). These are the same two plantfix2 argued EQUIVALENT
  (plantfix2_report.md, "Self-test and mutants"). My change touches neither clause, so the
  argument still holds.
- 0 harness errors.

**One drill the harness cannot reach:** the window runner's asserted reason. I changed
`plant_expect S3012` to a pattern that never occurs (`... PLAN: `), ran `--plant S3012`, and
restored the file (`git status` clean afterwards). The run printed
`PLANT S3012 RED BUT NOT BY ITS DETECTOR (^FAIL: site inrun#[0-9]+ PLAN: ; driver passed failed: 6897 43): FAIL: site inrun#2602 DECIDE: ...`
with rc 1. So the reason is asserted, not decorative.

**Flake noted, not mine:** in T2's run, the old case "a grandchild escapes the group, holding the
pipes" (15 s bound) also FAILED. The box was loaded at the time: two harness workers plus the r99
gate. It passed in every other run (the control, T1, T3-T15, and both self-test runs).

## Validation

All runs were on the Mac with gcc-16, under `worktrees/.mac-suite.lock` (owner line naming
s3012fix), with TMPDIR=`$PCREC_TMPDIR/scratch/s3012fix/tmp`. The logs are copied to
`docs/dev/lanes/s3012fix_evidence/`.

| what (exact file/command) | result |
|---|---|
| PREMISE: `python3 -I scripts/m6read_check_sab_anchors.py` at the cut | `runner plants checked: 81`, `twins checked: 39` (as the brief states) |
| `bash memfn/tests/run_g2_win.sh --plant S3012` (the tip's runner) | `PLANT S3012 RED   (driver passed failed: 6897 43): FAIL: site inrun#2602 DECIDE: stop 1@7, the reference 1@1`, **rc 0**, about 45 s (`win_plant_S3012.log`; run twice, identical) |
| the same command with `plant_expect S3012` changed to a pattern that never occurs (restored afterwards) | `PLANT S3012 RED BUT NOT BY ITS DETECTOR (...)`, **rc 1** (`win_plant_S3012_wrong_reason_drill.log`) |
| `python3 -I scripts/m6read_check_sab_anchors.py` (both halves, final tip) | rc 0: 1404 rows / 1463 anchor sites resolve; `runner plants checked: 81 (89 edits, 4 runners, each at its pin)`; `runner plant twins checked: 39` (`live_pass.out`) |
| `... --selftest` pooled and `... --selftest --serial` (final code) | `plant pass selftest: 68 cases, 11 unit rows, 0 failed`, rc 0 both ways; the stdout of the two runs is **byte-identical** (`cmp`); serial wall 69 s (`selftest_serial.out`) |
| harness `docs/dev/lanes/plantfix2_evidence/harness.py` (all 80) | the control GREEN; 78 killed; P15 and N15 equivalent (as plantfix2 argued) (`mutants_all.out`) |
| `make CC=gcc-16 strict` | **0 warnings**. rc 2 only from the PRE-EXISTING aarch64 targets-check: `MISMATCH the host family MF_FAM_AARCH64 compared no target`, the features control, level admission 0/0. That is the known Mac state the brief names. |
| `make CC=gcc-16 -j8 test-codegen` | rc 2. **19/22 scripts passed.** The 3 reds are exactly the PRE-EXISTING Mac-only ones: `run_size_term.sh` (K100), `run_case_spelling_identity.sh` (empty `.text`, Mach-O) and `run_residual_twins.sh` (no PLT on Mach-O). The suite's own `[SABANCHOR]` row is PASS: 1404 rows, 81 runner plants at their pins, selftest 68 cases + 11 unit rows, 0 failed. |
| `bash scripts/check_claudemd_size.sh --all` | 440 files within limits |

No kit byte moved, so the mech half's anchors and the codegen identity are unaffected. The
`--selftest` is what [SABANCHOR] runs inside test-codegen.

## STATE AT HANDOFF

- STATE: complete. Validation is complete and nothing is owed by this lane. Rulings file:
  **R-1 applied** (the last and only entry): (1) below, and (2) the member list below.
- Tip: see the handback; the branch is lane/s3012fix.
- **For main's x86 run (R-1 (1)).** The PR #1 gate is S3012 detected on x86. From a checkout of
  lane/s3012fix at the tip, on the Linux dev box (plain `gcc` is GNU there), run:

      bash memfn/tests/run_g2_win.sh --plant S3012

  No env is needed: the plant mode builds its kit from memfn/src and needs no LIB. TMPDIR is
  optional and defaults to /tmp, so on the dev box set `TMPDIR=$PCREC_TMPDIR`, by RUNS.md's rule.
  The PASS is a line beginning `PLANT S3012 RED   (driver passed failed: ` that ends with a
  `FAIL: site inrun#<N> DECIDE: ...` line, and **rc 0**. The Mac printed
  `PLANT S3012 RED   (driver passed failed: 6897 43): FAIL: site inrun#2602 DECIDE: stop 1@7, the reference 1@1`.
  Each of these is NOT a pass and gives rc 1:
  - `PLANT S3012 GREEN (NOT DETECTED; ...)`
  - `PLANT S3012 RED BUT NOT BY ITS DETECTOR`
  The window path is host-independent (r98), so expect the same 43 failures.
- **PLAN item for MAIN** (not closed here; main files it as ONE row, per R-1 (2)).
  - **Class:** runner plants are checked to APPLY (the [SABANCHOR] plant pass, every
    test-codegen), never to DETECT. A runner plant whose witness stops reaching its site reads
    GREEN only when someone runs `--plants`. S3012 sat GREEN for 11 days (d5f9da41b, 2026-11-13,
    to the dev box's job 200, 2026-11-24).
    - The twin clause added here catches the case where a twin's mech row was re-aimed.
    - It cannot catch a runner plant with no mech twin (42 of 81: win 38, proof 2, wreply 2), or a twin whose row has not
      been re-aimed yet.
  - **Row:** a scheduled `--plants` detect job per runner, main's and the kit's, on the Linux dev
    box: a box-queue job, red on any line other than `PLANT <id> RED` (or `PLANT <id>: RED` for
    wreply) and on a non-zero rc.
  - **Trigger:** the measurement exists now (S3012's GREEN, job 200-main-pres7; D77). Schedule it
    nightly, or at least on every kit merge that touches memfn/src.
  - **Box:** the Linux dev box. The pres runner's x86-v3/x86-64 passes and its plants S3098-S3103
    run only there; the Mac skips those targets.
  - **The kit's 4 runners (member list), each one's `--plants` wall:**

    | runner | plants | `--plants` wall | basis |
    |---|---|---|---|
    | `memfn/tests/run_g2_pres.sh --plants` | 34 | about 51 min (dev box) | MEASURED rate: job 200 ran 7 plants in 629 s on Zen 4, about 90 s a plant, times 34 |
    | `memfn/tests/run_g2_win.sh --plants` | 39 | about 30 min (ESTIMATE) | MEASURED one plant: S3012 in about 45 s on this Mac, NOASAN, times 39; the r99 coordinator's `--plants` run on this Mac (2026-11-24, crit-memfn-winsplit3) has the measured figure |
    | `tests/memfn/run_proof.sh --plants` | 6 | about 5 min (ESTIMATE) | one kit build + check/run per plant, not measured here |
    | `tests/memfn/run_wreply.sh --plants` | 2 | about 10 min (ESTIMATE) | each plant builds a whole pcrec copy (`make -j16`) under the box lock; not measured here |

    Main's own `--plants`/plant runners are main's to list; the kit's are the four above.
    [RUNNER-PLANTS-POOL] (a pool for these modes) would shorten each wall, and it is not a
    prerequisite for this row.
- Not done, by brief: no new ids; no kit byte; I did not touch the kit journal's line on the wrong
  pass form (history).
- The lock was taken and released twice. The r99 coordinator held it from 18:29 to 20:27 and I
  waited in the foreground, polling every 5 min.
- owed: none
