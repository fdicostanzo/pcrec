#!/usr/bin/env bash
# S788 ([START-LANDING] SL2, lane slbuild; docs/design/start_landing.md §7.5 row 11; docs/dev/lanes/slbuild_report.md) -- K78's dead-group fill omitted at the one success-site emitter.
# Detector: run_nomatch_caps.sh (`(a){0}(b){0}c|d` end-minus-width, `(a){0}\w+` landing: a success must write every pair).
SAB_ID='S788-success-site-fill-omitted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='nomatchcaps'
SAB_DESC='emit_search_success writes caps[0] and returns 1 without the dead-group PCREC_UNSET fill, so a DFA dead-group artifact leaves caps[1..] stale on a success'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S788.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a){0}\\w+" && grep -q "^#define RX_DFA_START \"landing\"" "$REACH_TMP/o.c" && echo REACH-DEAD-GROUP-LANDING'
SAB_REACH_EXPECT='REACH-DEAD-GROUP-LANDING'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                    " capture_spans[0][1] = (ptrdiff_t)%s; }\n", ind, start, end);
    emit_dead_group_fill(cx, c, ind);'
SAB_AFTER='                    " capture_spans[0][1] = (ptrdiff_t)%s; }\n", ind, start, end);
    /* SABOTAGE S788: emit_dead_group_fill omitted */'
