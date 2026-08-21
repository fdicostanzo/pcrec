# S86 — [M6.2 WAVE E] THE `\K` WRITE IS NOT TRAILED.
#
# THE CLAIM IT IS THE FAILING DIRECTION OF is assertions_design.md §6.2's one
# operative word: the `caps[0][0] = pos` write is "trailed like any other
# capture write, because `\K` inside a quantifier must be undone on backtrack
# exactly as a group start is". S85 guards where the value is READ from; this
# row guards whether it can be TAKEN BACK.
#
# THE SABOTAGE writes `stv[0]` directly instead of through `<PREFIX>_SET`,
# which is the macro that first records the slot's OLD value on the trail. The
# value written is identical, the slot is identical, the emitted line is one
# token shorter. What is lost is the undo — so a `\K` crossed on a path that
# LOSES stays crossed.
#
# MEASURED, and the two shapes fail differently, which is why the corpus
# carries both:
#
#     (?:a\K|ax)c   on "axc"    libpcre2 (0,3)   sabotaged (1,3)
#         the `a\K` branch writes 1, its follow fails, `ax` wins — and the
#         winning path never crossed a `\K` at all, so the correct answer is
#         the plain match start. A write that cannot be undone reports the
#         LOSING branch's position.
#
#     (?:a\K)*ab    on "aaab"   libpcre2 (2,4)   sabotaged (3,4)
#         the greedy loop writes 1, 2, 3; the follow fails at 3; the retreat
#         to two iterations succeeds. The correct answer needs the write of 3
#         GONE and the write of 2 STANDING — which is why the trail is exact
#         old-value RESTORE and not a clear (engine_m4.md §3.2). A sabotage
#         that cleared instead of restoring would get this cell wrong too, and
#         the first one right; only both cells together pin the mechanism.
#
# WHY IT IS A SEPARATE ROW FROM S85 rather than a second edit in it: the two
# defects have DISJOINT symptoms in the structural check. S85 fires rule 1's
# "caps_out still contains the unconditional caps[0][0] = start" branch; this
# one fires rule 1's "writes stv[0] DIRECTLY rather than through RX_SET"
# branch, and leaves caps_out completely correct. A single row exercising both
# would let either branch rot undetected behind the other.
#
# WHAT IT IS MEASURED TO MOVE:
#     tests/codegen/run_codegen_tests.sh   [M6.2-KRESET rule 1] RED, naming
#                                          the direct write.
#     tests/assertions/kreset.rxt          RED on SIX cases and green on all
#                                          the rest — the two UNDO families
#                                          and nothing else, which is itself
#                                          the evidence those sections are not
#                                          decoration and the reason the
#                                          corpus carries them at all.
#     run_kreset_diff.sh                   RED in §1 and §2.
#
# MEASURED through the CANONICAL DRIVER (`run_sabotage_matrix.sh S86`,
# 2026-08-19, tree 6ced17f): **codegen:1fail/55pass, corpus:6fail/590pass,
# kresetdiff:3fail/6pass -- DETECTED.**
# Compare S85's 210 failing cases on the same corpus: a wrong-PROVENANCE bug
# is wrong nearly everywhere and a missing-UNDO bug is wrong in SIX places,
# which is exactly why the second one needs a corpus written to contain those
# six rather than a sweep hoping to wander into them.
SAB_ID="S86-kreset-write-untrailed"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness kresetdiff"
SAB_HARNESS_TARGET="tests/assertions/kreset.rxt"
SAB_DESC="the emitted \\K write goes straight to stv[0] instead of through <PREFIX>_SET, so it is never recorded on the trail and a backtrack cannot undo it. A \\K crossed on a LOSING path stays crossed: '(?:a\\K|ax)c' on \"axc\" answers (1,3) where PCRE2 answers (0,3), and '(?:a\\K)*ab' on \"aaab\" answers (3,4) where PCRE2 answers (2,4)"
SAB_DOC_FIGURE="codegen:1fail/55pass,corpus:6fail/590pass,kresetdiff:3fail/6pass -- DETECTED (canonical matrix run, 2026-08-19)"
SAB_COUNT=1
SAB_BEFORE='        vm_set(v, 0, "(ptrdiff_t)scan_position",
               "\\K resets the reported start of the match to here");'
SAB_AFTER='        sb_printf(b, "    slot_values[0] = (ptrdiff_t)scan_position;\n");   /* SABOTAGE S86 */'
