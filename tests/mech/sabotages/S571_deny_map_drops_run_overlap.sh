#!/usr/bin/env bash
# S571 ([MEMFN] M1b, lane m1b) -- PCREC'S DENY MAP DROPS BIT 43.
#
# The deny must REACH every site (R-5's risk list): pcrec maps its flag bits
# onto the kit's MF_D_* denies through ONE table (src/gen/memfn_sites.c,
# `deny_map`), read by every site's `denies`, the attempt's mf_art_begin and,
# reversed, `--list-axes`. The plant maps bit 43 to nothing, so the kit never
# learns of -fno-run-overlap: the flag still parses and still lands in
# rx_info's masking, but every OFS/PRE run term and every VM literal run keeps
# its word form. S570's symptom from pcrec's side of the boundary (the kit is
# correct, the deny never arrives). Detector: tests/codegen/runcmp_check.py's
# `-fno-run-overlap` arm.
SAB_ID="S571-deny-map-drops-run-overlap"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="codegen"
SAB_DESC="pcrec's in-emitter deny map sends no MF_D_RUN_OVERLAP for -fno-run-overlap, so the kit renders word compares under the deny on every site"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/m1b_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S571."
SAB_REACH='"$PCREC" --features all -fno-run-overlap -p rx -o "$REACH_TMP/o.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/o.c" && grep -qF "!memcmp(subject + cand, \"/user\", 5)" "$REACH_TMP/o.c" && echo REACH-DENIED-RUN-TERM-IS-MEMCMP'
SAB_REACH_EXPECT="REACH-DENIED-RUN-TERM-IS-MEMCMP"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { PCREC_NO_RUN_OVERLAP, MF_D_RUN_OVERLAP },'
SAB_AFTER='    { PCREC_NO_RUN_OVERLAP, 0 },   /* SABOTAGE S571 */'
