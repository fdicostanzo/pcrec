# S437 (K79, lane k7980) -- THE EMITTERS SEE THE CALLER'S PREFIX AGAIN.
#
# compile_driver hands the emitters the two-byte render placeholder as
# `opt->prefix` and writes the caller's `-p` spelling onto the finished text,
# so every size-predicated selection is decided at a canonical prefix length.
# The plant hands them the real prefix instead -- the pre-abi-54 behaviour.
# Every artifact still compiles and answers correctly (the render simply finds
# nothing to rewrite), so the corpus is green by construction; what moves is
# SELECTION: the VM entry-shape knee is crossed by the prefix's own bytes
# (`(foo|bar)[0-9]{2,5}(x)` takes `inline` at -p rx and `plain` at 60 chars)
# and `<PREFIX>_VM_PROGRAM_BYTES` grows with the prefix. The detector is
# tests/codegen/run_prefix_invariance.sh (PART 1 full-text identity, PART 2
# value stamps, PART 3 the flipped witnesses).
SAB_ID="S437-k7980-emitters-see-real-prefix"
SAB_FILE="src/core/compile.c"
SAB_SUITES="prefixinv"
SAB_DESC="compile_driver passes the caller's -p prefix to the emitters instead of the render placeholder, so size-predicated selections (the VM entry shape) read the prefix's length again"
SAB_DOC_FIGURE="Read the current figure from a run (lane k7980 measured the detector against the pre-fix compiler: 9 of 9 checks red; docs/dev/lanes/k7980_report.md)."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "(foo|bar)[0-9]{2,5}(x)"'
SAB_REACH_EXPECT='#define RX_VM_ENTRY_SHAPE "inline"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    defo.prefix = PCREC_PREFIX_PLACEHOLDER;'
SAB_AFTER='    defo.prefix = user_prefix;'
