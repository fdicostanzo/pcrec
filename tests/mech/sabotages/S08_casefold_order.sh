# S08 — p_class folds AFTER negating instead of before (OS-1 section of
# tests/codegen/CLAUDE.md table, row 1). "[^a]" caseless should mean "neither
# a nor A"; folding the complement instead yields every byte. Documented
# result: 1 codegen check ("-i '[^a]' is not '[^aA]'") + 6 caseless.rxt cases.
# [M5.0 stage 4, lane utf8s4] RE-ANCHORED. Stage 4 made `cls_casefold` take the
# fold as a PARAMETER (the relation is the ENCODING's now, `PcrecEnc.fold`) and
# put the produced sets' union between the fold and the negation, so this row's
# recorded anchor no longer exists. The CLAIM is unchanged and was re-verified
# against the live source, not carried over: the fold must be applied to the POSITIVE set, before the negation, and the
# two lines swapped below are the same two lines the row has always aimed at.
# S-U1 is this row's utf8 SIBLING: the same edit, a DIFFERENT DETECTOR
# (tests/utf8 rather than tests/base/caseless.rxt), because the byte tier's
# witness ([^a] on A) and the cross-block one ([^k] on U+212A) are different
# populations and a single row would certify only one of them.
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
SAB_BEFORE="    if (cx->mods->caseless) cls_casefold(cx, &set, cls_enc(cx)->fold);
    pcrec_cpset_add_set(&set, prod.iv, prod.n);
    if (neg) pcrec_cpset_complement(&set, cls_universe(cx));"
SAB_AFTER="    /* SABOTAGE S08: negate first, then fold */
    pcrec_cpset_add_set(&set, prod.iv, prod.n);
    if (neg) pcrec_cpset_complement(&set, cls_universe(cx));
    if (cx->mods->caseless) cls_casefold(cx, &set, cls_enc(cx)->fold);"
