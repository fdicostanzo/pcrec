# S3587 — [DATA-PLAN] A1 THE UCD WALL (r97 W-1..W-3): a backslash-spliced include of the generated file (the name is split across two physical lines)
#
# Detector: tests/core/ucd_wall_check.py (via ucd_wall_check.sh, run by
# run_core_tests.sh).  The plant holds a SHAPE the wall's needle words do not
# contain literally, so the row proves the structural rule, not a word list.
SAB_ID="S3587-wall_spliced_include"
SAB_FILE="src/parse/mod_ucp.c"
SAB_SUITES="core"
SAB_DESC="a backslash-spliced include of the generated file (the name is split across two physical lines)"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3587."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "ucd_tables.h"'
SAB_AFTER='#include "ucd_tables.h"
#include "ucd_tables\
.inc"   /* SABOTAGE S3587 */'
