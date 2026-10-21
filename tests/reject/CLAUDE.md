# tests/reject — the "never miscompile" mandate, tested

The project rule is that a construct outside the base tier must fail with a
clean `requires module 'X'` error and never miscompile. Until 2026-08-09
nothing checked that, and the gap was not hypothetical — see below.

## Files

- **run_reject_tests.sh** — 306 rows asserted by hand (moved 268→275 at MOD-0.6's K10 slice: the seven `[\N{U+41}]`-shaped in-class cells, offset-pinned, the first ...

## The accept-controls are not optional

A parser that rejected EVERYTHING would score 100% on a table made only of
rejections. The 45 `accept` rows (literals, alternation, groups, every
quantifier form, classes, `.`, anchors, the character escapes, escaped
punctuation, and since FIX-1/R7 the malformed and whitespace-bearing braces)
are what stop that, and they are the same lesson the trie identity check
learned the hard way — a control has to sit inside the range of what it
certifies.

**A control has to be symmetric with the code it controls, too** (R7/T-5).
K5's over-reach guard had three accept-controls and all three overflowed the
FIRST number, so mirroring the mistake onto the second number rejected five
patterns libpcre2 compiles with every suite green. The four `a{1,65536x}`-shaped
rows close that half.

The summary enforces exact counts AND a manifest. The counts alone are not
enough: a critic moved the 65535 ceiling by one, deleted the single row that
caught it, bumped the count as the failure message itself invites, and got a
green `make test` in a two-line diff. The manifest names those rows by pattern,
so deleting one fails with a message that does not offer a number to edit.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__reject.md`.
