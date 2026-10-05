#!/usr/bin/env bash
# S460 ([K82], lane k82fix) -- THE LEAD IS EMITTED AFTER THE RUN SEARCH.
#
# The point of the row is ORDER: a window lacking the rare byte must cost one
# memchr and never the run search. This plant emits the one-byte check after
# the run call, so userpass's run search (a pass on every call, K82 cause A)
# runs first again and '=' only rejects after it. Answer-invisible. Detector:
# run_prechecks.sh §5.11, whose lead is the first `!memchr(...)` ABOVE the
# first `rx_reqrun(` call (reads "-").
SAB_ID="S460-lead-after-run"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="the set-leads row's one-byte check is emitted after the run search instead of before it, so the run search's cost is paid on every call the rare byte would have rejected"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S460."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:user|USER)[ \\t]*=" && grep -q "^#define RX_REQ_RUN \"55534552@0/dfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "!memchr(subject + search_from, 61," "$REACH_TMP/o.c" && echo REACH-SET-LEADS'
SAB_REACH_EXPECT="REACH-SET-LEADS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (req_lead_byte(cx) >= 0)
            emit_req_one_byte(c, indent, posvar, subjvar, lenvar,
                              req_lead_byte(cx));
        emit_req_run_check(cx, c, indent, posvar, subjvar, lenvar);'
SAB_AFTER='        emit_req_run_check(cx, c, indent, posvar, subjvar, lenvar);   /* SABOTAGE S460: lead after */
        if (req_lead_byte(cx) >= 0)
            emit_req_one_byte(c, indent, posvar, subjvar, lenvar,
                              req_lead_byte(cx));'
