# S371 — [OPT-HYB-RESEED] THE ADAPTIVE TEXT NEVER EMITTED (src/gen/emit_vm.c,
# `vm_emit_search_body`): the table still selects an adaptive row and the
# artifact still stamps RX_VM_RESEED "adaptive", but the retry is the
# pre-abi-49 one — a clamp-free over-approximating hybrid steps every
# position after its first failed attempt. The stamp-vs-text lie D46 exists
# to forbid, and the defect the row was chartered for.
#
# TWO DETECTORS, deliberately different in kind, both in
# tests/codegen/run_codegen_tests.sh's [OPT-HYB-RESEED] block: the structural
# one (an adaptive witness's search loop carries ONE prefilter call site where
# two are expected, and none of the calibration literals is in the file) and
# the budget one (one failing candidate then 20,000 non-candidates gives up
# `steps` under --step-budget=2000). The answer corpus stays green: the plant
# changes no answer.
SAB_ID="S371-hyb-reseed-adaptive-text-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen"
SAB_DESC="the adaptive retry's text is never emitted while vm_plan_reseed still selects an adaptive row and RX_VM_RESEED still says so: every over-approximating clamp-free hybrid steps every position after one failed attempt, the pre-abi-49 defect, under a stamp that claims otherwise"
SAB_DOC_FIGURE="OWED (lane reseedfix re-anchor, 2026-09-30) -- prior: MEASURED 2026-09-29 (lane reseed): DETECTED, reach:ok(1/1),codegen:8fail/117pass -- the adaptive witnesses' prefilter-call-site and step-exit checks, the clamped witness's window_end check, both budget subjects answering steps, and [SABANCHOR]. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S371."
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "(?<=é)x" && grep -qF "#define RX_VM_RESEED \"adaptive\"" "$REACH_TMP/o.c" && grep -qF "if (reseed_steps) reseed_steps--;" "$REACH_TMP/o.c" && echo REACH-ADAPTIVE-TEXT'
SAB_REACH_EXPECT="REACH-ADAPTIVE-TEXT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (rs->row && rs->row->action != VRS_A_FIXED) {'
SAB_AFTER='    if (0 && rs->row && rs->row->action != VRS_A_FIXED) {   /* SABOTAGE S371 */'
