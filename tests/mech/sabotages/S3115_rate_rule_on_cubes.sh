#!/usr/bin/env bash
# S3115 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1.1 D0 [r2pd P18], [r3pd FIX-3]; lane partd).
# THE SITE FILE'S HASH CONTROL. The rate rule for a set position (each member rated) applied to today's
# stream's cubes too: a second draw on the MAIN rng per cube position shifts every later site, so today's
# site file is no longer byte-identical. A generator plant (no kit byte moves): its detector is
# run_g2_pres.sh's SITE_HASHES literals, which nothing else checks.
SAB_ID="S3115-rate-rule-on-cubes"
SAB_FILE="memfn/tests/g2/g2_pres_gen.c"
SAB_SUITES="g2pres"
SAB_DESC='the presence generator rates each member of a two-member cube on the main rng too: the site file of today'"'"'s stream moves (the hashed site file reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3115."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        for (unsigned j = 0; j < g->L; j++) g->rate[g->run[j]] = rnd(200000);'
SAB_AFTER='        for (unsigned j = 0; j < g->L; j++) { g->rate[g->run[j]] = rnd(200000); if (g->mask[j] != 0xFF) g->rate[g->run[j] ^ (uint8_t)~g->mask[j]] = rnd(200000); }   /* SABOTAGE S3115 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
