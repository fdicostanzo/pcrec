# ic1bwritten report: the `once` rule sees the lookaround as written

## Summary
`(?*a|b)(?C"x,once")c` was accepted while `(?:a|b)(?C"x,once")c` was refused: the parse-time lookaround rewrite (`pcrec_look_t3`, row `ctx-node`) turned a one-character non-atomic lookaround into an `A_CTX` node before `pcrec_callout_sites` ran, hiding its alternation. Fixed generally: the rewrite records the as-written lookaround on the node it builds, and `co_choice` reads it. Refusals now name the lookaround, the inner construct, offsets and the fix. No emitted byte moves.

## Rewrite survey
Rewrites before `pcrec_callout_sites` (parse, the compose/derive hooks): probed ~65 patterns with a `once` site after the construct (variable quantifier, alternation, call, atomic and non-atomic lookaround, `{1}`/`{0}` folds, `(?i:...)`, possessive, nested lookarounds). Result against the §11.8¶3 table: the ONLY hole is `pcrec_look_t3`. Affected before the fix: any `(?*X)` / `(?<*X)` whose body is a single-byte-character language AND holds an alternation (`(?*a|b)`, `(?<*a|b)`, `(?*(?:a|b))`, `(?*[ab]|c)`, `(?*a{1}|b)`, nested `(?*(?*a|b))`). Not holes: `(?*[ab])`, `(?*.)` (no choice inside), atomic lookarounds, `x{1}`/`x{0}` folds (stay refused/inert as written), compose/derive output (inert `rmax 0` groups), bodies with quantifiers (not a single-char language, so no A_CTX). Module-gated constructs (`(?|`, conditionals, verbs, `\R`, `\X`) are not implemented and refuse earlier.

## Fix
- `src/core/internal.h`: `u.ctx.written`, the `A_LOOK` as written (off-tree, never walked).
- `src/parse/mod_lookaround.c`: records it when the lookaround is non-atomic.
- `src/opt/callout.c`: `co_choice` on `A_CTX` returns `co_choice(written)`; the lookaround arm, `co_culprit` and `co_at` are unchanged, so no special case in the walk.
- `docs/spec/match_api.md` §11.8¶3: one sentence.

## Tests
- tests/callouts arm 5: five refusal rows (alternation under `(?*`, `(?<*`, `(?*(?:...))`, `(?*[ab]|c)`, nested) plus three accepted rows (`(?>(?*a|b))`, `(?=a|b)`, `(?*[ab])`). `make test-callouts`: 100 passed, 0 failed.
- Sabotages S1667 (fact unread), S1668 (fact unrecorded), S1669 (recorded atomic); fields validated (VALIDATE_ONLY), rows owed in the mech job.
- Byte-neutrality: `scripts/emit_sweep.py --ref <previous head>`, streams c-default, c-vm, emit-ir: population 6218, movers=0, asymmetric=0 in all three; DONE rc=0.

## STATE AT HANDOFF
Rulings file: no entries ("none yet"). Owed (queued, not-before 2026-10-27T12:00): 550-ic1bwritten-test, 551-ic1bwritten-mech (32 rows incl. S1667-S1669), 552-ic1bwritten-axes. The make test, strict, the full movers census and the mech/axes verdicts are OWED.
