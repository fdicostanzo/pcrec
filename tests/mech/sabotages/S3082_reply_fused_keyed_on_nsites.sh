#!/usr/bin/env bash
# S3082 ([MEMFN] plan_frame.md 3.0b, row (H); lane b30b) -- REPLY FUSED KEYED ON NSITES.
#
# WHAT IT BREAKS AND WHO CATCHES IT: the reply's fused is keyed on the art's site count (FN iff nsites > 0, 1d's plant pattern): the purity harness's whole-reply memcmp after interleaved defines is red and its hex-dump control moves.
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3082-reply-fused-keyed-on-nsites"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the reply'"'"'s fused is keyed on the art'"'"'s site count (FN iff nsites > 0, 1d'"'"'s plant pattern): the purity harness'"'"'s whole-reply memcmp after interleaved defines is red and its hex-dump control moves'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 88 failed, traced 1323. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3082.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        fp->fused = MF_WFUSED_NO;
        fp->search = r == E_FIND ? wsearch_of(fx->pick) : MF_WSEARCH_NONE;'
SAB_AFTER='        fp->fused = art->nsites > 0 ? MF_WFUSED_FN : MF_WFUSED_NO;   /* SABOTAGE S3082 */
        fp->search = r == E_FIND ? wsearch_of(fx->pick) : MF_WSEARCH_NONE;'
