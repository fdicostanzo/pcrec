# S254 — [REVW.U L5-R2] THE SATURATING-MULTIPLY BOUNDARY IS WEAKENED BY ONE,
# AND NO ANSWER-LEVEL CHECK CAN SEE IT.
#
# RE-ANCHORED at [PATFACTS] step 3.6 (R3, 2026-09-28, lane pf36): the three
# separate `pcrec_mrl_sat_mul`/`pcrec_vm_fmul`/`pcrec_cg_sat_mul` functions
# this row was written against are now TWO — mrl.c's and callgraph.c's
# copies were the same four-line algorithm typed twice (R3's finding) and
# are now ONE shared `pcrec_sat_mul(a, b, cap)` (src/opt/mrl.c), taking the
# ceiling as a parameter; `pcrec_vm_fmul` (src/gen/emit_vm.c) is untouched.
# The row's SITE, PLANT and DETECTOR are UNCHANGED IN SHAPE — only the
# function name and the ceiling's spelling (a parameter `cap` rather than
# the file-local `MRL_MINW_MAX` macro) moved, and the intent was
# re-verified by applying it (see the updated SAB_DOC_FIGURE below): a
# weakened `pcrec_sat_mul` now disagrees with `pcrec_vm_fmul` at exactly
# the same boundary pair as before, since `pcrec_sat_mul` is called with
# `MRL_MINW_MAX == PCREC_MINW_MAX` at every real site (mrl.c AND
# callgraph.c now share this one call, so a weakening here weakens BOTH
# callers, not just mrl.c's — which is stronger detection than the row
# had, not weaker).
#
# `pcrec_sat_mul`'s overflow guard changes from `a > cap / b` to
# `a >= cap / b` — one character. At the exact boundary pair where
# `a == cap / b` (integer division), the unsabotaged function still
# computes `a * b` (which fits, by construction of the guard); the
# sabotaged one now saturates to `cap` one pair early instead.
#
# THIS IS lens 5's OWN "THE ONE THAT MATTERS" (lens_reports/
# lens5_unit_seams.md R2): it under-estimates by one, and under-estimating
# is `pcrec_minw`'s SAFE direction (`src/gen/emit_vm.c`'s own comment on
# `pcrec_vm_fadd`: "under-estimating is the safe direction and saturation is an
# under-estimate"). A too-small `minw` prunes LESS, never deletes a live
# match — so NO PATTERN IN THE WHOLE CORPUS ANSWERS DIFFERENTLY. `make
# test`'s whole answer-level suite, `tests/mrl/run_mrldiff.sh`'s own
# differential (byte-identical for 701 of 944 patterns already, by its own
# stated acceptance), and the `.rxt` corpus are all structurally blind to
# it: the bound is merely LOOSER than it could be, and every one of them
# only ever checks that the bound holds, never that it is TIGHT.
#
# WHAT SEES IT: `tests/core/sat_arith_check.c`'s CHECK 1 (cross-family
# equality) — `pcrec_sat_mul`'s boundary pair now disagrees with
# `pcrec_vm_fmul`, which still carries the unweakened `>` — at
# EXACTLY one pair and no other.
SAB_ID="S254-mrl-sat-mul-boundary-off-by-one"
SAB_FILE="src/opt/mrl.c"
SAB_SUITES="core"
SAB_DESC="pcrec_sat_mul's overflow guard a > cap / b weakens to a >= cap / b, saturating one pair earlier than pcrec_vm_fmul at the exact boundary -- an UNDER-estimate, pcrec_minw's safe direction, so no pattern in the corpus answers differently and every answer-level check in the tree is structurally blind to it; only the cross-family agreement check (tests/core/sat_arith_check.c) sees the single differing pair. Since [PATFACTS] step 3.6 this one shared function is called by both mrl.c and callgraph.c, so the plant reaches both callers at once"
SAB_DOC_FIGURE="RE-MEASURED 2026-09-28 against this worktree's tree (lane pf36, post-unification): bash tests/core/run_core_tests.sh reports 'mul: pcrec_sat_mul/pcrec_vm_fmul DISAGREE at (1, 549755813889): 1099511627776 / 549755813889' -- CHECK 1 (add) and every other sub-check stay green, and run_core_tests.sh's own summary moves from 'checks passed: 7 / checks failed: 0' to 'checks passed: 6 / checks failed: 1' -- the identical numbers the pre-unification row recorded (2026-09-17: 'DISAGREE at (1, 549755813889): 1099511627776 / 549755813889 / 549755813889'), confirming the merge changed nothing about this boundary. Reverted before commit. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S254."
SAB_COUNT=1
SAB_BEFORE='    if (a > cap / b) return cap;'
SAB_AFTER='    if (a >= cap / b) return cap;   /* SABOTAGE S254: boundary weakened by one */'
