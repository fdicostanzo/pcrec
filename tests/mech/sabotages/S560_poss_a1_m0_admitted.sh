# S560 — [ART-POSS-ARMS]: ARM A1 ADMITS m = 0
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# A1's premise needs a known LEFT character at every retreat exit; with
# m = 0 the e_0 exit's left character is whatever precedes Q (poss_arms.md
# §2.4). Witness ` \w?\b` on " aa": 10.46 (0,1), the plant NOMATCH.
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S560-poss-a1-m0-admitted"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm A1 values a gate for a loop with m = 0, whose e_0 exit has an unknown left character'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S560."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\'' \w+\b'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x2u$" "$REACH_TMP/o.c" && echo REACH-S560'
SAB_REACH_EXPECT="REACH-S560"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern  \\w\?\\b$|1
tests/possessify/arms_reach.tsv|^ \\w\?\\b[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (P->fq.arm_a && base_ok && !lazy && a->u.rep.rmin >= 1 &&'
SAB_AFTER='    if (P->fq.arm_a && base_ok && !lazy &&  /* SABOTAGE S560: m >= 1 dropped */'
