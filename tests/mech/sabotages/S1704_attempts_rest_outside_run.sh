#!/usr/bin/env bash
# S1704 ([REQRUN-VM], lane reqvm1) -- THE RE-ENTRY ADMITS A PART OUTSIDE THE
# RUN. `handoff-attempts` re-asks the whole pre-check after each failed
# attempt, which stays linear only where every other part is a byte or slice
# of the whole run; the plant drops that conjunct, so `(ab)c?userpass` (its
# set-rest bytes `a`/`b` are not in the run `userpass`) re-enters and rescans
# at every re-find. (Re-aimed, lane sar1reach: since R1 a repeat is its copies,
# so `x{2,5}(?i:cat)`'s run `xxCAT` holds `x` and is a re-entry row unplanted.) NO ANSWER MOVES (the re-ask is sound, only its cost is not bounded),
# so the attempt-loop section of tests/memfn/run_handoff_reach.sh, which pins
# that witness to the entry-only row, is the detector (arm memfnreach).
# RE-AIMED 2026-11-12 (lane reqpast, [REQ-PAST-LAST]): the reach floor reads
# 7 >= 6 (`a+xyz` and `[^@ ]+@x` are the unbounded row's witnesses now).
SAB_ID='S1704-attempts-rest-outside-run'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='the VM attempt loop re-enters the handoff where a pre-check part is not a byte of the whole run, so each re-find may rescan the subject'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1704.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='attempt-loop reach floor: 7 >= 6
(ab)c?userpass (byte): reaches the attempt loop'\''s entry row'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return req_handoff_entry_applies(s) && req_parts_in_whole(s->cx);'
SAB_AFTER='    return req_handoff_entry_applies(s);   /* SABOTAGE S1704 */'
