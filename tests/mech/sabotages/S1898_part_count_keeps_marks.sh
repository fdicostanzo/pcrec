# S1898 ([XARCH-DEV] U3, lane u3d27; D27 region suite F1) -- a part's `<PREFIX>__X_SIMD_GUARDED_BYTES` counts its held marks (3 bytes per held header line), which its shell takes out: the part's stamp then reads nonzero on a part that renders no form and carries no target text.
# Detector (arm memfntargets): tests/memfn/run_targets.sh section 4b's F1 checks (every part's count 0 on the compound controls).
SAB_ID="S1898-part-count-keeps-marks"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfntargets"
SAB_DESC="a compound part's guarded-bytes stamp counts its held header marks"
SAB_DOC_FIGURE="memfntargets: run_targets.sh's F1 part-count check reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1898."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                             job->hsb.simd_guarded - held));'
SAB_AFTER='                                             job->hsb.simd_guarded - 0 * held));   /* SABOTAGE S1898 */'
