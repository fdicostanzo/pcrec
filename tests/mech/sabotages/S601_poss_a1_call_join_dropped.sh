# S601 — [ART-POSS-ARMS]: A1'S CONTINUATION CROSSES A CALLED GROUP'S END WITHOUT THE JOIN
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# A-F1 (§2.3a): a call re-runs the group under the call site's follow, so a
# continuation leaving the group must union the joined context. Because the
# continuation SUMMARY is also what R-5 checks against FOLLOW at every
# verdict, the build's own internal-error check fires on every call-bearing
# verdict: the detection is a compile refusal (`internal error: possessify:
# A1 continuation disagrees with FOLLOW`), which is that check doing its
# job. Witness `(a+(?:\b|))|b(?1)a` on "baa": 10.46 (0,3).
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S601-poss-a1-call-join-dropped"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='A1'\''s continuation crosses a called group'\''s end without unioning its call sites'\'' joined context (A-F1)'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S601."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(a+(?:\b|))|b(?1)a'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x0u$" "$REACH_TMP/o.c" && echo REACH-S601'
SAB_REACH_EXPECT="REACH-S601"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(a\+\(\?:\\b\|\)\)\|b\(\?1\)a$|1
tests/possessify/arms_reach.tsv|^\(a\+\(\?:\\b\|\)\)\|b\(\?1\)a[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (P->cc && c->capend < P->ncc) {'
SAB_AFTER='            if (0) {  /* SABOTAGE S601: the call-site join dropped */'
