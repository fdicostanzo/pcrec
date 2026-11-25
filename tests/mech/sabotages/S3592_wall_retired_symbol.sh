# S3592 — [DATA-PLAN] A1 THE UCD WALL (r97 W-1..W-3): a caller names a symbol of the RETIRED pair-array interface
#
# Detector: tests/core/ucd_wall_check.py (via ucd_wall_check.sh, run by
# run_core_tests.sh).  The plant holds a SHAPE the wall's needle words do not
# contain literally, so the row proves the structural rule, not a word list.
SAB_ID="S3592-wall_retired_symbol"
SAB_FILE="src/parse/mod_code.c"
SAB_SUITES="core"
SAB_DESC="a caller names a symbol of the RETIRED pair-array interface"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3592."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "parse/ucd_tables.h"'
SAB_AFTER='#include "parse/ucd_tables.h"
#define S3592_OLD PCREC_UPROPS_UNICODE_VERSION   /* SABOTAGE S3592 */'
