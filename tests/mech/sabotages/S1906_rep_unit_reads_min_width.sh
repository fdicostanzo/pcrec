#!/usr/bin/env bash
# S1906 (lane sae1, 2026-11-09; span_arms E1, witness W-R4,
# docs/design/span_arms.md §3.6) -- T2 ROW 1 READS THE MINIMUM WIDTH.
#
# Row 1 of the necessary-run walk's repeat table (src/facts/req.c
# `rb_rep_rows`) is "the body's MAXIMUM width is 0". This plant reads the
# minimum width, so the nullable body of `ab(?:c?){2}de` counts as width 0, the
# repeat becomes the unit and the run `abde` is claimed: the pre-check deletes
# every match that takes a `c`. Detector: the harness on
# tests/litscan/spanarms.rxt (both engines).
SAB_ID="S1906-rep-unit-reads-min-width"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC="the necessary-run walk's width-0 repeat row reads the body's minimum width instead of its maximum, so a nullable body that can consume becomes the unit, a run is claimed across it and the pre-check deletes the matches that consume there"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1906."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "ab(?:c?){2}de" && grep -qE "^#define RX_REQ_RUN \"(6465|6162)(@[0-9])?\"$" "$REACH_TMP/o.c" && echo REACH-WR4-RUN-SPLIT'
SAB_REACH_EXPECT="REACH-WR4-RUN-SPLIT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return b->runs.maxw == 0;'
SAB_AFTER='    return pcrec_minw(a->l) == 0;   /* SABOTAGE S1906 */'
# RE-AIMED REACH (lane k382cm, 2026-11-12, R-38 K38-2): `<PREFIX>_REQ_RUN` now carries `@idx` only where
# this artifact's search reads a run position (match_api.md §6.3.7¶7 rows 1-2); this witness is row 3
# (`RX_REQ_WHY "dominated"`, no run part rendered) and emits the hex alone, so the old reach, which
# required an `@`, read UNREACHED (found by lane k382cm's clean-tree reach probe; its cloud shard 12 of run 43239936557 died before running it). The `@` is now optional; the run it asserts, the site and
# the intent are unchanged.
