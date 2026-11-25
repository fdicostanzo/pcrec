# S3576 — [DATA-PLAN] A1 THE UCD WALL: a caller (mod_ucp.c) declares a private table symbol of the module, so it reaches the blob around the interface
#
# Detector: tests/core/ucd_wall_check.sh (run by run_core_tests.sh): no file
# outside src/parse/ucd_tables.c and its generator names the generated file or
# its private symbols.  The plant compiles (or is inert), so nothing but the
# wall notices it: that is the point of the row.
SAB_ID="S3576-wall_extern_symbol"
SAB_FILE="src/parse/mod_ucp.c"
SAB_SUITES="core"
SAB_DESC="a caller (mod_ucp.c) declares a private table symbol of the module, so it reaches the blob around the interface"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3576."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "ucd_tables.h"'
SAB_AFTER='#include "ucd_tables.h"
extern const unsigned char ucd_iv_blob[];   /* SABOTAGE S3576 */'
