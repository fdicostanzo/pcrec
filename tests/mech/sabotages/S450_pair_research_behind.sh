#!/usr/bin/env bash
# S450 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE PAIR ARM RE-SEARCHES A
# STREAM ONLY WHEN ITS HIT FALLS BEHIND `pos`.
#
# After a failed verify `pos = cand + 1`, and the hit that produced `cand`
# sits at `cand + k*`, so a re-search bound of `< pos` keeps it: the next
# candidate is the same `cand` and the block never advances -- a HANG on any
# subject whose first scan hit fails its verify. The bound is `< pos + k*`.
# Detector: the harness on reqcube.rxt's re-search block, whose per-case
# timeout is the hang's own detector, and reqcube_check.py's re-search text
# check. (Design's provisional S449.)
SAB_ID="S450-pair-research-behind"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness codegen"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the pair arm's re-search bound is '< pos' instead of '< pos + k*', so after a failed verify the stream keeps the hit that produced the candidate and the block loops on it forever"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S450."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?i)select" && grep -q "^#define RX_REQ_RUN \"53454c454354@4/dfdfdfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "ha < pos + 4" "$REACH_TMP/o.c" && echo REACH-PAIR-ARM'
SAB_REACH_EXPECT="REACH-PAIR-ARM"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    const char *lim = at;   /* the re-search bound: a hit below pos + k* is stale */'
SAB_AFTER='    const char *lim = "pos";   /* SABOTAGE S450: the re-search bound falls behind the hit */'
