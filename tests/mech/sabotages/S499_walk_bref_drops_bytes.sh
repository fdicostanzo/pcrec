#!/usr/bin/env bash
# S499 ([START-SET] stage 2; startset.md §6.3) -- THE WALK's A_BREF ARM
# returns the empty set, non-nullable: `(?=(a))\1b` (S = all, nullable, not a
# mover) becomes a mover with an empty S and the seek finds no start.
# Detector (arm vmhat): vmhat_walk.rxt (`ab` -> (0,2), checks-F4's witness).
# [INLINE-C] stage 1a (lane ic1a, 2026-10-26) RE-AIMED: the arm now reads the
# per-kind attribute row (src/core/kindrow.def); the anchor follows the arm's
# new text and the plant is unchanged in meaning: the backreference now shares the row-read arm (ss_row); the plant splits it out
SAB_ID='S499-walk-bref-drops-bytes'
SAB_FILE='src/facts/startset.c'
SAB_SUITES='vmhat'
SAB_DESC='the start-set walk'\''s A_BREF arm returns the empty set (non-nullable) instead of every byte, nullable'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild2_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S499.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?=(a))\1b'\'' && grep -q '\''RX_VM_PREFILTER "none"'\'' "$REACH_TMP/o.c" && echo REACH-BREF-VM'
SAB_REACH_EXPECT='REACH-BREF-VM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_BREF:
        case A_VAR:
            /* [INLINE-C] 1a: the kind ROW answers (`ss_row`): text ZERO for
             * every kind above the backreference, ANY for the two. */
            return ss_row(a, acc);'
SAB_AFTER='        case A_VAR:
            return ss_row(a, acc);
        case A_BREF: {   /* SABOTAGE S499: the arm drops its bytes */
            StartSet z = ss_empty();
            z.nullable = false;
            return z;
        }'
