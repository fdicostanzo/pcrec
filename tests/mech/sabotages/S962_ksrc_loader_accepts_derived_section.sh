# S962 — [KNOW-SRC] K3 (docs/design/measure_sets.md rev 3 §8.5, §9.6): THE
# LOADER ACCEPTS A DERIVED VIEW FED BACK AS AN INPUT. A file carrying one of
# the kind's derived section names (`--list-analysis`'s `chain`, `resolution`,
# `declarations`, `targets`; the decoded view's `decoded`, `item`) is a
# listing, never an input, and the resolver refuses it naming the section and
# pointing at `--view=canonical` (src/core/ksrc.c, `ks_probe_dir`). With the
# refusal planted out, the file reaches the `.rxt` reader, which refuses it
# for an unrelated reason (a TSV row is not a directive) — so the plant moves
# the diagnostic's CLASS, and the detector holds the class, not just a
# refusal.
#
# Detector: run_knowledge_tests.sh's derived-section checks (the shipped
# NAME listing and the decoded view, each fed back through -I).
SAB_ID="S962-ksrc-loader-accepts-derived-section"
SAB_FILE="src/core/ksrc.c"
SAB_SUITES="knowledge"
SAB_DESC="the resolver's derived-section refusal is planted out: an -I file carrying '#section chain' or '#section decoded' reaches the .rxt reader instead of being refused as a listing fed back"
SAB_DOC_FIGURE="MEASURED 2026-10-17 at 66c51d710: knowledge:2fail/210pass, the two derived-section checks (refused, but not by the derived-section rule). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S962."
SAB_REACH='d="$REACH_TMP/d"; mkdir -p "$d" && "$PCREC" --list-analysis log > "$d/log.rxt" && ! "$PCREC" -I "$d" --list-analysis log 2>"$REACH_TMP/e" >/dev/null && grep -q "carries .#section chain." "$REACH_TMP/e" && echo REACH-KSRC-DERIVED-REFUSED'
SAB_REACH_EXPECT="REACH-KSRC-DERIVED-REFUSED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (sec) {'
SAB_AFTER='        if (sec && 0) {   /* SABOTAGE S962 */'
