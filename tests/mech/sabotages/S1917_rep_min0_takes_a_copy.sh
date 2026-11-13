#!/usr/bin/env bash
# S1917 (lane sar1, 2026-11-09; span_arms R1, witness W-R3, docs/design/span_arms.md §3.6) -- A MIN-0 REPEAT UNROLLS ONE COPY.
#
# T2 row 3 at `m = 0` (src/facts/req.c `rr_rep_split`) unrolls no copy: the
# repeat is today's gap. This plant takes the count from max(m, 1), the
# shape the old C-comment note warns of, so `ab(?:cd){0,2}ef` claims `abcd`
# or `cdef` and the pre-check deletes `abef`. Detector: the harness on
# tests/litscan/spanarms.rxt (both engines).
SAB_ID="S1917-rep-min0-takes-a-copy"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_DESC="the necessary-run walk unrolls one copy of a repeat that may match zero times, so the run claims a copy that the empty iteration lacks and the pre-check deletes those matches"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1917."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "ab(?:cd){0,2}ef" && grep -qE "^#define RX_REQ_RUN \"6162(@[0-9]+)?\"$" "$REACH_TMP/o.c" && echo REACH-WR3-RUN'
SAB_REACH_EXPECT="REACH-WR3-RUN"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    RbRuns p = rr_pow(w, b, rr_pow_count(&b, m));'
SAB_AFTER='    RbRuns p = rr_pow(w, b, rr_pow_count(&b, m > 1 ? m : 1));   /* SABOTAGE S1917 */'
# RE-AIMED REACH (lane sar1fix, 2026-11-09, review r5): the two 2-byte runs
# `ab` and `ef` tie on information and the run choice takes the rarer scan
# byte (`b`, 9886 ppm, over `f`, 14787), so the clean run is `ab`.
# RE-ANCHORED (lane sar1fix, 2026-11-09, review r5): the run walk's helpers take the
# walk `w` (the run choice reads its byte-rate); same site, same plant.
# RE-AIMED REACH (lane k382cm, 2026-11-12, R-38 K38-2): `<PREFIX>_REQ_RUN` now carries `@idx` only where
# this artifact's search reads a run position (match_api.md §6.3.7¶7 rows 1-2); this witness is row 3
# (`RX_REQ_WHY "dominated"`, no run part rendered) and emits the hex alone, so the old reach, which
# required an `@`, read UNREACHED (cloud run 43239936557 shard 17). The `@` is now optional; the run it asserts, the site and
# the intent are unchanged.
