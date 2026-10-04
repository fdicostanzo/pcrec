#!/usr/bin/env bash
# S457 ([K82], lane k82fix) -- THE `set-leads` ROW NEVER APPLIES.
#
# The admission table's (A) row is what puts a rarer necessary-set byte's
# memchr in front of the run search (tuning.md §2.40). This plant makes its
# predicate false, so every artifact falls through to `emitted` and is the
# abi-59 program: userpass's '=' guard is gone again and K82's ~57x returns.
# No answer moves (the lead is a necessary byte; on the no-DFA-scan route
# K65's rest memchrs it anyway), so the detector is STRUCTURAL:
# run_prechecks.sh §5.11 (lead 61 / 99 / 61 read "-") and §5.8/§5.9 (the
# rest regains the byte the lead tested).
SAB_ID="S457-set-leads-never-applies"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="the pre-check admission's set-leads row never applies, so a necessary-set byte rarer than the run's scan member is no longer tested before the run search (the abi-59 program, K82 cause A)"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S457."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:user|USER)[ \\t]*=" && grep -q "^#define RX_REQ_RUN \"55534552@0/dfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "!memchr(subject + search_from, 61," "$REACH_TMP/o.c" && echo REACH-SET-LEADS'
SAB_REACH_EXPECT="REACH-SET-LEADS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if ((q = req_set_pick(s->cx)) < 0) return false;'
SAB_AFTER='    if ((q = req_set_pick(s->cx)) < 0 || 1) return false;   /* SABOTAGE S457 */'
