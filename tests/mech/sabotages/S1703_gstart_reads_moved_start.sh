#!/usr/bin/env bash
# S1703 ([REQRUN-VM], lane reqvm1) -- `\G` READS THE MOVED START. The VM
# attempt loop's handoff moves `attempt_position` only; `\G` keeps asserting
# at `search_from` (the caller's startpos). The plant moves `search_from` with
# it, so `\G` asserts at the handoff's position: `(?:\Gab|x)(cat)dog` from 0
# on `zzabcatdog` reports (2,10) where the answer is no match. Detector:
# tests/litscan/handoff_vm.rxt.
SAB_ID='S1703-gstart-reads-moved-start'
SAB_FILE='src/gen/emit_vm.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/litscan/handoff_vm.rxt'
SAB_DESC='the VM attempt loop'\''s handoff also moves search_from, so \G asserts at the handoff position instead of the caller'\''s startpos'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1703.'
# RE-AIMED 2026-11-13 (lane s2tri, [RUN-POS-SET] flip 2 -> 128): the alternation union {b, x}
# became the run's lead position (RX_REQ_RUN "[6278]636174646f67@6", was "636174646f67@5"),
# so K moved 2 -> 1 and the probe's pinned "2" read UNREACHED. Same witness as the detector
# (handoff_vm.rxt's row); the handoff (the run's 'b' at 3, minus K 1) is still 2, where the
# plant's moved search_from lets \Gab match, so the probe pins K 1.
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?:\Gab|x)(cat)dog'\'' && grep -q '\''^#define RX_REQ_HANDOFF "1"'\'' "$REACH_TMP/o.c" && grep -q '\''attempt_position = handoff_position;'\'' "$REACH_TMP/o.c" && echo REACH-G-ATTEMPT-HANDOFF'
SAB_REACH_EXPECT='REACH-G-ATTEMPT-HANDOFF'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "    attempt_position = %s;\n", first);'
SAB_AFTER='        pcrec_sb_printf(c, "    attempt_position = %s;\n    search_from = attempt_position;   /* SABOTAGE S1703 */\n", first);'
