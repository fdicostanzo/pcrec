#!/usr/bin/env bash
# S981 ([SWEEPARM], lane sweeparm; scripts/CLAUDE.md emit_sweep) -- opt_argv drops `-fmemfn-simd` and ONLY that flag: the -fmemfn-simd arms compile at their base's argv, byte-identical to the base on both sides, so identity passes; only the arm's DIFFER_PINS floor and manifest can see it.
# RE-AIMED 2026-11-08 (lane u3tgt, [XARCH-DEV] U3): the arm now names its CPU target (-fmemfn-simd=TARGET), so the plant drops the flag in either spelling.
# Detector (arm emitsweep): scripts/tests/emit_sweep.py.test (`--arms start` over the manifest population: the floor cells' manifest must differ under the arm).
SAB_ID='S981-memfn-simd-arm-dropped'
SAB_FILE='scripts/emit_sweep.py'
SAB_SUITES='emitsweep'
SAB_DESC='opt_argv drops -fmemfn-simd only: the -fmemfn-simd arms read byte-identical to their base on both sides and pass identity; the DIFFER manifest/floor is the only detector'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/sweeparm_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S981.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return [a.decode("utf-8", "surrogateescape") if isinstance(a, bytes) else a
            for a in extra]'
SAB_AFTER='    return [a.decode("utf-8", "surrogateescape") if isinstance(a, bytes) else a
            for a in extra if str(a).split("=")[0] != "-fmemfn-simd"]   # SABOTAGE S981'
