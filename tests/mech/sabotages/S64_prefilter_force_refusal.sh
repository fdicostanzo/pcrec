# S64 — [M4.6f] THE PREFILTER FORCE-ON DO-OR-DIE REFUSAL REMOVED.
#
# D46's controllability half requires that a strategy which cannot honour a
# forced request REFUSE cleanly rather than silently ignore the flag or
# silently build something the caller did not ask for (D47.3's do-or-die
# posture, the same one --engine itself uses). `-fprefilter` on a pattern
# that compiles to the DFA engine has no VM artifact to attach a prefilter
# to, so src/opt/select_engine.c refuses it. This sabotage removes exactly
# that refusal, leaving `fit.prefilter` set to `true` unconditionally on the
# force-on path even when `fit.chosen == ENGM_DFA`.
#
# WHAT ACTUALLY HAPPENS ON THE SABOTAGED TREE, so the row's own history
# does not need re-deriving by hand next time it is touched: `fit.prefilter`
# becomes structurally inert in this case rather than causing a crash or a
# miscompile — compile.c's DFA-pair build guard
# (`fit.chosen == ENGM_DFA || fit.prefilter`) already builds the DFA pair
# whenever the DFA engine is chosen, and the emitter that runs
# (`emit_dfa.c`, since `fit.chosen != ENGM_VM`) never reads `fit.prefilter`
# at all — that field only has a consumer on the VM path. So the pattern
# compiles SUCCESSFULLY where it should have been refused: exactly the
# silent-honour failure mode D46/D47.3 exist to forbid, invisible to every
# correctness check in the tree because the emitted artifact is unchanged
# from an ordinary DFA build.
#
# tests/prefilter/run_prefilter_tests.sh check 3 ("force-on vs explicit
# --engine=dfa" / "force-on vs auto-routed-DFA") is the ONLY thing in the
# tree that asserts this refusal happens at all -- no .rxt corpus, no
# differential, and no other structural check can see a REQUEST that was
# supposed to fail compiling instead.
SAB_ID="S64-prefilter-force-refusal"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="prefilter"
SAB_DESC="the -fprefilter do-or-die refusal (fit.chosen != ENGM_VM) is removed, so --engine=dfa -fprefilter and --no-captures -fprefilter compile SUCCESSFULLY instead of refusing -- fit.prefilter=true is set but has no consumer on the DFA emission path, so the artifact is silently identical to an unforced DFA build"
SAB_DOC_FIGURE="docs/dev/decisions.md D46 (do-or-die); src/opt/CLAUDE.md's [M4.6f] entry"
SAB_COUNT=1
SAB_BEFORE='        if (force_on && fit.chosen != ENGM_VM)
            ctx_fail(cx, why_pos,
                     "-fprefilter requires the VM engine; this pattern "
                     "compiles to the DFA engine, which carries no separate "
                     "prefilter to force (pass --engine=vm, or drop "
                     "-fprefilter)");
'
SAB_AFTER='        /* SABOTAGE S64: do-or-die refusal removed -- force_on now sets
         * fit.prefilter=true unconditionally, even when fit.chosen is
         * ENGM_DFA, where nothing ever reads it. */
'
