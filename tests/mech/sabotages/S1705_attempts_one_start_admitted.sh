#!/usr/bin/env bash
# S1705 ([REQRUN-VM], lane reqvm1) -- THE ONE-ATTEMPT DECLINE IS DROPPED. A
# pattern whose attempt loop runs one attempt (`^`, `\A`, a `\G` start) has
# nothing to skip; the plant admits it. NO ANSWER MOVES (moving the one
# attempt later than startpos happens only where no match is at startpos), so
# the decline pin of tests/memfn/run_handoff_reach.sh is the detector (arm
# memfnreach): `^(?:ab|x)cdef`, whose pre-check IS emitted (`^abcd` and
# `\Gabcd` decline earlier, at the admission's `one-attempt` row), reads
# RX_REQ_HANDOFF "none".
SAB_ID='S1705-attempts-one-start-admitted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='the VM attempt loop handoff is admitted on a one-attempt pattern (^, \A, \G start)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1705.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: ^(?:ab|x)cdef (byte): declined (RX_REQ_HANDOFF none)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (CAND_BOUND_ONE(CAND_SLOT_FIRST, &vs, "handoff-attempts")) return false;'
SAB_AFTER='    (void)vs;   /* SABOTAGE S1705: one attempt admitted */'
