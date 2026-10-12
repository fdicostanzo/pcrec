#!/usr/bin/env bash
# S767 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- `nl_last` answers "no tie" for every machine, so a tie-capable walk emits no tie arm.
# Detector: the answer net's tie families (the seed that reached first wins the end) and run_rev_end.sh's tie-arm witnesses.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# `nl_last` is now F1's predicate, so the plant sends every artifact to F1:
# the tie families' nl cells answer the n-1 end (`\s+$` on "a \n"). Reach: `\s+$`
# takes form tagged (the row the plant removes).
SAB_ID='S767-nl-last-overclaims'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness revend'
SAB_DESC='`nl_last` answers "no tie" for every machine, so a tie-capable walk emits no tie arm'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S767.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\s+$" | grep -F "form=tagged" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (d->s0 < 0 || d->s0 >= d->n) return false;
    stack[n++] = d->s0;'
SAB_AFTER='    return false;   /* SABOTAGE S767: nl_last always false */
    stack[n++] = d->s0;'
