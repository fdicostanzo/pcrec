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
SAB_DOC_FIGURE="RE-ANCHORED and HAND-MEASURED by lane m7 2026-10-08 (plant applied, tree rebuilt): memfnstamps 2 failed / 8 passed (C11 quick: the vars cells read LIBC strlen while the object calls memcmp,strlen). NOT an equivalent mutant: a variable compare is pcrec text calling memcmp. The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx -o - --pattern "abcdefghq" | grep -o "RX_MEMFN_LIBC \"memchr,memcmp\""'
SAB_REACH_EXPECT='RX_MEMFN_LIBC "memchr,memcmp"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-ANCHORED 2026-10-08 ([MEMFN] M7, lane m7): the M7 rider deleted the
# dead "memchr" entry from this line (S513's equivalence), so the anchor is
# the line as it now reads. Intent unchanged.
SAB_BEFORE='    "memcmp", "memcpy", "memmove", "memset", "strcat", "strchr",'
SAB_AFTER='    "memcpy", "memmove", "memset", "strcat", "strchr", /* SABOTAGE S517 */'
