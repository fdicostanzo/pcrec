#!/usr/bin/env bash
# S515 ([MEMFN] R4a′, lane memfnstamp) -- THE IDIOM-MEMCPY EXCLUSION BROKEN.
#
# Q53: a `memcpy` of a constant 1-8 bytes is a register load and is NOT in
# the record. The plant narrows the producer's range to 1-2, so the run
# compare's 4- and 8-byte word loads (runcmp.c's `<p>_wN` helpers) are
# recorded as `memcpy` calls. Detector: C11's LIBC assertion, arm
# memfnstamps; its control applies the same rule through the COMPILER (a
# prelude routes constant 1-8 byte memcpys to c11_idiom_memcpy), so the
# object shows no memcpy. Reach: an artifact with a 4-byte word load whose
# record omits memcpy.
SAB_ID="S515-c11-idiom-exclusion-broken"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfnstamps"
SAB_DESC='the idiom-memcpy exclusion stops at 2 bytes: 4- and 8-byte word loads are recorded as memcpy calls'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnstamp_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S515.'
SAB_REACH='"$PCREC" -p rx -o - --pattern "x(a|b)abcdefg" | grep -o -e "memcpy(&w, p, 4)" -e "RX_MEMFN_LIBC \"memchr\""'
SAB_REACH_EXPECT='memcpy(&w, p, 4)
RX_MEMFN_LIBC "memchr"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return skip_space(t, len_end, d) == len_end && v >= 1 && v <= 8;'
SAB_AFTER='    return skip_space(t, len_end, d) == len_end && v >= 1 && v <= 2; /* SABOTAGE S515 */'
