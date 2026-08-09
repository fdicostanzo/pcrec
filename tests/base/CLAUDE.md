# tests/base — base-tier regex test corpus

Comprehensive test suite for base-tier PCRE features: literals, character classes, quantifiers, alternation, anchors, groups, and basic escapes. Every expectation is cross-verified against python3 re to ensure semantics match PCRE for this tier.

## Files

- **literals.rxt** — literal character and substring matching
- **dot.rxt** — dot (.) matching (any byte)
- **classes.rxt** — character class [...] syntax and behavior
- **quantifiers.rxt** — *, +, ? quantifiers
- **bounded_repeats.rxt** — {m,n} repeat syntax
- **alternation.rxt** — | alternation and precedence
- **anchors.rxt** — ^ and $ anchors
- **groups.rxt** — (...) capturing and (?:...) non-capturing groups
- **escapes.rxt** — \\ \" \n \t metachar and control escapes
- **empty_matches.rxt** — patterns matching empty strings
- **precedence.rxt** — operator precedence and grouping
- **leftmost_semantics.rxt** — leftmost-first match semantics (greedy/lazy precedence)
- **syntax_errors.rxt** — malformed patterns and diagnostic accuracy

## Conventions

Format: `pattern <regex>` followed by `m "<subject>" START END` (match expected) or `n "<subject>"` (no match). Escapes in subjects (\" \\ \n etc) are encoded as literal backslash sequences for shell safety; driver.c decodes them. Run via `make test` or `bash tests/harness/run.sh tests/base/`.

Maintenance: update this file when .rxt files are added/removed or feature coverage changes.
