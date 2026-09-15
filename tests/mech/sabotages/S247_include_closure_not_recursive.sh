# S247 — [DD-13b.W23.3a] `include`'s CLOSURE WALK STOPS AT DEPTH ONE.
#
# `rxt_expand_closure`'s own recursive call — the line that makes the walk
# follow a FRAGMENT's own `include` lines, not only the entry's — is
# deleted. A fragment's OWN nested includes are then silently never
# spliced: the walk records the fragment itself (`rxt_expansion+=("$_n")`
# still runs) and simply never asks whether THAT file has includes of its
# own.
#
# THIS IS THE PLANT THAT PROVES `W23-S7` NEEDS THE NESTED FIXTURE AND NOT
# ONLY THE FLAT ONE (§1.10's own "in include order, DEPTH FIRST", format_
# design.md §2.5). A check built only from `include_basic.rxtin` (one
# fragment, no nesting) cannot see this: `include_basic`'s own closure has
# nothing at depth two to lose, so it stays green under this plant. Only
# `include_nested.rxtin` — whose first fragment includes a second — goes
# from `fragments spliced: 2` to `fragments spliced: 1`, silently dropping
# `include_nested_frag2.rxtfrag`'s own `leaf` pattern and its case.
#
# THE CORPUS ARM STAYS GREEN, AND THAT IS THE POINT (§6.3a's own
# acceptance line): the shipped corpus has zero `include` lines, so there
# is nothing at depth one for this plant to touch depth two of. A plant
# that turned the CORPUS control red too would not distinguish "the
# closure walk lost its recursion" from "the subtraction pass broke" —
# W23-S7's fixture arm and corpus arm are two different questions and this
# row is scoped to answer only the first.
SAB_ID="S247-include-closure-not-recursive"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="rxtsource"
SAB_DESC="rxt_expand_closure's own recursive call is deleted, so a fragment's OWN nested include lines are never followed -- the walk stops at depth one and silently drops every fragment reachable only through another fragment"
SAB_DOC_FIGURE="docs/design/dd13_format/w23_impl.md REVISION 1.1 sec1.10.2 rule 4 (depth first); sec3.1's W23-S7 row; docs/dev/lanes/w233a_report.md sec3 item 3 -- expected: include_nested's own W23-S7 checks (leg B fragments-spliced and cases-passed) turn red, include_basic's and the corpus control stay green"
SAB_COUNT=1
# REACH: the row rests on `rxt_expand_closure` still being the ONE
# function `run.sh` uses to walk a closure, called recursively. If a
# future rewrite stops calling itself by this name the plant has nothing
# to delete and must score UNREACHED rather than pass.
SAB_REACH='grep -c "rxt_expand_closure \"\$_n\" \"\$seen\" || return 1" "$TREE/tests/harness/run.sh"'
SAB_REACH_EXPECT='1'
SAB_BEFORE='        assoc_set "$seen" "$_n" 1
        rxt_expansion+=("$_n")
        rxt_expand_closure "$_n" "$seen" || return 1'
SAB_AFTER='        assoc_set "$seen" "$_n" 1
        rxt_expansion+=("$_n")
        # SABOTAGE S247: the recursive call is gone -- this file'"'"'s OWN
        # include lines are never followed, only recorded.'
