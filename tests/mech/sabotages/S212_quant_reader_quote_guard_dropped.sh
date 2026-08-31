# S212 ([M4-QUOTING] TIER-1 MISCOMPILE, found by the D27 corpus on the
# merged tree, 2026-08-31) — THE QUANTIFIER READER STOPS PROTECTING AN
# OPEN QUOTE.
#
# WHAT IT BREAKS. `p_rep`'s quantifier-detection loop reads `*`/`+`/`?`/`{`
# off the RAW byte at `cx->pos` after `xskip`. While a quote is open with
# real content pending, `xskip` is a no-op (see its own comment: every
# byte there is quoted content, never skippable) -- so without this guard,
# a quantifier-shaped BYTE VALUE inside a non-empty `\Q...\E` span is read
# as a LIVE quantifier on the atom immediately before it, exactly as if it
# were unquoted. `\Qa*b\E` (measured against libpcre2 10.46: the module's
# only oracle, since python has no `\Q` at all) is the three-byte literal
# "a*b" -- ONE match spanning all three bytes, subject "aaab" NOMATCH. The
# sabotaged tree instead compiles `a*` (a REAL quantified atom) followed by
# the literal `b`: on subject "a*b" the search retries at every start
# position and only finds `b` alone at offset 2 once `a*` backs off to
# zero repetitions (MEASURED on the sabotaged build: `match 2 3`, not the
# clean tree's `match 0 3`), and on subject "aaab" it now WRONGLY matches
# (MEASURED: `match 0 4`, where the clean tree correctly answers nomatch)
# -- the two-directional flip that makes this a tier-1 miscompile rather
# than a refusal.
#
# WHY NOTHING IN THIS LANE'S OWN VALIDATION CAUGHT IT FIRST, recorded
# because the lesson generalises past this one row: the lane's own
# differential probe set tested the STRUCTURAL metacharacters (`)` `(` `[`
# `]` `|`) as literal quoted content extensively, and tested the
# BOUNDARY-TRANSPARENCY axis (empty `\Q\E`, a quantifier immediately AFTER
# a closed quote) exhaustively -- but never enumerated "a quantifier
# metacharacter as ORDINARY quoted content, with more quoted text
# following it inside the SAME open quote" as its own axis, even though it
# is a direct corollary of the module's own first semantics rule ("no
# metacharacters inside \Q...\E"). An absent test case, not a broken
# harness or a misread oracle -- confirmed by grep over every probe file
# the lane wrote before this fix: no `a*b`/`a+b`/`a?b`/`a{2,3}` shape
# appears anywhere in them.
#
# THE FIX AND WHAT IT DELIBERATELY LEAVES UNCHANGED. The guard mirrors
# `p_atom`'s own top-of-function `if (cx->in_quote) return p_quote_next
# (cx);` one level up: while a quote is open there is a real quoted byte
# pending (`cat_ends`/`xskip` both close an EXHAUSTED quote -- on `\E` or
# true end -- before control ever reaches here), so quantifier-scanning
# for the CURRENT atom stops exactly as it already does for any other
# non-quantifier byte, and the quoted byte becomes its OWN literal atom on
# `p_cat`'s next iteration. It does NOT touch the two measured
# transparency properties the lane's probes DO cover and which must keep
# passing: an EMPTY `\Q\E` never sets `cx->in_quote` at all (so `a\Q\E*`
# still compiles to ONE bytecode node, `*` reaching `a`), and a quantifier
# immediately after a quote CLOSES still binds to the last quoted atom
# (`\Qab\E*` unaffected -- the guard cannot fire there, since `in_quote`
# reads false by the time this line is reached for `b`, per `xskip`'s own
# close-on-`\E` at the SAME quantifier-check call).
#
# THE HARNESS TARGET HAS NO tests/quoting/ CORPUS YET IN THIS TREE.
# D27 reserves that corpus for a blinded writer denied src/tests, on
# branch qd27; SAB_HARNESS_TARGET below names the file it delivers,
# tests/quoting/d27/basics.rxt, which merges into this history right after
# this fix lands. The manager validates this row SOLO, POST-MERGE, once
# that file exists -- this lane confirmed the definition's own FIELDS
# (VALIDATE_ONLY=1) and the anchor's exact-once match against
# src/parse/parse.c, and separately hand-verified the sabotage's predicted
# flip against a scratch build (below), but could not run the row itself
# against its own detector before that corpus lands.
SAB_ID="S212-quant-reader-quote-guard-dropped"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/quoting/d27/basics.rxt"
SAB_DESC="p_rep's quantifier-detection loop drops its 'if (cx->in_quote) break;' guard, so a quantifier-shaped BYTE VALUE (*, +, ?, {) inside a non-empty \\Q...\\E span is read as a LIVE quantifier on the preceding quoted atom instead of ordinary literal content. '\\Qa*b\\E' flips from the libpcre2-measured 3-byte literal (subject 'a*b' matches whole at 0 3, 'aaab' nomatch) to a real quantified 'a*' followed by literal 'b' (subject 'a*b' matches only 'b' at 2 3, subject 'aaab' WRONGLY matches at 0 4) -- a tier-1 miscompile, not a refusal. Found by the D27 blinded corpus (branch qd27) on the merged tree; the lane's own differential probe set never enumerated this axis (structural metacharacters and the empty-quote/post-close transparency axis were both tested exhaustively, quantifier-metacharacters-as-ordinary-quoted-content was not). Its only detector is tests/quoting/d27/basics.rxt (D27 corpus, not yet merged into this branch), so the manager validates this row solo post-merge"
SAB_DOC_FIGURE="PREDICTED (this row's detector corpus is not in this tree yet -- see the header): harness:>0fail on tests/quoting/d27/basics.rxt, on whichever of its cells exercise a quantifier-shaped byte inside a non-empty quote. MEASURED instead on a scratch build (this lane, 2026-08-31, pre-merge, reverted clean after): sabotaged tree compiles '\\Qa*b\\E' to a live 'a*' + literal 'b' -- subject 'a*b' -> 'match 2 3' (clean tree: 'match 0 3'), subject 'aaab' -> 'match 0 4' (clean tree: nomatch). Canonical figure owed from run_sabotage_matrix.sh S212, post-qd27-merge."
SAB_COUNT=1
SAB_BEFORE='        if (cx->in_quote) break;
        int c = peekc(cx);
        int rmin, rmax;'
SAB_AFTER='        int c = peekc(cx);
        int rmin, rmax;'
