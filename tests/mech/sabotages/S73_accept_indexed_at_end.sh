# S73 — [M6.2 wave B] THE CLASS-INDEXED ACCEPT MOVED ABOVE ITS `scan_position >= subject_length`
# GUARD.
#
# assertions_design.md §3.6.2's composition rule: two axes select an accept
# bit — the VIEW axis by POSITION and the CLASS axis by the NEXT BYTE — and at
# `scan_position == subject_length` there IS no next byte, so the accept is the view's SCALAR one and
# is never class-indexed.
#
#     accept_at(forward_state, scan_position) = scan_position <  subject_length -> acc_cls[view(forward_state, scan_position)][fcls[subject[scan_position]]]
#                          scan_position == subject_length -> acc    [view(forward_state, subject_length)]
#
# The sabotage restores the shape the pre-wave loop had — evaluate the accept,
# then test for the end — with the accept now class-indexed. That reads
# `subject[scan_position]` at `scan_position == subject_length`: an OUT-OF-BOUNDS READ IN EMITTED CODE, which is
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
# class-indexed read to go through the guarded `forward_class` local; and the asan axis,
# where the read is a genuine heap-buffer-overflow rather than an inference.
SAB_ID="S73-accept-indexed-at-match_end_position"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/assertions/wordb.rxt"
SAB_DESC="the forward loop's class-indexed accept is emitted ABOVE its 'pos >= subject_length' guard, so the emitted matcher computes fcls[subject[scan_position]] at scan_position == subject_length -- an out-of-bounds read in generated code (S3.6.2, K27's class) that usually changes no answer"
SAB_DOC_FIGURE="tests/codegen/run_codegen_tests.sh: [M6.2-WORDB rule 1] reports the guard after the first class-indexed accept"
SAB_COUNT=1
SAB_BEFORE='        sb_printf(c, "        if (scan_position >= subject_length) {\n"
                     "            if (%s_forward_is_accepting[%s]) last_accept_position = scan_position;\n"
                     "            break;\n"
                     "        }\n", p, fsrc);
        sb_printf(c, "        {\n"
                     "            unsigned forward_class = %s_forward_byte_class[subject[scan_position]];\n"'
SAB_AFTER='        sb_printf(c, "        if (%s_forward_is_accepting_by_class[%s * %d + %s_forward_byte_class[subject[scan_position]]]) last_accept_position = scan_position;\n"   /* SABOTAGE S73 */
                     "        if (scan_position >= subject_length) {\n"
                     "            if (%s_forward_is_accepting[%s]) last_accept_position = scan_position;\n"
                     "            break;\n"
                     "        }\n", p, fsrc, fd->ncls, p, p, fsrc);
        sb_printf(c, "        {\n"
                     "            unsigned forward_class = %s_forward_byte_class[subject[scan_position]];\n"'
