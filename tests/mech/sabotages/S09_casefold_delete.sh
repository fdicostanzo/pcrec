# S09 — char_node stops folding: classes still fold (via p_class) but bare
# literal escapes/chars do not (OS-1 section of tests/codegen/CLAUDE.md
# table, row 2). Documented result: 1 codegen check + 14 caseless.rxt cases.
# [M5.0 stage 4, lane utf8s4] RE-ANCHORED. Stage 4 made `cls_casefold` take the
# fold as a PARAMETER (the relation is the ENCODING's now, `PcrecEnc.fold`) and
# put the produced sets' union between the fold and the negation, so this row's
# recorded anchor no longer exists. The CLAIM is unchanged and was re-verified
# against the live source, not carried over: a literal atom's own constructor must fold. The anchor is now the ONE line
# that does it in `char_node`, which is tighter than the whole-body anchor the
# row carried before and cannot be staled by an edit to the comment above it.
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
SAB_BEFORE="    if (cx->mods->caseless) cls_casefold(cx, &s, cls_enc(cx)->fold);"
SAB_AFTER="    /* SABOTAGE S09: the literal constructor stops folding */"
