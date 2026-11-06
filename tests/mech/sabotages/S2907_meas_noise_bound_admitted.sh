# S2907 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (h);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (h) the loader admits a format-2 noise past 10^15.
# Detector: mfixtures.py's bad/f2-noise-bound (noise 10^15 + 1, its digest correct) must refuse with 'is past 10^15'; it loads.
SAB_ID="S2907-meas-noise-bound-admitted"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='(h) the loader admits a format-2 noise past 10^15'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2907.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (m->noise_e6 > KS_MEAS_MAX)'
SAB_AFTER='    if (0 && m->noise_e6 > KS_MEAS_MAX)   /* SABOTAGE S2907 */'
