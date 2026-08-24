# S135 ([M6.6.2] wave D, design row S-LA8) — THE START-OF-SUBJECT GUARD IS
# CLAMPED TO `startpos`, SO A LOOKBEHIND STOPS SEEING BEHIND THE SEARCH WINDOW.
#
# THE CLAIM IT DEFENDS IS A CONTRACT QUESTION, NOT A SYNTAX ONE (design §3.8).
# A lookbehind READS SUBJECT BYTES BEFORE `startpos`, and that is the
# semantics: MEASURED in BOTH oracles, `(?<=a)b` on "ab" AT STARTPOS 1 matches
# (1,2), and `(?<!a)b` on the same input at the same startpos does NOT. The
# assertion is evaluated against the REAL SUBJECT, not against the search
# window — for the VM that is free, because `subject` is the whole subject and
# `scan_position` is an ABSOLUTE offset, which is exactly why a plausible
# "surely we should not read before where we were asked to start" edit
# compiles, passes every startpos-0 cell in the tree, and is wrong.
#
# IT IS THE `assertions_design.md` §3.8 MECHANISM-4 QUESTION ARRIVING FOR A
# SECOND CONSTRUCT (R30's E1), which is why it gets a row rather than a
# comment.
#
# TWO SITES BECAUSE THE GUARD HAS TWO ARMS — the LAST branch fails and every
# other branch falls through to the next one — and a clamp on one arm only
# would leave the multi-branch cells half-right, which is a weaker and more
# confusing detector than either half alone. Site 1 also bumps `v->ngst` so the
# artifact carries the `<prefix>_search_from` parameter the clamp reads; that
# parameter is emitted only where a `\G` exists, and without the bump the
# sabotaged compiler emits code that does not build (a COMPILE-FAIL is an
# anomaly, not a detection).
#
# THE PREDICTION NAMES BOTH DIRECTIONS. `startpos.rxt`'s `ms`/`ns` cells go
# RED; every startpos-0 cell in `lookbehind.rxt`, `lookbehind_widths.rxt` and
# `nonatomic_behind.rxt` stays GREEN. A row that took the whole corpus with it
# would not be evidence that this axis is covered.
SAB_ID="S135-backstep-clamped-to-startpos"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="vm_look_behind's start-of-subject guard is clamped to the SEARCH WINDOW (scan_position - search_from < k) instead of the subject, so a lookbehind can no longer read bytes before startpos — which is what design §3.8 measures both oracles doing"
SAB_DOC_FIGURE="PREDICTED: tests/lookaround/startpos.rxt RED on its ms/ns cells (a positive lookbehind stops matching, and a NEGATIVE one starts matching where it must not — a FALSE MATCH); every startpos-0 cell in lookbehind.rxt, lookbehind_widths.rxt and nonatomic_behind.rxt GREEN. Canonical figure owed from run_sabotage_matrix.sh S135."
SAB_COUNT=1
SAB_BEFORE='            if (k > 0)
                sb_printf(b, "    if (scan_position < %d) goto %s_fail;\n",
                          k, v->p);'
SAB_AFTER='            v->ngst++;   /* SABOTAGE S135: force the search_from parameter */
            if (k > 0)
                sb_printf(b, "    if (scan_position - %s_search_from < %d)"
                             " goto %s_fail;\n", v->p, k, v->p);'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='                sb_printf(b, "    if (scan_position < %d) goto %s_L%d;\n",
                          k, v->p, bl[i + 1]);'
SAB_AFTER2='                sb_printf(b, "    if (scan_position - %s_search_from < %d)"
                             " goto %s_L%d;\n", v->p, k, v->p, bl[i + 1]);'
