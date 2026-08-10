# tests/base — base-tier regex test corpus

Comprehensive test suite for base-tier PCRE features: literals, character classes, quantifiers, alternation, anchors, groups, and basic escapes. Every expectation is cross-verified against python3 re to ensure semantics match PCRE for this tier.

## Files

- **literals.rxt** — literal character and substring matching
- **dot.rxt** — dot (.) matching (any byte)
- **classes.rxt** — character class [...] syntax and behavior
- **quantifiers.rxt** — *, +, ? quantifiers
- **bounded_repeats.rxt** — {m,n} repeat syntax
- **alternation.rxt** — | alternation and precedence
- **alternation_trie.rxt** — priority hazards of M2.8 prefix-trie factoring (D9): shorter-branch-first shapes, overlapping-but-distinct classes, mixed eligible/ineligible runs. Each guard is sabotage-validated — disabling the disjointness guard fails 2 cases, disabling index-range partitioning fails 7
- **anchors.rxt** — ^ and $ anchors
- **eol_engine.rxt** — M2.7 regressions: `$` patterns on the O(n) unanchored engine
- **eol_scan_avoidance.rxt** — M2.12 regressions: prefilter/skip loops restored on the `$` path (D11). The original 13 patterns all failed the first M2.12 attempt, which bounded skips at n-1 but still evaluated the EOL view before the skip ran. R3.4 adds the other half of D11's interaction, which had no case at all: a forward skip state whose PLAIN accept flag is set, so `last` must survive a skip that crosses already-accepting positions. Both halves are sabotage-validated and need different patterns — restricting the EOL accept to the boundary fails 3 cases of `a.*|b$` / `a[^\n]*|\n$`, dropping the non-EOL post-skip `last = pos` fails 10 cases of `[a-z].*|q$` / `a.*|b` / `=.*|;`, and the original 13 catch NEITHER
- **groups.rxt** — (...) capturing and (?:...) non-capturing groups
- **escapes.rxt** — \\ \" \n \t metachar and control escapes
- **empty_matches.rxt** — patterns matching empty strings
- **precedence.rxt** — operator precedence and grouping
- **leftmost_semantics.rxt** — leftmost-first match semantics (greedy/lazy precedence)
- **syntax_errors.rxt** — malformed patterns and diagnostic accuracy, including the K5/K6 brace miscompiles fixed 2026-08-10 (FIX-1). Two halves that must be read together: the `perr` blocks assert the rejections, and the literal-match blocks below them assert what must KEEP compiling (`a{`, `{}`, `{,}`, `a{65536x}`, …) — without those, the obvious over-reach of either fix passes every rejection. The seven K5 blocks carry `# pcre2-only` because python `re` accepts counts up to 4294967296 (U5); `tests/reject/` pins the DIAGNOSTIC for all of them, which `perr` cannot express

## Conventions

Format: `pattern <regex>` followed by `m "<subject>" START END` (match expected) or `n "<subject>"` (no match). Escapes in subjects (\" \\ \n etc) are encoded as literal backslash sequences for shell safety; driver.c decodes them. Run via `make test` or `bash tests/harness/run.sh tests/base/`.

Maintenance: update this file when .rxt files are added/removed or feature coverage changes.
