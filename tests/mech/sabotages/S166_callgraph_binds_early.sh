# S166 ([DD-14] wave B+C; wave A2's PASS-ORDERING FINDING, commit 513de65) --
# `u.call.body` IS BOUND OVER THE FINAL TREE.
#
# THE FINDING THE SWITCH CENSUS COULD NOT SEE, and it is wave A2's rather than
# the design's: `subroutines_design.md` does not address it anywhere. `.body`
# is filled by the end-of-parse resolution pass, and TWO LATER PASSES REBUILD
# NODES rather than mutating them --
#
#   `pcrec_altcls`             `altcls_walk`'s A_REP/A_CAP arms do
#                              `*r = *a; r->l = body;`, and stages 1 and 2
#                              rebuild spines and merge branches into a FRESH
#                              `A_CLASS`. On `((?:a|b))(?1)` the tree's group 1
#                              becomes a NEW `A_CAP` over `[ab]`.
#   `pcrec_discharge_atomic`   SPLICES an `A_ATOMIC` out.
#
# -- so a pointer captured at resolution can name a subtree that is no longer
# in the tree, and under `CALL_LINKAGE` the callee REGION is then emitted from
# the stale subtree while the LEXICAL occurrence comes from the new one.
#
# WAVE B+C OWED ONE OF THREE ANSWERS and took the first: resolve `.body` AFTER
# the rewriting passes (a late BIND driven from `target`, which is the durable
# fact, with `.body` as its cache). The other two are worse for reasons
# `src/opt/callgraph.c`'s header records: (b) "every rewriting pass updates it"
# puts the obligation on every FUTURE pass with no diagnostic when one forgets,
# and (c) "exempt callee subtrees from rewriting" makes a called group's
# emitted code differ from an uncalled one's for no semantic reason.
#
# MEASURED, AND THE MEASUREMENT NARROWED THE CLAIM. Applying this sabotage and
# diffing artifacts shows `((?:a|b))(?1)` emitting TWO DIFFERENT PROGRAMS FOR
# ONE GROUP (a merged class test lexically, the un-merged alternation with its
# own resume push in the region) and `RX_RESUME_FRAMES` moving 2 -> 3.
# **The ANSWERS do not change** -- altcls is answer-preserving in both
# directions -- so no corpus cell can see this, which is why the detector is a
# STRUCTURAL rule.
#
# AND THE DISCHARGE WITNESS IS NOT A HAZARD, which is worth recording because
# wave A2 named both passes. `((?>a)b)(?1)` compiles BYTE-IDENTICALLY under
# this sabotage: `pcrec_discharge_atomic` splices by rewriting the PARENT's
# `->l` in place, so the `A_CAP` a callee is rooted at keeps its identity and
# sees the discharge. Only the pass that REBUILDS the node matters, and only
# one of the two does.
#
# TWO SITES BY CONSTRUCTION: the call has to be REMOVED from its correct
# position and INSERTED at the wrong one, and `replace.py`'s exact-count rule
# refuses to express that as one edit.
SAB_ID="S166-callgraph-binds-early"
SAB_FILE="src/core/compile.c"
SAB_SUITES="codegen recursion"
SAB_DESC="pcrec_callgraph_build runs BEFORE pcrec_altcls, so u.call.body is bound over the PRE-REWRITE tree and the callee region is emitted from a subtree that is no longer in the tree -- two different programs for one group"
SAB_DOC_FIGURE="MEASURED ON THIS TREE rather than predicted. Moving the bind above pcrec_altcls and diffing the artifacts: '((?:a|b))(?1)' has its LEXICAL occurrence emit a merged class test while the CALLEE REGION emits the un-merged two-branch alternation with its own RX_PUSH and two extra labels, and RX_RESUME_FRAMES moves 2 -> 3 with it. THE ANSWERS ARE UNCHANGED on every subject (altcls is answer-preserving in both directions), which is why the detector is [DD-14-RECURSION rule 3] in tests/codegen and NOT a corpus cell. AND THE DISCHARGE WITNESS IS MEASURED NOT TO BE A HAZARD: '((?>a)b)(?1)' compiles byte-identically under the same sabotage, because pcrec_discharge_atomic splices by rewriting the parent's ->l IN PLACE and the A_CAP keeps its identity."
SAB_COUNT=1
SAB_BEFORE='    pcrec_callgraph_build(&cx, root);
'
SAB_AFTER=''
SAB_FILE2="src/core/compile.c"
SAB_COUNT2=1
SAB_BEFORE2='    root = pcrec_altcls(&cx, root);
'
SAB_AFTER2='    pcrec_callgraph_build(&cx, root);   /* SABOTAGE S166 */
    root = pcrec_altcls(&cx, root);
'
