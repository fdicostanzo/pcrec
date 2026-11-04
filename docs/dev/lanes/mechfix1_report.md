# mechfix1 report (2026-11-04): repair the stale and non-compiling mech plants, [MECH-NOCOMPILE] part 1

Scope kept: only tests/mech/sabotages/*.sh, the plan row note, this report. No src/, cli/, lib/, memfn/ edit.
"Before" = the single-row run (or the plant built and run by hand) at main a42deaac4; "after" = checked by hand on a
scratch plant tree (plant applied by replace.py, `make all`, the row's arm run directly: zero `file:L:C: error:` lines,
failures still present). The runner's single-row verdict for each changed row is OWED (queued, see STATE AT HANDOFF):
a row's final DETECTED word is the runner's, not the by-hand check's.

| row | before | change | after |
|---|---|---|---|
| S1152 | ANOMALY: `(?m)(\n^)` under the A_BOL plant is unsatisfiable, its prefilter leaves `window` uninitialised (-Werror=maybe-uninitialized) | plant is now the wrong ROW (`(?m)^` builds MLINE_EOL, not the wrong node); keeps the `if (multiline)` | by hand: assertions dir 0 compile errors, 538 failed / 12797 passed. Runner verdict OWED |
| S1159 | ANOMALY: same cause (`\z` patterns unsatisfiable once has_end is never set) | the hoist is skipped for every row but the SUBJECT_END pin, so only `(?m)$`/`(?m)^` lose the view | by hand: 0 compile errors, 587 failed / 12748 passed. Runner verdict OWED |
| S1174 | ANOMALY: same cause (the swap makes `a\z` and `\Aa` unsatisfiable) | one-sided: `\z` is built as `\Z` (A_EOL); the `\A` half is dropped (any pin swap is unsatisfiable on some corpus pattern) | by hand: 0 compile errors, 197 failed / 13138 passed. Runner verdict OWED |
| S135 | does not score ANOMALY any more; already built | NONE (reported, not touched) | single-row run DETECTED: corpus 20 fail / 2409 pass, laround 1 / 4, laexpand 0 / 11 |
| S231 | ANOMALY: `unused parameter 'b'` in tests/mrl/cwmax_check.c | `(void)b;` in the plant | runner verdict OWED (not checked by hand: the arm needs the whole mrl driver) |
| S272 | ANOMALY: gen.c `unused parameter 'vars'` AND `too few arguments to function 'rx_prefilter'` (pattern `^a(?=${v})bc$`) | NONE: the plant's own description says the failure is a compile error; with the prefilter forced on for a var pattern the emitter produces C that cannot build (a real error, not a warning) and pcrec itself refuses most cases with an internal error. Cannot be made warning-clean without changing what it plants | PROPOSAL: a designed compile-time catch, goes with S07 S1112 S184 S989 S1242 to the runner's per-row declaration (out of scope here) |
| S666 | ANOMALY: `unused parameter 'n'` in the kit's generated compare (bound dropped) | the bound is still emitted behind `0 &&`, so `n` is read and the compare no longer stops at the subject end | single-row run DETECTED: reach ok 2/2, memfnarms 6 fail / 368 pass, trailer `1 rows (... anomalies 0)` |
| S1418 | does not score ANOMALY any more | NONE (reported, not touched) | single-row run DETECTED: corpus 0 / 98, offsetskip 8 fail / 18 pass |
| S739 | ANOMALY: `unused variable 'landmark_position'` (the misderived route emits the entry front where nothing reads the landmark) | second pair emits `(void)landmark_position;` after the declaration | by hand (prefilter.rxt): 0 compile errors, 34 failed / 19 passed. Runner verdict OWED |
| S676 | ANOMALY: `'rx_class_bitmap1' defined but not used` (term 0 only: later class tables never referenced) | later terms are still built and emitted as `&& (1 \|\| (...))`, so the tables stay referenced; same mutant | by hand, harness arm: 0 compile errors but 0 failures (3653 pass), so the harness arm alone does NOT detect it; the memfnarms arm is expected to (S677's plant fails 32 there). Runner verdict OWED; if it reads UNDETECTED that is a finding, not a repair |
| S678 | skipped, per brief (already clean) | none | none |
| S719 | ANOMALY: `-Werror=parentheses` (`1 \|\| a == b && c`) | second pair closes the compare in a parenthesis: `if (1 \|\| (` ... `))` | by hand (g2simd --quick): 0 compile errors, 573 failed / 1043 passed. Runner verdict OWED |
| S707 | ANOMALY: `comparison of unsigned expression in '< 0'` (`rmin - 1` is 0 for a lazy `{1,}`) | cap is `rmin > 1 ? rmin - 1 : rmin`: short only where it can be | by hand (vm_lazy_rmin_prefix.rxt): 0 compile errors, 68 failed / 70 passed. Runner verdict OWED |
| S53 | ANOMALY (mechtri3 re-aim builds, but 11 patterns fail to compile) | the re-aim marked the source with `\x01`, which is PCREC_PREFIX_LEAD (the placeholder every `vm_rolef` text begins with), so vm_r_set's untrailed branch fired on every prefixed source and printed an unrewritten `q_...` name. Marker changed to `\x02`. No new witness pattern was needed: `(a?){0,17}b` reaches both re-aimed texts | by hand, counterkdiff arm: 1 diverged (`(a?){0,17}b`), 58 agreed, 0 compile failures (clean tree: 59 agreed, 0 diverged). Runner verdict OWED |
| S57 | same | same marker fix; the same pattern is the witness (the span-loop low-water mark of `a?` inside the counter loop) | by hand: identical counterkdiff line. Runner verdict OWED |
| S271 | ANOMALY: `rx_span_match_caseless` implicitly declared | not stale in the way mechtri3 read it: the call's name now comes from the VmVarOps `caseless` field, not `seam_entry`, so the plant left the artifact calling the caseless entry with no declaration. Second pair reads that field as false | by hand (vars/caseless.rxt): 0 compile errors, 9 failed / 16 passed. Runner verdict OWED |
| S403 | ANOMALY: `rx_class_bitmap0` undeclared | NONE. Not stale: its own header says the artifact "names arrays it lacks and fails to compile"; the fault IS a build failure | PROPOSAL: a designed compile-time catch (like S272), for the runner's per-row declaration; not retired |

## Findings outside the brief

- S86 (mechtri3's re-aim, S86_kreset_write_untrailed.sh) carries the same `\x01` marker bug as S53/S57; it was not in this lane's list and is NOT
  touched. Its queued re-validation (322-main-mechtri3) will show the same compile failures if run. Fix is the same one-character change.
- The generated-code warning behind S1152/S1159/S1174 is a real, general wart: any pattern the DFA proves unsatisfiable gets a prefilter whose
  `window` array gcc reads as maybe-uninitialised under -Wall -Wextra -Werror. The clean tree never meets it on the corpus. Not fixed (no build go); noted for the owner.
- S676: the harness arm detects nothing now (it did 20 / 3537 for the plant as it was measured on 2026-10-08, but those were compile failures of the old plant, see above); the row's detection rests on memfnarms.

## Method note

The runner's own single-row run takes ~5 min and waits on the box lock behind the queue; the plants were iterated with a scratch script
(plant tree from `git archive HEAD` + replace.py + `make all`, then the arm run directly), under $PCREC_TMPDIR/scratch/mechfix1/ (mkplant.sh, qc.sh).

## STATE AT HANDOFF

- Branch lane/mechfix1, all rows committed (WIP commit 69212b12e plus the report/plan commit); worktree clean. No rulings file entry (none existed).
- Plants changed: S1152 S1159 S1174 S231 S271 S53 S57 S666 S676 S707 S719 S739. Untouched: S135 S1418 (DETECTED already), S272 S403 (designed compile-time catches), S678 (clean).
- DETECTED by the runner's single-row mode: S666, S135, S1418 (logs $PCREC_TMPDIR/scratch/mechfix1/before.S666.log, before.S135.log, before.S1418.log).
- OWED, queued (boxqueue, one job per 4 rows, each `expect rows=4`): `200-mechfix1-mechA` (key mechfix1-mechA) (S739 S676 S719 S707), `201-mechfix1-mechB` (key mechfix1-mechB) (S53 S57 S271 S1152), `202-mechfix1-mechC` (key mechfix1-mechC) (S1159 S1174 S231 S666). Read each trailer `== mech run COMPLETE: 4 rows (...anomalies 0...)`. The jobs run worktrees/mechfix1 at its HEAD: do not remove the worktree before they finish. The queue was behind the kit's sp1b2 chain when queued.
- After the verdicts: update the SAB_DOC_FIGURE of S1152 S1159 S1174 S676 S707 S719 S739 (stale figures for the old plants) and the plan row (13-row inventory shrinks to S272 S403 plus the 5 designed catches for the runner declaration). S86 needs the `\x02` fix.
- Scratch: $PCREC_TMPDIR/scratch/mechfix1/ (plant trees t_*, logs, jobs/).
