# S561 — [ART-POSS-ARMS]: ARM A1 READS POLARITY FROM X'S FIRST, NOT ITS LAST
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# The character left of a retreat exit is the LAST character of an
# iteration (§2.3). Witness `(?:a\.)+\b` on "a.a.": 10.46 (0,2), the plant
# NOMATCH.
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S561-poss-a1-polarity-from-first"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm A1 reads the left polarity from the body'\''s FIRST positions instead of its LAST'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S561."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:a\.)+\B'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x2u$" "$REACH_TMP/o.c" && echo REACH-S561'
SAB_REACH_EXPECT="REACH-S561"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(\?:a\\\.\)\+\\b$|1
tests/possessify/arms_reach.tsv|^\(\?:a\\\.\)\+\\b[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    memcpy(g->last, p.last, 32);'
SAB_AFTER='    memcpy(g->last, p.first, 32);  /* SABOTAGE S561: FIRST read as LAST */'
