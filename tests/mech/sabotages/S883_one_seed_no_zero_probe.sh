#!/usr/bin/env bash
# S883 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P3; docs/dev/lanes/b3build_report.md) -- F1 skips the zero-length probe at n where the n-1 walk accepts nowhere
# Detector: tests/endmark/b3_rows.rxt (endmark arm): `\B$` on "a\n" loses (2,2).
# Reach: `\B$` takes form one-seed (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S883-one-seed-no-zero-probe'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='endmark'
SAB_DESC='F1 skips the zero-length probe at n where the n-1 walk accepts nowhere'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S883.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\B$" | grep -F "form=one-seed" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (zero_at_n)
'
SAB_AFTER='    if (0 && zero_at_n)   /* SABOTAGE S883 */
'
