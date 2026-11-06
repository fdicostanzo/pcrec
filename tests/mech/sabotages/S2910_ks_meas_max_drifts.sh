# S2910 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (t);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (t) KS_MEAS_MAX, the loader's copy of the kit's MF_MEASURE_MAX, edited to 10^16.
# Detector: tests/knowledge/meas_store_check.c _Static_asserts KS_MEAS_MAX == MF_MEASURE_MAX: its build fails and run_measures_tests.sh reports the compiler error (a designed compile-time catch).
SAB_ID="S2910-ks-meas-max-drifts"
SAB_FILE="src/core/ks_measures.h"
SAB_SUITES="knowledge"
SAB_DESC='(t) KS_MEAS_MAX, the loader'"'"'s copy of the kit'"'"'s MF_MEASURE_MAX, edited to 10^16'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2910.'
SAB_EXPECT=COMPILE-CATCH   # [MECH-NOCOMPILE] designed: the equality TU fails to build
SAB_COUNT=1
SAB_BEFORE='#define KS_MEAS_MAX 1000000000000000LL'
SAB_AFTER='#define KS_MEAS_MAX 10000000000000000LL   /* SABOTAGE S2910 */'
