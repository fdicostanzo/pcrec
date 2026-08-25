# S30 — the unknown-name REFUSE at mod_verbs.c:329 blames `nstart` (the
# name's own start, one past the '*') instead of `at` (the doorway's
# default, the '('). Same message text either way ("(*VERB) not recognized
# or malformed" / "(*alpha_assertion) not recognized"), so this is the
# generalized shape of S27's finding: a "blame the name more precisely"
# refactor at any of the doorway's message-only REFUSE(at, ...) sites is
# invisible to a check that reads the text and not the offset. MOD-0.4d.
SAB_ID="S30-verb-unknown-name-blames-nstart"
SAB_FILE="src/parse/mod_verbs.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_ext_verb: the unknown-name REFUSE blames nstart (the name start) instead of at (the doorway default)"
SAB_DOC_FIGURE="measured MOD-0.4d: see landing report for the failing-direction result (both directions)"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS AN OFFSET, as S27's is: the sabotage moves the
# unknown-name blame from `at` (the doorway default, offset 0) to `nstart`
# (the name start), and the sentence is identical either way. Asserting
# `(pattern offset 0)` is asserting the thing that moves.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "(*FOO)"'
SAB_REACH_EXPECT="(*VERB) not recognized or malformed (pattern offset 0)"
SAB_COUNT=1
SAB_BEFORE="    if (!v) REFUSE(at, \"%s\", t->unknown_msg);"
SAB_AFTER="    if (!v) REFUSE(nstart, \"%s\", t->unknown_msg);"
