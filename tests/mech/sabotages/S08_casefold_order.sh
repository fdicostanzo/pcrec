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
SAB_BEFORE="    if (cx->mods->caseless) cls_casefold(a->cls);
    if (neg)
        for (int i = 0; i < 32; i++) a->cls[i] = (uint8_t)~a->cls[i];
    return a;"
SAB_AFTER="    if (neg)
        for (int i = 0; i < 32; i++) a->cls[i] = (uint8_t)~a->cls[i];
    if (cx->mods->caseless) cls_casefold(a->cls);
    return a;"
