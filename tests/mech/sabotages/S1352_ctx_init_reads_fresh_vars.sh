# S1352 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: rx_subst_ctx_init reads it->vars on a FRESH iterator with no rx_iter_vars (F-R3-1).
# Witness (RETIRED, see SAB_EXPECT note): the `varunset` cell's dirty arm (`${!v}-$1`, no variables, every rx_iter field 0xA5): a wild pointer read.
# Reach (K35): token S1352 (cell varunset); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1352-ctx-init-reads-fresh-vars"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='rx_subst_ctx_init reads it->vars on a FRESH iterator with no rx_iter_vars (F-R3-1)'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1352.'
# RE-DECIDED 2026-10-24 (lane s1352; mech job 611 read subst:0fail/7567pass): an
# EQUIVALENT MUTANT now. Its only witness was the subst suite's dirty arm
# (every rx_iter field 0xA5), retired by lane substland3 when main's
# RX_ITER_INIT began writing every field (match_api.md 3.8p5: "RX_ITER_INIT
# writes every field ... the setters' defaults"; rx_iter_init emits
# { FRESH, 1, 0, s, n, 0, NULL, 0, NULL }). The plant makes the read of
# it->vars/nvars unconditional. Over every state the contract admits
# (3.8p4/p9a: a caller writes the struct only through RX_ITER_INIT and the
# setters, and only while FRESH; vars/nvars "hold valid values in every state"):
# FRESH w/o rx_iter_vars -> NULL/0, the loop body never runs, same as v=NULL,
# nv=0; FRESH with it, BOUND -> the original reads them too; ENDED, and a BOUND
# iterator whose refused setter set hdr=0 -> setters change nothing in vars, so
# they still hold the init/rx_iter_vars values. Only a never-initialized or
# 0xA5-filled struct differs, and that is outside the contract (3.8p5).
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (it->hdr == PCREC_ITER_BOUND\n"'
SAB_AFTER='"    if (1 || it->hdr == PCREC_ITER_BOUND   /* SABOTAGE S1352 */\n"'
