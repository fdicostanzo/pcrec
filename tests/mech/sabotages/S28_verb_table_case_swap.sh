# S28 — pcrec_registry_verb_table returns the WRONG table for the first
# name byte: lowercase selects the upper (ACCEPT-family) table and
# non-lowercase selects the lower (pla-family) table, so unknown-name
# diagnostics and every name lookup cross tables. MOD-0.4c.
SAB_ID="S28-verb-table-case-swap"
SAB_FILE="src/parse/mod_verbs.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_registry_verb_table: swap the upper/lower table return so case selects the wrong one"
SAB_DOC_FIGURE="measured MOD-0.4c: 52 reject failures on first measurement, no new pin needed"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS A PAIR, because the sabotage SWAPS two tables and a
# single probe cannot see a swap: `(*FOO)` (upper) and `(*foo)` (lower)
# must produce DIFFERENT sentences, and both are asserted. One of them
# alone would go on passing after the other's table stopped being reached.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "(*FOO)"; "$PCREC" --features none -p rx -o "$REACH_TMP/o1.c" -- "(*foo)"'
SAB_REACH_EXPECT="(*VERB) not recognized or malformed (pattern offset 0)
(*alpha_assertion) not recognized (pattern offset 0)"
SAB_COUNT=1
SAB_BEFORE="    return (first >= 'a' && first <= 'z') ? &verb_tables[1] : &verb_tables[0];"
SAB_AFTER="    return (first >= 'a' && first <= 'z') ? &verb_tables[0] : &verb_tables[1];"
