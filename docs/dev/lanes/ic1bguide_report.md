# ic1bguide report: [INLINE-C] stage 1b, clear guidance for the `once` rule

## Summary
The `once` rule is unchanged (syntactic, on the pattern as written; no optimizer
proofs). Only the words changed: the refusal, the listing note and one spec
table. One behaviour-adjacent code change: `co_choice` now returns the
non-atomic lookaround itself (not its inner choice) as the live construct, so
the text can name it; WHICH sites are accepted is untouched (callouts suite:
87 checks passed, 59 corpus cases, 0 failed). Files: src/opt/callout.c,
docs/spec/match_api.md §11.8¶3-4, docs/spec/ir_listing.md §3.7¶2,
docs/spec/pattern_language.md §7.11¶3, tests/callouts/run_callouts_tests.sh,
tests/codegen/manifests/ir_listing_baseline/3ed51727.ir (re-baselined: the two
`note` cells), sabotages S1664-S1666.

## Refusal text
Every `once` refusal keeps construct, offset, fix. New for a live choice inside
a non-atomic lookaround: `the non-atomic lookaround at offset 0 keeps the
quantifier at offset 4 live after it completes; use (?=...) / (?!...) (atomic),
or wrap it: (?>(?*...))` (lookbehind spelling for `(?<*`). Nested lookarounds
descend to the innermost culprit. Quantifier / alternation / call texts are as
before. Observed, not changed (STOP RULE): `(?*a|b)(?C"x,once")c` is accepted,
because the parse hook turns a one-character-language lookaround body into a
context node (pcrec_look_t3) before the callout walk sees it; this is an
existing parse-time rewrite, flagged for the manager since it makes the rule
depend on that rewrite for this one shape.

## Spec table
match_api.md §11.8¶3 holds the one table (backtrackable construct -> fix, five
rows) and the as-written / flag-independent statement; §11.8¶4 lists what is
not backtrackable. §11.7, ir_listing §3.7 and pattern_language §7.11 point to it.
`make test-spec-history` passes (11 checks); the numbering/pre-commit spec
checks passed (79); scripts/spec_toc.py --check run on the three files.

## List-callouts reason
There is no `--list-callouts` flag; the per-site listing is `--emit-ir`'s
`callouts` section. Its `note` column was a generic sentence for a live-choice
site; it is now the same string the refusal uses (`why` is computed once in
co_site and the refusal prints it), and for a repeat site "inside the repeat
whose quantifier at offset N has a maximum of 2 or more". Test: the new arm-5
loop asserts the note is contained in the refusal for each culprit kind.

## Tests
tests/callouts/run_callouts_tests.sh arm 5: six refusal rows (greedy and lazy
quantifier, alternation, subroutine call, non-atomic lookaround, nested
lookaround) each checked for construct+offset+fix and note==reason; four fixes
checked accepted. `make test-callouts` green. Sabotages S1664 (lookaround not
named), S1665 (listing note generic), S1666 (fix wording cut) REACH_ONLY
reached 4/4 with S1660 (re-anchored to the new line). Full make test, mech and
axes are owed (below). `make test-spec` (D27 spec checks) cannot link here
(libpcre2 dev symbols), unrelated to this change.

## STATE AT HANDOFF
Branch lane/ic1b. Rulings file ic1bguide_rulings.md: no entries at the last
re-read. Committed. Owed (queued, not-before 2026-10-27T12:00, base = merge-base
9e0500443): 550-ic1bguide-test, 551-ic1bguide-mech (adds S1664-S1666),
552-ic1bguide-axes. Job files: docs/dev/lanes/ic1bguide_{test,mech,axes}_job.
