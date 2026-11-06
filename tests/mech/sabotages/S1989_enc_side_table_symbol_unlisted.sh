# S1989 ([VLOOKBEHIND] stage 1, review r4 F16) -- THE SEAM READER STOPS LISTING
# byte's UCP caseless row's SIDE TABLE (`span_ci_fold_pairs`, enc.c's
# `enc_row_side_table` arm of `pcrec_enc_entry_symbols`). The artifact still
# defines the table; DD12a(i) must no longer excise it on the byte side and so
# goes red. Before F16 the excision map was one across both backends and the
# utf8 rows' own `span_ci_fold_pairs` kept it excised: GREEN (review SEAM-2,
# plant PB).
SAB_ID="S1989-enc-side-table-symbol-unlisted"
SAB_FILE="src/enc/enc.c"
SAB_SUITES="encoding"
SAB_DESC='pcrec_enc_entry_symbols stops listing the byte UCP row'\''s side-table symbol, which the artifact still defines'
SAB_DOC_FIGURE='MEASURED (lane vlbfix, tools/review/plant.sh + run_encoding_checks.sh at the default 250-block slice; clean 14/0): 13 pass / 2 fail, DD12a(i) "4 of 241 strict-identity pairs differ OUTSIDE the named encoding-owned regions" (the byte table no longer excised) and the [K50] undeclared-form exception list mismatch. Before F16 (one symbol map across both backends): GREEN.'
SAB_COUNT=1
SAB_BEFORE='        if (enc_row_side_table(t)) each(enc_latin1_fold_table_sym, u);'
SAB_AFTER='        (void)enc_row_side_table;   /* SABOTAGE S1989: the side table unlisted */'
