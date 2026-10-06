#!/usr/bin/env bash
# S550 ([START-TABLE] C0, lane stc0 row A; docs/dev/lanes/stc0_report.md §2) -- opt_argv drops every option: each arm compiles at its base's argv, so it is byte-identical to its base on both sides and identity passes; only the DIFFER floors/manifests can see it.
# Detector (arm emitsweep): scripts/tests/emit_sweep.py.test.
SAB_ID='S550-extra-arm-flag-dropped'
SAB_FILE='scripts/emit_sweep.py'
SAB_SUITES='emitsweep'
SAB_DESC='opt_argv drops every option: each arm compiles at its base'\''s argv, so it is byte-identical to its base on both sides and identity passes; only the DIFFER floors/manifests can see it'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc0_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S550.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return [a.decode("utf-8", "surrogateescape") if isinstance(a, bytes) else a
            for a in extra]'
SAB_AFTER='    return []   # SABOTAGE S550'
