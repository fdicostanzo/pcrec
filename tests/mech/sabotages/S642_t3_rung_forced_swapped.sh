#!/usr/bin/env bash
# S642 ([DEC-FALLBACK] B2, lane decfbB2) -- T3's rung and forced rows swapped, so a [SEL-1] rung collapse would stamp the forced language reason.
# S-T3a. Detector at B2: the gate oracle on (1{0,30}?[^]abc][^abc]){28,30}0+|a (fbt (a) gate-sel1, (d) or-g-sel1); from B5 fbt (c).
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S642-t3-rung-forced-swapped'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T3's rung and forced rows swapped, so a [SEL-1] rung collapse would stamp the forced language reason"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S642. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "rung",     pflw_rung,   true,  PFLW_PASS,
      .axlist = { { "prefilter-lang", 1, "count-collapsed", PCREC_NO_PREFILTER_COLLAPSE, PCREC_FORCE_PREFILTER_COLLAPSE, "",
                    "these machines serve only as the VM'\''s prefilter (the DFA is not the engine), a counted repeat with rmin > 1 or rmax > 1 exists, AND either -fprefilter-collapse was passed or compile_driver took a retry rung (a DFA state cap overflowed, or an emitted-size cap refused the exact artifact). There is no state-count knee: the default is the exact language (Frank'\''s ruling B). Every X{m,n} then lowers as X{min(m,1),}" } } },
    { "forced",   pflw_worth,  true,  PFLW_FORCED, .axlist = FB_NO_LIST },'
SAB_AFTER='    { "forced",   pflw_worth,  true,  PFLW_FORCED, .axlist = FB_NO_LIST },
    { "rung",     pflw_rung,   true,  PFLW_PASS,
      .axlist = { { "prefilter-lang", 1, "count-collapsed", PCREC_NO_PREFILTER_COLLAPSE, PCREC_FORCE_PREFILTER_COLLAPSE, "",
                    "these machines serve only as the VM'\''s prefilter (the DFA is not the engine), a counted repeat with rmin > 1 or rmax > 1 exists, AND either -fprefilter-collapse was passed or compile_driver took a retry rung (a DFA state cap overflowed, or an emitted-size cap refused the exact artifact). There is no state-count knee: the default is the exact language (Frank'\''s ruling B). Every X{m,n} then lowers as X{min(m,1),}" } } },   /* SABOTAGE S642 */'
