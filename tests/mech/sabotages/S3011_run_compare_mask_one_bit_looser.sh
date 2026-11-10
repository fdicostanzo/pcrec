#!/usr/bin/env bash
# S3011 -- R-38 K38-2a, review 2026-11-10 r2 k382a FAM-3 (lane k382afix; docs/design/memfn/
# span_runs_sheet.md rev 1.3 §2.4 C2, "its compares cover exactly the extent"). THE RUN COMPARE
# IS ONE BIT LOOSER: the words form (runcmp.c rc_emit_words) drops the lowest set bit of every
# mask byte that has more than one (a caseless position's 0xDF becomes 0xDE), so a byte one bit
# off a member is compared as a member. The filler probe could not see it: the filler differs
# from the member in other bits too.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), C2's classifier: EXTENT's per-bit
# near-misses (each member of each verified position with one bit flipped out of its set must
# not be yielded); the oracle also reds on the uses' near-miss occurrences.
SAB_ID="S3011-run-compare-mask-one-bit-looser"
SAB_FILE="memfn/src/runcmp.c"
SAB_SUITES="g2pres"
SAB_DESC="the run compare's words form loosens each multi-bit mask byte by its lowest bit: EXTENT's per-bit near-misses must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382afix 2026-11-10 (docs/dev/lanes/k382afix_report.md): memfn/tests/run_g2_pres.sh --plant S3011 RED (EXTENT near-miss; oracle also RED, violations=162); the same plant against the pre-fix driver GREEN (oracle rows=50178 violations=0). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3011."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            t[i] = skip ? 0x00 : r->t[at + i];'
SAB_AFTER='            t[i] = skip ? 0x00 : r->t[at + i];
            if (k[i] != 0xFF && (k[i] & (k[i] - 1))) { k[i] &= (uint8_t)(k[i] - 1); t[i] &= k[i]; }   /* SABOTAGE S3011 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-WORDS-COMPARE"
