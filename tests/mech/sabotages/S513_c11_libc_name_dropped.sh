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
#
# RE-AIMED 2026-10-08 ([MEMFN] M7, lane m7; RULED Q-R8-7): M7's rider deleted
# the dead "memchr" entry this row planted (its equivalence above), so the row
# now drops a name pcrec's OWN text still calls: `strlen`, the `${...}`
# variable resolver's. A hand plant showed C11's quick arm reaches it (its
# sample compiles `^${v}$` and `^${v:-\xff}$`, whose objects call strlen),
# so the row is a live detector again, not retired. Intent unchanged: the
# producer drops one name and MEMFN_LIBC under-reports.
SAB_ID="S513-c11-libc-name-dropped"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfnstamps"
SAB_DESC='strlen is dropped from the libc inventory pass: MEMFN_LIBC under-reports on a variable artifact while the object still calls strlen'
SAB_DOC_FIGURE="RE-AIMED and HAND-MEASURED by lane m7 2026-10-08 (plant applied, tree rebuilt): memfnstamps 2 failed / 8 passed (C11 quick: the two vars cells). Before the re-aim: MEASURED UNDETECTED 2026-10-08 (slot11), an equivalent mutant on memchr after M4. The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "a\${v}b" | grep -o "RX_MEMFN_LIBC \"memchr,memcmp,strlen\""'
SAB_REACH_EXPECT='RX_MEMFN_LIBC "memchr,memcmp,strlen"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    "strcmp", "strcoll", "strcpy", "strcspn", "strerror", "strlen", "strncat",'
SAB_AFTER='    "strcmp", "strcoll", "strcpy", "strcspn", "strerror", "strncat", /* SABOTAGE S513 */'
