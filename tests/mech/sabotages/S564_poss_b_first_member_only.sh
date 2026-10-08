# S564 — [ART-POSS-ARMS]: ARM B READS ONLY THE FIRST MEMBER OF refs[]
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# A duplicated name resolves at match time to the first SET member, so
# FIRST(\n) is the union over ALL members (§3.2). Witness
# `(?J)(?:(?<n>a)|(?<n>x))x+\k<n>` on "xxx": 10.46 (0,3), the plant NOMATCH.
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S564-poss-b-first-member-only"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm B unions only the first group a reference can name'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S564."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(a)x+\1'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x4u$" "$REACH_TMP/o.c" && echo REACH-S564'
SAB_REACH_EXPECT="REACH-S564"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(\?J\)\(\?:\(\?<n>a\)\|\(\?<n>x\)\)x\+\\k<n>$|1
tests/possessify/arms_reach.tsv|^\(\?J\)\(\?:\(\?<n>a\)\|\(\?<n>x\)\)x\+\\k<n>[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int i = 0; i < a->u.bref.nrefs; i++) {'
SAB_AFTER='    for (int i = 0; i < 1; i++) {  /* SABOTAGE S564: refs[0] only */'
