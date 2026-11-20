#!/usr/bin/env bash
# S3355 (review r53 F1, lane l1fix 2026-11-19; docs/design/span_arms.md §14.3 D-9, RM-6) -- THE NEGATIVE-LOOKAROUND NEVER OVERRIDE IS DROPPED: `pcrec_ast_row` no longer picks NEVER = NO for a negative `A_LOOK`, so it reads the kind row's BODY and a negative lookaround of a never body reads never (it always holds). The split derivation then prunes the arm `(?!^)b$` of `^a|(?!^)b$` once its `^` is killed, and Q reads never where the twin derives `b$`.
# Detector: test-compound's B2 (tests/compound/check_derive.py) on the twin case `hand4:r53negnever` (docs/design/compound/twin/results/cases2_owed.tsv). The pattern is not an admitted compound (it routes RX_COMPOUND "none"), so no answer suite sees it: B2 compares the derivation directly.
# HAND-MEASURED by lane l1fix 2026-11-19 (plant on a scratch export of the lane tip, B2 alone): `FAIL: hand4:r53negnever byte b'^a|(?!^)b$': never disagrees: twin False, build True`, 1 failure of 115 cases; unplanted: 115 cases, 0 failures.
SAB_ID='S3355-never-neg-look-override-dropped'
SAB_FILE='src/core/internal.h'
SAB_SUITES='compound'
SAB_DESC='pcrec_ast_row reads a negative lookaround'\''s NEVER as the kind row'\''s BODY, so a negative lookaround of a never body reads never and the split derivation prunes a live arm'
SAB_DOC_FIGURE='HAND-MEASURED by lane l1fix 2026-11-19: B2 1 failure (hand4:r53negnever, never disagrees); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3355.'
SAB_REACH_POP='docs/design/compound/twin/results/cases2_owed.tsv|^hand4:r53negnever[[:space:]]byte[[:space:]]5e617c283f215e296224[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (a->k == A_LOOK && a->u.look.neg) r.never = KNEVER_NO;'
SAB_AFTER='    /* SABOTAGE S3355: the negative-lookaround NEVER override dropped */'
