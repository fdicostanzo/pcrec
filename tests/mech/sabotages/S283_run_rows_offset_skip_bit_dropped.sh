# S283 — [OPT-LITSCAN] S1 THE TWO-BIT DENY'S SECOND HALF DROPPED
# (src/gen/emit_dfa.c, `dfa_pfs[]`): the run rows carry
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
SAB_REACH='"$PCREC" --features all -p rx -fno-offset-skip -o "$REACH_TMP/o.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"memchr\"" "$REACH_TMP/o.c" && "$PCREC" --features all -p rx -o "$REACH_TMP/p.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/p.c" && echo REACH-OFFSET-SKIP-DENIES-RUN-ROWS'
SAB_REACH_EXPECT="REACH-OFFSET-SKIP-DENIES-RUN-ROWS"
SAB_COUNT=2
SAB_BEFORE='PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run'
SAB_AFTER='PCREC_NO_RUN_PREFILTER /* SABOTAGE S283 */, pf_run'
