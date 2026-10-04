#!/usr/bin/env bash
# S451 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE ALTERNATION'S COMMON HEAD
# COMPARES T AND KEEPS THE LEFT BRANCH'S MASK.
#
# Round 0's rule, which the r1 panel's S1 refuted: order-dependent and
# unsound. `(?:S(?i:ab)|(?i:sab))` claims an exact S at position 0, so the
# pre-check deletes `sab`. The cube hull K' = Ka & Kb & ~(Ta ^ Tb) is
# symmetric. Detector: the harness on reqcube.rxt's S1 head, branch order A
# (order B is unaffected by this plant, which is the order-dependence).
# (Design's provisional S450.)
SAB_ID="S451-req-hull-keeps-left"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the alternation's common head keeps the left branch's mask wherever the two branches' T agree, so an exact left branch beside a caseless right one claims an exact byte the right branch need not carry, and its matches are deleted"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S451."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:S(?i:ab)|(?i:sab))" && grep -q "^#define RX_REQ_RUN \"534142@2/dfdfdf\"" "$REACH_TMP/o.c" && echo REACH-HULL-HEAD'
SAB_REACH_EXPECT="REACH-HULL-HEAD"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        int k = rn_hull_mask(a.bytes[o.n], a.mask[o.n], b.bytes[o.n], b.mask[o.n]);'
SAB_AFTER='        int k = a.bytes[o.n] == b.bytes[o.n] ? a.mask[o.n] : 0;   /* SABOTAGE S451: round 0'\''s rule */'
