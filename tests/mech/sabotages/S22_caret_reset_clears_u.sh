# S22 — (?^) resets ungreedy too, contradicting the measured U-survives-^
# rule ([MOD-0.5a] ruling 3, probe_mod05b.c: "unset imnsx" is the rule, U
# and J both live through `(?^)`). MOD-0.5e.
SAB_ID="S22-caret-clears-ungreedy"
SAB_FILE="src/parse/mod_modifiers.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/reset.rxt"
SAB_DESC="pcrec_modport_optrun: (?^) no longer preserves ungreedy across the reset"
SAB_DOC_FIGURE="measured MOD-0.5e: 1 harness case (tests/modifiers/reset.rxt, the U-survives-(?^) block)"
SAB_COUNT=1
# RE-ANCHORED 2026-08-21 (sabanchors lane): [M6.2] wave A (parse_mods.h)
# renamed ModState to ParseMods and turned Ctx.mods into a pointer, so
# `ModState ns = cx->mods;` became `ParseMods ns = *cx->mods;` (both the
# type name and the deref changed). Intent (the (?^) reset also clears
# ungreedy, contradicting the measured U-survives-^ rule) unchanged.
# RE-ANCHORED AGAIN 2026-08-22 ([M6.5.2]): `(?^)` now preserves `dupnames`
# alongside `ungreedy`, because `(?J)(?<a>x)(?^)(?<a>y)` COMPILES in libpcre2
# 10.46 -- measured, not inherited from the letter list, and clearing it would
# turn a legal pattern into an error. The anchor spans the whole reset block
# so the flip still clears EVERY preserved letter rather than only the one
# that existed when the row was written; intent (the (?^) reset clears
# ungreedy, contradicting the measured U-survives-^ rule) unchanged.
SAB_BEFORE="    ParseMods ns = *cx->mods;
    if (caret) {
        bool keep_ungreedy = ns.ungreedy;"
SAB_AFTER="    ParseMods ns = *cx->mods;
    if (caret) {
        bool keep_ungreedy = false;   /* SABOTAGE S22: the reset clears U */"
