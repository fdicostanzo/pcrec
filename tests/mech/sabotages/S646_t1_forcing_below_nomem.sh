#!/usr/bin/env bash
# S646 ([DEC-FALLBACK] B3, lane decfbB3) -- T1 rows 0 and 1 swapped: `nomem`
# is asked ahead of `forcing`, so an allocation failure INSIDE `--emit-facts`'
# force loop (labels forcing|nomem) propagates and the listing refuses a
# compile that succeeded, where row 0 absorbs it as `decline:force-failed`.
# S-F0 (dec_fallback.md §4.4; critB1 MAJOR-3: the forcing test came first
# because it ABSORBS a nomem arrival inside the loop). Live from B3, when the
# walk became the dispatch. Detector (arm resource): run_resource_tests.sh
# §2b runs tests/core/alloc_check.c, whose W5 witness requires every in-loop
# forced failure to answer rc 0 with exactly one force-failed row (code 22,
# "was REFUSED", under the plant).
SAB_ID='S646-t1-forcing-below-nomem'
SAB_FILE='src/core/compile.c'
SAB_SUITES='resource'
SAB_DESC="T1 rows 0/1 swapped: a nomem arrival inside --emit-facts' force loop propagates (the listing refuses) instead of becoming decline:force-failed"
SAB_DOC_FIGURE='tests/core/alloc_check.c W5 (make alloc): the in-loop trial reads "was REFUSED" under the plant. Re-run: bash tests/mech/run_sabotage_matrix.sh S646. docs/dev/lanes/decfbB3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    /* 0 [PATFACTS] a forced ask failed after the artifact was complete */
    { .name = "forcing", .deny = 0, .degrading = false, .applies = fit_always,
      .act = FIT_FORCE_NEXT, .on = FIT_L_FORCING, .fof = FIT_FOF_OUT,
      .sets = FIT_SETS_NONE, .cells = FIT_CELLS_PASS, .ukw = NULL,
      .note = { NULL, NULL }, .retries = 0, .repeat = FIT_REP_MANY },
    /* 1 [K60] a genuine allocation failure propagates */
    { .name = "nomem", .deny = 0, .degrading = false, .applies = fit_always,
      .act = FIT_PROPAGATE, .on = FIT_L_NOMEM, .fof = FIT_FOF_OUT,
      .sets = FIT_SETS_NONE, .cells = FIT_CELLS_PASS, .ukw = NULL,
      .note = { NULL, NULL }, .retries = 0, .repeat = FIT_REP_ONCE },
'
SAB_AFTER='    /* 1 [K60] a genuine allocation failure propagates */
    { .name = "nomem", .deny = 0, .degrading = false, .applies = fit_always,
      .act = FIT_PROPAGATE, .on = FIT_L_NOMEM, .fof = FIT_FOF_OUT,
      .sets = FIT_SETS_NONE, .cells = FIT_CELLS_PASS, .ukw = NULL,
      .note = { NULL, NULL }, .retries = 0, .repeat = FIT_REP_ONCE },
    /* 0 [PATFACTS] a forced ask failed after the artifact was complete */
    { .name = "forcing", .deny = 0, .degrading = false, .applies = fit_always,
      .act = FIT_FORCE_NEXT, .on = FIT_L_FORCING, .fof = FIT_FOF_OUT,
      .sets = FIT_SETS_NONE, .cells = FIT_CELLS_PASS, .ukw = NULL,
      .note = { NULL, NULL }, .retries = 0, .repeat = FIT_REP_MANY },
    /* SABOTAGE S646 */
'
