#!/usr/bin/env bash
# S514 ([MEMFN] R4a′, lane memfnstamp) -- THE PRODUCER LISTS AN EXTRA NAME.
#
# Q53's "a producer that lists an extra name": the finishing pass notes
# `strlen` on every artifact, whether or not its text calls it. Detector:
# C11's LIBC assertion, arm memfnstamps (the compiled object of a
# memchr-only artifact has no undefined strlen).
SAB_ID="S514-c11-libc-name-extra"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfnstamps"
SAB_DESC='every artifact notes strlen in MEMFN_LIBC, called or not: the record over-reports'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnstamp_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S514.'
SAB_REACH='"$PCREC" -p rx -o - --pattern "a(b|c)+d" | grep -o "RX_MEMFN_LIBC \"memchr\""'
SAB_REACH_EXPECT='RX_MEMFN_LIBC "memchr"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-06 ([MEMFN] R4c, lane r4ccore): the stamp pass no longer
# ends the art in this expression (pcrec_memfn_art_end follows it); the
# anchor is the mf_stamps call alone. Intent unchanged.
SAB_BEFORE='             mf_stamps(art, &sink);'
SAB_AFTER='             mf_art_note_libc(art, "strlen") || /* SABOTAGE S514 */
             mf_stamps(art, &sink);'
