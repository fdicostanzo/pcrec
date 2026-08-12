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
SAB_BEFORE="    ModState ns = cx->mods;
    if (caret) {
        bool keep_ungreedy = ns.ungreedy;
        ns = (ModState){0};
        ns.ungreedy = keep_ungreedy;
    }"
SAB_AFTER="    ModState ns = cx->mods;
    if (caret) {
        ns = (ModState){0};
    }"
