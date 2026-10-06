#!/usr/bin/env bash
# S517 ([MEMFN] R4a′, lane memfnstamp) -- `memcmp` DROPPED FROM THE RECORD.
#
# integration.md §17.6's [rev4.6] row: `memcmp` dropped from MEMFN_LIBC on
# an artifact whose code calls it (the run compares' memcmp row). Separate
# from S513 because the two names reach different artifacts: memcmp only
# where a run compare is a memcmp. Detector: C11's LIBC assertion, arm
# memfnstamps. The sibling row, a non-constant `memcpy` dropped, is
# UNREACHED and not built: no corpus artifact calls memcpy with a
# non-constant length (C11's calls line reads no memcpy).
SAB_ID="S517-c11-memcmp-dropped"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfnstamps"
SAB_DESC='memcmp is dropped from the libc inventory pass: run-compare artifacts under-report'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnstamp_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S517.'
SAB_REACH='"$PCREC" -p rx -o - --pattern "abcdefghq" | grep -o "RX_MEMFN_LIBC \"memchr,memcmp\""'
SAB_REACH_EXPECT='RX_MEMFN_LIBC "memchr,memcmp"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    "memchr", "memcmp", "memcpy", "memmove", "memset", "strcat", "strchr",'
SAB_AFTER='    "memchr", "memcpy", "memmove", "memset", "strcat", "strchr", /* SABOTAGE S517 */'
