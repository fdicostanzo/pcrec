#!/usr/bin/env bash
# S3111 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p6'; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3111 (its plant_spec; one source of the text).
SAB_ID="S3111-set-test-member-dropped"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="g2pres"
SAB_DESC='the verify chain'"'"'s set test drops its lowest member: an occurrence holding it is missed (the occurrence oracle reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3111, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3111."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            kit_set_test(&test, t->set, byte.p);'
SAB_AFTER='            { uint8_t s2[32]; memcpy(s2, t->set, 32); for (int z = 0; z < 256; z++) if (s2[z >> 3] >> (z & 7) & 1) { s2[z >> 3] &= (uint8_t)~(1u << (z & 7)); break; } kit_set_test(&test, s2, byte.p); }   /* SABOTAGE S3111 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
