#!/usr/bin/env bash
# S605 ([START-TABLE] C5, lane stc5, 2026-10-07; start_table.md §3.5's
# "no comparison reads a cand_rows[] row NAME", K84's rule widened to every
# slot) -- `vm_plan_reseed` DECIDES THE ARMED STATE BY THE RETRY ROW's
# SPELLING again: `strcmp(pcrec_cand_tok(rs->row), "adaptive-dense")` where
# the row's own payload field (`u.reseed.armed`) says it. Byte- and
# answer-invisible on every row today (only `adaptive-dense` is armed), which
# is the point: a new armed row with any other name would start unarmed.
#
# Detector: tests/codegen/run_cand_rows.sh's [cand-no-name-strcmp], widened at
# C5 to the WINDOW/WIDTH/RETRY/BOUND rows under the row-name-expression rule
# (their names are ordinary words, so a literal alone does not fire; here the
# call also reads `pcrec_cand_tok(`). The corpus arm is not named: the plant
# moves no artifact byte.
SAB_ID="S605-cand-retry-row-read-by-name"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="candrows"
SAB_DESC="vm_plan_reseed decides the retry's armed state by strcmp on the RETRY row's spelling (pcrec_cand_tok == \"adaptive-dense\") instead of its u.reseed.armed field: byte-identical today, the K84 shape the start table's check forbids on every slot since C5"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/stc5_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S605."
# [MECH-REACH] the planted line runs on every hybrid; this one is armed.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''[a-z](?=the)'\'' && grep -q '\''^#define RX_VM_RESEED "adaptive-dense"'\'' "$REACH_TMP/o.c" && echo REACH-ARMED-RESEED'
SAB_REACH_EXPECT="REACH-ARMED-RESEED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    rs->block0 = u->armed ? rs->cal.block : 0;'
SAB_AFTER='    rs->block0 = !strcmp(pcrec_cand_tok(rs->row), "adaptive-dense") ? rs->cal.block : 0;   /* SABOTAGE S605 */'
