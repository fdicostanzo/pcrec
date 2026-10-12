#!/usr/bin/env bash
# S882 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P2; docs/dev/lanes/b3build_report.md) -- `mark_prio` records the LAST distance accepting at an END closure, not the first in priority order
# Detector: tests/endmark/b3_rows.rxt (endmark arm): `\s+$` (const0) on "a \n" ends at n-1.
# Reach: `\s+$` takes form tagged, mark_prio const0 (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S882-mark-prio-second-distance'
SAB_FILE='src/ir/dfa.c'
SAB_SUITES='endmark'
SAB_DESC='`mark_prio` records the LAST distance accepting at an END closure, not the first in priority order'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S882.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\s+$" | grep -F "form=tagged,prio=const0" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                d->prio_seen |= (uint8_t)(1u << first);'
SAB_AFTER='                d->prio_seen |= (uint8_t)(1u << (31 - __builtin_clz((unsigned)acc)));   /* SABOTAGE S882 */'
