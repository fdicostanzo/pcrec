# S2912 — span_pick stage 2 unit S2a K138 fix (lane s2ak138; docs/dev/known_issues.md K138;
# docs/spec/measures.md §2.2¶3, §7¶1).
#
# Plant: the loader admits a row's value_e6 past 10^15 in magnitude (the kit then refuses it at mf_art_begin).
# Detector: mfixtures.py's bad/value-bound (10^15 + 1) and bad/value-bound-neg must refuse with 'is past 10^15'; both load.
SAB_ID="S2912-meas-value-bound-admitted"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the loader admits a value_e6 past 10^15 in magnitude (K138)'
SAB_DOC_FIGURE='MEASURED by lane s2ak138 planted and reverted (docs/dev/lanes/s2ak138_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2912.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        } else if (m->value_e6 > KS_MEAS_MAX || m->value_e6 < -KS_MEAS_MAX) {'
SAB_AFTER='        } else if (0 && (m->value_e6 > KS_MEAS_MAX || m->value_e6 < -KS_MEAS_MAX)) {   /* SABOTAGE S2912 */'
