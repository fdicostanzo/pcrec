#!/usr/bin/env bash
# S887 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P7; docs/dev/lanes/b3build_report.md) -- a tagged machine's class-indexed accept reads the UNION of the distance sets over every context atom
# Detector: tests/endmark/b3_rows.rxt (endmark arm): `(?:\Bx\n|x)$` on " x\n" (no tie under the non-word atom) answers (1,3) where PCRE2 answers (1,2).
# Reach: `(?:\Bx\n|x)$` takes form tagged (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S887-distance-class-blind'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='endmark'
SAB_DESC='a tagged machine'\''s class-indexed accept reads the UNION of the distance sets over every context atom'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S887.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "(?:\\Bx\\n|x)$" | grep -F "form=tagged" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static int accw_cell(const Dfa *d, int i, int cl)
{
    return d->st[i].up[upc_of_class(d, cl)].accept;
}'
SAB_AFTER='static int accw_cell(const Dfa *d, int i, int cl)
{
    if (d->tagged) { int a = 0; for (int u = 0; u < d->natoms; u++) a |= d->st[i].up[u].accept; return a; }   /* SABOTAGE S887 */
    return d->st[i].up[upc_of_class(d, cl)].accept;
}'
