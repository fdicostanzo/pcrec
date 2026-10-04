# S441 — [OPT-HYB-RESEED-FORM] A1: ROW `anchored` NEVER HOLDS
# (src/gen/emit_vm.c, `vm_reseed_holds`): the row stays in
# `pcrec_reseed_rows` and `--list-axes` still prints it, but its predicate
# answers false, so a start-anchored over-approximating hybrid falls through
# to `adaptive-dense` and carries the adaptive retry tail its attempt loop
# can never reach — the abi-55 shape this row removed. (S440 was claimed by
# lane vedge, building in parallel; this lane takes S441.)
#
# DETECTOR: tests/codegen/run_codegen_tests.sh's [OPT-HYB-RESEED] block,
# check (5): the `anchored` and `gstart` witnesses stamp `adaptive-dense`
# where `anchored` is expected, carry two prefilter call sites where one is,
# and no longer equal their -fno-hyb-reseed artifacts. No answer moves (the
# tail is unreachable), so the answer corpus stays green by design.
SAB_ID="S441-hyb-reseed-anchored-row-never-holds"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen"
SAB_DESC="row anchored's predicate answers false: a start-anchored hybrid takes adaptive-dense and carries the unreachable adaptive retry tail instead of the deny's retry"
SAB_DOC_FIGURE="OWED (lane rsform, 2026-10-03). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S441."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "^(?>a|ab): (.*)\$" && grep -qF "#define RX_VM_RESEED \"anchored\"" "$REACH_TMP/o.c" && echo REACH-ANCHORED-ROW'
SAB_REACH_EXPECT="REACH-ANCHORED-ROW"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        return pcrec_fact_start_anchor(v->cx) != PCREC_SANCH_NONE;
    case VRS_P_DENSE:'
SAB_AFTER='        return 0 && pcrec_fact_start_anchor(v->cx) != PCREC_SANCH_NONE;   /* SABOTAGE S441 */
    case VRS_P_DENSE:'
