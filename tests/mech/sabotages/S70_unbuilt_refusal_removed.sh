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
# ==========================================================================
# [srMech, 2026-08-25] THE WITNESS EXPIRED BY BEING IMPLEMENTED, AND THE ROW
# WENT BLIND. The full matrix scored this row UNDETECTED on a tree where the
# sabotage APPLIES CORRECTLY and the diagnostic is genuinely lost.
#
# THE MEASURED CAUSE, in one sentence with the file:line: after [M6.5.2]
# retired the `\k` (backrefs) pin, NOT ONE row anywhere in the tree still
# reached `UNBUILT(at, "\%c", c)` at src/parse/ext.c:326 -- the ESCAPE
# doorway's out-of-class epilogue, which is the only text this row deletes.
# The four gate-OPEN escape rows this header names below (`\b \B \G \K`,
# `reject_gated assertions`) were retired one per wave through [M6.2] B..E as
# module `assertions` BUILT them; their replacement pins were re-homed, but
# every survivor reaches a DIFFERENT site:
#
#   ext.c:308-320  the IN-CLASS wording, spliced beside the K12 endpoint
#                  payload and explicitly NOT through the macro
#                  <- `reject_gated quoting '[\Q]'`
#   ext.c:509      the GROUP doorway's own UNBUILT call
#                  <- `reject_gated conditionals '(?(1)a|b)'`
#   (no site)      `reject_gated recursion '\g<1>'` stopped asserting the
#                  enabled-but-unbuilt sentence at [DD-14] wave D; it pins the
#                  error-115-class sentence now
#
# So the population had moved OFF the sabotaged site entirely while the
# arm itself stayed live and large -- the shape tests/reject/'s own re-home
# paragraph warns about, arriving one module later than it was watching for.
# THIS IS NOT A DEFECT IN THE RE-HOME: it is the fourth time the pin has had
# to move, and the third time nobody noticed that the move changed WHICH SITE
# was covered rather than only which module.
#
# THE FIX IS A WITNESS RE-POINT, NOT A SUITE ADDITION. Two rows were added to
# tests/reject/run_reject_tests.sh at the escape doorway, on two modules with
# rows and no producer: `reject_gated quoting '\Q'` and
# `reject_gated misc '\R'`. `\Q` shares its LETTER with the in-class row
# beside it on purpose -- one module, one letter, two positions, two sentences
# from two sites -- so this row now discriminates the two sites rather than
# assuming they move together. Gated count 78 -> 80.
#
# WHAT STILL DOES NOT NOTICE is unchanged and is still worth reading: the
# `.rxt` corpus (a `perr` block asserts only a nonzero exit), the gate-CLOSED
# rows (the old sentence is correct there and this edit does not touch it),
# every differential (no answer moves), and `tests/assertions/`'s arm, which
# asserts the module's BUILT constructs compile and is the control that stops
# the reject rows passing on an empty module rather than a detector itself.
# ==========================================================================
SAB_ID="S70-unbuilt-refusal-removed"
SAB_FILE="src/parse/ext.c"
SAB_SUITES="reject assertions"
SAB_DESC="the escape doorway's enabled-but-unbuilt epilogue is deleted, so an ENABLED module with no producer for a construct answers 'requires module X' — telling the user to enable what they already enabled"
SAB_DOC_FIGURE="RE-MEASURED 2026-08-25 after the row scored UNDETECTED. SUPERSEDES the wave A figure, which named the four gate-OPEN escape rows \\b \\B \\G \\K: those retired one per wave through [M6.2] B..E as module assertions built them, and after [M6.5.2] retired the \\k (backrefs) pin NO row in the tree reached the escape doorway's out-of-class epilogue at src/parse/ext.c:326 at all. NEW WITNESSES, at that site: reject_gated quoting '\\Q' and reject_gated misc '\\R'. MEASURED 2026-08-25 through the driver at 47f2648: SABOTAGED reject 2fail/587pass, assertions 0fail/52pass -> DETECTED; CLEAN (control, same commit, no edit) reject 0fail/589pass, assertions 0fail/52pass. Exactly two checks move and 587+2 = 589, so the detection is the two new rows and nothing else. Both fail with the LIE the row exists to catch, verbatim: \"want substring: module 'quoting' is enabled but \\Q is not implemented yet ; got: pcrec: \\Q requires module 'quoting'\" (and the same shape for \\R / misc) -- an ENABLED module being told to enable itself. The gate-CLOSED rows, the two in-class/group-doorway pins and the whole corpus stay green either way -- they reach different sites. tests/assertions/ is the CONTROL half (it asserts the module's built constructs compile, so the reject rows cannot pass on an empty module) and is not expected to move."
# [MECH-REACH, 2026-08-25] AND NOW THE ROW DECLARES ITS OWN REACH, so the
# blindness above cannot recur silently. The re-point two paragraphs up fixed
# THIS row; the fields below fix the CLASS. Both halves of the claim are
# stated separately because they expire separately:
#
#   SAB_REACH proves the SITE still answers -- `\Q` and `\R` at the ESCAPE
#     doorway, out of class, both produced by the single UNBUILT() call this
#     row deletes. Both are asserted, not one: asserting one witness is how
#     the four this row started with expired one at a time without anything
#     going red.
#   SAB_REACH_POP proves the WITNESS ROWS are still in the suite that scores
#     the row. A reach probe alone would stay green if somebody retired the
#     two `reject_gated` lines, since the compiler would go on producing the
#     sentence nobody was asking for any more. The regexes deliberately do
#     NOT match the IN-CLASS row (`'[\Q]'`, ext.c:308-320), which reaches a
#     DIFFERENT site: the whole point of the re-point was to stop treating
#     the two positions as one population.
SAB_REACH='"$PCREC" --features quoting -p rx -o "$REACH_TMP/q.c" -- "\\Q"; "$PCREC" --features misc -p rx -o "$REACH_TMP/r.c" -- "\\R"'
SAB_REACH_EXPECT="module 'quoting' is enabled but \\Q is not implemented yet
module 'misc' is enabled but \\R is not implemented yet"
SAB_REACH_POP="tests/reject/run_reject_tests.sh|^reject_gated +quoting +'.Q'|1
tests/reject/run_reject_tests.sh|^reject_gated +misc +'.R'|1"
SAB_COUNT=1
SAB_BEFORE='    if (want == WANT_RESULT) {
        if (r->diag == RD_MODULE_OCTAL)
            UNBUILT(at, "\\%c (backreference/octal)", c);
        UNBUILT(at, "\\%c", c);
    }'
SAB_AFTER='    /* SABOTAGE S70 */'
