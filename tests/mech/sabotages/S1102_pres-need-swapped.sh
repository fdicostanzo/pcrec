#!/usr/bin/env bash
# S1102 (lane b3afix, [MEMFN] R17-b' B3a review MAJOR-2) -- the presence spans' NEED is swapped (REQUIRED where a DFA scan fronts the route, OPTIONAL on VM_ATTEMPT): answer- and byte-invisible before B3b, since no row renders the stated spans; its detector is C10 check 7 (tests/memfn/c10_presence.tsv), which lands with main's apply of docs/design/memfn/r17b_prime/b3a/proposed/c10_presence.diff
SAB_ID="S1102-pres-need-swapped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfndeleg"
SAB_DESC="the presence spans' NEED is swapped in req_pres_spans (REQUIRED off VM_ATTEMPT, OPTIONAL on it); C10 check 7 reads the stated need off the MFPRES record of each presence fixture"
SAB_REACH='test -f "$TREE/tests/memfn/c10_presence.tsv" && grep -q "the presence fixtures" "$TREE/tests/memfn/run_deleg_sites.sh" && echo REACH-C10-PRESENCE-FIXTURES'
SAB_REACH_EXPECT="REACH-C10-PRESENCE-FIXTURES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    mf_need need = site_kind_of(cx, SKS_PRE) == MF_SK_VM_ATTEMPT ? MF_REQUIRED : MF_OPTIONAL;'
SAB_AFTER='    mf_need need = site_kind_of(cx, SKS_PRE) == MF_SK_VM_ATTEMPT ? MF_OPTIONAL : MF_REQUIRED;   /* SABOTAGE S1102 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, reach:ok(1/1),memfndeleg:5fail/13pass DETECTED at ebfb5a88a)."
