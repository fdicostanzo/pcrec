#!/usr/bin/env bash
# S1918 (lane sar1, 2026-11-09; span_arms R1, witness W-R5, docs/design/span_arms.md §3.6) -- THE COPY COUNT STOPS ONE SHORT.
#
# `rr_pow_count` (src/facts/req.c) unrolls an `all` body of width w up to
# ceil(32/w) copies, where its stored head is full. This plant stops one copy
# short: `(?:abc){20}` lists 30 positions where 32 are stored. The shorter
# run is still sound, so no answer moves; the detector is the facts listing,
# tests/codegen/run_facts_checks.sh [facts-rep].
SAB_ID="S1918-rep-saturates-one-short"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the necessary-run walk's copy count stops one copy before the run's storage bound is full, so an exact repeat of a literal states a shorter run than the bound allows (sound, a listing-only loss)"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1918."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern "(?:abc){20}" | grep -qP "^byte\treq_whole_run\t.*\t(616263){10}6162\t" && echo REACH-WR5-RUN32'
SAB_REACH_EXPECT="REACH-WR5-RUN32"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            : b->maxw > 0 ? (int)((PCREC_MAX_REQ_RUN_SCAN + b->maxw - 1) / b->maxw)'
SAB_AFTER='            : b->maxw > 0 ? (int)((PCREC_MAX_REQ_RUN_SCAN + b->maxw - 1) / b->maxw) - 1   /* SABOTAGE S1918 */'
