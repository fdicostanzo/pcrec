# S1392 — a malformed `\p` with module unicode-props ENABLED asks for the
# module again ("requires module 'unicode-props'"), the speclang finding-6
# shape lane langfix fixed. The open-gate pins in tests/reject/ catch it.
SAB_ID="S1392-uprops-malformed-promises"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="reject"
SAB_DESC="UP_MALFORMED: the open-gate (WANT_RESULT) branch dropped, so the module is promised at either gate"
SAB_DOC_FIGURE="PREDICTED: 2 reject_gated rows ('\\p{L', '\\p!' under unicode-props). Canonical figure owed from run_sabotage_matrix.sh S1392."
SAB_COUNT=1
SAB_BEFORE="        if (want == WANT_RESULT)                                             \\
            REFUSE((pos), \"\\\\%c: malformed property escape\", sel);         \\"
SAB_AFTER='        (void)want;  /* SABOTAGE S1392 */                                \\'
