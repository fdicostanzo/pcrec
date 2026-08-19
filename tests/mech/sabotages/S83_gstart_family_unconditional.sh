# S83 — [M6.2 WAVE D] THE `\G` START FAMILY EMITTED UNCONDITIONALLY.
#
# THE CLAIM THIS ROW IS THE FAILING DIRECTION OF: a pattern with no `\G` pays
# nothing for `\G` — the same states, the same tables, the same start
# dispatch, the same emitted bytes. `tests/codegen/run_gstart_identity.sh` is
# the check; without a measured way to make it go red it is a check with no
# failing direction, which is what waves A, B and C each say about their own
# gates and what R30 E3 is the standing evidence for (the design's first draft
# of the analogous byte-identity claim was WRONG, argued from prose, and would
# have shipped).
#
# THE SABOTAGE forces `dfa_needs_gseed` true, so every ENG_ATTEMPT artifact in
# the corpus takes the three-way `start == startpos` dispatch instead of the
# two-way or constant one it takes today. NOTHING MISCOMPILES — on a machine
# with no N_GSTART the two interior families hold the same state ids, so all
# three arms of the ternary lead to the same label and every answer is
# unchanged. That is precisely why it is worth a row: a defect whose only
# symptom is emitted bytes is invisible to every corpus in the tree, and the
# identity gate is the ONLY instrument that can see it.
#
# It is also the sharper of the two directions this wave could have sabotaged.
# `-DPCREC_NO_GSTART` (the reference knob the gate builds against) makes `\G`
# behave as `\A` and would go red in the CORPUS; this one goes red ONLY in the
# identity gate, so a run where the gate is the sole failure is the gate
# reporting exactly what it exists for.
#
# MEASURED before this row shipped: 93 of the 1175 `\G`-free corpus patterns
# that compile in both builds change emitted bytes under it, and the whole
# `.rxt` corpus — gpos.rxt included, 286 cases — stays green.
#
# **THIS ROW IS ALSO WHY THIS WAVE'S REFERENCE KNOB IS AT THE EMITTER RATHER
# THAN IN THE ANALYSIS, and the history is worth keeping.** Wave D's first
# draft put `-DPCREC_NO_GSTART` in `src/ir/dfa.c` beside `_WORDCTX`,
# `_MLINECTX` and `_ENDVAR`. Under this sabotage the identity sweep then
# stayed 1175/1175 IDENTICAL — because the reference compiler is built from
# THE SAME (sabotaged) SOURCES, so an edit to a function the knob does not
# gate applies to both builds and CANCELS. The same measurement on wave B's
# S71 shows it is not specific to this row: `run_wordctx_identity.sh`'s sweep
# stays 1135/1135 identical under S71 too, and that script fails only through
# a side effect (`has_word` becomes unused, so the reference build warns).
# Moving this wave's knob to the three EMITTER decision points makes the
# reference build structurally the pre-wave emitter, which no edit to the
# analysis can undo — and doing so immediately exposed a real defect in the
# wave's own emitter that the mis-placed knob had hidden (a dead `gseed[]`
# table on every `\b`/`(?m)` artifact). S71 and S76 are ANNOTATED with the
# measurement; re-placing their knobs is a manager decision, not this wave's.
SAB_ID="S83-gstart-family-unconditional"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="gstartidentity"
SAB_DESC="dfa_needs_gseed answers true unconditionally, so every ENG_ATTEMPT artifact emits the three-way \\G start dispatch whether or not the pattern contains a \\G. No answer changes; only bytes do — which is the whole reason the byte-identity gate exists"
SAB_DOC_FIGURE="tests/codegen/run_gstart_identity.sh's identity sweep goes red over the \\G-free corpus population (and nothing else in the tree moves)"
SAB_COUNT=1
SAB_BEFORE='    for (int u = 0; u < UPC_N; u++)
        if (d->s1g[u] != d->s1u[u]) return true;
    return false;
}'
SAB_AFTER='    for (int u = 0; u < UPC_N; u++)
        if (d->s1g[u] != d->s1u[u]) return true;
    return true;   /* SABOTAGE S83 */
}'
