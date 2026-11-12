#!/usr/bin/env bash
# S3062 -- R-38 K38-2 (docs/design/memfn/span_runs_sheet.md rev 1.3 §3.3 item 5, §3.5 W-K2;
# lane k382). THE RE-ENTRY FLOORS AT ITS LO: a use whose `lo` is not the activation's origin (the
# define's `start` hook: the RE-ENTRY) floors its run part at `lo`, not max(0, lo + omin); the
# entry keeps the right floor. The plant records the define's `start` (precheck_define) and
# compares the use's `lo` with it in run_floor.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), the §3.5 witness W-K2 (run `abab`,
# omin -2, subject `abababcc`, re-entry lo 3: expected candidate 2); the oracle step reds too.
SAB_ID="S3062-reentry-floor-is-lo"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="g2pres"
SAB_DESC="a re-entry use (lo not the activation's origin) floors its run part at lo: W-K2 must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3062 RED (W-K2: the re-entry from 3 on \"abababcc\" yields -1, the stated rule 2). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3062."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int part = 0;
    for (uint32_t i = 0; i < s->npred; i++) {'
SAB_AFTER='    { extern const char *s3062_origin; s3062_origin = h ? h->start : NULL; }   /* SABOTAGE S3062 */
    int part = 0;
    for (uint32_t i = 0; i < s->npred; i++) {'
SAB_FILE2="memfn/src/precheck.c"
SAB_COUNT2=1
SAB_BEFORE2='static const char *run_floor(mf_art *art, const mf_hooks *h, const mf_site *s)
{
    int run = kit_pres_run(s);
    int32_t omin = run >= 0 ? s->pspans[run].omin : 0;
    if (omin >= 0) return h->lo;'
SAB_AFTER2='const char *s3062_origin;   /* SABOTAGE S3062 */
static const char *run_floor(mf_art *art, const mf_hooks *h, const mf_site *s)
{
    int run = kit_pres_run(s);
    int32_t omin = run >= 0 ? s->pspans[run].omin : 0;
    if (omin >= 0 || (s3062_origin && h->lo && strcmp(h->lo, s3062_origin))) return h->lo;'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-NEG-FLOOR"
