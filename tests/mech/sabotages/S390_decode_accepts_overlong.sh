# S390 ([CLS-TREE] S4, lane s4build) -- THE ONE-CHARACTER DECODE ACCEPTS AN
# OVERLONG FORM.
#
# THE CLAIM (cls_tree_design.md §2.2): `$_decode` rejects exactly the lowered
# automaton's ill-formed set, so a wide class tested by decode + kit on the VM
# and the same class walked as a byte alternation (DFA, or `-fno-cls-kit`)
# reject the same bytes. The plant drops the overlong floor, so `C0 80`
# decodes to U+0000 and `E0 80 80` to U+0000 -- members of `[^a]`, `.`,
# `\P{L}` and `\P{Unknown}` -- and the VM matches where the automaton does not.
#
# THE WITNESS IS A SUBJECT: tests/utf8/wclass_illformed.rxt's `engine vm`
# blocks with the overlong cells (the default-engine blocks stay green,
# which is the row's own point: only the kit route moved).
SAB_ID="S390-decode-accepts-overlong"
SAB_FILE="src/enc/enc_utf8.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8/wclass_illformed.rxt"
SAB_DESC="the utf8 backend's one-character decode (\$_decode) loses its overlong floor, so an overlong 2-4 byte form decodes to a small code point that the kit route then accepts"
SAB_DOC_FIGURE="PREDICTED: the engine-vm blocks of tests/utf8/wclass_illformed.rxt whose class holds U+0000 (PL, PUnknown, notA, dot) red on their overlong2/overlong3/overlong4 cells; the default-engine blocks green."
SAB_REACH='"$PCREC" -e utf8 --engine=vm -p rx -o - --pattern "x[^a]y"'
SAB_REACH_EXPECT='rx_decode(subject, subject_length, scan_position'
SAB_REACH_POP='tests/utf8/wclass_illformed.rxt|xc0.x80|8'
SAB_COUNT=1
SAB_BEFORE='"    if (v < floor || v > 0x10FFFFu || (v >= 0xD800u && v <= 0xDFFFu)) return 0;\n"'
SAB_AFTER='"    if (v > 0x10FFFFu || (v >= 0xD800u && v <= 0xDFFFu)) return 0;\n"'
