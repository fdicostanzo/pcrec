#!/usr/bin/env bash
# S885 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P5; docs/dev/lanes/b3build_report.md) -- `mark_prio`'s probe overflowing its cap answers a constant instead of state-dependent
# Detector: tests/endmark/run_b3_checks.sh §5: under -DPCREC_MARK_PRIO_MAX_STATES=2, `\s+$` reads const0 where state-dependent is required.
# Reach: `\s+$` takes form tagged, mark_prio const0 (the probe runs on it) (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S885-mark-prio-overflow-const'
SAB_FILE='src/core/compile.c'
SAB_SUITES='endmark'
SAB_DESC='`mark_prio`'\''s probe overflowing its cap answers a constant instead of state-dependent'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S885.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\s+$" | grep -F "form=tagged,prio=const0" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (job->xprio.overflowed || (seen & (seen - 1))) job->mark_prio = MP_STATE;'
SAB_AFTER='        if (seen & (seen - 1)) job->mark_prio = MP_STATE;   /* SABOTAGE S885 */'
