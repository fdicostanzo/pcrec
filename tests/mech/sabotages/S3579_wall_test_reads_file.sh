# S3579 — [DATA-PLAN] A1 THE UCD WALL: a test helper (ucd_dump.c) names the generated file, a second reader of the format
#
# Detector: tests/core/ucd_wall_check.sh (run by run_core_tests.sh): no file
# outside src/parse/ucd_tables.c and its generator names the generated file or
# its private symbols.  The plant compiles (or is inert), so nothing but the
# wall notices it: that is the point of the row.
SAB_ID="S3579-wall_test_reads_file"
SAB_FILE="tests/uprops/ucd_dump.c"
SAB_SUITES="core"
SAB_DESC="a test helper (ucd_dump.c) names the generated file, a second reader of the format"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3579."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "parse/ucd_tables.h"'
SAB_AFTER='#include "parse/ucd_tables.h"
#define UCD_SAB_S3579 "src/parse/ucd_tables.inc"   /* SABOTAGE S3579 */'
