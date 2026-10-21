# S1242 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the measures row includes core/internal.h, so a tool linking the parts and this row would link the compiler (S989's rule, for the row).
# Detector: tests/core/ksrc_deps_check.sh (a') and (b').
SAB_ID="S1242-ks-measures-includes-internal"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="core"
SAB_DESC='the measures row includes core/internal.h, so a tool linking the parts and this row would link the compiler (S989'"'"'s rule, for the row)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1242.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "core/ks_measures.h"
#include "core/ksrc.h"'
SAB_AFTER='#include "core/internal.h"   /* SABOTAGE S1242 */
#include "core/ks_measures.h"
#include "core/ksrc.h"'
