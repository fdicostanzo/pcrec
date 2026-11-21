# S3409 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-T3a (span_arms §5.7): BACK's `lg ++ head` keeps the LAST 32 positions (`rn_pre`) instead of the
# first, so `(?<=a^20)b^8 z b^11` states `a^12 b^8 z b^11` at -20 (truly -12) and the body starts 8
# bytes late: NOMATCH where the oracle answers (20,40).
# Detector: tests/litscan/spanarms.rxt (the L3 blocks, both routes).
SAB_ID="S3409-back-join-keeps-last"
SAB_FILE="src/facts/req.c"
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A): the pick rule keeps BASE's consumed run on a compile that
# may re-enter a forward scan, so the witness reaches the K < 0 site under `--engine=vm` (the detector's vm blocks).
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='TOP'\''s BACK candidate keeps the last positions of lg ++ head, so a truncated run is stated at the wrong K and the move passes the match'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3409."
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?<=aaaaaaaaaaaaaaaaaaaa)bbbbbbbbzbbbbbbbbbbb'\'' && grep -q '\''^#define RX_REQ_HANDOFF "-20"$'\'' "$REACH_TMP/o.c" && echo REACH-WT3A'
SAB_REACH_EXPECT='REACH-WT3A'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    RbRun r = rn_app(root->lg, root->head);'
SAB_AFTER='    RbRun r = rn_pre(root->lg, root->head);   /* SABOTAGE S3409 */'
