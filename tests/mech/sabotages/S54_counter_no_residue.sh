# S54 — [ENG-BREP counter-K] THE RESIDUE TAIL DELETED.
#
# A phase of `count` iterations emits `floor(count/K)` trips of K copies plus a
# tail of `count mod K` copies. Zeroing the residue makes the emitted loop cover
# only the multiple-of-K part, so `{0,12}` at K=8 becomes `{0,8}` — a quantifier
# that matches strictly fewer iterations than it promises.
#
# IT IS INVISIBLE AT EVERY COUNT THE RESIDUE IS ALREADY ZERO, which is the whole
# reason patterns.txt is built on a RESIDUE AXIS rather than on round numbers.
# At `{0,8}`, `{0,16}`, `{0,24}` this sabotage changes nothing at all; it is
# detectable only where `count mod K != 0`. A population whose counts happened
# to share the residue 0 would report this row UNDETECTED and be telling the
# truth about itself while saying nothing about the emitter.
SAB_ID="S54-counter-no-residue"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="counterkdiff"
SAB_DESC="the counter phase's residue tail is emitted at zero copies, so the quantifier silently loses its count mod K iterations"
SAB_DOC_FIGURE="docs/design/counterk_impl/counterk_design.md §3.2, the residue is a compile-time constant"
SAB_COUNT=1
SAB_BEFORE='    const int residue = count % K;'
SAB_AFTER='    const int residue = 0;  /* SABOTAGE S54 */'
