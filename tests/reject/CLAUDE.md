# tests/reject — the "never miscompile" mandate, tested

The project rule is that a construct outside the base tier must fail with a
clean `requires module 'X'` error and never miscompile. Until 2026-08-09
nothing checked that, and the gap was not hypothetical — see below.

## Files

- **run_reject_tests.sh** — 93 constructs asserted to be rejected by hand, 66
  more reached by iterating `pcrec --list-syntax`, plus 19 accept-controls.
  Part of `make test`; env: PCREC, KEEP=1.

## Two layers, and why neither replaces the other (SR-4)

SR-4's plan text said to iterate the dump INSTEAD of the hand-written rows.
That trade was not taken, and the reason is measurable rather than aesthetic.

Since SR-2, module names live in exactly ONE place — `src/parse/registry.c` —
and the parser renders its diagnostics from it. A test that reads that same
table and asks "does the diagnostic match the table" therefore cannot see a
WRONG name: change `\d`'s row from `classes` to `misc` and the parser and the
loop agree, in unison, about the wrong answer.

Measured on a sabotaged copy of the tree:

| sabotage (exact edit) | hand-written | iterated |
|---|---|---|
| `ESC('d', "\d", classes, ...)` → `ESC('d', "\d", misc, ...)` | **2 fail** | 0 |
| `ESC('s', "\s", ...)` → `ESC('s', "zz", ...)` (a `syntax` that does not reach its doorway) | 0 | **1 fail** |
| `pcrec_syntax_tsv` returns an empty string | 0 | 0, but the vacuity guard fires |
| a NEW row with a plausible wrong module and no hand-written entry | 0 | 0 |

The last row is the honest limit: **SR-4 did not close R4's residual
circularity.** Iteration guarantees COVERAGE — no row escapes a probe, and
adding a row needs no edit here. The hand-written rows are an independent HUMAN
source for the name a caller is actually given. The maintenance cost of the
second one IS the check; that is the same rule the accept-controls follow and
the same lesson the trie-identity check learned. An external answer for the
remaining gap needs libpcre2, not another reading of our own table — see PC-3.

## What iteration structurally cannot reach

Three things, so "the dump covers it" is never read as more than it is:

- `\x{...}` and the possessive `+` have **no registry row** — they are
  sub-cases of base constructs, deliberately (D24) — so they are hand-written
  and always will be.
- the **in-class spelling** of an escape (`[\d]`) is a different diagnostic
  from the atom spelling that the `syntax` field probes.
- anything rejected by the **base grammar** (`a{1,2`, unmatched `)`, an
  out-of-order range) has no row at all.

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
rejections. The 19 `accept` rows (literals, alternation, groups, every
quantifier form, classes, `.`, anchors, the character escapes, escaped
punctuation) are what stop that, and they are the same lesson the trie
identity check learned the hard way — a control has to sit inside the range of
what it certifies. The summary also enforces a floor on both counts, so
deleting coverage fails rather than quietly shrinking the table.

## Over-rejection is the opposite failure, and just as wrong

The POSIX collating rows are the reason the accept-controls are not decoration.
PCRE2 rejects `[[.a.]]`, but only when a matching `.]` terminator is present —
`[.a]`, `[.]`, `[[.]`, `[a[.b]`, `[^.a.]` and `[a.b.]` are all ordinary classes
that PCRE2 compiles. A naive "reject any `[.` in a class" would have passed
every rejection row here while silently breaking patterns that work today. All
18 forms were checked against libpcre2 10.46 and pcrec now agrees on every one;
the six that must compile are accept-controls for exactly that reason.

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
