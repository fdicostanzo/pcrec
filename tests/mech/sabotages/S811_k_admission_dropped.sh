#!/usr/bin/env bash
# S811 ([REQ-HANDOFF-L1], lane rlhbuild) -- THE K ADMISSION ALWAYS ADMITS:
# the re-entry replaces the start-byte scan however close the landmark's
# expected hits sit against K (or the displaced row's own skip), so `[a-y]\d{0,150}:` (K 151 against the
# colon's prior gap) re-enters. Answer-invisible (the scan only moves
# forward, so it stays linear and exact); the admission's witnesses in
# run_prechecks.sh §5.12m are the detector.
SAB_ID='S811-k-admission-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='prechecks'
SAB_DESC='the K admission of the re-entered handoff admits every K, so a landmark whose expected hit gap is shorter than K replaces the start-byte scan'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S811.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''[a-y]\d{0,150}:'\'' && grep -q '\''^#define RX_REQ_HANDOFF "151"'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_DFA_PREFILTER "byte-class"'\'' "$REACH_TMP/o.c" && echo REACH-ADMISSION-DECLINES'
SAB_REACH_EXPECT='REACH-ADMISSION-DECLINES'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if ((unsigned long long)k * h >= 1000000u) return false;
    return (1000000u - (unsigned long long)k * h) * m > 1000000u * h;'
SAB_AFTER='    return true;   /* SABOTAGE S811 */'
