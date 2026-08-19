# S73 — [M6.2 wave B] THE CLASS-INDEXED ACCEPT MOVED ABOVE ITS `pos >= n`
# GUARD.
#
# assertions_design.md §3.6.2's composition rule: two axes select an accept
# bit — the VIEW axis by POSITION and the CLASS axis by the NEXT BYTE — and at
# `pos == n` there IS no next byte, so the accept is the view's SCALAR one and
# is never class-indexed.
#
#     accept_at(st, pos) = pos <  n -> acc_cls[view(st, pos)][fcls[s[pos]]]
#                          pos == n -> acc    [view(st, n)]
#
# The sabotage restores the shape the pre-wave loop had — evaluate the accept,
# then test for the end — with the accept now class-indexed. That reads
# `s[pos]` at `pos == n`: an OUT-OF-BOUNDS READ IN EMITTED CODE, which is
# K27's exact class, a generated matcher whose UB carries pcrec's name into a
# user's own sanitizer run.
#
# WHY A STRUCTURAL CHECK AND NOT A CORRECTNESS ONE. The byte one past the
# subject is very often readable and its class is very often the same as some
# in-range byte's, so the answer usually does not change — the corpus goes
# green and the artifact is unsound. `probe_acc_by_class.sh:33` papered over
# exactly this position by indexing with class 0, legal only because that
# probe's variant is answer-preserving; §3.6.2 discloses the shortcut in place
# rather than fixing it, and names this rule as what the DESIGN takes instead.
#
# The instrument that sees it is tests/codegen/run_codegen_tests.sh's
# [M6.2-WORDB rule 1], which requires the guard to come first AND every
# class-indexed read to go through the guarded `cl` local; and the asan axis,
# where the read is a genuine heap-buffer-overflow rather than an inference.
SAB_ID="S73-accept-indexed-at-end"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/assertions/wordb.rxt"
SAB_DESC="the forward loop's class-indexed accept is emitted ABOVE its 'pos >= n' guard, so the emitted matcher computes fcls[s[pos]] at pos == n -- an out-of-bounds read in generated code (S3.6.2, K27's class) that usually changes no answer"
SAB_DOC_FIGURE="tests/codegen/run_codegen_tests.sh: [M6.2-WORDB rule 1] reports the guard after the first class-indexed accept"
SAB_COUNT=1
SAB_BEFORE='        sb_printf(c, "        if (pos >= n) {\\n"
                     "            if (%s_facc[%s]) last = pos;\\n"
                     "            break;\\n"
                     "        }\\n", p, fsrc);
        sb_printf(c, "        {\\n"
                     "            unsigned cl = %s_fcls[s[pos]];\\n"'
SAB_AFTER='        sb_printf(c, "        if (%s_facc2[%s * %d + %s_fcls[s[pos]]]) last = pos;\\n"   /* SABOTAGE S73 */
                     "        if (pos >= n) {\\n"
                     "            if (%s_facc[%s]) last = pos;\\n"
                     "            break;\\n"
                     "        }\\n", p, fsrc, fd->ncls, p, p, fsrc);
        sb_printf(c, "        {\\n"
                     "            unsigned cl = %s_fcls[s[pos]];\\n"'
