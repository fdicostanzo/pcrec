# S210 ([M4-QUOTING] mech review) — `cat_ends` STOPS PROTECTING AN OPEN QUOTE.
#
# WHAT IT BREAKS. `\Q...\E` reads straight through pattern structure — `)`,
# `|`, `(`, `[`, `]` are all just literal bytes while a quote is open, exactly
# as libpcre2 reads them (measured: `(a\Qb)c\E)` compiles identically on both
# — the `\Q` opens right after `a`'s atom, quotes "b)c" across the first `)`,
# and only the SECOND `)`, past `\E`, closes the group). `cat_ends` is where
# that has to be enforced: it decides whether a `)`/`|`/end-of-pattern has
# been reached BEFORE `p_cat`'s loop asks for another atom, and while a real
# quoted byte is pending it must say "no" regardless of what that byte's own
# VALUE is. This plant removes the whole `if (cx->in_quote) { ... }` guard,
# so `cat_ends` goes back to reading `)` and `|` off the raw byte at
# `cx->pos` even when that byte is quoted content.
#
# THE FAILURE MODE. On `(a\Qb)c\E)` the quoted `)` right after `b` is now
# read as a REAL group terminator: the group closes one atom early, `c\E)`
# is left dangling as top-level pattern text with `\E` an unmatched stray
# close (still harmlessly transparent) and a genuinely unmatched `)` after
# it — "unmatched closing parenthesis" (verified live on the sabotaged
# tree, pattern offset 9). The clean tree compiles the same pattern
# successfully (rc 0), so this is a straightforward flip from ACCEPT to
# REFUSE, not a subtler answer change.
#
# WHY NOTHING ELSE IN THE TREE CAN SEE IT. There is no tests/quoting/
# corpus yet (D27 reserves it for the blinded writer), and every OTHER
# `\Q...\E` shape a hand-written accept-control might use compiles under
# BOTH the clean and the sabotaged reading unless it specifically nests a
# quoted STRUCTURAL byte inside real pattern structure the way this one
# does — a `\Q...\E` with no `)`/`|`/`(` inside it is byte-for-byte
# unaffected by this guard either way. tests/reject/run_reject_tests.sh's
# new accept-control is therefore the row's only detector.
SAB_ID="S210-cat-ends-quote-guard-dropped"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="reject harness"
SAB_HARNESS_TARGET="tests/base/groups.rxt"
SAB_DESC="cat_ends's whole 'if (cx->in_quote) { ... }' guard is deleted, so a byte inside an OPEN \\Q...\\E quote is read as an ordinary ')'/'|'/end-of-pattern the instant its own VALUE looks like one -- '(a\\Qb)c\\E)' (quoted content \"b)c\") closes its group one atom early on the quoted ')' and the pattern becomes unbalanced, where the clean tree (and libpcre2) both compile it. No answer-checking corpus reaches it (no tests/quoting/ yet, and every other hand-written \\Q shape either has no structural byte inside the quote or is unaffected either way), so the accept-control tests/reject/run_reject_tests.sh added for this row is its only detector"
SAB_DOC_FIGURE="MEASURED via 'bash tests/mech/run_sabotage_matrix.sh S210' (single-row, PROCS=4) at 3122d96: DETECTED, reject:1fail/590pass, corpus:0fail/26pass (1 rows, unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0), matching the prediction exactly. Also verified by hand before wiring: clean tree compiles '(a\\Qb)c\\E)' rc 0; sabotaged tree refuses with 'unmatched closing parenthesis' at pattern offset 9, rc 1."
SAB_COUNT=1
SAB_BEFORE='static bool cat_ends(Ctx *cx)
{
    if (cx->in_quote) {
        if (peekc(cx) == '\''\\'\'' && peekc2(cx) == '\''E'\'') {
            cx->pos += 2;
            cx->in_quote = false;
        } else if (peekc(cx) < 0) {
            cx->in_quote = false;
        } else {
            return false;
        }
    }
    int c = peekc(cx);
    return c < 0 || c == '\''|'\'' || c == '\'')'\'';
}'
SAB_AFTER='static bool cat_ends(Ctx *cx)
{
    /* SABOTAGE S210: the in_quote guard is gone */
    int c = peekc(cx);
    return c < 0 || c == '\''|'\'' || c == '\'')'\'';
}'
