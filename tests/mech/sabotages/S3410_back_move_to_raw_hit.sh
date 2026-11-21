# S3410 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-L10 / W-L13 (span_arms §5.7, the BACK move): at K < 0 the move lands at the hit, not the hit plus
# B (rev 1's move): `(?<=ab)ab[a-z]*q` on "abababq" from 3 answers (2,7), a match before the start
# offset, where the oracle answers (4,7).
# Detector: tests/litscan/spanarms.rxt (the L3 blocks, both routes).
SAB_ID="S3410-back-move-to-raw-hit"
SAB_FILE="src/gen/emit_dfa.c"
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A): the pick rule keeps BASE's consumed run on a compile that
# may re-enter a forward scan, so the witness reaches the K < 0 site under `--engine=vm` (the detector's vm blocks).
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='the K < 0 move lands at the hit itself rather than B bytes after it, so an attempt starts before the start offset'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3410."
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?<=ab)ab[a-z]*q(\w*)\1'\'' && grep -q '\''^#define RX_REQ_HANDOFF "-2"$'\'' "$REACH_TMP/o.c" && echo REACH-WL13'
SAB_REACH_EXPECT='REACH-WL13'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            pcrec_sb_printf(c, "%s    %s += %lld;\n", ind, target, -k);
        else
            pcrec_sb_printf(c, "%s    %s = %s + %lld;\n", ind, target, hit, -k);'
SAB_AFTER='            pcrec_sb_printf(c, "%s    %s += %lld;\n", ind, target, 0LL);   /* SABOTAGE S3410 */
        else
            pcrec_sb_printf(c, "%s    %s = %s + %lld;\n", ind, target, hit, 0LL);'
