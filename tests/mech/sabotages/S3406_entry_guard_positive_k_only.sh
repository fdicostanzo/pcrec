# S3406 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-L15 (review r51 READYL3-1): the entry move's guard is restored to `k > 0 || round.len > 0`, so no
# move is emitted at K < 0 under `byte` and the VM attempt loop starts at the raw hit: `(?<=a)a(\w)\1` on
# "-aaaaaq-b" from 3 answers (2,5) where the oracle answers (3,6).
# Detector: tests/litscan/spanarms.rxt (the L3 blocks, both routes).
SAB_ID="S3406-entry-guard-positive-k-only"
SAB_FILE="src/gen/emit_dfa.c"
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A): the pick rule keeps BASE's consumed run on a compile that
# may re-enter a forward scan, so the witness reaches the K < 0 site under `--engine=vm` (the detector's vm blocks).
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='the entry'\''s move block is emitted only at K > 0 (or a round-up), so at K < 0 the first attempt is at the raw hit, before the start offset'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3406."
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?<=a)a(\w)\1'\'' && grep -q '\''^#define RX_REQ_HANDOFF "-1"$'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_VM_PREFILTER "none"$'\'' "$REACH_TMP/o.c" && echo REACH-WL15'
SAB_REACH_EXPECT='REACH-WL15'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (k != 0 || round.len > 0) {'
SAB_AFTER='        if (k > 0 || round.len > 0) {   /* SABOTAGE S3406 */'
