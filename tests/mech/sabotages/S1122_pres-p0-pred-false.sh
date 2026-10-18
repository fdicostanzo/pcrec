#!/usr/bin/env bash
# S1122 (lane b3bfix, 2026-10-18; id allocated by main). [MEMFN] R17-b' B3b, b3brev
# finding 5 -- THE P0-PREDICATE-FALSE SUBSTITUTION. P0's predicate never holds
# (its required facts gain one no presence span carries), so a REQUIRED span
# falls through P3 (whose gate declines REQUIRED) to P9, whose link is P0's
# exact shape (verify, the whole run, every member): every artifact is
# byte-identical and no answer moves. Only the DECIDING ROW tells, which pcrec
# now records from the kit's mf_class.pres_row instead of inferring it from
# the link (b3brev U5; the old inference read need == REQUIRED as P0 and
# could not see this). Reaches the non-DFA route only. Detectors: the kit's
# finder check (fd-P0 decides P9; hand-measured finder_check 3 failed / 946
# passed), the row manifest (make test-memfn-rows: fd/P0's witness row NOT
# chosen, 1 failed / 237 passed; no mech arm runs it) and, in the heavy chain,
# the routed census (P0's VM_ATTEMPT cells under their floor).
SAB_ID="S1122-pres-p0-pred-false"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the PRES row P0's predicate never holds, so P9 decides every REQUIRED presence span with P0's own link shape: byte-identical artifacts, only the deciding row moves (b3brev U5)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "P0", FD_PRES, KN_P, SF_REQUIRED, 0, { { FL_NONE, NULL, 0, NULL, NULL } },'
SAB_AFTER='    { "P0", FD_PRES, KN_P, SF_REQUIRED | SF_SPAN0, 0, { { FL_NONE, NULL, 0, NULL, NULL } },   /* SABOTAGE S1122 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3bfix on the planted tree: make test-memfn-finder finder_check 3 failed / 946 passed (fd-P0 decided P9); see docs/dev/lanes/b3b_report.md section 8."
