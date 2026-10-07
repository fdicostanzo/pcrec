# S562 — [ART-POSS-ARMS]: ARM A1 COLLAPSES A MIXED LAST TO ONE POLARITY
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# P_C is the SET of the LAST classes' polarities; a mixed set admits both
# memberships and must narrow nothing (§2.4). Witness `(?:a[a.])+\b` on
# "a.a.": 10.46 (0,2), the plant NOMATCH.
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S562-poss-a1-mixed-last-collapsed"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm A1 reads a mixed LAST polarity set as all-in-C'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S562."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''\w+\b'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x2u$" "$REACH_TMP/o.c" && echo REACH-S562'
SAB_REACH_EXPECT="REACH-S562"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(\?:a\[a\.\]\)\+\\b$|1
tests/possessify/arms_reach.tsv|^\(\?:a\[a\.\]\)\+\\b[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (cls_has(g->last, (unsigned)i)) pm |= cls_polarity(g->cls[i], C, n);
    return pm;'
SAB_AFTER='        if (cls_has(g->last, (unsigned)i)) pm |= cls_polarity(g->cls[i], C, n);
    return pm == 3u ? 2u : pm;  /* SABOTAGE S562: mixed LAST collapsed */'
