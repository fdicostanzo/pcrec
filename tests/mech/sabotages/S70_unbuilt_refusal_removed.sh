# S70 — [M6.2 wave A] THE ENABLED-BUT-UNBUILT REFUSAL REMOVED, so a
# half-landed module tells the user to enable what they have already enabled.
#
# assertions_design.md §9.2: the waves land constructs incrementally, so there
# is an interval where `--features assertions` is ON and `\b` has no producer.
# "\b requires module 'assertions'" is then a LIE — and the actionable kind,
# since the one thing it asks for has already been done. The cure is a
# distinct diagnostic naming the CONSTRUCT, on the `--encoding=utf8`
# PRINCIPLE: a name pcrec knows but cannot compile is refused by its own name,
# never as unknown and never as a promise it cannot keep.
#
# Deleting the epilogue restores the lie. Note what does NOT notice:
#
#   - the `.rxt` corpus, because a `perr` block asserts only a nonzero exit;
#   - tests/reject/, because every one of its `assertions` pins probes with
#     the gate CLOSED, where the old sentence is the CORRECT one and is
#     unchanged by this edit;
#   - every differential in the tree, because no answer moves — the pattern
#     is refused either way.
#
# tests/reject/'s four gate-OPEN escape rows (`reject_gated assertions`) are
# the only thing that can see it, which is why they are written directly under
# the six gate-CLOSED rows rather than as a separate set — and why
# tests/assertions/run_assertions_tests.sh carries the control that stops them
# passing on a build where the module produces nothing at all.
#
# SCOPE, stated because the row's own failure is narrower than its title: the
# edit removes the epilogue from the ESCAPE doorway only. The `m` letter's
# refusal is produced per letter in src/parse/mod_modifiers.c and keeps its
# own copy of the rule, so the two `(?m)` rows over there stay GREEN. That is
# the honest reading of "a letter's module is not the dispatching row's", and
# it is why those two rows exist separately.
SAB_ID="S70-unbuilt-refusal-removed"
SAB_FILE="src/parse/ext.c"
SAB_SUITES="reject assertions"
SAB_DESC="the escape doorway's enabled-but-unbuilt epilogue is deleted, so an ENABLED module with no producer for a construct answers 'requires module X' — telling the user to enable what they already enabled"
SAB_DOC_FIGURE="tests/reject/: the four gate-OPEN escape rows (\\b \\B \\G \\K) go red; the gate-CLOSED rows, the two (?m) rows and the whole corpus stay green"
SAB_COUNT=1
SAB_BEFORE='    if (want == WANT_RESULT) {
        if (r->diag == RD_MODULE_OCTAL)
            UNBUILT(at, "\\%c (backreference/octal)", c);
        UNBUILT(at, "\\%c", c);
    }'
SAB_AFTER='    /* SABOTAGE S70 */'
