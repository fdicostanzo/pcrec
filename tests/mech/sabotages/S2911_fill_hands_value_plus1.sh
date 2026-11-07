# S2911 — span_pick stage 2 unit S2a review fix (lane s2afix; docs/dev/reviews/2026-11-06-r8-memfn-s2a.md SEAM-1;
# docs/design/memfn/span_cards.md §4.2).
#
# Plant: the fill hands value_e6 + 1 for every row (the handed VALUE is wrong, noise and state right).
# Detector: tests/compound/run_part_measures.sh (C): the MFMEAS digest covers the handed value, so it differs from ks_ref.py handed.
SAB_ID="S2911-fill-hands-value-plus1"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="compound"
SAB_DESC='the fill hands value_e6 + 1: a wrong handed value that the noise-only record did not see'
SAB_DOC_FIGURE='MEASURED by lane s2afix planted and reverted (docs/dev/lanes/s2afix_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2911.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        rows[ms->nrows++] = (mf_measure){ r->col[KS_MR_key], r->value_e6,'
SAB_AFTER='        rows[ms->nrows++] = (mf_measure){ r->col[KS_MR_key], r->value_e6 + 1,   /* SABOTAGE S2911 */'
