#!/usr/bin/env bash
# S767 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- `nl_last` answers "no tie" for every machine, so a tie-capable walk emits no tie arm.
# Detector: the answer net's tie families (the seed that reached first wins the end) and run_rev_end.sh's tie-arm witnesses.
SAB_ID='S767-nl-last-overclaims'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness revend'
SAB_DESC='`nl_last` answers "no tie" for every machine, so a tie-capable walk emits no tie arm'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S767.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\s+$" && grep -q "for (int revend_seed = 0;" "$REACH_TMP/o.c" && echo REACH-WALK'
SAB_REACH_EXPECT='REACH-WALK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (d->s0 < 0 || d->s0 >= d->n) return false;
    stack[n++] = d->s0;'
SAB_AFTER='    return false;   /* SABOTAGE S767: nl_last always false */
    stack[n++] = d->s0;'
