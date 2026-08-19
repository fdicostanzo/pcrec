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
# The corpus sees it too, loudly, which is what makes this row cheaper than
# S71/S73 rather than more valuable: a `\b` that fires at digit boundaries is
# a wrong answer on ordinary subjects. The row is here because the STRUCTURAL
# rule is the one that would still hold if the two sets happened to agree on
# the corpus's alphabet, and because §7.2's whole argument is about a drift
# that has not happened yet.
SAB_ID="S75-wordb-second-wordset"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/assertions/wordb.rxt"
SAB_DESC="the VM's \\b arm interns pcrec_cls_digit_esc instead of pcrec_cls_word_esc, so \\b and \\w disagree about what a word character is and the artifact carries two class tables where it must carry one (assertions_design.md S7.2 item 3)"
SAB_DOC_FIGURE="tests/codegen/run_codegen_tests.sh: [M6.2-WORDB rule 3] reports 2 class tables in '(\\b\\w+\\b)'s artifact"
SAB_COUNT=1
SAB_BEFORE='        int wi = vm_cls(v, pcrec_cls_word_esc);'
SAB_AFTER='        int wi = vm_cls(v, pcrec_cls_digit_esc);   /* SABOTAGE S75 */'
