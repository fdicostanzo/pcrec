# S09 — char_node stops folding: classes still fold (via p_class) but bare
# literal escapes/chars do not (OS-1 section of tests/codegen/CLAUDE.md
# table, row 2). Documented result: 1 codegen check + 14 caseless.rxt cases.
SAB_ID="S09-casefold-delete"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/base/caseless.rxt"
SAB_DESC="char_node: delete the cls_casefold() call (literals stop folding under -i)"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 1 codegen check + 14 caseless.rxt cases"
SAB_COUNT=1
# RE-ANCHORED 2026-08-21 (sabanchors lane): same drift as S08 —
# Ctx.mods became a pointer to ParseMods at [M6.2] wave A, so
# \`cx->mods.caseless\` became \`cx->mods->caseless\`. Intent (delete the
# fold call) unchanged.
# [M5.0 stage 1] RE-AIMED at the interval payload: \`char_node\` builds into a
# \`PcrecCpSet\` and publishes once. The deletion this row makes, and everything
# it detects, is unchanged — a literal stops folding while classes keep doing
# it, which is what makes its symptom disjoint from S08's.
SAB_BEFORE="    Ast *a = node(cx, A_CLASS);
    PcrecCpSet s;
    pcrec_cpset_init(&s, &cx->arena);
    /* [M5.0 stage 2] no \`& 0xff\` mask any more: \`c\` is a CODE POINT. Every
     * pre-stage-2 caller passed a byte, for which the mask was the identity;
     * the new callers (\`\x{...}\`, the multi-byte literal reader) pass values
     * the parser has already range-checked against the encoding's universe,
     * and masking one would silently alias U+0141 onto 'A'. */
    pcrec_cpset_add(&s, c, c);
    if (cx->mods->caseless) cls_casefold(&s);
    pcrec_cpset_publish(&s, a);
    return a;"
SAB_AFTER="    Ast *a = node(cx, A_CLASS);
    PcrecCpSet s;
    pcrec_cpset_init(&s, &cx->arena);
    /* [M5.0 stage 2] no \`& 0xff\` mask any more: \`c\` is a CODE POINT. Every
     * pre-stage-2 caller passed a byte, for which the mask was the identity;
     * the new callers (\`\x{...}\`, the multi-byte literal reader) pass values
     * the parser has already range-checked against the encoding's universe,
     * and masking one would silently alias U+0141 onto 'A'. */
    pcrec_cpset_add(&s, c, c);
    pcrec_cpset_publish(&s, a);
    return a;"
