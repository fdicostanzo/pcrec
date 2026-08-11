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
SAB_BEFORE="static Ast *char_node(Ctx *cx, unsigned c)
{
    Ast *a = node(cx, A_CLASS);
    cls_set(a->cls, c & 0xff);
    if (cx->caseless) cls_casefold(a->cls);
    return a;
}"
SAB_AFTER="static Ast *char_node(Ctx *cx, unsigned c)
{
    Ast *a = node(cx, A_CLASS);
    cls_set(a->cls, c & 0xff);
    return a;
}"
