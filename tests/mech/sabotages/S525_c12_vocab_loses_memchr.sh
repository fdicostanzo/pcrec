#!/usr/bin/env bash
# S525 ([MEMFN] R4c, lane r4cchecks) -- THE VOCABULARY STOPS SEEING memchr.
#
# C12's other failure direction: the ceiling is a ratchet, so a lexer or
# vocabulary that stops seeing a form reads as every memchr row STALE (counted
# 0 against a ceiling of 2), never as a quiet pass. The libc-call line loses
# `memchr` from its alternation. Detector: C12 (arm memfnforms); C17's rule 4
# goes red beside it. SAB_REACH_POP: the alternation is there to edit;
# SAB_REACH: the clean tree's memchr rows sit at their ceiling and every form
# check passes (`checks failed: 0`, as its siblings S526/S527).
SAB_ID="S525-c12-vocab-loses-memchr"
SAB_FILE="tests/memfn/search_vocab.tsv"
SAB_SUITES="memfnforms"
SAB_DESC='search_vocab.tsv libc-call line loses memchr: since M4 no C12 ceiling row counts memchr, so the expected verdict is UNDETECTED (an equivalent-mutant tripwire)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S525. MEASURED UNDETECTED 2026-10-08 (slot11, lane/memfn-m4 @ 32197d74, Linux): reach ok, pop 1, memfnforms 0fail/4pass. EQUIVALENT MUTANT SINCE M4 ([MEMFN] R-7, a3d65a59): the emit_dfa.c memchr row left tests/memfn/c12_ceilings.tsv with the last pcrec-spelled memchr, so no C12 group counts memchr and a vocabulary blind to it changes nothing C12 checks. Re-pinned UNDETECTED (EXPECTED); a TRIPWIRE that reads DETECTED if a memchr ceiling row returns. A NEW memchr( outside the kit is S524s row. Triage: worktrees/memfn-slot/slot11/S525_triage.md (lane s525tri).'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_form_checks.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: C12: every group is at its ceiling
checks failed: 0'
SAB_REACH_POP='tests/memfn/search_vocab.tsv|[(][?]:memchr[|]memrchr[|]|1'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='(?:memchr|memrchr|'
SAB_AFTER='(?:memrchr|'
