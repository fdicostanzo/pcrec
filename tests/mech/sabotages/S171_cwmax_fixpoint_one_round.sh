# S171 ([DD-14.LB]; re-pointed at [M5.0] stage 2, when the maxw fixpoint
# became the CHARACTER-unit `cwmax` fixpoint — utf8_design.md §5.6.2) -- THE
# `cwmax` FIXPOINT RUNS EXACTLY ONE ROUND.
#
# THE CLAIM: `u.call.cwmax` is a FIXPOINT over the call graph and not a single
# pass. One round settles every callee whose own body contains no call; a
# callee that calls another needs the round after that, and a chain of length k
# needs k. src/opt/callgraph.c iterates to a fixed point and ASSERTS that round
# `n + 1` changes nothing, for the same Knuth superior-function argument the
# `minw` fixpoint one function up carries.
#
# WHY THIS ROW EXISTS SEPARATELY FROM S169/S170: those two defend the pass that
# ASKS the width question. This one defends the ANSWER. A single-pass `cwmax`
# looks completely correct on the cell the whole feature was built for --
# `^(?:(?<g>ab)){0}ab(?<=(?&g))$`, whose callee has no calls of its own and is
# settled in round 0 -- and is wrong the moment a callee calls a callee.
#
# WHAT THE ARTIFACT DOES, PREDICTED: the TWO-HOP ACYCLIC CHAIN block
# (`^(?:(?<h>cd)){0}(?:(?<g>(?&h)e)){0}cde(?<=(?&g))$`) is REFUSED, because
# `g`'s width is still the initial `PCREC_W_UNBOUNDED` when the fixpoint stops
# -- a pattern-compile failure, and a tier-2 OVER-rejection rather than a
# miscompile, which is the safe direction this analysis is built to fail in.
# Every other block in the file still passes: that is the point of the row and
# the reason the two-hop cell was written.
#
# `changed` GOES UNUSED UNDER THE EDIT and gcc says so (-Wunused-but-set-
# variable); `-Werror` is deliberately not the default (CLAUDE.md, R5-Q1), so
# the sabotaged tree still builds and the row scores on behaviour.
SAB_ID="S171-cwmax-fixpoint-one-round"
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/inlookaround.rxt"
SAB_DESC="the call graph's cwmax iteration stops after one round, so a callee that calls another callee keeps its initial PCREC_W_UNBOUNDED and a lookbehind over a two-hop acyclic chain is refused"
SAB_DOC_FIGURE="PREDICTED ([DD-14.LB]): exactly ONE block fails in tests/recursion/inlookaround.rxt -- the two-hop acyclic chain, as a pattern-compile failure. The one-hop cells settle in round 0 and are unmoved, which is precisely why a single-pass cwmax would have looked correct without this cell. MEASURED at [DD-14.LB], FINAL corpus: harness corpus:2fail/48pass, DETECTED -- the two-hop chain block's two cases and NOTHING ELSE out of 50, which is the row's whole claim: every one-hop cell settles in round 0 and a single-pass cwmax looks correct on all of them."
SAB_COUNT=1
SAB_BEFORE='            cg_walk(root, cg_cwmax_publish, &m);
            for (int i = 0; i < n; i++) {
                long long nv = pcrec_cwmax(cg->body[i]);
                if (nv < val[i]) { val[i] = nv; changed = true; }
            }
            if (!changed) break;'
SAB_AFTER='            cg_walk(root, cg_cwmax_publish, &m);
            for (int i = 0; i < n; i++) {
                long long nv = pcrec_cwmax(cg->body[i]);
                if (nv < val[i]) { val[i] = nv; changed = true; }
            }
            break;   /* SABOTAGE S171: one round only */'
