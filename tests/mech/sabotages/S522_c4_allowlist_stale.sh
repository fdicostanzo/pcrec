#!/usr/bin/env bash
# S522 ([MEMFN] R4c, lane r4cchecks) -- AN ALLOWLIST ROW ALLOWS MORE THAN EXISTS.
#
# C4's allowlist only descends: a row that allows more hits than the tree
# holds is STALE and red, so a removed hit cannot leave room for a new one.
# The prefix_k.c row (1 hit, the glibc measurement comment) is inflated to 2.
# Detector: C4 (arm memfnarch). SAB_REACH_POP asserts the row is there to
# inflate.
SAB_ID="S522-c4-allowlist-stale"
SAB_FILE="tests/memfn/c4_allowlist.tsv"
SAB_SUITES="memfnarch"
SAB_DESC='the C4 allowlist row for src/opt/prefix_k.c allows 2 hits where the tree holds 1: a stale row leaves room for a new hit'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S522.'
SAB_REACH_POP='tests/memfn/c4_allowlist.tsv|^code[[:space:]]+src/opt/prefix_k.c[[:space:]]+1[[:space:]]+1[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'code\tsrc/opt/prefix_k.c\t1\t1\t'
SAB_AFTER=$'code\tsrc/opt/prefix_k.c\t1\t2\t'
