# S2906 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (g);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (g) the canonical writer writes a format-2 '-' noise as 0.
# Detector: fx-f2 holds '-' noise rows: its canonical view no longer re-loads to its digest (INT64_MIN vs 0; a derived or null row's 0 refuses outright), so R1/R2/R3 go red on fx-f2.
SAB_ID="S2906-meas-canonical-noise-dash-as-0"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='(g) the canonical writer writes a format-2 '"'"'-'"'"' noise as 0'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2906.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        rc = put_row(o, set->rows[r].col, KS_MEAS_NROWCOL);'
SAB_AFTER='        { const char *t[KS_MEAS_NROWCOL]; memcpy(t, set->rows[r].col, sizeof t); if (set->format == 2 && set->rows[r].noise_e6 == KS_MEAS_EMPTY) t[KS_MR_noise_e6] = "0"; rc = put_row(o, t, KS_MEAS_NROWCOL); }   /* SABOTAGE S2906 */'
