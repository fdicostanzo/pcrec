# S2902 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (c);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (c) the fill reads the noise TEXT column whatever the format, so a format-1 row with numeric noise text is handed as MEASURED.
# Detector: tests/compound/run_part_measures.sh (C): fx-f1noise carries numeric noise text on every row, so the MFMEAS MEASURED count is 3, not 0, and the noise digest differs from ks_ref.py handed.
SAB_ID="S2902-fill-hands-f1-noise"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="compound"
SAB_DESC='(c) the fill reads the noise TEXT column whatever the format, so a format-1 row with numeric noise text is handed as MEASURED'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2902.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        bool measured = r->noise_e6 != KS_MEAS_EMPTY;'
SAB_AFTER='        bool measured = strcmp(r->col[KS_MR_noise_e6], "-") != 0;   /* SABOTAGE S2902 */'
SAB_FILE2="src/gen/memfn_sites.c"
SAB_COUNT2=1
SAB_BEFORE2='                                          measured ? r->noise_e6 : 0 };'
SAB_AFTER2='                                          measured ? strtoll(r->col[KS_MR_noise_e6], NULL, 10) : 0 };   /* SABOTAGE S2902 */'
