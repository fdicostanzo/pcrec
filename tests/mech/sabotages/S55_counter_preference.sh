# S55 — [ENG-BREP counter-K] THE OPTIONAL PHASE'S PREFERENCE INVERTED.
#
# Greedy and lazy differ by exactly which side is the fallthrough and which is
# the pushed resume (§3.2/§3.3). A greedy iteration prefers the BODY and pushes
# the skip; flipping the pushed label to the body makes the frame resume into
# another iteration instead of out of the loop.
#
# THIS IS THE ROW THAT GUARDS A MEASURED LIVE DEFECT rather than a hypothetical.
# §3.3's whole argument is that a counter LOOP is preference-equivalent to
# `vm_opt_chain`'s NESTED optional chain and not to a CHAINED one, and the
# witness for the difference — `(?:ab|a){0,2}?b` on "abab" giving [0,2) where
# PCRE2 and python give [0,4) — is already a recorded defect in `src/ir/nfa.c`
# and in `vm_opt_chain`'s own comment. A preference bug in this rung would
# reproduce a bug the project has already paid for once.
SAB_ID="S55-counter-preference"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="counterkdiff"
SAB_DESC="the greedy optional phase pushes the body instead of the skip, inverting the backtrack preference the loop is supposed to share with the nested optional chain"
SAB_DOC_FIGURE="docs/design/counterk_impl/counterk_design.md §3.3"
SAB_COUNT=1
SAB_BEFORE='                vm_push(v, skip, "greedy: leaving the loop here is the resume");'
SAB_AFTER='                vm_push(v, bodyl, "greedy");  /* SABOTAGE S55 */'
