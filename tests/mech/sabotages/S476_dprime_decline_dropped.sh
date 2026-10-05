#!/usr/bin/env bash
# S476 ([K82] (B), lane k82hbuild) -- THE (d') DECLINE IS DROPPED.
#
# Its measured population is zero (no census hybrid mover carries \G), so the
# witness is constructed: (?:\Gab|x)(cat)\w{0,3}dog, a \G hybrid stamping
# RX_VM_PRUNE_CEILING "prefilter-window". Detector: run_prechecks.sh §5.12i.
SAB_ID="S476-dprime-decline-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC='the handoff'\''s (d'\'') decline is dropped, so a VM hybrid whose program has a \G start family and whose prefilter window is its match ceiling hands off: the prefilter'\''s \G reads the moved start and window_end is set from that answer'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S476.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:\Gab|x)(cat)\w{0,3}dog'\'' && grep -q '\''^#define RX_VM_PRUNE_CEILING "prefilter-window"'\'' "$REACH_TMP/o.c" && echo REACH-DPRIME'
SAB_REACH_EXPECT='REACH-DPRIME'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|\(\?:\\Gab\|x\)\(cat\)\\w\{0,3\}dog|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cx->job->fit.chosen == ENGM_VM && dfa_has_gstart_family(&cx->job->dfa) &&
        pcrec_vm_prefilter_window(cx))
        return false;'
SAB_AFTER='    /* SABOTAGE S476: the (d'\'') decline is dropped */'
