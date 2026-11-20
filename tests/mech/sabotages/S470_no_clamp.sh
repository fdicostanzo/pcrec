#!/usr/bin/env bash
# S470 ([K82] (B), lane k82hbuild) -- THE UNDERFLOW-SAFE CLAMP IS REPLACED BY c - K.
#
# Witness: x{2,5}(?i:cat) on "xxxxxCaT" at startpos 3 on the attempt and
# hybrid routes: (3,8) becomes (0,8), below the startpos. Detector:
# handoff.rxt's startpos 1..K rows.
SAB_ID="S470-no-clamp"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='the handoff'\''s clamp is gone: c - K is taken whatever the distance from search_from, so a start below the caller'\''s startpos is scanned (and c < K wraps)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S470.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?m)^x{2,5}(?i:cat)'\'' && grep -q '\''if (handoff_position - search_from > 3) {'\'' "$REACH_TMP/o.c" && echo REACH-CLAMP-K3'
SAB_REACH_EXPECT='REACH-CLAMP-K3'
SAB_REACH_POP='tests/litscan/handoff.rxt|^ms 3 "xxxxxCaT" |1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(c, "%sif (%s - %s > %lld) {\n", ind, hit, pos, k);'
SAB_AFTER='    pcrec_sb_printf(c, in_place ? "%sif (1 || %s - %s > %lld) { /* SABOTAGE S470 */\n"
                                : "%sif (%s - %s > %lld) {\n", ind, hit, pos, k);'
# RE-AIMED REACH (lane sar1fix, 2026-11-09): since span arms R1 the run is
# `xxCAT` (the two required x copies join), so K is 3, not 5; the detector
# (handoff.rxt's `ms 3 "xxxxxCaT"`: the run's hit at 3 minus K is 0, below the
# startpos) is unchanged.
# RE-AIMED 2026-11-12 (lane rpfix2, [REQ-PAST-LAST]): the clamp's printf moved
# one level deeper (the bounded branch); same site, same fault.
# RE-AIMED 2026-11-20 (lane l3build, span_arms L3 RM-3, D-8): the move's arithmetic is ONE emitter,
# `emit_req_move_open`; the plant keys on its IN-PLACE branch (`in_place`, the entry's), so the
# clamp is dropped at the entry only and per-caller detection survives. Intent unchanged.
