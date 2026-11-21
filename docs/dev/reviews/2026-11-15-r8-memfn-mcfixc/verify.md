# Verdicts

## Verdicts
ADQ-1 HOLDS, ADQ-2 HOLDS, ADQ-3 HOLDS

## ADQ-1: HOLDS
Ran `python3 -I adequacy/py/arm_keys.py $S` (S = slot dir of review tree). Output:
J4 7 verify null -> timed_form null; J4 4 verify rc-memcmp callees None; J4 12 verify rc-words callees None; J4 12 verify settest callees None; J4 1 ctl walk ()
link.py TIMED_CALLEES rows: mfind- (), fn-memchr (memchr), libc (memchr), pair (memchr), walk (), null (); timed_callees returns None (any external) when no prefix matches.
Pre-existing at BASE 6ab3f485b: yes, its TIMED_CALLEES has no settest/rc-* rows (only the `null` row is new in SUBJECT). Asymmetry (null keyed, verify arms any-external) is as described.

## ADQ-2: HOLDS
`grep -n -e "--second" 609-kit-mfcard-time 610-kit-mfcard-confirm common.sh` -> no matches (rc 1). 609 line 39: `d197_rule.py rule "$RUNDIR" "$RUNDIR.avx2libc"`; 610 line 41: `... rule "$RUNDIR" "$RUNDIR.avx2libc" --confirm "$CRD" "$CRD.avx2libc"`.
d197_rule.tsv:105: "then this rule again with the SAME arguments (a second run's --second included) plus --confirm"; :109: "ONE re-run allowed ... scored with `--second` naming this run's two records"; :108 "NOT-WIN second-run".
Ran (rundirs from est._synth, window mfcard, shipped record binds memchr=avx2 => INCONCLUSIVE; script verify/adq2.py):
A) `python3 -I $S/d197_rule.py rule verify/s/run verify/s/run.avx2libc` -> all 3 levels `INCONCLUSIVE (shipped-arm-no-verdict) -> the ONE re-run`
B) same + `--second verify/s/first verify/s/first.avx2libc` -> all 3 levels `NOT-WIN (second-run-without-a-verdict)`
So the jobs as staged (A shape) can never yield NOT-WIN on a re-queued second window; only a hand-added --second does. Not tested: 610 on a second-window CONFIRM path (reasoned from line 41 hard-coding).

## ADQ-3: HOLDS
Built est._synth(window="mfcard") (verify/adq3.py), deleted ONE line (`cells_sha256_J2`) from run_record.tsv (4 pins present before), ran `python3 -I $S/est.py rows verify/s3`:
rc=0, 211 stdout lines, stderr only `est: NOTE cells.J2.tsv: the record pins no cells sha-256 (finalized before r6): read unpinned` (printed twice). Priced, not refused.
Real records in the review tree: see counts below (window key / cells_sha256 lines per record).
s2d1: window-lines=0 cells_sha256-lines=0
s2d2: window-lines=0 cells_sha256-lines=0
(committed s2d1/s2d2 run_record.tsv at SUBJECT; path docs/design/memfn/span_cards/s2dN/)
VERIFY COMPLETE
