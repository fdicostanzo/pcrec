# S99 — [M6.4.2] THE LIFT ACCEPTS A LAZY BODY (CARVE-OUT TWO REMOVED).
#
# R31's re-check finding N1, as a row, and it is the SECOND time the same claim
# was refuted the same way. The possessive rungs are GREEDY-ONLY BY SIGNATURE —
# `vm_opt_chain` takes `bool greedy`; `vm_poss_chain`, `vm_poss_star` and
# `vm_counter_poss_opt` do not and never read it; `vm_cursor_rep`'s possessive
# scan is unconditionally maximal — because `emit_vm.c:2053-2062` argues the
# PREFERENCE COLLAPSE as a §2.2 CONSEQUENCE: under disjointness a greedy loop
# tops out by preference and a LAZY one is FORCED to the same top. A
# USER-WRITTEN possessive deletes that antecedent.
#
# MEASURED before the carve-out existed: 7 of 8 lift-eligible lazy cells
# MISCOMPILE, three of them the design's own §6 table rows 14, 15 and 16.
#
#     (?>a*?)b   on "aaab"   both oracles (3,4)   through the lift (0,4)
#     (?>a*?)a   on "aaa"    both oracles (0,1)   through the lift nomatch
#     (?>a+?)b   on "aaab"   both oracles (2,4)   through the lift (0,4)
#
# ITS GREEDY WITNESSES STAY GREEN, which is why `[M6.4-ATOMIC rule 5]` drives
# BOTH preferences on every dispatch path: a per-path check with only the
# greedy column would be green on exactly this row.
SAB_ID="S99-lift-accepts-lazy"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_quant.rxt"
SAB_DESC="vm_lifts drops its greedy condition, so a LAZY A_REP under an A_ATOMIC is routed onto the possessive rungs whose shape ignores preference. '(?>a*?)b' on \"aaab\" then answers (0,4) where both oracles give (3,4): the cut must commit to the LAZY choice, which is EMPTY, so the match starts at 3"
SAB_DOC_FIGURE="PREDICTED: the lazy-inside corpus RED (tests/atomic_groups/atomic_quant.rxt section 4), codegen rule 5's LAZY witnesses RED with its GREEDY witnesses GREEN -- that asymmetry is why the per-path check needs both columns. Canonical figure owed from run_sabotage_matrix.sh S99."
SAB_COUNT=1
SAB_BEFORE='    if (!r->u.rep.greedy)        return false;   /* carve-out TWO  (§3.2.2a) */'
SAB_AFTER='    /* SABOTAGE S99: carve-out two removed */'
