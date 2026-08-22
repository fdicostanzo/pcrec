# [M6.4.3] `atomic-groups` D27 acceptance corpus

## Author and blindness statement

Written by the [M6.4.3] D27 blinded test author, working entirely inside
`worktrees/agd27-cell/` -- at authoring time a non-git, allowlist-filtered
copy containing only `GOAL_FACTS.md`, `docs/testing.md`,
`docs/spec/match_api.md`, the libpcre2 ctypes probe, and a prebuilt
`build/pcrec` that refused every atomic-group and possessive-quantifier
construct outright ("requires module 'atomic-groups'"). This author never
had access to `src/` or `tests/` (pcrec's real parser, lowering, or
existing test corpus for any module), and wrote every case in the original
corpus from PCRE2's documented behavior as measured directly against
libpcre2 10.46 -- never from pcrec's implementation, which did not exist
yet for this module at the time, and never from memory or intuition about
what "should" happen. That is the whole of what D27 blinding buys: a
corpus that cannot have inherited an implementer's alphabet, because there
was no implementation to read.

The `atomic-groups` module has since landed ([M6.4.2]) and this cell's
`build/pcrec` was refreshed to the post-module compiler for an acceptance
run and a subsequent triage pass, both recorded below. The blindness
statement above describes how the corpus was WRITTEN; it does not
retroactively change once the module exists to check it against, and this
author did exactly what D27 exists for at that point -- see "Acceptance
run" below.

## Files

| File | Patterns | m/n/ms/ns | g/gp | perr | Lines |
|---|---:|---:|---:|---:|---:|
| `atomic_basic.rxt` | 15 | 18 | 0 | 0 | 112 |
| `possessive_spellings.rxt` | 34 | 35 | 0 | 0 | 189 |
| `captures_under_cut.rxt` | 9 | 9 | 15 | 0 | 96 |
| `atomic_in_quantifiers.rxt` | 9 | 9 | 0 | 0 | 75 |
| `interactions.rxt` | 11 | 11 | 0 | 0 | 146 |
| `find_all_loop.rxt` | 5 | 10 | 0 | 0 | 59 |
| `syntax_errors.rxt` | 13 | 0 | 0 | 13 | 97 |
| `gating.rxt` | 14 | 7 | 0 | 7 | 101 |
| **Total** | **110** | **99** | **15** | **20** | **875** |

Counts are grep-counted, not hand-tallied:
`grep -c '^pattern '`, `grep -cE '^(m|n|ms|ns) '`, `grep -cE '^(g|gp) '`,
`grep -c '^perr$'`, `wc -l`, per file. 99 + 15 + 20 = 134 total measured
checks, matching `oracle.py`'s own total below exactly. (These counts are
POST-triage; see "Acceptance run" for how they moved from the original
113/95/15/27/838 -- `interactions.rxt` lost 3 live patterns to a commented-
out, unbuildable-today block, and `gating.rxt`'s 7 enabled-direction blocks
changed from `perr` to `m`, changing its own perr/m split but not its
pattern count.)

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
  locks the count too. **This file's last block is the real miscompile
  the acceptance run found -- see below.**
- **`interactions.rxt`** -- `\K`, `\G`, `(?i)`, `(?m)` beside or inside a
  cut. The first nine blocks are independent re-measurements of GOAL_FACTS
  B.3's `\K`/`\G`/`(?i)` witnesses. Three lookaround-beside-a-cut blocks
  are commented out (module not built today) -- see below.
- **`find_all_loop.rxt`** -- the absolute-offset promise and the
  empty-match advance rule (`docs/spec/match_api.md` S3.1) hand-simulated
  step by step via `ms`/`ns` at the startpos values a real loop would
  visit, for atomic and possessive constructs that can match empty.
- **`syntax_errors.rxt`** -- thirteen genuine PCRE2 compile-time
  rejections (quantifier-stacking, unclosed/unmatched atomic-group
  parens, out-of-order and oversized `{}` bounds, a quantified bare
  anchor), all with `features atomic-groups` enabled, so this file tests
  syntax rejection distinct from module gating.
- **`gating.rxt`** -- the `--features` refusal direction on seven
  otherwise-valid patterns, module disabled. pcrec-CLI-level, measured
  against `build/pcrec` directly, not a PCRE2 claim. (Its enabled-direction
  blocks are no longer `perr` -- see below.)

Every real (non-`perr`) block carries `features atomic-groups`, plus
whatever OTHER module the rest of its pattern needs -- `\d` needs
`classes`, `(?i)`/`(?m)` need `modifiers` (and `(?m)`'s multiline `^`/`$`
needs `assertions` too, on top of `modifiers` for the inline-option
syntax), `\K`/`\G` need `assertions`. **The mechanism, confirmed directly
against the CLI: a block's `features` directive REPLACES pcrec's default
feature set (`std1` = `{classes, modifiers}`) rather than adding to it.**
A block that only says `features atomic-groups` gets `classes` and
`modifiers` turned OFF, not left on -- so any other gated construct in the
same pattern needs its own module named explicitly in the same list. This
was gotten wrong twice during this corpus's life and fixed both times; see
"Acceptance run" below for the full account of both passes.

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
It does not, and cannot, check the miscompile the acceptance run found
below -- that is a claim about pcrec, and libpcre2 alone has no opinion on
it (libpcre2 IS the "nomatch" answer pcrec's `(?:aa|a)++ab` cell asserts;
oracle.py already independently confirms that expectation is what
libpcre2 gives).

Run:

```sh
cd tests/atomic_groups/d27
python3 oracle.py
```

Per-file result (this session, libpcre2 10.46 2025-08-27, post-triage):

```
libpcre2: 10.46 2025-08-27
atomic_basic.rxt             OK    pass=18   fail=0
atomic_in_quantifiers.rxt    OK    pass=9    fail=0
captures_under_cut.rxt       OK    pass=24   fail=0
find_all_loop.rxt            OK    pass=10   fail=0
gating.rxt                   OK    pass=14   fail=0
interactions.rxt             OK    pass=11   fail=0
possessive_spellings.rxt     OK    pass=35   fail=0
syntax_errors.rxt            OK    pass=13   fail=0

TOTAL: pass=134 fail=0
```

Every case in every file was independently re-derived from libpcre2 by
`oracle.py`, not hand-verified once and then trusted.

## Acceptance run at [M6.4.2]'s merge review, and this cell's triage

**First run against the real implementation: 121 pass / 16 fail.** One of
those 16 was a REAL MISCOMPILE this corpus found that the implementer's
own 39,326-cell differential did not:
`atomic_in_quantifiers.rxt`'s `(?:aa|a)++ab` on `"aaab"` expects `nomatch`
(the whole repeated construct is possessive, so its iteration COUNT is
locked and cannot be reduced to rescue the match -- see that file's own
comment); pcrec answered `(0,4)`. **That cell is unchanged, exactly as
originally written** -- the implementation is being fixed, not the test.
This is D27 doing what it exists for: a corpus derived from the goal, not
the code, catching a defect the code's own alphabet couldn't see.

The other 15 failures were genuinely this corpus's own mistakes, both
falling out of the SAME mechanism (`features` REPLACES, not ADDS, the
default set -- confirmed directly against the refreshed CLI, both
directions, during this triage):

**(a) Eight directive errors.** A block enabling `atomic-groups` alone
silently turned OFF `classes`/`modifiers`/`assertions` for any OTHER
gated construct sharing the same pattern, and the original corpus never
added them back:
- `interactions.rxt`: `(?>(?i)a|ab)c`, `(?i)(?>abc)` needed `modifiers`
  added; `(?m)^(?>a+)$` needed BOTH `modifiers` (the inline `(?m...)`
  spelling) AND `assertions` (multiline `^`/`$` itself) -- found in two
  steps: fixing to `atomic-groups,modifiers` alone still refused with
  "inline option 'm' (multiline) requires module 'assertions'", which is
  how the second module was found, not assumed.
- `possessive_spellings.rxt`: `\d++` and `\d*+\d` needed `classes` added.
- Three lookaround-beside-a-cut cells (`(?<=a)(?>b+)c`, `(?>a+)(?=b)`,
  `(?>a+)(?!b)`) turned out to be a DIFFERENT problem: `lookaround` is not
  built at all yet (confirmed directly: `--features
  atomic-groups,lookaround` on these still refuses, "module 'lookaround'
  is enabled but (?<...) is not implemented yet"). No available build can
  accept them today, so they are now commented out in `interactions.rxt`
  (not parsed as `pattern` blocks, so `run.sh` never sees them and they
  count toward neither pass nor fail) with their intended expectations
  preserved inline for whoever lands `lookaround`.

Every fix was found by re-running the exact failing pattern against the
refreshed CLI with candidate `--features` lists until the refusal
message's OWN wording named the missing module -- never guessed from the
module list.

**(b) Seven `gating.rxt` cells.** These are the file's ENABLED-direction
blocks (`features atomic-groups`, one per possessive/atomic pattern) --
originally written as `perr` (expect refusal) because at authoring time
the module did not exist and EVERY construct was refused regardless of
the gate's state. That `perr` assertion was VACUOUS from the day it was
written: it was never testing "is the module properly gated", only
"does an implementation exist" -- which happened to also read `perr` at
the time, for an entirely unrelated reason. Once the module became real,
the vacuous truth flipped to false (the harness compiled these patterns
successfully, correctly), and the failure was the corpus finally being
asked a question it was never actually testing. Fixed by changing these
seven blocks from `perr` to real `m` cases, with the expected span
verified two ways: against libpcre2 directly, and end-to-end against the
refreshed `build/pcrec` itself (`--emit-main`, compiled with `gcc -O1
-std=gnu11`, and run) -- since this file is explicitly pcrec-CLI-scoped
in the first place (never a blind-authorship boundary; see its own header
comment), running the real binary here is the correct verification, not a
blindness violation. The DISABLED-direction blocks (no `features` line)
needed no change -- confirmed directly against the refreshed CLI that
they still refuse, unchanged, and `oracle.py` already confirmed
independently that every pattern in this file is valid PCRE2 syntax (so a
disabled-direction refusal is unambiguously the module gate, never a
syntax rejection in disguise).

**Verification after the fixes** (this triage session): `oracle.py`
green, 134/134 (table above). Additionally, since this cell's
`build/pcrec` is now the real, post-module binary, every LIVE block in
the corpus was re-run against it directly (`--features` from the block,
`--emit-main`, `gcc -O1 -std=gnu11`, executed, output compared) as a
local sanity pass before reporting back -- 111 of 112 directly-checked
cases (`m`/`n` cases at `startpos 0`; the `ms`/`ns` cases need a startpos
argument this cell's `--emit-main` binary doesn't take, so they are left
to `run.sh`'s own driver, already covered by the acceptance run's 121/137)
agreed with the real implementation, the ONE disagreement being exactly
the known, left-as-written miscompile above -- confirming the 15 fixes
above are solid and introducing no new corpus-side error.

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

## What was, and was not, checked against pcrec

At original authoring time, nothing in this corpus was checked against
pcrec: the module did not exist, and `build/pcrec` was used only to
confirm the refusal-direction cells in `gating.rxt` and to independently
measure that several `syntax_errors.rxt` patterns are ALREADY rejected
for reasons unrelated to the module gate (documented inline in that
file). Every `m`/`n`/`ms`/`ns`/`g`/`gp` expectation in the corpus was, and
remains, a measurement of libpcre2 alone -- the acceptance run and this
triage did not change any expectation to match the implementation; the
one real miscompile they found stays exactly as originally written, and
the 15 corpus-side fixes were directive/gating-mechanism corrections, not
semantic ones. What WAS additionally checked against the real, refreshed
`build/pcrec` during this triage -- the seven `gating.rxt` enabled-
direction spans, and a local re-run of every live block's `m`/`n` case at
`startpos 0` (111/112 agreeing, the one disagreement being the known
miscompile) -- is recorded above under "Acceptance run", not folded
silently into the oracle-verification section, which stays libpcre2-only.
