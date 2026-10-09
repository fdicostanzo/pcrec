#!/usr/bin/env bash
# S627 ([DEC-FALLBACK] B2, lane decfbB2) -- T1's two [SEL-1] rows swapped: sel1-drop is asked first, so the walk takes it on the first overflow where today's code takes sel1-collapse.
# S-F3 (dec_fallback.md §4.4). Detector at B2: the both-derivations oracle's arrival check (fbt (a) and (d), W_SEL1/W_OVF); from B3 fbt (b)'s collapsed-prefilter witness.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S627-t1-sel1-rows-swapped'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T1's two [SEL-1] rows swapped: sel1-drop is asked first, so the walk takes it on the first overflow where today's code takes sel1-collapse"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S627. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    /* 3 [SEL-1]/[OPT-4] the collapsed-prefilter rung */
    { .name = "sel1-collapse", .deny = PCREC_NO_PREFILTER_COLLAPSE, .degrading = true,
      .applies = fit_sel1_collapse_applies, .act = FIT_SEL1_COLLAPSE,
      .on = FIT_L_OVERFLOW, .fof = FIT_FOF_OUT,
      .sets = { FIT_DD_SET, FIT_CR_TO_SEL1, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },
      .cells = { { ESEL_COLLAPSED_PREFILTER, ESEL_ROLE }, PFLW_SEL1, NULL },
      .ukw = NULL, .note = { NULL, NULL }, .retries = 1, .repeat = FIT_REP_ONCE,
      .axlist = { { "engine-route", 3, "collapsed-prefilter", 0, 0, "",
                    "auto, a DFA build overflowed a cap, and compile_driver'\''s retry KEPT a prefilter by rebuilding it from the count-collapsed language ([OPT-4]/K39; -fno-prefilter-collapse skips this rung)" },
                  { "engine-route", 5, "overflowed-dfa", 0, 0, "",
                    "auto, the DFA was to be the ENGINE, its build overflowed, and no prefilter survived the fallback ([SEL-1]/K40)" },
                  { "engine-route", 6, "overflowed-prefilter", 0, 0, "",
                    "auto, the VM was already chosen for another reason, and only its auto-selected PREFILTER'\''s DFA overflowed, so the prefilter was dropped" } } },
    /* 4 [SEL-1] the prefilter-drop rung */
    { .name = "sel1-drop", .deny = 0, .degrading = true,
      .applies = fit_sel1_drop_applies, .act = FIT_SEL1_DROP,
      .on = FIT_L_OVERFLOW, .fof = FIT_FOF_OUT,
      .sets = { FIT_DD_SET, FIT_CR_TO_NONE, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },
      .cells = { { ESEL_ROLE, ESEL_ROLE }, PFLW_PASS, NULL },
      .ukw = NULL, .note = { NULL, NULL }, .retries = 1, .repeat = FIT_REP_ONCE },
'
SAB_AFTER='    /* 4 [SEL-1] the prefilter-drop rung */
    { .name = "sel1-drop", .deny = 0, .degrading = true,
      .applies = fit_sel1_drop_applies, .act = FIT_SEL1_DROP,
      .on = FIT_L_OVERFLOW, .fof = FIT_FOF_OUT,
      .sets = { FIT_DD_SET, FIT_CR_TO_NONE, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },
      .cells = { { ESEL_ROLE, ESEL_ROLE }, PFLW_PASS, NULL },
      .ukw = NULL, .note = { NULL, NULL }, .retries = 1, .repeat = FIT_REP_ONCE },
    /* 3 [SEL-1]/[OPT-4] the collapsed-prefilter rung */
    { .name = "sel1-collapse", .deny = PCREC_NO_PREFILTER_COLLAPSE, .degrading = true,
      .applies = fit_sel1_collapse_applies, .act = FIT_SEL1_COLLAPSE,
      .on = FIT_L_OVERFLOW, .fof = FIT_FOF_OUT,
      .sets = { FIT_DD_SET, FIT_CR_TO_SEL1, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },
      .cells = { { ESEL_COLLAPSED_PREFILTER, ESEL_ROLE }, PFLW_SEL1, NULL },
      .ukw = NULL, .note = { NULL, NULL }, .retries = 1, .repeat = FIT_REP_ONCE,
      .axlist = { { "engine-route", 3, "collapsed-prefilter", 0, 0, "",
                    "auto, a DFA build overflowed a cap, and compile_driver'\''s retry KEPT a prefilter by rebuilding it from the count-collapsed language ([OPT-4]/K39; -fno-prefilter-collapse skips this rung)" },
                  { "engine-route", 5, "overflowed-dfa", 0, 0, "",
                    "auto, the DFA was to be the ENGINE, its build overflowed, and no prefilter survived the fallback ([SEL-1]/K40)" },
                  { "engine-route", 6, "overflowed-prefilter", 0, 0, "",
                    "auto, the VM was already chosen for another reason, and only its auto-selected PREFILTER'\''s DFA overflowed, so the prefilter was dropped" } } },
    /* SABOTAGE S627 */
'
