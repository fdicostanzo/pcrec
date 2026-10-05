#!/usr/bin/env bash
# S471 ([K82] (B), lane k82hbuild) -- THE UTF8 ROUND-UP IS DROPPED.
#
# Detector: run_prechecks.sh §5.12h (the round-up is present iff the encoding
# restricts a position, inside the moving branch).
SAB_ID="S471-roundup-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC='the utf8 round-up of the moved start is dropped, so the body may begin at a continuation byte; measured answer-equivalent (r1 S-F5: 0 diffs over 13 shapes), so the structural check is its detector'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S471.'
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern '\''(?i)straße'\'' && grep -q '\''handoff_position >= subject_length ||'\'' "$REACH_TMP/o.c" && echo REACH-ROUNDUP'
SAB_REACH_EXPECT='REACH-ROUNDUP'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|emit "\$a" .\(\?i\)straße. -e utf8|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_emit_start_zero(cx, &round, dfa_fragf(cx, "%s    ", indent),
                          "handoff_position", subjvar, lenvar,
                          PCREC_START0_ROUNDUP);'
SAB_AFTER='    (void)subjvar; /* SABOTAGE S471: no round-up */'
