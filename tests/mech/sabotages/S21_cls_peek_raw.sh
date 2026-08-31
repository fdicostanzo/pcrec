# S21 — cls_peek_past_dash reverts to a raw two-byte peek, blind through
# xx's class-interior deletion (MOD-0.5e; the D30 §7 hazard the module was
# reordered after `classes` to fix — docs/dev/plan_completed.md [MOD-0.5]). The
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
# RE-ANCHORED 2026-08-21 (sabanchors lane): same drift as S08/S09 —
# Ctx.mods became a pointer to ParseMods at [M6.2] wave A, so
# `cx->mods.xlevel` became `cx->mods->xlevel`. Intent (drop the
# xlevel>=2 skip-through) unchanged.
# ANCHOR RE-DERIVED 2026-08-31 from the live file: [M4-QUOTING] rewrote
# cls_peek_past_dash into a for(;;) that also dissolves empty \Q\E pairs;
# this row's subject is ONLY the xx ws-deletion, so the anchor narrows to
# that branch and the quoting branch is left untouched by the plant.
SAB_BEFORE="        if (cx->mods->xlevel >= 2)
            while (i < cx->patlen &&
                   (cx->pat[i] == ' ' || cx->pat[i] == '\\t')) i++;"
SAB_AFTER="        /* SABOTAGE S21: xx ws-deletion dropped from the dash lookahead */"
