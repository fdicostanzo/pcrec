# Lane formsfixi report: review r39's K1-K6, K8, K12 on the span forms' cards (rev 11)

Lane formsfixi (opus), 2026-11-17, branch `lane/memfn-formsfixi` from `lane/memfn-forms` @ 1aec5d4d3.
Brief: the kit manager's, from review r39's RULED section (`docs/dev/reviews/2026-11-17-r39-memfn-forms5.md`).
Files: `memfn/tests/span_forms/cards.py`, `docs/design/memfn/r45_reply.md` (rev 11), the review file and its
index line, `memfn/tests/NOTES.md` (K12), `docs/design/memfn/CLAUDE.md` (the rev line). No compiler or kit
source moved; no timing, no queue job, no cloud run.

## Summary

Rev 11 closes r39's EXE level with LAYOUT TWINS, as RULED. A layout twin is the same compiled object linked a
second time behind a padding object, so every function of the artifact and its driver sits at another
address: byte-different, the same object code, the same answers (gated like any cell). Step 1 times I's twin
`I.lt` as one more arm of I's pool in every C1-C2 cell, and `aa-twin` is now `aa`'s layout twin. A new LAYOUT
TWIN TERM (the RMS of `ln(t(I.lt) / t(I))`, df = exe pairs) floors every cell, and `rule` prints the night's
MEASURED between-exe offset. The confirm re-runs on FRESH twins (`I.cf`, `h<N>.cf`), so an exe's offset
cannot replicate. The confirm now feeds ONE predicate, step (4)'s win (reading B, K4). R0 reads every
reading, the confirm's included (K2). The confirm's per-arm reading is kept and the text now matches it
(K3). `rule` and `rerun` compute their owed list through one function with one recorded G2 list (K6). Two
printed controls are now checked (K8). The plan prints the confirm's bound (K5), and the docs are updated
(K12). Every rev 10 drill and the class drill still pass, the new rows pass, and every new control fails
as it must (Validation).

## Fixes

| id | fix | where |
|---|---|---|
| K1 | Layout twins. The perturbation: a padding object of 1,040 (layout 1) or 2,080 (layout 2) bytes of `.text` linked BEFORE the artifact's object (`pad_object`, `build_cell`). The TU is now compiled once to an object keyed by its text, and every exe is a link of it. The proof (`cards.py dry`, 11-17, WIDTH_FLAG=none): 38 twin exes, all byte-different, `rxa_search` moved in all 38 (shifts 1,056/1,088 and 2,080-2,112 B), every twin cell answer-gated (120 step 1 twin cells + 108 `I.cf` cells, 0 failures). `I.lt` is in I's pool; `aa-twin` is lay 1; the layout term `max`es into every cell's floor; `rule` prints `BETWEEN-EXE offset sigma per exe (MEASURED)`; the confirm times `I.cf` and `h<N>.cf`. Drill rows: per-exe offsets held across every reading at tau 1/2/3 % give P(h* != 64) 0.000/0.000/0.000, with confirm cells on those no-win nights at mean 0.00/0.01/0.00 (max 0/4/0). The measured offset reads back as 0.0097/0.0197/0.0296 (0.0004 at tau 0). Control: rev 10's floor+confirm gives 0.647. The §3 sentence "exactly what a head against I is" is corrected. Step 1's expected wall: +9.1 % (0.105 -> 0.115 h; `plan`, UNMEASURED constants) | cards.py `LAYOUT_PAD`, `arm_base/arm_lay/arm_head`, `pad_object`, `build_cell`, `layout_proof`, `layout_sigma`, `analyse`; r45_reply §3 "The layout twin term", "The floor `f`" |
| K2 | R0 scans every results file the night holds, read alike (step 1 + its re-run, C3, the confirm). A gate failure of `I.cf` makes the night DEFECTIVE; one of `h<N>.cf` removes H(N) | `analyse` R0 block; §3 R0 row |
| K3 | Sound choice: the script's per-arm reading. A head's confirm reads `I.cf` against `h<N>.cf` only. Another head's void says nothing about this head's win, and voiding every confirm on any arm would cost power for no protection. The text is corrected to say so. A selftest row checks both directions | `confirmed()`; §3 "Confirm by re-run" |
| K4 | Reading B: `r1(..., wins_ok=)` gates step (4)'s `won` only, and W, E and dominance read the first reading (R3's per-class pick too). Multi-winner power row: 275/300 (accept >= 85 %). Control (rev 10's reading, `READING_B=False`): 107/300. One-winner 4 % row as RECORD: 184/300 | `r1`, `analyse`; §3 step (4), drill (xxii) |
| K5 | The plan prints the confirm's BOUND (56 cells, 456 arm cells, 0.061 h) beside the one-win case (H(8): 14 cells, 0.004 h), with the selftest figures labelled RECORD. Night order step 1 names the confirm before h is frozen | `cmd_plan`; night order step 1 |
| K6 | `owed_now(rundir, g2file)` is THE one computation, called by `cmd_rule` and `cmd_rerun`. `--g2 FILE` given to either is recorded in `RUNDIR/rule_g2.json`, and a call without it reads the record. Drill: 12 nights through the commands on disk with G2 = {16}: 0 stalled, and `rerun` timed exactly `rule`'s owed list on every pass. Control (record removed, rev 10's rerun): 5/12 stalled | `night_g2`, `owed_now`, `confirm_cells`; §3 "Confirm by re-run" |
| K8 | `check(pj2i <= 0.05)` (the J2 cut in rounds under rev 9's floor) and `check(picks9 > 15)` (the fast split under rev 9's rule), each now its own selftest line. The §6 sentence says which levels have a control, plus a "comparison kinds" list | selftest; r45_reply §6 |
| K12 | cards.py usage text (rev 11; `rerun` = voids + the confirm into `results_confirm.tsv`; the G2 record; `rule`'s exit 3 names a confirm; `selftest --rev11`). S3310-S3312 named in memfn/tests/NOTES.md. NOT done here: their lines in `tests/compound/CLAUDE.md` (4) and `run_shell_checks.sh`'s header, which are lane formsfixj's files (brief: do not touch) | cards.py docstring; memfn/tests/NOTES.md |

Review file: `docs/dev/reviews/2026-11-17-r39-memfn-forms5.md` (r39 verified free on main, lane/covs2b and every
`lane/memfn-*` branch; r33-r38 taken), with its RULED section, and the reviews CLAUDE.md line. Sabotage ids
S3325-S3329: none taken. The cards' controls are selftest rows (each "control:" line must FAIL under the rule
it names); no mech row was needed.

Recorded limit (rev 11 text): the layout term is ONE night-wide number. An exe-offset size that differs by
pattern is pooled over the night's 18 exe pairs, because a per-pattern estimate would have df 2. The confirm on
fresh twins covers the rest, since an offset a fresh exe does not share cannot replicate.

## Validation

SELFTEST_PLACEHOLDER

- `cards.py dry` (WIDTH_FLAG=none, JOBS=6, this worktree's build, full 1 MiB subjects;
  `/var/tmp/pcrec-pcrec/scratch/memfn/formsfixi/dry1.log`):
  `# dry: cells 1482, built and gated 1482, failures 0`;
  `# dry: layout twins (rev 11, r39 K1): 38 twin exes (20 step 1, 18 confirm I.cf), byte-different 38,
  rxa_search moved 38 (shifts 1056,1088,2080,2096,2112 B); answer-gated: 120 step 1 twin cells + 108 I.cf
  cells, failures 0`. Step 2b's deny check prints WOULD REFUSE (VACUOUS: H(64) loops nowhere in C3/C4 at
  width 32). That is expected on this subject tree, which lacks main's width option; r39's NOTED item says
  the night runs the COMBINED branch's binary.
- `cards.py plan`: 1482 cells (AA 24, C1 528, C2 660, C3 144, C4 48, C5 78); 267 distinct compiles + 20
  layout-twin links; run 860 cells timed, 0.11 h (0.115; rev 10's step 1 0.105 h: +9.1 %); c3 0.01 h;
  confirm bound 0.061 h; 132 cells, 4,300 timed launches.
- `make strict`: rc 0 ("whole tree compiles clean with -Werror -Wshadow; the kit's target table check passes").
- Doc checks: `make test-spec-history` 11/0; `scripts/check_claudemd_size.sh --all` 370 files within limits
  (docs/dev/reviews/CLAUDE.md 11,642 B).
- Not run (brief): make test, queue jobs, timing, cloud.

## STATE AT HANDOFF

- Branch `lane/memfn-formsfixi`, every piece committed (tip in the handback message).
- Rulings file `docs/dev/lanes/formsfixi_rulings.md`: empty at every read (no entry to apply).
- The night's job set (`/var/tmp/pcrec-pcrec/scratch/memfn/fcards/jobs/`, read only): no edit needed. Twins are
  built and gated in `dry` (700) and linked in `rerun` (701), and the plan format is unchanged. A G2 list now
  reaches `rule` and `rerun` only through `RUNDIR/rule_g2.json`, written by a `--g2` call; the jobs pass none
  today (told to the kit manager).
- For the landing: K12's two remaining doc lines (tests/compound/CLAUDE.md (4), run_shell_checks.sh's header)
  sit in lane formsfixj's files.
- OWED: none
