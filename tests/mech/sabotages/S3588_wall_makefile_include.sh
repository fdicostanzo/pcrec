# S3588 — [DATA-PLAN] A1 THE UCD WALL (r97 W-1..W-3): a Makefile include directive reaches the generated tables through GEN_TABLES, not the file name
#
# Detector: tests/core/ucd_wall_check.py (via ucd_wall_check.sh, run by
# run_core_tests.sh).  The plant holds a SHAPE the wall's needle words do not
# contain literally, so the row proves the structural rule, not a word list.
SAB_ID="S3588-wall_makefile_include"
SAB_FILE="Makefile"
SAB_SUITES="core"
SAB_DESC="a Makefile include directive reaches the generated tables through GEN_TABLES, not the file name"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3588."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='GEN_TABLES := src/parse/ucd_tables.inc src/core/fold_tables.inc \'
SAB_AFTER='-include $(GEN_TABLES:.inc=.sab)   # SABOTAGE S3588
GEN_TABLES := src/parse/ucd_tables.inc src/core/fold_tables.inc \'
