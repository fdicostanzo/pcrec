# S3575 — [DATA-PLAN] A1 THE UCD WALL: a second translation unit (mod_uprops.c) includes the generated table file, so the storage format has two readers
#
# Detector: tests/core/ucd_wall_check.sh (run by run_core_tests.sh): no file
# outside src/parse/ucd_tables.c and its generator names the generated file or
# its private symbols.  The plant compiles (or is inert), so nothing but the
# wall notices it: that is the point of the row.
SAB_ID="S3575-wall_second_includer"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="core"
SAB_DESC="a second translation unit (mod_uprops.c) includes the generated table file, so the storage format has two readers"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3575."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "ucd_tables.h"   /* the property tables, through their ONE interface */'
SAB_AFTER='#include "ucd_tables.h"   /* the property tables, through their ONE interface */
#include "ucd_tables.inc"   /* SABOTAGE S3575 */'
