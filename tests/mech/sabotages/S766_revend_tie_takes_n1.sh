#!/usr/bin/env bash
# S766 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- a tie takes end n-1 without the anchored run.
# Detector: the answer net's greedy ties: `\s*$` on " \n" is (0,2), `\s+$` on "a \n".
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# a tie of a `tagged` walk is FINISH's `prio-const` where mark_prio is a
# constant; the plant takes n-1 instead (c := 1): `\s+$` (const0) on "a \n".
SAB_ID='S766-revend-tie-takes-n1'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='a tie takes end n-1 without the anchored run'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S766.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\s+$" | grep -F "prio=const0" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "    if (revend_dist & (revend_dist - 1)) revend_end = subject_length - %d;\n",
                        cx->job->mark_prio_c);'
SAB_AFTER='        pcrec_sb_printf(c, "    if (revend_dist & (revend_dist - 1)) revend_end = subject_length - %d;\n",
                        1 + 0 * cx->job->mark_prio_c);   /* SABOTAGE S766 */'
