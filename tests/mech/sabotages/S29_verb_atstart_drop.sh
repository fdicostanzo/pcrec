# S29 — the VF_ATSTART position check dropped: `x(*CR)` and every other
# start-of-pattern-only option stop being refused for POSITION, so a
# recognised option away from offset 0 falls through to "requires module
# 'verbs'" instead of the table's "not recognized" answer. MOD-0.4c.
SAB_ID="S29-verb-atstart-drop"
SAB_FILE="src/parse/mod_verbs.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_ext_verb: delete the (v->forms & VF_ATSTART) && at != 0 position check"
SAB_DOC_FIGURE="measured MOD-0.4c: see landing report for the failing-direction result"
SAB_COUNT=1
SAB_BEFORE="    if ((v->forms & VF_ATSTART) && at != 0)
        REFUSE(at, \"%s\", t->unknown_msg);

    /* K14"
SAB_AFTER="    /* K14"
