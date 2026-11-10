#!/usr/bin/env bash
# S2992 -- span_pick unit 3.0a (docs/design/memfn/plan_frame.md rev 2.2 §5 row (Q), [rev2 F5]; lane s30a).
# THE LIBC UNION OVER TWO PIECES: E-find's libc and include facts read the SEARCH and STREAM rows only, so a
# B-walk or B-hors site whose CHECK has run compares (memcmp row, memcpy word loads, runcmp.c) reports
# libc_free 1 and no <string.h>.
#
# Plant: wf_find_prepare's union drops the check renderer row's term (`libc_runs && nrun`).
# Detector: none today, measured. The design names emit_sweep on `--memfn=no-fd-d1 abcdef` and the reply-class
# pin; lane s30a planted it by hand (build, then base vs HEAD on 12 patterns x 4 arms, the witness among them,
# and tests/memfn/run_finder.sh): NO byte moves and the finder suite stays green. pcrec's artifact includes
# <string.h> on its own (memfn_sites.c adds the kit's include only where the job lacks it) and its
# RX_MEMFN_LIBC stamp reads `none` on both sides; the class's libc_free is read by pcrec only in
# cand_class_eq (ask vs define, both from this one plan); arm_fixtures --query's independent libc reading
# greps the text for `memchr(`/`memcmp(` alone, and the witness's run compare loads words by `memcpy`.
# RE-ANCHORED at the r1 s30a review fixes (lane s30arev): the union is one function's return over the three
# pieces (`pieces_libc`, E-find and the floor), read by both; intent unchanged.
# What would close it: an independent libc reading that counts `memcpy(` too, over a B-walk fixture with a
# run term (plan_frame.md 3.0a deviation, lane report).
SAB_ID="S2992-wf-libc-union-two-pieces"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='E-find'"'"'s libc union reads the search and stream rows only (the check'"'"'s run compares dropped): libc_free 1 on a B-walk site with run compares'
SAB_DOC_FIGURE='MEASURED UNDETECTED 2026-11-09 BY HAND after the re-aim, planted by hand on a git archive of lane/memfn-s30a c8d54df7c (lane s30arev, review r1 s30a fixes), built with nice make -j2; 15 patterns x 4 arms compiled by the planted and the clean pcrec and classed: SAME 60 (the witness --memfn=no-fd-d1 abcdef among them); memfnfinder 0fail/3316pass. Earlier: lane s30a 2026-11-07, the same. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S2992.'
SAB_EXPECT=UNDETECTED
SAB_EXPECT_REASON='no reader sees libc_free on a window site: pcrec includes <string.h> itself, RX_MEMFN_LIBC is none on both sides, and arm_fixtures --query reads only memchr(/memcmp( (the run compare loads by memcpy)'
SAB_COUNT=1
SAB_BEFORE='    return (uint8_t)((w->srch && w->srch->libc) || w->strm->libc || (w->chk->libc_runs && w->nrun));'
SAB_AFTER='    return (uint8_t)((w->srch && w->srch->libc) || w->strm->libc);   /* SABOTAGE S2992 */'
