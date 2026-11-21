# S3412 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-L1 (span_arms §5.7, the kit's witness): the run span states `omin` 0, so the kit's pre-check scans
# from the start offset, not max(0, startpos + K): `(?<=foo)bar` on "foobar" from 2 or 3 misses the run
# at 0 and answers NOMATCH where the oracle answers (3,6).
# Detector: tests/litscan/spanarms.rxt (the L3 blocks, both routes).
# RE-ANCHORED 2026-11-20 (lane l3r65, review r65 H): the run's omin has one writer, in the entry loop.
SAB_ID="S3412-run-span-omin-zero"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='the run'\''s presence span states omin 0 for a run that begins inside a lookbehind, so the pre-check scans from the start offset and misses it'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3412."
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?<=foo)bar'\'' && grep -q '\''^#define RX_REQ_HANDOFF "-3"$'\'' "$REACH_TMP/o.c" && echo REACH-WL1'
SAB_REACH_EXPECT='REACH-WL1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        p[i].omin = run->whole_len >= 2 && i == np - 1 ? (int32_t)pcrec_run_omin(run) : 0;'
SAB_AFTER='        p[i].omin = 0;   /* SABOTAGE S3412: the run'\''s omin stays 0 */'
