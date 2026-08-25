# S29 — the VF_ATSTART position check dropped: `x(*CR)` and every other
# start-of-pattern-only option stop being refused for POSITION, so a
# recognised option away from offset 0 falls through to "requires module
# 'verbs'" instead of the table's "not recognized" answer. MOD-0.4c.
SAB_ID="S29-verb-atstart-drop"
SAB_FILE="src/parse/mod_verbs.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_ext_verb: delete the (v->forms & VF_ATSTART) && at != 0 position check"
SAB_DOC_FIGURE="measured MOD-0.4c: 1 reject failure (the a(*CR) manifest pin); the same edit measured 20-capped via PC-3 — see tests/registry/CLAUDE.md sabotage table"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS A VF_ATSTART VERB AWAY FROM THE START -- the only
# population the deleted position check governs. `(*UTF)` at offset 1 is
# refused BY THAT CHECK on the clean tree; a `(*UTF)` at offset 0 compiles
# and would tell us nothing. If the verbs module ever BUILDS these names,
# the refusal disappears and this row needs a new witness rather than a
# verdict.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "a(*UTF)"'
SAB_REACH_EXPECT="(*VERB) not recognized or malformed (pattern offset 1)"
SAB_COUNT=1
SAB_BEFORE="    if ((v->forms & VF_ATSTART) && at != 0)
        REFUSE(at, \"%s\", t->unknown_msg);

    /* K14"
SAB_AFTER="    /* K14"
