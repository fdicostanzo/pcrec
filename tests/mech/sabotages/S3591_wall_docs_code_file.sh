# S3591 — [DATA-PLAN] A1 THE UCD WALL (r97 W-1..W-3): a code file under docs/ (not prose) reads a private table symbol
#
# Detector: tests/core/ucd_wall_check.py (via ucd_wall_check.sh, run by
# run_core_tests.sh).  The plant holds a SHAPE the wall's needle words do not
# contain literally, so the row proves the structural rule, not a word list.
SAB_ID="S3591-wall_docs_code_file"
SAB_FILE="docs/design/compound/twin/cost.py"
SAB_SUITES="core"
SAB_DESC="a code file under docs/ (not prose) reads a private table symbol"
SAB_DOC_FIGURE="core red on ucd_wall_check (the offender list names the planted file). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3591."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#!/usr/bin/env python3'
SAB_AFTER='#!/usr/bin/env python3
SAB_S3591 = "ucd_set_off"   # SABOTAGE S3591: a docs/ code file naming a private symbol'
