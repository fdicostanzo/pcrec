# S49 — [ENG-BREP] A ZERO-WIDTH ASSERTION IN THE FOLLOW TREATED AS THOUGH THE
# `$` EXEMPTION COVERED IT.
#
# eng_brep_design.md §2.5: modelling a zero-width assertion as "not in the
# follow, because it consumes nothing" is UNSOUND. `[ab]{0,4}\b` on "abc" is
# (0,0) greedy and (3,3) possessive — an assertion at a retreat position can
# succeed where it fails at the maximal exit, which is exactly what a
# first-BYTE set cannot express.
#
# End-of-subject is the ONE exemption, and it is measured rather than assumed:
# 0 of 720 diverging cells, on an upward-closure argument (it holds only at the
# top one or two positions of the subject, and a retreat moves strictly left).
# Start-of-subject is the counter-case in the same family, 80 of 240 diverging,
# because it is DOWNWARD-closed instead — a retreat CAN reach offset 0 from a
# position that is not offset 0.
#
# This sabotage extends the exemption to the assertion it does not cover, which
# is the mistake the exemption invites: it looks like a statement about
# zero-width assertions and is really a statement about which END of the
# subject the assertion pins. pcrec has no word boundary today (module
# `assertions`), so A_BOL is the whole available population and is the right
# target.
#
# RE-AIMED at [DD-11.5] P2e (lane ctxp2e, 2026-10-20): `^`/`\A` is no longer
# the kind A_BOL but the A_CTX row SUBJECT_START, and first_of decides it in
# the A_CTX arm's class switch (CTX_PIN_START). The plant gives that case the
# end pin's answer (transparent), the same mistake at its new site.
SAB_ID="S49-poss-bol-follow-ignored"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="possdiff"
SAB_DESC="start-of-subject in the follow treated as transparently as end-of-subject: the upward-closure argument behind the one measured exemption applied to an assertion it does not cover"
SAB_DOC_FIGURE="tests/possessify/run_possdiff.sh: the a{0,4}^ family diverges"
SAB_COUNT=1
SAB_BEFORE='             * `pcrec_poss_ctx_admits` never narrows it. */
        case CTX_CONTEXT:'
SAB_AFTER='             * `pcrec_poss_ctx_admits` never narrows it. */
            return fst_empty(true);  /* SABOTAGE S49 */
        case CTX_CONTEXT:'
