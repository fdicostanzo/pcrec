#!/usr/bin/env bash
# S486 ([START-SET] stage 3; docs/design/startset.md §6.3, r3's S480) -- THE
# DFA HAT'S T WIDENED BY ONE BYTE that cannot begin a match: the lowest byte of
# E \ S joins the scanned set after the re-seed premise guard has passed. Sound
# (a wider skip set only stops more often) and answer-invisible; the cost
# regression firstset §9 names.
#
# Detector (arm dfahat): [dfa-table] -- on every mover the scanned set EQUALS
# the `start_set` fact (`--emit-facts`) and is a PROPER subset of the deny
# arm's E (the expectation rev 2 corrected: r3's "S ∩ the deny table" pinned
# the sound-F1 defect); and [dfa-wit] (aws, |T| = 1, is no longer the memchr
# form).
SAB_ID='S486-dfahat-t-widened'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahatstruct'
SAB_DESC='the DFA hat'\''s scanned set gains one byte of E outside S after the re-seed premise guard (sound, a cost regression)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S486.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\b((?:A3T[A-Z0-9]|AKIA|AGPA)[A-Z0-9]{16})\b'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-memchr-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-AWS-MOVER'
SAB_REACH_EXPECT='REACH-AWS-MOVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                       "seed (startset.md §6.4.3 item 2)");
    cand_derive(t, tv, 0);'
SAB_AFTER='                       "seed (startset.md §6.4.3 item 2)");
    for (int b = 0; b < 256; b++) if (u->cand.set[b] && !tv[b]) { tv[b] = 1; break; }   /* SABOTAGE S486 */
    cand_derive(t, tv, 0);'
