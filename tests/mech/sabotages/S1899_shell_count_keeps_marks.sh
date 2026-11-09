# S1899 ([XARCH-DEV] U3, lane u3d27; D27 region suite F1) -- the shell's guarded record keeps the held marks' bytes after the render took them out, so `<PREFIX>_SIMD_GUARDED_BYTES` on a compound with held header lines exceeds its target's own text by 3 bytes per held line.
# Detector (arm memfntargets): tests/memfn/run_targets.sh section 4b's F1 check that the --emit-main compound's count equals a plain --emit-main artifact's (both the v3 target's text alone).
SAB_ID="S1899-shell-count-keeps-marks"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfntargets"
SAB_DESC="a compound's guarded-bytes stamp still counts the held marks the render took out"
SAB_DOC_FIGURE="memfntargets: run_targets.sh's F1 count check reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1899."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                     - nheld * strlen(held);'
SAB_AFTER='                     - 0 * nheld * strlen(held);   /* SABOTAGE S1899 */'
