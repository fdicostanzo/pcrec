#!/usr/bin/env bash
# S456 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE HULL STORES THE UPPER MEMBER.
#
# A run position is canonical: T is the LOWER member, every free bit clear
# (litscan_s4.md §2.3.1, r2 R2-S3), because the pair scan's second stream is
# T | ~K and the masked compare tests (s & K) == T. This plant stores the
# upper member in the alternation's common head. The walk's one position
# constructor (rn_put) refuses it as an internal error on the first hull it
# meets, so `frank|fred` stops compiling. Detector: the harness on
# reqcube.rxt's `frank|fred` block (a refused compile fails its cells); were
# the refusal removed too, reqcube_check.py's canonical-form sweep.
# (Design's provisional S455.)
SAB_ID="S456-cube-stores-upper"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the alternation's common head stores each hull position's upper member instead of the lower, a non-canonical position the walk's constructor refuses as an internal error"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S456."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "frank|fred" && grep -q "^#define RX_REQ_RUN \"667261@0/fffffb\"" "$REACH_TMP/o.c" && echo REACH-HULL-CANON'
SAB_REACH_EXPECT="REACH-HULL-CANON"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        rn_put(w, &o, a.bytes[o.n] & k, k);'
SAB_AFTER='        rn_put(w, &o, (a.bytes[o.n] | ~k) & 0xFF, k);   /* SABOTAGE S456: the upper member */'
