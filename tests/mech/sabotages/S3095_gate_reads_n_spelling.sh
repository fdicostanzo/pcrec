#!/usr/bin/env bash
# S3095 ([MEMFN] plan_frame.md 3.0b, row (AD); lane b30b) -- GATE READS N SPELLING.
#
# WHAT IT BREAKS AND WHO CATCHES IT: a gate class reads n's spelling beyond its class (n spelled `len` is OTHER): the same-class-different-text fixture (STMT sites asked with EMIT, every text hook renamed within its class) moves the PF site's frame row and is red.
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3095-gate-reads-n-spelling"
SAB_FILE="memfn/src/gate.c"
SAB_SUITES="memfnfinder"
SAB_DESC='a gate class reads n'"'"'s spelling beyond its class (n spelled `len` is OTHER): the same-class-different-text fixture (STMT sites asked with EMIT, every text hook renamed within its class) moves the PF site'"'"'s frame row and is red'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 2 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3095.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static int cl_n(const gate_in *in)  { return ident_or_other(in->h ? in->h->n : NULL); }'
SAB_AFTER='static int cl_n(const gate_in *in)  { return in->h && in->h->n && !strcmp(in->h->n, "len") ? CL_OTHER : ident_or_other(in->h ? in->h->n : NULL); }   /* SABOTAGE S3095 */'
