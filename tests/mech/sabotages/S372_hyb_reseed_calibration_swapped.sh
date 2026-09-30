# S372 — [OPT-HYB-RESEED] THE TWO CALIBRATION ROWS SWAPPED (src/gen/emit_vm.c,
# `vm_plan_reseed`): the frameless class reads the framed row and the framed
# class the frameless one, so a frameless hybrid re-seeds almost at once
# (first 2, gap 4) and a framed one steps 64 positions before its first
# re-seed. No answer moves, and the codegen block's budget arm stays green:
# in the sparse tail the first probe re-seed jumps to the end whichever row
# is read, so any finite block passes it (r1 panel chk F4, the finding this
# row pins). Only the per-class CALIBRATION check of
# tests/codegen/run_codegen_tests.sh's [OPT-HYB-RESEED] block can see it —
# every adaptive witness's retry spells the other class's literals.
SAB_ID="S372-hyb-reseed-calibration-swapped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen"
SAB_DESC="the hybrid retry's two calibration rows are swapped: each program class re-seeds with the other class's crossover gap, block, cap and first budget -- no answer moves and the budget arm stays green, so only the per-class calibration literal check can see a calibration row moved"
SAB_DOC_FIGURE="OWED (lane reseedfix, 2026-09-30): expected DETECTED by the five adaptive witnesses' calibration checks plus [SABANCHOR]. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S372."
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "(?<=é)x" && grep -qF "#define RX_VM_FRAMELESS 1" "$REACH_TMP/o.c" && grep -qF "unsigned reseed_steps = 64, reseed_block = 0;" "$REACH_TMP/o.c" && echo REACH-FRAMELESS-CAL'
SAB_REACH_EXPECT="REACH-FRAMELESS-CAL"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    rs->cal = vm_reseed_cal[v->has_push];'
SAB_AFTER='    rs->cal = vm_reseed_cal[!v->has_push];   /* SABOTAGE S372 */'
