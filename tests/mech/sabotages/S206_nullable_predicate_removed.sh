# S206 (S-OPT41-1) — [OPT-4.1] THE NULLABILITY PREDICATE REMOVED: THE
# COUNT-COLLAPSED RESCUE IS BUILT AGAIN ON EVERY PATTERN THAT CANNOT USE IT,
# AND EVERY ANSWER IN THE TREE IS STILL RIGHT.
#
# WHAT IT BREAKS. `EngineFit.prefilter_lang_nullable` is written once, at
# `src/opt/select_engine.c`'s fit site, as `pcrec_minw(root) == 0` — the one
# derivation both readers of the decision consult (the `fit.prefilter` clause,
# which drops the prefilter on a ladder RUNG, and `src/core/compile.c`'s build
# gate, which declines the collapse under `-fprefilter-collapse`). This plant
# pins it FALSE, which is the shipped compiler of the day before [OPT-4.1]: the
# collapsed prefilter is built for a language that matches the empty string at
# every position, so the filter can never dismiss one and the artifact pays a
# scan whose every answer is "maybe".
#
# **THE COST IS MEASURED AND IT IS NOT SMALL.** pcrec-bench measured this exact
# shape at pin 96e44c2 (its O-10 item 3): `[a-z]{0,32768}` collapses to
# `[a-z]*` and goes 3.57x SLOWER on search, 1.880 -> 6.899 ns/B on throughput,
# and 1.65x slower on `t-digits-016k` — the subject the filter was expected to
# DISMISS and cannot. Three of the bench's ten labelled points lose 1.2-9.9x.
#
# **WHY NO ORACLE, NO DIFFERENTIAL AND NO IDENTITY GATE CAN BE RED FOR IT.**
# The prefilter is a FILTER (docs/spec/match_api.md §6.3, H1/H2/H3): its
# contract is soundness of REJECTION and a lower bound on the match start, and
# a superset supplies both, with the VM re-deriving the answer from every
# candidate it is handed. So the collapsed prefilter answers IDENTICALLY to no
# prefilter at all — the whole `.rxt` corpus, both oracles, `make test-axes`,
# every `*_diff.sh` and every byte-identity gate are green on this plant, and
# the corpus arm below is EXPECTED to read `0fail`. That is this arm working,
# in exactly the sense `sizeterm` and `offsetskip` already document.
#
# **WHAT DOES SEE IT, and each sees a different half.** `pfcollapse` §6b is
# the sharp one: the nullable overflow witness `(?:(?:a|b)*a(?:a|b){15})?` — the
# exponential-DFA shape plus one `?`, three characters from its own
# non-nullable control in the same section — keeps a `count-collapsed`
# prefilter where it must have none, and `RX_ENGINE_SEL` reads
# `collapsed-prefilter` — the stamp naming a rescue that was taken where it
# had to be refused, which is the artifact agreeing with the defect. §7b's
# `declined-nullable` witness then finds that route unreachable, which is the
# K35 half: a closed value set silently losing a member. §2's two
# `exact-nullable` rows fail on the `-fprefilter-collapse` axis, where the
# decline is a POLICY the flag must not override. And `resource`'s nullable
# size-rung cell fails on a THIRD path — the size rung, where the decline's
# benefit is a smaller artifact rather than a faster one.
#
# THE PLANT IS ONE TOKEN AND IT IS THE PREDICATE ITSELF, not one of its two
# readers: a plant at either reader would leave the other one working and this
# row would be reporting a partial removal as a whole one.
SAB_ID="S206-nullable-predicate-removed"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="pfcollapse resource harness"
SAB_HARNESS_TARGET="tests/base/bounded_repeats.rxt"
SAB_DESC="[OPT-4.1]'s nullability predicate is pinned false, so the count-collapsed prefilter rescue is built again for languages that match the empty string at every position and can therefore dismiss nothing — the 1.2-9.9x regression pcrec-bench measured at O-10 item 3, with every answer in the tree still right (the prefilter is a FILTER, so a useless one is answer-identical to none)"
SAB_DOC_FIGURE="CANONICAL RUN 2026-08-30 (run_sabotage_matrix.sh S206 at 412eb52): reach:ok(1/1), pfcollapse:5fail/50pass, resource:1fail/28pass, corpus:0fail/51pass -- DETECTED, with all three SAB_REACH_POP floors met (exact-nullable=2, [sel1n]=16, size_rung_cell=2). THE TWO CELLS TO READ: resource:1fail is the NULLABLE size-rung cell ALONE, its non-nullable twin GREEN -- that asymmetry is what says the plant removed a PREDICATE rather than the rung, and a row that reddened both would not distinguish them. corpus:0fail/51pass is the answer-identity this arm exists for: the prefilter is a FILTER, so a useless one is answer-identical to none, and no oracle, differential or identity gate in the tree can be red for this plant. An EARLIER run at 44ad88a (before r47sel finding 1 was fixed) read pfcollapse:5fail/49pass with everything else identical; the one-cell difference is section 6b(2c), which the fix ADDED and which this plant correctly does not redden -- (2c) is about the collapsible-repeat conjunct, not the nullability one."
SAB_REACH='"$PCREC" --features all -p rx -o - -- "(?:(?:a|b)*a(?:a|b){15})?"'
SAB_REACH_EXPECT="declined-nullable"
SAB_REACH_POP="tests/codegen/run_prefilter_collapse.sh|^lang_witness exact-nullable|2
tests/codegen/run_prefilter_collapse.sh|\[sel1n\]|10
tests/resource/run_resource_tests.sh|^size_rung_cell |2"
SAB_COUNT=1
SAB_BEFORE='        fit.prefilter_lang_nullable = pcrec_minw(root) == 0;'
SAB_AFTER='        fit.prefilter_lang_nullable = false;   /* SABOTAGE S206 */'
