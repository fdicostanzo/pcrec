#!/usr/bin/env bash
# S500 ([START-SET] stage 2; startset.md §6.3) -- THE WALK's A_VAR ARM
# returns the empty set, non-nullable: `${v}x` (S = all, nullable, not a
# mover) becomes a mover with an empty S and the seek finds no start.
# Detector (arm vars): tests/vars/startset.rxt, under that directory's own
# libpcre2-splice oracle (`zzax` with v = a -> (2,4)).
SAB_ID='S500-walk-var-drops-bytes'
SAB_FILE='src/facts/startset.c'
SAB_SUITES='vars'
SAB_DESC='the start-set walk'\''s A_VAR arm returns the empty set (non-nullable) instead of every byte, nullable'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild2_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S500.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''${v}x'\'' && grep -q '\''RX_VM_PREFILTER "none"'\'' "$REACH_TMP/o.c" && echo REACH-VAR-VM'
SAB_REACH_EXPECT='REACH-VAR-VM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_BREF:
        case A_CALL:
        case A_VAR:
            return ss_all();'
SAB_AFTER='        case A_BREF:
        case A_CALL:
            return ss_all();
        case A_VAR: {   /* SABOTAGE S500: the arm drops its bytes */
            StartSet z = ss_empty();
            z.nullable = false;
            return z;
        }'
