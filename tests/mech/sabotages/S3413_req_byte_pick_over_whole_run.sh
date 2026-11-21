# S3413 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-S4c (span_arms §5.7, A13 at BACK): the `req_byte` pick reads the WHOLE run, lookbehind bytes
# included, so `(?<=qz)ab` names `q` or `z`, outside req_set {97,98}: reqcube_check.py check 4.
# Detector: tests/codegen/reqcube_check.py (WIT row ws4c) via run_codegen_tests.sh.
SAB_ID="S3413-req-byte-pick-over-whole-run"
SAB_FILE="src/facts/req.c"
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A): the pick rule keeps BASE's consumed run on a compile that
# may re-enter a forward scan, so the witness reaches the K < 0 site under `--engine=vm` (the detector's vm blocks).
SAB_SUITES="codegen"
SAB_DESC='the req_byte pick reads every run position, so a run that begins inside a lookbehind names a byte no match consumes'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3413."
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?<=qz)ab'\'' && grep -q '\''^#define RX_REQ_BYTE "98"$'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_REQ_HANDOFF "-2"$'\'' "$REACH_TMP/o.c" && echo REACH-WS4C'
SAB_REACH_EXPECT='REACH-WS4C'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        i = pcrec_run_scan_index(rate, run, lo, hi);    /* -1: an empty extent */'
SAB_AFTER='        i = pcrec_run_scan_index(rate, run, 0, run->whole_len);    /* SABOTAGE S3413 */'
