#!/usr/bin/env bash
# S3110 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p5; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3110 (its plant_spec; one source of the text).
SAB_ID="S3110-wide-position-cube-hull"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2pres"
SAB_DESC='a wide verified position rendered by its cube hull: bytes outside the set pass the verify (G2'"'"'s classifier reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3110, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3110."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            memcpy(t->set, run->set[j], 32);'
SAB_AFTER='            memcpy(t->set, run->set[j], 32);
            { int a0 = 255, o0 = 0; for (int z = 0; z < 256; z++) if (run->set[j][z >> 3] >> (z & 7) & 1) { a0 &= z; o0 |= z; } int k0 = ~(a0 ^ o0) & 255; for (int z = 0; z < 256; z++) if ((z & k0) == (a0 & k0)) t->set[z >> 3] |= (uint8_t)(1u << (z & 7)); }   /* SABOTAGE S3110 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
