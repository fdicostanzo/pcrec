# S08 — p_class folds AFTER negating instead of before (OS-1 section of
# tests/codegen/CLAUDE.md table, row 1). "[^a]" caseless should mean "neither
# a nor A"; folding the complement instead yields every byte. Documented
# result: 1 codegen check ("-i '[^a]' is not '[^aA]'") + 6 caseless.rxt cases.
SAB_ID="S08-casefold-order"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/base/caseless.rxt"
SAB_DESC="p_class: move the cls_casefold() call from before the negation loop to after it"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 1 codegen check + 6 caseless.rxt cases"
SAB_COUNT=1
# RE-ANCHORED 2026-08-21 (sabanchors lane): [M6.2] wave A (parse_mods.h)
# turned Ctx.mods from a ModState struct value into a pointer to an
# incomplete ParseMods, so every `cx->mods.FIELD` site in this file became
# `cx->mods->FIELD`. Anchor text updated to match; the sabotage's intent
# (move the fold call from before the negation loop to after it) is
# unchanged.
# [M5.0 stage 1] RE-AIMED at the interval payload. The RULE is unchanged and
# so is this row's whole point — fold the POSITIVE set, then complement — but
# the two lines that spell it moved from a bitmap loop to `pcrec_cpset_*`
# calls, and the complement's universe now comes from the ENCODING
# (`cls_universe(cx)`, docs/design/utf8_design.md §2.7.1) rather than being the
# bitmap's implicit 0..255. Under `--encoding=byte` the two are the same
# function on the same set, which is why this row's detector corpus
# (tests/base/caseless.rxt) is unchanged and its cells are the same cells.
SAB_BEFORE="    if (cx->mods->caseless) cls_casefold(&set);
    if (neg) pcrec_cpset_complement(&set, cls_universe(cx));
    pcrec_cpset_publish(&set, a);
    return a;"
SAB_AFTER="    if (neg) pcrec_cpset_complement(&set, cls_universe(cx));
    if (cx->mods->caseless) cls_casefold(&set);
    pcrec_cpset_publish(&set, a);
    return a;"
