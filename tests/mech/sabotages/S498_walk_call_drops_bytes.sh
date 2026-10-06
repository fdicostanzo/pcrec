#!/usr/bin/env bash
# S498 ([START-SET] stage 2; startset.md §6.3, r3's S481) -- THE WALK's
# A_CALL ARM returns the empty set, non-nullable, instead of "every byte,
# nullable": a call-led pattern's S loses the callee's bytes and the seek
# skips the match. Detector (arm vmhat): vmhat.rxt's VMC block `(?1)x(y)`
# under --engine=vm (`yxy` -> (0,3)), and the differential.
SAB_ID='S498-walk-call-drops-bytes'
SAB_FILE='src/facts/startset.c'
SAB_SUITES='vmhat'
SAB_DESC='the start-set walk'\''s A_CALL arm returns the empty set (non-nullable) instead of every byte, nullable'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild2_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S498.'
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''x(?1)(y)'\'' && grep -q '\''RX_VM_START_SCAN "first-class"'\'' "$REACH_TMP/o.c" && echo REACH-CALL-VMHAT'
SAB_REACH_EXPECT='REACH-CALL-VMHAT'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_BREF:
        case A_CALL:
        case A_VAR:
            return ss_all();'
SAB_AFTER='        case A_BREF:
        case A_VAR:
            return ss_all();
        case A_CALL: {   /* SABOTAGE S498: the arm drops its bytes */
            StartSet z = ss_empty();
            z.nullable = false;
            return z;
        }'
