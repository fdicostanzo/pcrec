#!/usr/bin/env bash
# S513 ([MEMFN] R4a′, lane memfnstamp) -- THE PRODUCER DROPS A LIBC NAME.
#
# integration.md §17.6's rows "`MEMFN_LIBC` forced to `none` on an artifact
# that calls `memchr`" and Q53's "a producer that drops one name": `memchr`
# leaves the finishing pass's recogniser (src/gen/memfn_stamps.c
# `libc_names`), so every memchr-calling artifact under-reports and a
# memchr-only one reads "none". Detector: C11's LIBC assertion (names from
# `nm -u` of the compiled object), arm memfnstamps.
SAB_ID="S513-c11-libc-name-dropped"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfnstamps"
SAB_DESC='memchr is dropped from the libc inventory pass: MEMFN_LIBC under-reports (a memchr-only artifact reads "none") while the object still calls memchr'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnstamp_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S513.'
SAB_REACH='"$PCREC" -p rx -o - --pattern "a(b|c)+d" | grep -o "RX_MEMFN_LIBC \"memchr\""'
SAB_REACH_EXPECT='RX_MEMFN_LIBC "memchr"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    "memchr", "memcmp", "memcpy", "memmove", "memset", "strcat", "strchr",'
SAB_AFTER='    "memcmp", "memcpy", "memmove", "memset", "strcat", "strchr", /* SABOTAGE S513 */'
