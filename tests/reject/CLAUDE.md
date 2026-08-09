# tests/reject — the "never miscompile" mandate, tested

The project rule is that a construct outside the base tier must fail with a
clean `requires module 'X'` error and never miscompile. Until 2026-08-09
nothing checked that, and the gap was not hypothetical — see below.

## Files

- **run_reject_tests.sh** — 85 constructs asserted to be rejected, plus 12
  accept-controls. Part of `make test`; env: PCREC, KEEP=1.

## Why it cannot live in the .rxt corpus

A `.rxt` `perr` block requires the python oracle to ALSO fail to compile the
pattern (`verify_rxt.py` fails the block if `re.compile` succeeds). Python
happily compiles `\d`, `\b`, `(?i)`, `\p{L}` and nearly every other
module-routed construct, so none of them could be asserted there. The
`# pcre2-only` escape hatch does not help either: `verify_rxt.py` consults
`cur_skip` only on `m`/`n` lines, never in its `perr` branch.

A `perr` block also could not express the part that matters most — that the
diagnostic names the RIGHT module. That name is the caller's only pointer to
what would implement the construct.

## What each row asserts

1. exit status is exactly **1** — not 0 (accepted, therefore possibly
   miscompiled) and not >= 124 (crash/timeout). A crash must never satisfy a
   rejection expectation; the .rxt harness applies the same rule to `perr`
   (R1 P-C1).
2. the diagnostic contains the expected `requires module 'NAME'` text.
3. no output file is left behind by a failed compile.

## The accept-controls are not optional

A parser that rejected EVERYTHING would score 100% on a table made only of
rejections. The 12 `accept` rows (literals, alternation, groups, every
quantifier form, classes, `.`, anchors, the character escapes, escaped
punctuation) are what stop that, and they are the same lesson the trie
identity check learned the hard way — a control has to sit inside the range of
what it certifies. The summary also enforces a floor on both counts, so
deleting coverage fails rather than quietly shrinking the table.

## The bug that motivated this

`\v` was decoded as vertical tab (0x0B). PCRE2 defines it as vertical
WHITESPACE — measured against libpcre2 10.46, `\v` matches 0x0a 0x0b 0x0c 0x0d
0x85. Six bytes against one, inside classes as well as outside, and a silent
miscompile rather than a rejection.

It survived because **python `re` also reads `\v` as 0x0B**, so the base-tier
oracle agreed with the bug and `tests/base/escapes.rxt` asserted the wrong
answer and passed. Where python and PCRE2 disagree, a python-verified corpus
certifies the divergence instead of catching it — recorded in
`docs/upstream_issues.md` and in `docs/pcre2_compliance.md`.

## Validated sabotages

Record the exact edit, not just the count.

| sabotage (exact edit) | result |
|---|---|
| drop `{'d', "classes"},` from `esc_modules` so `\d` reports `unknown escape` instead of naming its module | 2 reject checks, **0** corpus cases |
| add `case 'd': return 'd';` to `esc_char_value` so `\d` silently compiles as the literal `d` — the exact shape of the `\v` bug | 2 reject checks, **0** corpus cases, **0** codegen checks |

The second is the one to remember: a silent miscompile of a class escape is
invisible to every other test in this repo.

Maintenance: when a module lands, delete its constructs from the reject table
in the SAME change that adds their corpus coverage — a construct cannot be both
supported and asserted to be rejected. Update `docs/pcre2_compliance.md` too;
its `REJECTED` rows are only true because this table says so.
