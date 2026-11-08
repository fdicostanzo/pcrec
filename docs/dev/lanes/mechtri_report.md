# mechtri report (2026-11-08, sonnet)

Triage of the three UNEXPECTED rows in full battery 500-main-fullsuite2 (mech.log, main a0a829246): S50-revdet-no-reverse-check, S806-set-offset-nearer-branch, S-U10-cwmin-fixpoint-one-round. All three: no real miscompile, no real coverage gap in src/; the planted code paths moved under the alternation landing (f77ed1130) and variable lookbehind, so each row's witness no longer shows the plant. Class for all: witness no longer reaches / no longer shows the site.

## Per-row diagnosis

Method: built the tree at HEAD (git archive) and one copy per plant in $PCREC_TMPDIR/scratch/mechtri, applied each row's SAB_BEFORE/AFTER, compared clean vs planted by hand.

- S50. `(?:ab|b){m,n}` is folded to `a?b`-shaped code by [ALT-NF] before the revdet rung looks at it. Planted and clean both stamp PA_VM_RUNGS 0x2 (FRAMES_BOUNDED) on every patterns.txt member, so the plant is never reached. Witness no longer reaches site.
- S806. `(?:ab:|c:)` is factored to `(?:ab|c):`: ':' is a trailing literal, not a set member carried through both branches, so rb_intersect is not on its path (RX_REQ_HANDOFF "2" clean and planted). Witness no longer reaches site (the same shape as the 2026-10-11 re-aim, moved again).
- S-U10. The planted tree still compiles the two-hop cell with the same answers. What changed: since [VLOOKBEHIND] a wrong cwmin does not refuse the lookbehind; it opens the pair (cwmin != cwmax), the branch VARIES and compiles as a variable lookbehind (extra RX_SLOT_LB_LO0, two back-step sites). The .rxt cell cannot see that. Detector's symptom changed (refusal to varying form).

## Fixes

- S50: new tests/rungselect/patterns_revambig.txt (hand-written, 6 bodies deterministic forward, ambiguous backward, not rewritten by the folds, e.g. `(?:ab|[bc]){1,3}c`); run_rungdiff.sh runs it by default after patterns.txt. Planted: 6 patterns diverge (":abcb:abc" rung 6,9 vs replication 1,4). Row header notes the re-aim.
- S806: new 5.12a row `(?:ab:y|c:)` in tests/codegen/run_prechecks.sh (K 2 clean, 1 planted); row's SAB_REACH re-aimed to the same pattern.
- S-U10: new fixture `residlbcall` in tests/codegen/run_codegen_tests.sh (`back_step:1`; population guard 9 -> 10); planted gives 2 call sites and the existing seam checks FAIL. Row SAB_SUITES now "codegen harness".

## Checks

Done here (hand-run on scratch trees, not through the matrix because the box lock is held by the battery):
- clean: run_codegen_tests.sh 336 pass / 0 fail; run_prechecks.sh 396 pass / 0 fail; run_rungdiff.sh default 211 agreed, 0 diverged.
- planted: codegen fails on residlbcall (5 FAIL lines); prechecks 1 fail (the new row); rungdiff 6 diverged.
- VALIDATE_ONLY on the three rows: fields OK; m6read_check_sab_anchors.py: all 1167 anchors resolve.

Undetected/unreached vs the previous green record (full-suite 20261104_daf6f002b mech.log: undetected 18, unreached 16): this run undetected 21 = those same 18 + the three rows above; unreached 16, identical names. No movement besides the three.

## STATE AT HANDOFF

- Branch lane/mechtri, commit db8c00fef (plus this report commit). Rulings file empty; last entry applied: none.
- OWED (queued, one chain, each waits for the one before): 460-main-b202611081406162216137.build, 461-...test (make test via perfrun; touches codegen and rungselect scripts), 462-...mech (S50 S806 S-U10: expect DETECTED, rows=3, unexpected 0).
- Not done: no real matrix run of the three rows yet (verdicts come from 462).
