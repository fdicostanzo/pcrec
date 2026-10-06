#!/usr/bin/env bash
# S479 ([START-SET] stage 2, D148 addendum 2 Q-R5) -- THE VM HAT's ONE-BYTE
# (`memchr`) FORM starts its seek one byte late.
#
# DECLARED UNREACHED: Q-R5 ruled the TABLE form only at stage 2, so no
# VM-route row takes a `memchr` form, and `pcrec_emit_vm_start_seek` fails the
# compile with an internal error if one ever does (its assertion is this row's
# guard). The plant marks that assertion's prose; the REACH probe compiles a
# one-byte-S VM-hat pattern and greps for a `memchr` seek, so the day the form
# is built this row reads NOW REACHED and must be re-aimed at its offset.
SAB_ID='S479-vmhat-memchr-seek-late'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='vmhat'
SAB_DESC='the VM hat'\''s memchr form seeks from one byte past the attempt position; unreachable while the VM hat emits the table form only (Q-R5)'
SAB_DOC_FIGURE='UNREACHED by construction (see SAB_EXPECT_REASON); no figure is owed until the construct is reachable.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(ab)\1'\'' && grep -q '\''memchr(subject + attempt_position'\'' "$REACH_TMP/o.c" && echo REACH-VM-MEMCHR'
SAB_REACH_EXPECT='REACH-VM-MEMCHR'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='Q-R5 (D148 addendum 2) ships the VM hat'\''s table form only: no VM-route row takes a memchr form, and pcrec_emit_vm_start_seek refuses one with an internal error. The REACH probe looks for a memchr seek on a one-byte-S mover; it reads NOW REACHED the day the form is built.'
SAB_COUNT=1
SAB_BEFORE=' *   - THE TABLE FORM ONLY (Q-R5): no VM-route row may take a `memchr` form at'
SAB_AFTER=' *   - [SABOTAGE S479: marked] THE TABLE FORM ONLY (Q-R5): no VM-route row may take a `memchr` form at'
