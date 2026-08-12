# S28 — pcrec_registry_verb_table returns the WRONG table for the first
# name byte: lowercase selects the upper (ACCEPT-family) table and
# non-lowercase selects the lower (pla-family) table, so unknown-name
# diagnostics and every name lookup cross tables. MOD-0.4c.
SAB_ID="S28-verb-table-case-swap"
SAB_FILE="src/parse/mod_verbs.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_registry_verb_table: swap the upper/lower table return so case selects the wrong one"
SAB_DOC_FIGURE="measured MOD-0.4c: see landing report for the failing-direction result"
SAB_COUNT=1
SAB_BEFORE="    return (first >= 'a' && first <= 'z') ? &verb_tables[1] : &verb_tables[0];"
SAB_AFTER="    return (first >= 'a' && first <= 'z') ? &verb_tables[0] : &verb_tables[1];"
