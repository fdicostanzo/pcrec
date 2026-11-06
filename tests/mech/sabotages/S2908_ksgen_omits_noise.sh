# S2908 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (r);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (r) ksgen omits the appended KsMeasRow.noise_e6 field, so the pre-parse holds C's 0 where a fresh parse holds KS_MEAS_EMPTY or the parsed noise.
# Detector: run_measures_tests.sh builds ksgen from this tree and runs it over mfixtures.py's format-2 store: meas_store_check's raw-row compare reads noise 0 against the fresh parse's 1730 and KS_MEAS_EMPTY (red). After `make gen-measures` the same compare reads 0 against KS_MEAS_EMPTY on all 68 of grid1's rows (the mech tree does not regenerate the committed .inc, so the fixture store is the arm's detector).
SAB_ID="S2908-ksgen-omits-noise"
SAB_FILE="scripts/ksgen.c"
SAB_SUITES="knowledge"
SAB_DESC='(r) ksgen omits the appended KsMeasRow.noise_e6 field, so the pre-parse holds C'"'"'s 0 where a fresh parse holds KS_MEAS_EMPTY or the parsed noise'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2908.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (m->noise_e6 == KS_MEAS_EMPTY) fputs(", KS_MEAS_EMPTY },\n", out);'
SAB_AFTER='            if (1) fputs(" },\n", out);   /* SABOTAGE S2908 */'
