#!/usr/bin/env bash
# S889 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P9; docs/dev/lanes/b3build_report.md) -- a lowered machine's overflow REFUSES the compile instead of declining the form to `overflow` (§R.5)
# Detector: tests/endmark/run_b3_checks.sh §5: under -DPCREC_ANCHORED_MAX_STATES=3, `\s*?$` (today's anchored machine fits, the lowered one does not) must read form overflow and answer; it refuses.
# Reach: `\s*?$` takes form tagged at the shipped caps (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S889-lowered-overflow-refuses'
SAB_FILE='src/core/compile.c'
SAB_SUITES='endmark'
SAB_DESC='a lowered machine'\''s overflow REFUSES the compile instead of declining the form to `overflow` (§R.5)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S889.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\s*?$" | grep -F "form=tagged" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_build_min_dfa(cx, nfa, d, prune, reverse, cap, root, true);'
SAB_AFTER='    pcrec_build_min_dfa(cx, nfa, d, prune, reverse, cap, root, false);   /* SABOTAGE S889 */'
