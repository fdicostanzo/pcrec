#!/usr/bin/env bash
# S497 ([START-SET] stage 2; startset.md §3.4, §6.3, r3's S483) -- the
# utf8 START-BYTE ASSERTION removed (every member of S is a character start).
#
# DECLARED UNREACHED: the population is empty by construction -- the only
# start sets that hold a continuation byte are all-256 sets, which the
# `|S| < 256` conjunct (asked first, sound-F4) refuses -- and a raw
# continuation byte cannot be spelled in a utf8 pattern. The REACH probe
# compiles one; the day pcrec accepts it as a mover, this row reads NOW
# REACHED.
SAB_ID='S497-vmhat-utf8-assertion'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='vmhat'
SAB_DESC='the VM hat'\''s assertion that every start-set member is a character start under the encoding is gone; unreachable by construction'
SAB_DOC_FIGURE='UNREACHED by construction (see SAB_EXPECT_REASON); no figure is owed until the construct is reachable.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o "$REACH_TMP/o.c" --pattern "$(printf '\''\200(a)\\1'\'')" && grep -q '\''RX_VM_START_SCAN "first-class"'\'' "$REACH_TMP/o.c" && echo REACH-UTF8-CONT'
SAB_REACH_EXPECT='REACH-UTF8-CONT'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='no utf8 start set that V admits holds a continuation byte: those sets are all 256 bytes and the |S| < 256 conjunct is asked first, and a utf8 pattern cannot spell a raw continuation byte. The REACH probe compiles one and reads NOW REACHED the day it is a mover.'
SAB_COUNT=1
SAB_BEFORE='    vm_start_assert_starts(cx, ss);
    return true;'
SAB_AFTER='    /* SABOTAGE S497: the utf8 start-byte assertion removed */
    return true;'
