#!/usr/bin/env bash
# S1026 ([RUNAXES], lane runaxes; tests/axes/CLAUDE.md "The --memfn= arm") -- the `--memfn=` arm's cell composition in run_axes.sh drops the row's `--memfn=no-NAME` spelling and ONLY that: the answer jobs run the default (or -fmemfn-simd) build against the default baseline and read AGREE on every case, so identity passes; only memfn_arm.py (the cells' own flag text, compiled against its base) can see that the flag never arrived.
# Detector (arm axesmemfn): run_axes.sh with MEMFN_REACH_ONLY=1 AXES=--memfn MEMFN_EVERY=40 (the reach alone, a corpus sample; classes, witnesses, the spelling-in-cell check, null arm and unknown-name control all apply on a sample, floors do not).
SAB_ID='S1026-memfn-axes-arm-flag-dropped'
SAB_FILE='tests/axes/run_axes.sh'
SAB_SUITES='axesmemfn'
SAB_DESC='run_axes.sh composes each memfn cell without the row spelling: the answer jobs compile the base build on both sides and pass identity; the arm reach (cell flags lack the spelling, DIFFER witness identical to its base) is the only detector'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/runaxes_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1026.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            _mflags="$_mspell"
            [ "$_mlayer" = simd ] && _mflags="$memfn_simd_flag $_mspell"'
SAB_AFTER='            _mflags=""   # SABOTAGE S1026
            [ "$_mlayer" = simd ] && _mflags="$memfn_simd_flag"'
