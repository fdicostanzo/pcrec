# S3589 — [DATA-PLAN] A1 THE UCD WALL (r97 W-1..W-3): an include whose name is built from adjacent string literals in a macro
#
# Detector: tests/core/ucd_wall_check.py (via ucd_wall_check.sh, run by
# run_core_tests.sh).  The plant holds a SHAPE the wall's needle words do not
# contain literally, so the row proves the structural rule, not a word list.
SAB_ID="S3589-wall_macro_include"
SAB_FILE="src/parse/mod_named_groups.c"
SAB_SUITES="core"
SAB_DESC="an include whose name is built from adjacent string literals in a macro"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3589."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "parse/ucd_tables.h"'
SAB_AFTER='#include "parse/ucd_tables.h"
#define S3589_HDR "ucd_" "tables" ".inc"   /* SABOTAGE S3589 */
#include S3589_HDR'
