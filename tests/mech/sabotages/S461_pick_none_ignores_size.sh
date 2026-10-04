#!/usr/bin/env bash
# S461 ([K82], lane k82fix) -- PICK'S NONE ANSWER IGNORES THE CANDIDATES' SIZES.
#
# [K82] (C): under NONE the PICK primitive prices a candidate by MASS's own
# NONE answer, its member count, so a run scans an exact position before a
# two-member pair. This plant prices every cube as one member, which is the
# abi-59 answer ("rightmost, whatever the candidates' sizes"): alt-shared
# (`日本|日曜|日付`, -e utf8) scans the UTF-8 lead-byte pair {E4, E6} again.
# Answer-invisible (every run position is necessary). Detector:
# run_prechecks.sh §5.11's (C) rows (REQ_RUN @3 / @5 where @2 / @0).
SAB_ID="S461-pick-none-ignores-size"
SAB_FILE="src/core/findings.c"
SAB_SUITES="prechecks"
SAB_DESC="the PICK primitive's NONE answer prices every cube as one member, so a NONE run scans its rightmost position even where it is a two-member pair beside an exact byte (the abi-59 answer, K82 cause C)"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S461."
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "日本|日曜|日付" && grep -q "^#define RX_REQ_RUN \"e697a5e4@2/fffffffd\"" "$REACH_TMP/o.c" && echo REACH-PICK-NONE-MASS'
SAB_REACH_EXPECT="REACH-PICK-NONE-MASS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!rate) return uniform_mass(1 << __builtin_popcount((unsigned)f));'
SAB_AFTER='    if (!rate) return uniform_mass(1);   /* SABOTAGE S461 */'
