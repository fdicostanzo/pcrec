# S69 — [M6.2 wave A] THE THIRD CLOSURE VIEW CANONICALIZED AGAINST THE BASE
# VIEW INSTEAD OF THE EOL VIEW.
#
# This is not an invented failure mode. It is the design's OWN first draft,
# refuted by the R30 panel (finding E3) one sentence at a time:
#
#   > `endvar` is -1 "when identical to the base", [and therefore] zero
#   > regression, since (T,T) == (T,F).
#
# Those are different comparisons. `endvar`'s view is (eol_ok, end_ok) =
# (T,T); the view it must be compared against is the EOL view (T,F), not the
# base view (F,F). Canonicalizing against the base makes every eol-differing
# state of every `$`-bearing pattern intern a live `endvar` — content-
# identical to its `eolvar`, and therefore a state, a table column and a
# selector branch that buy nothing — so `dfa_has_endvar` becomes true, the
# emitter takes the three-way branch, and the artifact is NOT byte-identical
# to the pre-wave one. Which is the exact opposite of the property §3.3
# claims, and the reason tests/codegen/run_endvar_identity.sh exists at all.
#
# WHAT MAKES THIS ROW WORTH ITS RUNTIME: the sabotage is SEMANTICS-PRESERVING.
# The extra endvar state is a duplicate of the eolvar state, so every emitted
# matcher still answers identically — the whole `.rxt` corpus, both oracles
# and every differential in the tree stay green. Only the byte-identity gate
# can see it, which is the case this project's check-design lesson is about:
# a claim of the form "X is impossible by construction" needs a construction
# check, and a construction check needs a measured failing direction.
SAB_ID="S69-endvar-against-base"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="endvaridentity harness"
# The harness arm is SCOPED to the `$`-engine corpus rather than run over
# the whole of tests/: this sabotage only perturbs `$`-bearing patterns, so
# `eol_engine.rxt` is exactly the population whose answers must be shown
# NOT to move, and the whole-corpus run costs minutes to say the same thing
# about patterns the edit cannot reach.
SAB_HARNESS_TARGET="tests/base/eol_engine.rxt"
SAB_DESC="make_state interns the \\z END view against the BASE view instead of against the EOL view (the design's own refuted first draft, R30 E3): every \$-bearing pattern gains a redundant endvar state and its emitted bytes move, with every answer unchanged"
SAB_DOC_FIGURE="tests/codegen/run_endvar_identity.sh: 1011/1011 identical becomes a large differing count; the corpus stays green. CANONICAL MATRIX RUN 2026-08-19 (after the [M6.2] repair slice): endvarid:1fail/2pass, corpus:0fail/32pass -- DETECTED, and the 0-fail corpus column is the semantics-preserving claim measured rather than asserted"
SAB_COUNT=1
# [M6.2 wave C] RE-EXPRESSED, same edit. make_state's three hand-written view
# comparisons became a loop over the class axis when `(?m)` made that axis
# three-valued; the sabotage is still "canonicalize the END view against the
# BASE view instead of against the EOL view", now spelled as the one changed
# subscript.
SAB_BEFORE='        while (u < UPC_N && view_same(&vw[V_EOL][u], &vw[V_END][u])) u++;'
SAB_AFTER='        while (u < UPC_N && view_same(&vw[V_BASE][u], &vw[V_END][u])) u++;   /* SABOTAGE S69 */'
