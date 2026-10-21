# S1234 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: a SYMMETRIC column swap: the reader resolves noise_e6 into the abs_ns_e6 slot (and back), and the canonical writer writes each slot back under the other's column, so the text round-trips byte for byte (design S983, renumbered).
# Detector: R5 on every loaded fixture: the decoded view prints abs_ns_e6 = the
# file's noise_e6 where ks_ref.py prints the file's abs_ns_e6, while R1-R3 stay
# green on them, which is the point of the row. (The store's committed
# pre-parse was generated without the plant, so its R4 and the embedded-store
# compare disagree too: hand-measured at the M0 head, 5 failures, 3 of them R5.)
SAB_ID="S1234-meas-symmetric-column-swap"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='a SYMMETRIC column swap: the reader resolves noise_e6 into the abs_ns_e6 slot (and back), and the canonical writer writes each slot back under the other'"'"'s column, so the text round-trips byte for byte (design S983, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1234.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if ((ix[j] = pcrec_ks_tsv_col(s, row_cols[j])) < 0)'
SAB_AFTER='        if ((ix[j] = pcrec_ks_tsv_col(s, j == KS_MR_abs_ns_e6 ? "noise_e6" : j == KS_MR_noise_e6 ? "abs_ns_e6" : row_cols[j])) < 0)   /* SABOTAGE S1234 */'
SAB_FILE2="src/core/ks_measures.c"
SAB_BEFORE2='        rc = put_row(o, set->rows[r].col, KS_MEAS_NROWCOL);'
SAB_AFTER2='        { const char *t[KS_MEAS_NROWCOL]; memcpy(t, set->rows[r].col, sizeof t); t[KS_MR_abs_ns_e6] = set->rows[r].col[KS_MR_noise_e6]; t[KS_MR_noise_e6] = set->rows[r].col[KS_MR_abs_ns_e6]; rc = put_row(o, t, KS_MEAS_NROWCOL); }   /* SABOTAGE S1234 */'
SAB_COUNT2=1
