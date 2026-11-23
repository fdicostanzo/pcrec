# S3411 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-L14 (span_arms §5.7, the re-entry's reaching witness): the move's K < 0 row is removed, so K < 0
# takes the K >= 0 text (`hit - pos > K` over unsigned operands). The block is then never entered, no
# move happens and the attempt runs at the raw position; W-L10/W-L13/W-L14 report a match before the
# start offset or (the design's prediction for the old re-entry text) loop; a hang is the gate's
# timeout, a finding.
# Detector: tests/litscan/spanarms.rxt (the L3 blocks, both routes).
SAB_ID="S3411-move-sign-rows-merged"
SAB_FILE="src/gen/emit_dfa.c"
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A): the pick rule keeps BASE's consumed run on a compile that
# may re-enter a forward scan, so the witness reaches the K < 0 site under `--engine=vm` (the detector's vm blocks).
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='the landmark move has one row for both signs of K, so at K < 0 the unsigned compare never moves and an attempt starts before the start offset'
SAB_DOC_FIGURE="MEASURED at landing (lane l3feat2, 2026-11-20): the K >= 0 text at a negative K compares a size_t difference with a negative literal, and the harness's generated-code compile refuses it (-Wsign-compare as an error), so the plant is caught at the artifact's build before any answer is read (1660 of 2130 cells red). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3411."
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?<=ab)ab(\w)\1'\'' && grep -q '\''^#define RX_REQ_HANDOFF "-2"$'\'' "$REACH_TMP/o.c" && echo REACH-WL14'
SAB_REACH_EXPECT='REACH-WL14'
SAB_EXPECT=COMPILE-CATCH
SAB_COUNT=1
SAB_BEFORE='    bool in_place = strcmp(target, hit) == 0;
    if (k < 0) {'
SAB_AFTER='    bool in_place = strcmp(target, hit) == 0;
    if (k < 0 && 0) {   /* SABOTAGE S3411 */'
