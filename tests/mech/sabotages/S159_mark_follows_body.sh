# S159 ([DD-14] wave B+C, design SS9.3 S-SR11) -- NO WHOLE-TREE PREDICATE
# FOLLOWS `.body`, AND THE FAILURE IS A NON-TERMINATING COMPILE.
#
# A HANG ROW, and the reason it must be one is the sharpest thing in design
# SS4.4. `Ast.u.call.body` is the AST's FIRST `Ast*` -> `Ast*` BACK EDGE. Every
# walker in `src/` was written for a TREE: `pcrec_minw`, `pcrec_has_atomic` and
# `pcrec_has_bref` are bare `const Ast *` walkers with NO context parameter, NO
# memo and NO visited set -- a tree-wide grep for `visited|memoi|acyclic|cycle`
# finds one unrelated hit. This design's FIRST VERSION told three of them to
# "descend into `.body`".
#
# ON `(a(?1))` THAT HANGS THE COMPILER, in predicates asked of EVERY PATTERN,
# and **no answer-comparison test can detect it because there is no answer**.
# What scores it is `tests/harness/run.sh`, which runs the `pcrec` invocation
# itself under `TIMEOUT_BIN` (budget from `tests/lib/gen_timeout.sh`, D45) and
# treats a non-zero exit -- timeout included -- as a FAILURE naming the case.
# The design asks for "`tests/mech/`'s timeout suite"; there is no such arm,
# and `harness` is where a hang is already scored.
#
# **THE ARM SABOTAGED IS `pcrec_bref_mark`'s, NOT `pcrec_has_atomic`'s, AND
# THE MOVE IS A FINDING.** The design names `pcrec_has_atomic` and this lane
# wrote that row first -- it scored UNDETECTED at corpus 0fail/346pass. The
# reason is a C short-circuit: `Vm.mrl_win` is
#
#     job->fit.prefilter && !pcrec_has_atomic(root) && !pcrec_has_lookaround(root)
#
# and `fit.prefilter` is FALSE for every call-bearing pattern (SS8.2's own
# predicate, landed in this wave), so **`pcrec_has_atomic` is never CALLED on a
# tree that contains a call**. The predicate the design picked is unreachable
# for this construct's whole population.
#
# `pcrec_bref_mark` is the one whole-tree walk that IS asked of a call-bearing
# tree AFTER `.body` is bound: `pcrec_emit_vm` runs it unconditionally to build
# the marked set. It is also the walk whose `A_CALL` arm is the ONE in
# `src/opt/atomic.c` that does not simply decline -- it marks the target and
# descends no further -- which makes "and no descent" the exact thing this row
# defends.
#
# THE RULE THAT REPLACED THE DESIGN'S FIRST VERSION is one sentence and it
# makes the descent REDUNDANT as well as fatal: every callee is ALSO A LEXICAL
# NODE OF THE SAME TREE, so a whole-tree predicate already visits it at its own
# lexical position. Where a subtree-relative answer genuinely IS the callee's,
# it goes through `src/opt/callgraph.c`'s memoised fixpoint and is read from a
# value CACHED ON THE NODE.
SAB_ID="S159-mark-follows-body"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="pcrec_bref_mark's A_CALL arm DESCENDS into u.call.body after marking, so a whole-tree walk follows the AST's back edge and the COMPILER does not terminate on a recursive callee -- there is no answer to compare, so no answer-comparison row can see it"
SAB_DOC_FIGURE="PREDICTED: the compiler HANGS and tests/harness/run.sh scores the timeout as a failure on every recursive cell. RE-POINTED FROM pcrec_has_atomic, which the design names and which is UNREACHABLE for this population: Vm.mrl_win short-circuits on fit.prefilter, which SS8.2's predicate makes false for every call-bearing pattern -- measured UNDETECTED at corpus 0fail/346pass before the move."
SAB_COUNT=1
SAB_BEFORE='        case A_CALL:
            if (a->u.call.target > 0 && a->u.call.target < nmark)
                mark[a->u.call.target] = true;
            return;'
SAB_AFTER='        case A_CALL:   /* SABOTAGE S159: follow the back edge */
            if (a->u.call.target > 0 && a->u.call.target < nmark)
                mark[a->u.call.target] = true;
            if (a->u.call.body) { a = a->u.call.body; continue; }
            return;'
