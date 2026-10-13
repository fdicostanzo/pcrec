#!/usr/bin/env bash
# S888 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P8; docs/dev/lanes/b3build_report.md) -- the scan-edge pass compares accept TRUTH (S3), so a chain merges states whose distance sets differ
# Detector: tests/endmark/b3_rows.rxt (endmark arm): `\n{1,4}$`'s newline cells.
# Reach: `\n{1,4}$` takes form tagged (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S888-scanedge-truth-compare'
SAB_FILE='src/opt/scanedge.c'
SAB_SUITES='endmark'
SAB_DESC='the scan-edge pass compares accept TRUTH (S3), so a chain merges states whose distance sets differ'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S888.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\n{1,4}$" | grep -F "form=tagged" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='{ return s < 0 ? 0 : d->st[s].up[UPC_PLAIN].accept; }'
SAB_AFTER='{ return s < 0 ? 0 : d->st[s].up[UPC_PLAIN].accept != 0; }   /* SABOTAGE S888 */'
