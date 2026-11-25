# S3578 — [DATA-PLAN] A1 THE UCD WALL: the module header names a private table symbol, so every includer is told about the layout
#
# Detector: tests/core/ucd_wall_check.sh (run by run_core_tests.sh): no file
# outside src/parse/ucd_tables.c and its generator names the generated file or
# its private symbols.  The plant compiles (or is inert), so nothing but the
# wall notices it: that is the point of the row.
SAB_ID="S3578-wall_header_leaks"
SAB_FILE="src/parse/ucd_tables.h"
SAB_SUITES="core"
SAB_DESC="the module header names a private table symbol, so every includer is told about the layout"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3578."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#define PCREC_UCD_NS_BARE 1u'
SAB_AFTER='#define PCREC_UCD_NS_BARE 1u
#define UCD_SAB_S3578 ucd_set_n   /* SABOTAGE S3578 */'
