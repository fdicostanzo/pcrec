# S21 — cls_peek_past_dash reverts to a raw two-byte peek, blind through
# xx's class-interior deletion (MOD-0.5e; the D30 §7 hazard the module was
# reordered after `classes` to fix — docs/plan.md [MOD-0.5]). The
# dash-vs-literal lookahead must see THROUGH deletion for `(?xx)[a- ]` to
# compile to members {a,-} instead of a bogus a-SPACE range; this sabotage
# makes the lookahead see the raw (undeleted) byte instead.
SAB_ID="S21-cls-peek-raw"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/xxmode.rxt"
SAB_DESC="cls_peek_past_dash: drop the xlevel>=2 skip-through, peek the raw next byte"
SAB_DOC_FIGURE="measured MOD-0.5e: 3 harness cases fail of 11 in tests/modifiers/xxmode.rxt (the (?xx)[a- ] hazard block's m/n cells go from matching {a,-} to a bogus a-SPACE range or an outright compile error)"
SAB_COUNT=1
SAB_BEFORE="static int cls_peek_past_dash(Ctx *cx)
{
    size_t i = cx->pos + 1;
    if (cx->mods.xlevel >= 2)
        while (i < cx->patlen &&
               (cx->pat[i] == ' ' || cx->pat[i] == '\\t')) i++;
    return i < cx->patlen ? (unsigned char)cx->pat[i] : -1;
}"
SAB_AFTER="static int cls_peek_past_dash(Ctx *cx)
{
    size_t i = cx->pos + 1;
    return i < cx->patlen ? (unsigned char)cx->pat[i] : -1;
}"
