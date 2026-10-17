# S1049 — [KNOW-SRC] K1 (docs/design/measure_sets.md rev 3 §9.5, [r2 M2]):
# THE ANALYSIS ROW'S `s2_mismatch` READS `refuse` (src/parse/ks_analysis.c).
# An `-I` file that defines no bundle of the requested name (a `lib`
# library beside the bundles is the common case) must FALL THROUGH with a
# note, the analysis kind's shipped and spec'd behaviour
# (docs/spec/findings.md's S2 row); `refuse` is the measures kind's value.
# The column is what made K1 zero-mover, so it gets its own row: S985 is the
# measures-side mirror (M0).
#
# Detector: run_findings_tests.sh §6 #7 (A/lib.rxt has no bundle, B/lib.rxt
# answers; the compile must stamp B's and print the note).
SAB_ID="S1049-ksrc-analysis-s2-mismatch-refuses"
SAB_FILE="src/parse/ks_analysis.c"
SAB_SUITES="findings"
SAB_DESC="the analysis kind's row sets s2_mismatch = refuse: an -I file naming no such bundle refuses the compile instead of falling through to the next stop with a note"
SAB_DOC_FIGURE="findings red on §6 [#7] (the fall-through compile refuses). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1049."
SAB_REACH='python3 "$TREE/tests/findings/res_fixtures.py" "$REACH_TMP/r" && "$PCREC" -p rx -I "$REACH_TMP/r/A" -I "$REACH_TMP/r/B" --analysis lib -o "$REACH_TMP/a.c" --pattern "abc" 2>"$REACH_TMP/e" && grep -q "continuing the search" "$REACH_TMP/e" && echo REACH-KSRC-S2-FALLTHROUGH'
SAB_REACH_EXPECT="REACH-KSRC-S2-FALLTHROUGH"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    .s2_mismatch   = KS_S2_FALLTHROUGH_NOTE,'
SAB_AFTER='    .s2_mismatch   = KS_S2_REFUSE,   /* SABOTAGE S1049 */'
