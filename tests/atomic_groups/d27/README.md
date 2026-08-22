# [M6.4.3] `atomic-groups` D27 acceptance corpus

## Author and blindness statement

Written by the [M6.4.3] D27 blinded test author, working entirely inside
`worktrees/agd27-cell/` -- a non-git, allowlist-filtered copy containing
only `GOAL_FACTS.md`, `docs/testing.md`, `docs/spec/match_api.md`, the
libpcre2 ctypes probe, and a prebuilt `build/pcrec` that refuses every
atomic-group and possessive-quantifier construct outright ("requires
module 'atomic-groups'"). This author never had access to `src/` or
`tests/` (pcrec's real parser, lowering, or existing test corpus for any
module), and wrote every case below from PCRE2's documented behavior as
measured directly against libpcre2 10.46 -- never from pcrec's
implementation, which does not exist yet for this module, and never from
memory or intuition about what "should" happen. That is the whole of what
D27 blinding buys: a corpus that cannot have inherited an implementer's
alphabet, because there was no implementation to read.

## Files

| File | Patterns | m/n/ms/ns | g/gp | perr | Lines |
|---|---:|---:|---:|---:|---:|
| `atomic_basic.rxt` | 15 | 18 | 0 | 0 | 112 |
| `possessive_spellings.rxt` | 34 | 35 | 0 | 0 | 179 |
| `captures_under_cut.rxt` | 9 | 9 | 15 | 0 | 96 |
| `atomic_in_quantifiers.rxt` | 9 | 9 | 0 | 0 | 75 |
| `interactions.rxt` | 14 | 14 | 0 | 0 | 123 |
| `find_all_loop.rxt` | 5 | 10 | 0 | 0 | 59 |
| `syntax_errors.rxt` | 13 | 0 | 0 | 13 | 97 |
| `gating.rxt` | 14 | 0 | 0 | 14 | 97 |
| **Total** | **113** | **95** | **15** | **27** | **838** |

Counts are grep-counted, not hand-tallied:
`grep -c '^pattern '`, `grep -cE '^(m|n|ms|ns) '`, `grep -cE '^(g|gp) '`,
`grep -c '^perr$'`, `wc -l`, per file. 95 + 15 + 27 = 137 total measured
checks, matching `oracle.py`'s own total below exactly.

Topic split, per the cell brief:

- **`atomic_basic.rxt`** -- `(?>X)` core semantics: commit-and-refuse,
  alternation priority (both orderings), nesting, lazy quantifiers
  committing to their own minimal attempt, the empty atomic group.
- **`possessive_spellings.rxt`** -- `*+ ++ ?+ {n}+ {n,m}+ {n,}+ {,n}+` on
  characters, classes, and groups; direct re-derivation of B.1's
  `X<possessive>` == `(?>X<quantifier>)` equivalence; the classic
  possessive-eats-the-required-character traps on both a literal class
  and `\d`.
- **`captures_under_cut.rxt`** -- capture retention on success,
  cross-iteration retention through an atomic body (R22 rule 1), the
  empty-final-iteration overwrite (R22 rule 2) under both `(?>...)` and a
  possessive quantifier, and captures genuinely set during an atomic
  group's own successful sub-match being reported UNSET when the
  enclosing alternative goes on to fail as a whole.
- **`atomic_in_quantifiers.rxt`** -- `(?>X)` as a quantifier's body:
  each iteration's own independent cut, versus the iteration COUNT
  itself still being backtrackable by an ordinary outer quantifier --
  and, measured directly, that this is genuinely NOT the same thing as
  making the whole repeated construct possessive (`(?:X)++`), which
  locks the count too.
- **`interactions.rxt`** -- `\K`, `\G`, `(?i)`, `(?m)`, and lookaround
  beside or inside a cut. The first nine blocks are independent
  re-measurements of GOAL_FACTS B.3's `\K`/`\G`/`(?i)` witnesses.
- **`find_all_loop.rxt`** -- the absolute-offset promise and the
  empty-match advance rule (`docs/spec/match_api.md` S3.1) hand-simulated
  step by step via `ms`/`ns` at the startpos values a real loop would
  visit, for atomic and possessive constructs that can match empty.
- **`syntax_errors.rxt`** -- thirteen genuine PCRE2 compile-time
  rejections (quantifier-stacking, unclosed/unmatched atomic-group
  parens, out-of-order and oversized `{}` bounds, a quantified bare
  anchor), all with `features atomic-groups` enabled, so this file tests
  syntax rejection distinct from module gating.
- **`gating.rxt`** -- the `--features` refusal direction, both ways, on
  seven otherwise-valid patterns (module disabled vs. module enabled but
  unimplemented). pcrec-CLI-level, measured against `build/pcrec`
  directly, not a PCRE2 claim.

Every real (non-`perr`) block carries `features atomic-groups` (plus
`assertions` or `lookaround` where `\K`/`\G` or lookaround also appear) --
`atomic-groups` is not in pcrec's default feature set
(`PCREC_DEFAULT_FEATURES` = `"std1"` = `{classes, modifiers}`), so a block
missing this directive would fail on the module gate alone once the
module exists, regardless of whether its semantics are implemented
correctly. This was caught and fixed during this corpus's own writing --
see the note in the report to the manager.

## Oracle verification

`oracle.py` is an INDEPENDENT re-checker: it does not import or trust
whatever process wrote these `.rxt` files. It re-implements the `.rxt`
grammar directly from `docs/testing.md` and re-queries libpcre2 10.46 via
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py` for every
`m`/`n`/`ms`/`ns`/`g`/`gp` expectation in every file, plus the perr
direction for `syntax_errors.rxt` (expects PCRE2 to genuinely reject the
pattern) and `gating.rxt` (expects PCRE2 to genuinely ACCEPT the pattern
-- its refusal is pcrec's own module gate, not a PCRE2 syntax error, and
that distinction is exactly what `oracle.py` checks for those two files).

Run:

```sh
cd tests/atomic_groups/d27
python3 oracle.py
```

Per-file result (this session, libpcre2 10.46 2025-08-27):

```
libpcre2: 10.46 2025-08-27
atomic_basic.rxt             OK    pass=18   fail=0
atomic_in_quantifiers.rxt    OK    pass=9    fail=0
captures_under_cut.rxt       OK    pass=24   fail=0
find_all_loop.rxt            OK    pass=10   fail=0
gating.rxt                   OK    pass=14   fail=0
interactions.rxt             OK    pass=14   fail=0
possessive_spellings.rxt     OK    pass=35   fail=0
syntax_errors.rxt            OK    pass=13   fail=0

TOTAL: pass=137 fail=0
```

Every case in every file was independently re-derived from libpcre2 by
`oracle.py`, not hand-verified once and then trusted.

## python-divergence list

Per GOAL_FACTS B.2/B.3, python3's `re` module (3.14.4 on this box) is a
usable second oracle except where it cannot express or cannot parse a
construct. This corpus hits that boundary on exactly the `\K`/`\G`/`(?i)`
family GOAL_FACTS B.3 documents, and nowhere else -- every other block in
this corpus (all of `atomic_basic.rxt`, `possessive_spellings.rxt`,
`captures_under_cut.rxt`, `atomic_in_quantifiers.rxt`, and
`find_all_loop.rxt`, and the non-`\K`/`\G`/`(?i)` blocks of
`interactions.rxt`) was independently cross-checked against python `re`
during this corpus's writing and AGREED with libpcre2 span-for-span
(and group-for-group, where captures are involved), including the
brace-possessive-family and U9 cells re-derived below -- confirming
GOAL_FACTS's own count of "nothing else diverges" rather than assuming it.

Nine blocks in `interactions.rxt` are marked `# pcre2-only`, each with its
own one-line reason inline:

| Pattern | Reason python can't be used as a second oracle |
|---|---|
| `(?>a\Kb)c` | python has no `\K` ("bad escape \K") |
| `(?>a\Kb\|ab)c` | same |
| `(?>a\|a\Kb)b` | same |
| `a\K(?>b\|bc)c` | same |
| `(?>\Ga\|b)c` (x2 subjects) | python has no `\G` ("bad escape \G") |
| `\G(?>a\|ab)c` | same |
| `(?>(?i)a\|ab)c` | python cannot PARSE a mid-pattern `(?i)` ("global flags not at the start of the expression") |
| `(?>a+\K)b` | python has no `\K` |

These are exactly GOAL_FACTS B.3's own `\K`/`\G`/`(?i)` rows (8 of its 15
listed cells), independently RE-MEASURED against libpcre2 here rather than
copied from the document -- every one reproduced the documented answer
exactly. The other 7 of GOAL_FACTS's 15 (the U9 family and the
brace-possessive family) were also independently re-measured, during
corpus development, and also reproduced exactly:

```
(?:a|ab){2}+      on "aba"    -> pcre2 (0,3)  python nomatch
(?:a|ab){2,3}+    on "ababa"  -> pcre2 (0,3)  python nomatch
(?:a|ab){2,}+     on "ababa"  -> pcre2 (0,3)  python nomatch
(?:a|ab){2}+c     on "abac"   -> pcre2 (0,4)  python nomatch
(?:a|ab){3}+      on "ababa"  -> pcre2 (0,5)  python nomatch
a?(?:b){0,4}+a    on "a"      -> pcre2 nomatch python (0,1)   [U9]
a?b{0,4}+a        on "a"      -> pcre2 (0,1)  python (0,1)   [U9 negative control: char item]
a?(?:b)*+a        on "a"      -> pcre2 (0,1)  python (0,1)   [U9 negative control: *+ not {m,n}+]
x?(?:b){0,4}+a    on "a"      -> pcre2 (0,1)  python (0,1)   [U9 negative control: no backtrackable prefix]
```

None of these seven ended up as direct `m`/`n` cells in this corpus (they
duplicate GOAL_FACTS's own witnesses rather than adding new coverage), but
re-measuring them was part of verifying GOAL_FACTS's claims were correct
before relying on them elsewhere in the corpus -- see "On GOAL_FACTS's
accuracy" below. `possessive_spellings.rxt` and `atomic_in_quantifiers.rxt`
do carry the brace-possessive family's OWN distinguishing property as
first-class cells with fresh subjects (the `{n}+`/`{n,m}+`/`{n,}+`
group-exit-vs-per-iteration cut, and the atomic-in-quantifier count-
flexibility contrast), independently re-derived rather than reusing
GOAL_FACTS's exact patterns.

## On GOAL_FACTS's accuracy

Every specific numeric claim in GOAL_FACTS that this corpus depended on
and independently re-measured -- all 15 of the B.3 divergence table's rows
(re-verified in full, not sampled), B.1's atomic/possessive equivalence
(6 pairs, all matching), and B.4's U9 witness and its three negative
controls -- reproduced exactly. Nothing in GOAL_FACTS was found to be
wrong.

## Not checked against pcrec

Nothing in this corpus was checked against pcrec. `build/pcrec` in this
cell does not implement the `atomic-groups` module (every atomic-group or
possessive-quantifier construct is refused outright, "requires module
'atomic-groups'" or the possessive equivalent) -- it was used only to
confirm the refusal-direction cells in `gating.rxt` and to independently
measure that several `syntax_errors.rxt` patterns are ALREADY rejected
today for reasons unrelated to the module gate (documented inline in that
file). Every `m`/`n`/`ms`/`ns`/`g`/`gp` expectation in this corpus is a
measurement of libpcre2 alone. The record above -- including the finding
about `(?>...)`'s refusal message distinguishing "disabled" from
"enabled but unimplemented" while every possessive-quantifier spelling
gives the identical message in both directions (`gating.rxt`'s header
comment) -- is exactly what this cell measured, and is left as written for
whoever runs this corpus against the real implementation at merge review.
