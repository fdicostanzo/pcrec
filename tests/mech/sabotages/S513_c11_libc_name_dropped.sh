#!/usr/bin/env bash
# S513 ([MEMFN] R4a′, lane memfnstamp) -- THE PRODUCER DROPS A LIBC NAME.
#
# integration.md §17.6's rows "`MEMFN_LIBC` forced to `none` on an artifact
# that calls `memchr`" and Q53's "a producer that drops one name": `memchr`
# leaves the finishing pass's recogniser (src/gen/memfn_stamps.c
# `libc_names`), so every memchr-calling artifact under-reports and a
# memchr-only one reads "none". Detector: C11's LIBC assertion (names from
# `nm -u` of the compiled object), arm memfnstamps.
#
# EQUIVALENT MUTANT SINCE M4 ([MEMFN] R-7, a3d65a59, 2026-10-08): the last
# pcrec-spelled `memchr(` (emit_attempt's (?m)^ skip) moved into the kit's
# pf_memchr_back row, and every kit row that calls memchr notes the name
# itself (mf_art_note_libc). The recogniser's memchr entry is now redundant,
# so dropping it changes no stamp: UNDETECTED is the expected verdict. The
# row stays as a TRIPWIRE: it reads DETECTED again the day pcrec spells a
# memchr call of its own (S524 is the row that catches that text appearing).
# Triage: worktrees/memfn-slot/slot11/S513_triage.md (lane s513tri).
SAB_ID="S513-c11-libc-name-dropped"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfnstamps"
SAB_DESC='memchr is dropped from the libc inventory pass: MEMFN_LIBC under-reports (a memchr-only artifact reads "none") while the object still calls memchr'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnstamp_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S513. MEASURED UNDETECTED 2026-10-08 (slot11, lane/memfn-m4 @ 32197d74, Linux): reach ok 1/1, memfnstamps 0fail/9pass -- an equivalent mutant after M4 (see header); re-pinned UNDETECTED (EXPECTED).'
SAB_REACH='"$PCREC" -p rx -o - --pattern "a(b|c)+d" | grep -o "RX_MEMFN_LIBC \"memchr\""'
SAB_REACH_EXPECT='RX_MEMFN_LIBC "memchr"'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='    "memchr", "memcmp", "memcpy", "memmove", "memset", "strcat", "strchr",'
SAB_AFTER='    "memcmp", "memcpy", "memmove", "memset", "strcat", "strchr", /* SABOTAGE S513 */'
