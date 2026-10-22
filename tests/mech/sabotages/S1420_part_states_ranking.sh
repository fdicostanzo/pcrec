#!/usr/bin/env bash
# S1420 (D172 S2 commit 6, lane wsc6; the kit manager's R1) -- PCREC STATES A
# RANKING ON A PRE-CHECK FUNC PART (src/gen/emit_dfa.c `req_site_define`):
# the part, which states its window facts and its name only, also carries
# rank_n 1. The ranking is the kit's renderer interface since commit 6 (the
# translation writes it); pcrec states none.
#
# SUCCESSOR of S731-S737 (retired at commit 6 with pcrec's ranking: the
# reader `pcrec_find_run_rank` and the builder `ofs_pred_rank`): the check
# they planted against (tests/memfn/run_rank.sh) now holds that pcrec states
# NO ranking, and this plant is its failing direction. The kit refuses the
# part too (window.c `wf_old_fields`), so the pre-check's compiles fail.
#
# Arm `rank` (tests/memfn/run_rank.sh): the probe's RANK line for the part
# reads rank_n 1, and rank_check.py's no-ranking claim goes red.
SAB_ID="S1420-part-states-ranking"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="rank"
SAB_DESC="pcrec's pre-check builder states rank_n 1 on each FUNC part (a renderer-interface field) beside its window facts, where it states no ranking"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1420."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        p[np++].fn_ref = (uint32_t)i + 1;'
SAB_AFTER='        p[np].rank_n = 1;   /* SABOTAGE S1420: a ranking stated */
        p[np++].fn_ref = (uint32_t)i + 1;'
