# S-U10 ([M5.0] stage 2; utf8_design.md §8.2) -- THE `cwmin` FIXPOINT RUNS
# EXACTLY ONE ROUND (S171's own shape, re-aimed at the pair's OTHER half).
#
# THE CLAIM: `u.call.cwmin` -- the character-minimum half of the lookbehind
# width pair, born at stage 2 when the maxw chain became `cwmax` and gained a
# `cwmin` partner (§5.6.2/§5.6.3) -- settles to a FIXPOINT over the call
# graph. One round settles every callee whose own body contains no call; a
# chain of length k needs k rounds. A one-round `cwmin` leaves a two-hop
# callee at its initial PCREC_MINW_MAX, so `cwmin != cwmax` and the width
# rule REFUSES a lookbehind 10.46 accepts -- a tier-2 over-rejection, the
# safe direction, and exactly S171's symptom arriving through the other
# half of the pair.
#
# WHY THIS ROW EXISTS BESIDE S171: the two fixpoints are two loops. An edit
# that truncates one leaves the other settling correctly, so S171's detector
# goes red for `cwmax` truncation and would stay GREEN for `cwmin`'s if the
# refusal read only one half -- it does not (the rule tests equality), which
# is what makes the same corpus cell this row's detector too. One row per
# loop is D69's one-row-per-claim, not duplication.
#
SAB_ID="S-U10-cwmin-fixpoint-one-round"
# REACH (clean tree): the two-hop acyclic chain — the ONE cell whose verdict
# needs a second fixpoint round — still COMPILES, i.e. the witness reaches the
# rule this row truncates. The population floor pins the detector file's own
# copy of that cell (a corpus that lost it would leave this row scoring green
# over nothing, [MECH-REACH]'s shape).
SAB_REACH='"$PCREC" --features all -p rx -o - -- "^(?:(?<h>cd)){0}(?:(?<g>(?&h)e)){0}cde(?<=(?&g))$"'
SAB_REACH_EXPECT='Pattern: ^(?:(?<h>cd)){0}(?:(?<g>(?&h)e)){0}cde(?<=(?&g))$'
SAB_REACH_POP='tests/recursion/inlookaround.rxt|\(\?&h\)e|1'
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/inlookaround.rxt"
SAB_DESC="the call graph's cwmin iteration stops after one round, so a callee that calls another callee keeps its initial PCREC_MINW_MAX, cwmin != cwmax opens, and a lookbehind over a two-hop acyclic chain is refused"
SAB_DOC_FIGURE="PREDICTED ([M5.0] stage 2, S171's measured shape): exactly ONE block fails in tests/recursion/inlookaround.rxt -- the two-hop acyclic chain, as a pattern-compile failure; every one-hop cell settles in round 0 and is unmoved. MEASURED at stage 2: harness corpus:2fail/48pass, DETECTED -- the two-hop chain block's two cases and nothing else, S171's own figure arriving through the pair's other half."
SAB_COUNT=1
SAB_BEFORE='            cg_walk(root, cg_cwmin_publish, &m);
            for (int i = 0; i < n; i++) {
                long long nv = pcrec_cwmin(cg->body[i]);
                if (nv < val[i]) { val[i] = nv; changed = true; }
            }
            if (!changed) break;'
SAB_AFTER='            cg_walk(root, cg_cwmin_publish, &m);
            for (int i = 0; i < n; i++) {
                long long nv = pcrec_cwmin(cg->body[i]);
                if (nv < val[i]) { val[i] = nv; changed = true; }
            }
            break;   /* SABOTAGE S-U10: one round only */'
