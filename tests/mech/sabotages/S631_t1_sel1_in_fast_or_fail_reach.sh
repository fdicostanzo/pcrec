#!/usr/bin/env bash
# S631 ([DEC-FALLBACK] B2, lane decfbB2) -- sel1-collapse is put inside --fast-or-fail's reach, so the switch denies the [SEL-1] collapse rung (Q2 ruled the reach to the size rows only).
# S-F4. Detector at B2: the oracle's arrival check on --fast-or-fail W_SEL1 (fbt (a) seq-fofsel1, (d) or-fofsel1); from B3 the witness takes sel1-drop.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S631-t1-sel1-in-fast-or-fail-reach'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="sel1-collapse is put inside --fast-or-fail's reach, so the switch denies the [SEL-1] collapse rung (Q2 ruled the reach to the size rows only)"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S631. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    /* 3 [SEL-1]/[OPT-4] the collapsed-prefilter rung */
    { .name = "sel1-collapse", .deny = PCREC_NO_PREFILTER_COLLAPSE, .degrading = true,
      .applies = fit_sel1_collapse_applies, .act = FIT_SEL1_COLLAPSE,
      .on = FIT_L_OVERFLOW, .fof = FIT_FOF_OUT,'
SAB_AFTER='    /* 3 [SEL-1]/[OPT-4] the collapsed-prefilter rung */
    { .name = "sel1-collapse", .deny = PCREC_NO_PREFILTER_COLLAPSE, .degrading = true,
      .applies = fit_sel1_collapse_applies, .act = FIT_SEL1_COLLAPSE,
      .on = FIT_L_OVERFLOW, .fof = FIT_FOF_IN,   /* SABOTAGE S631 */'
