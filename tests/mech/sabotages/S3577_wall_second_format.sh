# S3577 — [DATA-PLAN] A1 THE UCD WALL: the retired pair-array format comes back in a caller (mod_code.c), a second format beside the module's
#
# Detector: tests/core/ucd_wall_check.sh (run by run_core_tests.sh): no file
# outside src/parse/ucd_tables.c and its generator names the generated file or
# its private symbols.  The plant compiles (or is inert), so nothing but the
# wall notices it: that is the point of the row.
SAB_ID="S3577-wall_second_format"
SAB_FILE="src/parse/mod_code.c"
SAB_SUITES="core"
SAB_DESC="the retired pair-array format comes back in a caller (mod_code.c), a second format beside the module's"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3577."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "parse/ucd_tables.h"'
SAB_AFTER='#include "parse/ucd_tables.h"
#define PCREC_SAB_S3577 pcrec_uprop_iv   /* SABOTAGE S3577: the old pair-array symbol */'
