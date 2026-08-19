# S75 — [M6.2 wave B] `\b` READS A SECOND, DIFFERENT WORD SET.
#
# assertions_design.md §7.2 item 3: "pcrec already has the front-end answer and
# `\b` must reuse it, not copy it. `\w` compiles today from
# `pcrec_cls_word_esc`, oracle-generated against libpcre2 and re-measured by
# PC-4 every run. **Whatever `\w` means, `\b` must agree with**, and the only
# way to guarantee that is one definition with two readers. A second word-set
# spelling anywhere is this project's recorded check-design failure in its
# purest form."
#
# The sabotage points the VM's `\b` arm at a DIFFERENT generated set. That is
# the honest failure mode: nobody types out a 32-byte bitmap by hand, but
# `pcrec_cls_word_esc` sits in a file of near-identical neighbours
# (`_digit_esc`, `_space_esc`, `_hspace`, ...) and picking the wrong one is a
# one-token edit that compiles.
#
# WHAT SEES IT, and why the check needed BOTH of its assertions. Counting
# copies of the WORD bitmap does not: with `\b` reading the digit set the
# artifact still holds exactly one word bitmap, from `\w`. What sees it is the
# second assertion — `(\b\w+\b)` must emit exactly ONE class table in total,
# because the pattern names two constructs that must resolve to the same
# pooled set. Under this edit it emits two.
#
# WHAT THE CORPUS SAW, MEASURED RATHER THAN ASSUMED — and the measurement
# corrected this note's own first draft, which claimed "the corpus sees it
# too, loudly". On its first matrix run this row came back **UNDETECTED**:
# codegen 0fail/52pass AND corpus 0fail/3528pass. Two independent reasons,
# both worth keeping:
#
#  - the CHECK was blind. Its assertion at the time was "exactly one class
#    TABLE in the artifact", and the digit set is a contiguous RANGE, so it
#    compiles to a subtract-and-compare and emits no table at all. The rule
#    now counts distinct MEMBERSHIP TESTS, normalised over the byte
#    expression, which is blind to which of `vm_cls_test`'s three shapes a set
#    takes.
#  - the CORPUS was blind, and structurally. This edit is in `emit_vm.c`, and
#    every block in tests/assertions/wordb.rxt was capture-FREE, so every one
#    routed to the DFA and none reached the VM's `\b` arm. The file gained a
#    capture-bearing section in the same change; that section exists because
#    this row measured its absence.
#
# So the structural rule is not merely the cheaper instrument here — for the
# artifact class this edit lives in, it was for a while the ONLY one.
SAB_ID="S75-wordb-second-wordset"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/assertions/wordb.rxt"
SAB_DESC="the VM's \\b arm interns pcrec_cls_digit_esc instead of pcrec_cls_word_esc, so \\b and \\w disagree about what a word character is and the artifact carries two class tables where it must carry one (assertions_design.md S7.2 item 3)"
SAB_DOC_FIGURE="tests/codegen/run_codegen_tests.sh: [M6.2-WORDB rule 3] reports 2 class tables in '(\\b\\w+\\b)'s artifact"
SAB_COUNT=1
SAB_BEFORE='        int wi = vm_cls(v, pcrec_cls_word_esc);'
SAB_AFTER='        int wi = vm_cls(v, pcrec_cls_digit_esc);   /* SABOTAGE S75 */'
