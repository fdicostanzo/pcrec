#!/usr/bin/env bash
# S525 ([MEMFN] R4c, lane r4cchecks) -- THE VOCABULARY STOPS SEEING memchr.
#
# C12's other failure direction: the ceiling is a ratchet, so a lexer or
# vocabulary that stops seeing a form reads as every memchr row STALE (counted
# 0 against a ceiling of 8), never as a quiet pass. The libc-call line loses
# `memchr` from its alternation. Detector: C12 (arm memfnforms); C17's rule 4
# goes red beside it. SAB_REACH_POP: the alternation is there to edit.
SAB_ID="S525-c12-vocab-loses-memchr"
SAB_FILE="tests/memfn/search_vocab.tsv"
SAB_SUITES="memfnforms"
SAB_DESC='search_vocab.tsv libc-call line loses memchr: C12 counts 0 against a ceiling of 8'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S525.'
SAB_REACH_POP='tests/memfn/search_vocab.tsv|[(][?]:memchr[|]memrchr[|]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='(?:memchr|memrchr|'
SAB_AFTER='(?:memrchr|'
