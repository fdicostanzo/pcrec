#!/usr/bin/env bash
# S774 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2.1; docs/dev/lanes/revbuild_report.md) -- L2.1: RECOVER's absence reads `reverse-pass`, so a path that asks no RECOVER stamps a start recovery it does not run.
# Detector: run_dfa_stamps.sh [start]: `RX_DFA_START` against the text on every attempt/empty artifact.
SAB_ID='S774-start-absence-forked'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfastamps'
SAB_DESC='L2.1: RECOVER'\''s absence reads `reverse-pass`, so a path that asks no RECOVER stamps a start recovery it does not run'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S774.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "^ab" && grep -qF "#define RX_DFA_START \"attempt-start\"" "$REACH_TMP/o.c" && echo REACH-ABSENT'
SAB_REACH_EXPECT='REACH-ABSENT'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    [CAND_SLOT_RECOVER] = "attempt-start",'
SAB_AFTER='    [CAND_SLOT_RECOVER] = "reverse-pass",   /* SABOTAGE S774 */'
