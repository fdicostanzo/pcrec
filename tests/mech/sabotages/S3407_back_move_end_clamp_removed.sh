# S3407 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-L16 (review r51 READYL3-4, a SAFETY witness): the K < 0 move's end clamp is removed. The kit
# verifies only a stretch of the run (`Content-` here, inside the 16-byte lookbehind), so on a subject
# that ends inside the lookbehind the hit plus 16 passes the subject's end and the attempt starts there.
# Detector: tests/litscan/spanarms.rxt (the L3 blocks, both routes).
SAB_ID="S3407-back-move-end-clamp-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='the K < 0 move loses its end clamp, so a hit whose run ends past the subject moves the start beyond the subject'\''s end'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3407."
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?<=Content-Length: )\d'\'' && grep -q '\''^#define RX_REQ_HANDOFF "-16"$'\'' "$REACH_TMP/o.c" && echo REACH-WL16'
SAB_REACH_EXPECT='REACH-WL16'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "%sif (%s - %s < %lld) " REQ_ON_MISS "\n", ind, len, hit, -k);'
SAB_AFTER='        (void)len;   /* SABOTAGE S3407: the end clamp removed */'
