#!/usr/bin/env bash
# S881 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P1; docs/dev/lanes/b3build_report.md) -- the tagged walk's accept value collapsed to its truth: every distance set reads {0}
# Detector: tests/endmark/b3_rows.rxt (endmark arm): `\s*?$` on " \n" answers (0,2) where PCRE2 answers (0,1).
# Reach: `\s*?$` takes form tagged, mark_prio const1 (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S881-tags-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='endmark'
SAB_DESC='the tagged walk'\''s accept value collapsed to its truth: every distance set reads {0}'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S881.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\s*?$" | grep -F "form=tagged,prio=const1" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static int acc_cell(const Dfa *d, int i)
{
    return d->st[i].up[UPC_PLAIN].accept;
}'
SAB_AFTER='static int acc_cell(const Dfa *d, int i)
{
    return d->st[i].up[UPC_PLAIN].accept ? 1 : 0;   /* SABOTAGE S881 */
}'
