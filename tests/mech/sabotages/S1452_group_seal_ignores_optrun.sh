# S1452 — the group seal no longer covers a bare option run, so a group whose
# whole body is one inherits err 109 again: `(?:(?i))*a` refuses (K124).
# Lane langfix2; re-anchored by lane langfix3 (the seal clears the flag in
# place instead of wrapping, same intent).
SAB_ID="S1452-group-seal-ignores-optrun"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/optrun_group.rxt"
SAB_DESC="pcrec_wrap_bare_anchor: the flag clear is dropped, so the body node itself (still flagged) reaches p_rep"
SAB_DOC_FIGURE="PREDICTED: every accepted block of tests/modifiers/optrun_group.rxt whose group body is exactly one option run fails as a pattern-compile failure; the capturing/named/atomic/lookaround spellings too only where the body is returned unwrapped (non-capturing and scoped groups); the two-run control and the two perr controls stay green. Canonical figure owed from run_sabotage_matrix.sh S1452."
SAB_COUNT=1
SAB_BEFORE="    if (!pcrec_is_bare_anchor(body)) {
        body->not_repeatable = false;
        return body;"
SAB_AFTER="    if (!pcrec_is_bare_anchor(body)) {
        /* SABOTAGE S1452: the run keeps its flag */
        return body;"
