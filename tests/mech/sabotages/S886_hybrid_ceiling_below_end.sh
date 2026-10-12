#!/usr/bin/env bash
# S886 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P6; docs/dev/lanes/b3build_report.md) -- on a VM hybrid the prio-const end sits one byte below the reported end, so the VM's window ceiling cuts the match
# Detector: tests/endmark/b3_rows.rxt (endmark arm): `(\s+)$` on "a  \n": group 1 is (1,4), the VM reports (1,3).
# Reach: `(\s+)$` is a VM hybrid whose inlined walk takes form tagged (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S886-hybrid-ceiling-below-end'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='endmark'
SAB_DESC='on a VM hybrid the prio-const end sits one byte below the reported end, so the VM'\''s window ceiling cuts the match'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S886.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\s+)$" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && "$PCREC" --emit-facts --features all --pattern "(\\s+)$" | grep -qF "form=tagged,prio=const0" && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "    if (revend_dist & (revend_dist - 1)) revend_end = subject_length - %d;\n",
                        cx->job->mark_prio_c);'
SAB_AFTER='        pcrec_sb_printf(c, "    if (revend_dist & (revend_dist - 1)) revend_end = subject_length - %d;\n",
                        cx->job->mark_prio_c + (cand_finish_of(cx) == CAND_ROUTE_VM));   /* SABOTAGE S886 */'
