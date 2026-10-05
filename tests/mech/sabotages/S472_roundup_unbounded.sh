#!/usr/bin/env bash
# S472 ([K82] (B), lane k82hbuild) -- THE ROUND-UP'S SUBJECT-END BOUND IS DROPPED.
#
# Its answer-level witness needs a subject with no character start in
# [c - K, n), which a window holding an ASCII byte never allows (litscan_k82h.md
# §4.3), so the in-suite detector is structural: run_prechecks.sh §5.12h
# requires the loop's condition to carry handoff_position >= subject_length.
SAB_ID="S472-roundup-unbounded"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC='the round-up loses its subject-end bound (the predicate'\''s >= n clause), so on a subject whose tail is all continuation bytes it reads past the end'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S472.'
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern '\''(?i)straße'\'' && grep -q '\''handoff_position >= subject_length ||'\'' "$REACH_TMP/o.c" && echo REACH-ROUNDUP-BOUND'
SAB_REACH_EXPECT='REACH-ROUNDUP-BOUND'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|emit "\$a" .\(\?i\)straße. -e utf8|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "%swhile (!(%s)) %s++;\n", indent, g, posvar);'
SAB_AFTER='        pcrec_sb_printf(c, "%swhile (!(%s)) %s++; /* SABOTAGE S472 */\n", indent, strstr(g, "|| ") ? strstr(g, "|| ") + 3 : g, posvar);'
