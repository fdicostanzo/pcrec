#!/usr/bin/env bash
# S551 ([START-TABLE] C0, lane stc0 row B; docs/dev/lanes/stc0_report.md §2) -- opt_argv drops `-e utf8`: every utf8-base arm measures the BYTE delta against the BYTE base; the asserted zero (-fno-end-window at utf8, byte reads 288) and the plain -e utf8 arm are the controls that catch it by design.
# Detector (arm emitsweep): scripts/tests/emit_sweep.py.test.
SAB_ID='S551-utf8-base-dropped'
SAB_FILE='scripts/emit_sweep.py'
SAB_SUITES='emitsweep'
SAB_DESC='opt_argv drops `-e utf8`: every utf8-base arm measures the BYTE delta against the BYTE base; the asserted zero (-fno-end-window at utf8, byte reads 288) and the plain -e utf8 arm are the controls that catch it by design'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc0_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S551.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return [a.decode("utf-8", "surrogateescape") if isinstance(a, bytes) else a
            for a in extra]'
SAB_AFTER='    return [a.decode("utf-8", "surrogateescape") if isinstance(a, bytes) else a
            for a in extra if a not in ("-e", "utf8")]   # SABOTAGE S551'
