# S283 — [OPT-LITSCAN] S1 THE TWO-BIT DENY'S SECOND HALF DROPPED
# (src/gen/emit_dfa.c, `dfa_pfs[]`, `cand_rows[]` since [START-TABLE] C3): the run rows carry
# `PCREC_NO_RUN_PREFILTER` alone, so `-fno-offset-skip` no longer removes
# them and stops keeping lib/pcrec.h's promise of the pre-[OPT-K] artifact.
# litscan_s1.md §7.1 row (k), R3-8.
#
# INVISIBLE TO `make test-axes`: every axis still denies the rows through the
# surviving bit's own flag, answers are identical, and the sweep never asks
# WHICH bit did it. The detector is the one structural row that does.
SAB_ID="S283-run-rows-offset-skip-bit-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="the run-pinned rows lose PCREC_NO_OFFSET_SKIP from their deny mask, so -fno-offset-skip leaves router on run-pinned (the offset-skip block still emitted) instead of the pre-[OPT-K] memchr artifact"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane s1build, single-row mech): DETECTED -- reach:ok(1/1), prechecks:20fail/269pass (§5.10 row k, plus every §3.4b/§4.x arm that reads the run check under -fno-offset-skip). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S283."
# RE-AIMED 2026-10-11 (lane rlhbuild, [REQ-HANDOFF-L1]): as S282, the deny
# probe adds `-fno-req-handoff` (the re-entry outranks memchr otherwise).
SAB_REACH='"$PCREC" --features all -p rx -fno-offset-skip -fno-req-handoff -o "$REACH_TMP/o.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"memchr\"" "$REACH_TMP/o.c" && "$PCREC" --features all -p rx -o "$REACH_TMP/p.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/p.c" && echo REACH-OFFSET-SKIP-DENIES-RUN-ROWS'
SAB_REACH_EXPECT="REACH-OFFSET-SKIP-DENIES-RUN-ROWS"
# RE-AIMED 2026-10-07 (lane stc3, [START-TABLE] C3, start_table.md §3.5):
# `dfa_pfs[]` is deleted into `cand_rows[]`, whose two run rows break the
# line after the deny mask (stc2's S283 collision guard), so the anchor spans
# the break. Intent re-verified: the plant still drops PCREC_NO_OFFSET_SKIP
# from both run rows' deny and nothing else (count 2).
# RE-AIMED 2026-10-24 (lane fsfix, full-suite 20261023_5596c3207 triage): the
# deny mask's NO_OFFSET_SKIP bit became a REDUNDANT second reader when D172 S2
# (wsc3-wsc6) made pf_window_of state no window under -fno-offset-skip, so the
# run pin is gone before the mask is consulted: the one-site plant is an
# EQUIVALENT mutant (measured: /user|/users -fno-offset-skip -fno-req-handoff
# stays memchr under it; prechecks 0fail). The property -- the bit denies the
# run rows -- needs BOTH readers dropped: site 1 the mask (as before), site 2
# pf_window_of's own NO_OFFSET_SKIP clause. Measured with both: run-pinned.
SAB_COUNT=2
SAB_BEFORE='PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER,
             pf_run'
SAB_AFTER='PCREC_NO_RUN_PREFILTER /* SABOTAGE S283 */,
             pf_run'
SAB_FILE2="src/gen/emit_dfa.c"
SAB_COUNT2=1
SAB_BEFORE2='    if (wk && us->kind != DFA_PF_NONE && !pcrec_opt_has(cx->opt, PCREC_NO_OFFSET_SKIP) &&
        !pcrec_opt_has(cx->opt, PCREC_NO_RUN_PREFILTER)) {'
SAB_AFTER2='    if (wk && us->kind != DFA_PF_NONE &&   /* SABOTAGE S283 (site 2) */
        !pcrec_opt_has(cx->opt, PCREC_NO_RUN_PREFILTER)) {'
