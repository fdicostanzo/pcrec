#!/usr/bin/env bash
# S1047 ([SWFIX], lane swfix) -- the --engine=vm arm's composition producing floor (37, AT the measured value) raised by one: the arm's own floor must be able to FAIL. The plain arm's floors are not applied to an --extra arm; this entry is the arm's only one, so nothing else can see the plant.
# Detector (arm emitsweep): scripts/tests/emit_sweep.py.test (its vm-arm composition sweep must read clean at the real floors, and its own sed plants of +1 must go red).
SAB_ID='S1047-composition-producing-floor-raised'
SAB_FILE='scripts/emit_sweep.py'
SAB_SUITES='emitsweep'
SAB_DESC='the --engine=vm arm'\''s composition producing floor (37, AT the measured value) raised by one, so the arm'\''s clean ref-vs-ref sweep reads a COMPOSITION PRODUCING FLOOR VIOLATION'
SAB_DOC_FIGURE='Validated by plant at landing (lane swfix, scripts/tests/emit_sweep.py.test); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1047.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    ("--engine=vm",): {"composition_producing_floor": 37,'
SAB_AFTER='    ("--engine=vm",): {"composition_producing_floor": 38,   # SABOTAGE S1047'
