# S254 — [REVW.U L5-R2] THE SATURATING-MULTIPLY BOUNDARY IS WEAKENED BY ONE,
# AND NO ANSWER-LEVEL CHECK CAN SEE IT.
#
# `mrl_sat_mul`'s overflow guard changes from `a > MRL_MINW_MAX / b` to
# `a >= MRL_MINW_MAX / b` — one character. At the exact boundary pair where
# `a == MRL_MINW_MAX / b` (integer division), the unsabotaged function still
# computes `a * b` (which fits, by construction of the guard); the
# sabotaged one now saturates to `MRL_MINW_MAX` one pair early instead.
#
# THIS IS lens 5's OWN "THE ONE THAT MATTERS" (lens_reports/
# lens5_unit_seams.md R2): it under-estimates by one, and under-estimating
# is `pcrec_minw`'s SAFE direction (`src/gen/emit_vm.c`'s own comment on
# `vm_fadd`: "under-estimating is the safe direction and saturation is an
# under-estimate"). A too-small `minw` prunes LESS, never deletes a live
# match — so NO PATTERN IN THE WHOLE CORPUS ANSWERS DIFFERENTLY. `make
# test`'s whole answer-level suite, `tests/mrl/run_mrldiff.sh`'s own
# differential (byte-identical for 701 of 944 patterns already, by its own
# stated acceptance), and the `.rxt` corpus are all structurally blind to
# it: the bound is merely LOOSER than it could be, and every one of them
# only ever checks that the bound holds, never that it is TIGHT.
#
# WHAT SEES IT: `tests/core/sat_arith_check.c`'s CHECK 1 (cross-family
# equality) — `mrl_sat_mul`'s boundary pair now disagrees with
# `pcrec_vm_fmul`/`pcrec_cg_sat_mul`, which still carry the unweakened `>` — at
# EXACTLY one pair and no other.
SAB_ID="S254-mrl-sat-mul-boundary-off-by-one"
SAB_FILE="src/opt/mrl.c"
SAB_SUITES="core"
SAB_DESC="mrl_sat_mul's overflow guard a > MRL_MINW_MAX / b weakens to a >= MRL_MINW_MAX / b, saturating one pair earlier than pcrec_vm_fmul/pcrec_cg_sat_mul at the exact boundary -- an UNDER-estimate, pcrec_minw's safe direction, so no pattern in the corpus answers differently and every answer-level check in the tree is structurally blind to it; only the cross-family agreement check (tests/core/sat_arith_check.c) sees the single differing pair"
SAB_DOC_FIGURE="HAND-MEASURED 2026-09-17 against this worktree's tree (pre-mech): bash tests/core/run_core_tests.sh reports 'mul: mrl_sat_mul/pcrec_vm_fmul/pcrec_cg_sat_mul DISAGREE at (1, 549755813889): 1099511627776 / 549755813889 / 549755813889' -- CHECK 1 (add) and every other sub-check stay green, and run_core_tests.sh's own summary moves from 'checks passed: 7 / checks failed: 0' to 'checks passed: 6 / checks failed: 1'. Reverted before commit. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S254."
SAB_COUNT=1
SAB_BEFORE='    if (a > MRL_MINW_MAX / b) return MRL_MINW_MAX;'
SAB_AFTER='    if (a >= MRL_MINW_MAX / b) return MRL_MINW_MAX;   /* SABOTAGE S254: boundary weakened by one */'
