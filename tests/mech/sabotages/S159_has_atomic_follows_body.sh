# S159 ([DD-14] wave B+C, design SS9.3 S-SR11) -- NO WHOLE-TREE PREDICATE
# FOLLOWS `.body`, AND THE FAILURE IS A NON-TERMINATING COMPILE.
#
# A TIMEOUT ROW, and the reason it must be one is the sharpest thing in
# design SS4.4. `Ast.u.call.body` is the AST's FIRST `Ast*` -> `Ast*` BACK
# EDGE. Every walker in `src/` was written for a TREE: `pcrec_minw`,
# `pcrec_has_atomic` and `pcrec_has_bref` are bare `const Ast *` walkers with
# NO context parameter, NO memo and NO visited set -- a tree-wide grep for
# `visited|memoi|acyclic|cycle` finds one unrelated hit. This design's FIRST
# VERSION told three of them to "descend into `.body`".
#
# ON `(a(?1))` THAT HANGS THE COMPILER, in predicates asked of EVERY PATTERN,
# and **no answer-comparison test can detect it because there is no answer**.
# That is why the row sits in the `timeout` suite rather than in `harness`,
# where a hang reads as an infrastructure failure rather than as a finding.
#
# THE RULE THAT REPLACED THE FIRST VERSION is one sentence and it makes the
# descent REDUNDANT as well as fatal: every callee is ALSO A LEXICAL NODE OF
# THE SAME TREE -- `target` names an `A_CAP` that SS4.3 keeps alive, and
# `target == 0` is the root -- so a whole-tree predicate already visits the
# callee at the callee's own lexical position. Following the edge asks the same
# question a second time and never stops asking.
#
# WHERE A SUBTREE-RELATIVE ANSWER GENUINELY IS THE CALLEE'S, it goes through
# `src/opt/callgraph.c`'s memoised fixpoint over the graph instead --
# `pcrec_minw`, `vm_nullable` and `W` are the three, and each reads a value
# CACHED ON THE NODE rather than walking to it.
#
# THE ARM SABOTAGED is `pcrec_has_atomic`'s, which is asked of every pattern at
# emission (it is one of `Vm.mrl_win`'s two conjuncts), so the hang is on the
# shipped path rather than on a flag.
SAB_ID="S159-has-atomic-follows-body"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="timeout recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="pcrec_has_atomic's A_CALL arm DESCENDS into u.call.body, so a whole-tree predicate follows the AST's back edge and the COMPILER does not terminate on (a(?1)) -- there is no answer to compare, so no answer-comparison row can see it"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR11): THE COMPILER HANGS on (a(?1)). There is no answer to compare, so this row is scored by the harness TIMEOUT and it is the one sabotage in this module whose detector is 'the process did not finish'. NOTE the anchor: pcrec_has_atomic's arm is the FIRST \`case A_CALL:\\n            return false;\` in atomic.c, and the count is 1 because the six other whole-tree predicates in that file each phrase their decline differently."
SAB_COUNT=1
SAB_BEFORE='        case A_CALL:
            return false;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_atomic(a->r)) return true;'
SAB_AFTER='        case A_CALL:   /* SABOTAGE S159: follow the back edge */
            if (!a->u.call.body) return false;
            a = a->u.call.body;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_atomic(a->r)) return true;'
