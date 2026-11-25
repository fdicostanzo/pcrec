# S3590 — [DATA-PLAN] A1 THE UCD WALL (r97 W-1..W-3): a test helper includes the module source itself and calls its private decoder
#
# Detector: tests/core/ucd_wall_check.py (via ucd_wall_check.sh, run by
# run_core_tests.sh).  The plant holds a SHAPE the wall's needle words do not
# contain literally, so the row proves the structural rule, not a word list.
SAB_ID="S3590-wall_includes_module_c"
SAB_FILE="tests/uprops/ucd_dump.c"
SAB_SUITES="core"
SAB_DESC="a test helper includes the module source itself and calls its private decoder"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3590."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "parse/ucd_tables.h"'
SAB_AFTER='#include "parse/ucd_tables.h"
#include "../../src/parse/ucd_tables.c"   /* SABOTAGE S3590: ucd_decode on a raw set index */'
