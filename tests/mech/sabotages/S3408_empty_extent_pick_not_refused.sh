# S3408 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-L17..W-L19 (review r51 READYL3-6): the scan-index accessor no longer refuses an EMPTY stretch, so the
# `req_byte` pick over the empty consumed extent of `(?<=foobar)\d*x`, `(?<=foo)` or `(?<=a{32})b`
# asks the primitive over zero positions (an uninitialised candidate read, undefined behaviour).
# Detector: tests/codegen/run_facts_checks.sh [facts-look] W-L17/W-L18/W-L19 cells (req_byte 120 / none /
# 98): asked over zero positions the primitive reads its uninitialised candidate 0 and answers the index
# just BEFORE the stretch, a lookbehind byte. spanarms.rxt answers stay green (MEASURED, 0 of 2130).
SAB_ID="S3408-empty-extent-pick-not-refused"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='pcrec_run_scan_index asks the pick over an empty stretch, so the req_byte pick of an empty consumed extent names a lookbehind byte no match consumes'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3408."
SAB_REACH='"$PCREC" --features all --engine=vm --emit-facts --pattern '\''(?<=foobar)\d*x'\'' | grep -qP '\''^byte\treq_byte\t([^\t]*\t){4}120\t'\'' && echo REACH-WL17-EMPTY'
SAB_REACH_EXPECT='REACH-WL17-EMPTY'
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A): on the default route `(?<=foobar)\d*x` keeps no BACK run
# (its consumed extent is empty, the pick rule); the reach and the detector cells read `--engine=vm`.
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (lo >= hi) return -1;'
SAB_AFTER='    /* SABOTAGE S3408: an empty stretch is not refused */'
