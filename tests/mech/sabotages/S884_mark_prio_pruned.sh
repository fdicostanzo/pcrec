#!/usr/bin/env bash
# S884 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P4; docs/dev/lanes/b3build_report.md) -- `mark_prio` computed on the PRUNED anchored machine, where no END closure can hold two distances
# Detector: the tie fact and the probe disagree: every tagged compile that can tie refuses (an internal error), so tests/endmark/b3_rows.rxt's tie blocks fail to compile.
# Reach: `(?:\s+|x\s*?)$` takes mark_prio state-dependent (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S884-mark-prio-pruned'
SAB_FILE='src/core/compile.c'
SAB_SUITES='endmark'
SAB_DESC='`mark_prio` computed on the PRUNED anchored machine, where no END closure can hold two distances'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S884.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "(?:\\s+|x\\s*?)$" | grep -F "prio=state-dependent" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_build_dfa(cx, &job->xnfa, &job->xprio, false, false,'
SAB_AFTER='        pcrec_build_dfa(cx, &job->xnfa, &job->xprio, true, false,   /* SABOTAGE S884 */'
