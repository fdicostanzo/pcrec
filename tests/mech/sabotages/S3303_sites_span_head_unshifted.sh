#!/usr/bin/env bash
# S3303 -- lane formsfixf (review r37 H8: the sites half of the forwarded value).
SAB_ID="S3303-sites-span-head-unshifted"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="compound"
SAB_DESC="memfn_sites sends span_head, not span_head - 1 (one head too many): the accepted lever rows' forwarded-head comparison must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3303. lane formsfixf 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                             cx->emit_in->harness->span_head - 1)))'
SAB_AFTER='                                             cx->emit_in->harness->span_head)))   /* SABOTAGE S3303 */'
