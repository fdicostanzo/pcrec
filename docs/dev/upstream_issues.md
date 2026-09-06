# Upstream issues — suspected bugs & divergences in other engines

Findings about OTHER regex engines (PCRE2, python `re`, ...) discovered by
pcrec's differential tooling. Tracked here so they aren't mistaken for pcrec
bugs, so oracle exclusions have a citable rationale, and so genuine bugs can
be reported upstream. One entry per finding.

Status values: `suspected-bug` (worth reporting upstream) |
`divergence-by-design` (documented/intentional difference; constrains our
oracles) | `not-a-bug` (looked suspicious, resolved as correct behavior).

---

## U1 — PCRE2 10.46: `{0}`-quantified anchor group wrongly anchors the pattern

- **Status**: suspected-bug (candidate upstream report to the PCRE2 project)
- **Found**: 2026-08-09, M2.5 differential fuzzer (seed 2), minimized by the
  fuzzer agent; independently verified against `libpcre2-8.so.0` 10.46.
- **Repro**: pattern `(()|^){0}[b]` vs subject `"0b"` → PCRE2: nomatch
  (rc −1, genuine); pcrec and python `re`: match [1,2). Since `X{0}` is
  zero-width dead code, the pattern is semantically `[b]`.
- **Isolation**: `(^){0}[b]` agrees (matches); wrapping the anchor in an
  alternation `(()|^){0}` triggers it; a non-anchor branch `(()|a){0}[b]`
  does not; `{0,0}` behaves like `{0}`. Reading: PCRE2's static
  start-anchor optimization treats the never-executable `^` branch as
  anchoring the whole pattern, then never tries later offsets.
- **Impact on pcrec**: none on correctness; fuzz.py classifies this shape
  into a `pcre2_quirk` bucket (intentional divergence, does not fail runs).
  Regression coverage: tests/base/fuzz_regressions.rxt (python-verified).

## U2 — python `re`: bare `{,}` treated as `{0,}` (PCRE2/Perl treat as literal)

- **Status**: divergence-by-design (python documents that an omitted bound
  defaults; PCRE2 10.46 verified to treat `a{,}` as the four literal chars —
  `{,n}` WITH a digit is a quantifier in both since PCRE2 10.43).
- **Repro**: python `re.search('a{,}', 'aaa')` → (0,3); PCRE2 oracle
  `a{,}` vs "aaa" → nomatch. pcrec follows PCRE2 (literal).
- **Impact**: python cannot oracle `{,}` cases → `# pcre2-only` marker in
  the corpus (tests/base/fuzz_regressions.rxt).

## U3 — python `re`: `pos` past end-of-string clamps for nullable patterns

- **Status**: divergence-by-design / doc gap (python docs don't specify
  `pos > len` behavior; PCRE2 rejects a start offset past the subject end).
- **Repro**: python `re.compile('a*').search('bb', 3)` → matches (2,2);
  PCRE2 and pcrec (documented contract in lib/pcrec.h): no match when
  startpos > n.
- **Found**: 2026-08-09, M2.4 coverage agent building startpos corpus.
- **Impact**: those startpos cases carry `# pcre2-only`; verified against
  the real binary through the harness instead.

## U4 — PCRE2: match-limit (rc −47) on catastrophic-backtracking shapes

- **Status**: not-a-bug (documented PCRE2 resource safeguard), recorded
  because it silently poisoned our oracle once.
- **Repro**: `(((b{0,})){2,}){0,}$` vs a 'b'-run subject → pcre2_match
  returns −47 (MATCHLIMIT), which is not a nomatch verdict. pcrec's DFA
  answers instantly (no backtracking).
- **Impact**: tests/fuzz/pcre2_oracle.c distinguishes rc −1 (nomatch) from
  other negative codes (`mlimit`, treated as inconclusive, never compared).
  Any oracle comparing against a backtracker must do the same.

## U5 — python `re`: repeat counts above 65535 are accepted (PCRE2 error 105)

- **Status**: divergence-by-design (the two engines simply have different
  ceilings). PCRE2's is 65535; python 3.14's is **4294967294** (2^32 − 2), and
  above that it raises `OverflowError` rather than `re.error`.
  The round number 4294967296 stood here first, inferred from python's own
  "repetition number is too large" message rather than measured, and an R7
  critic caught it: `a{4294967294}` compiles, `a{4294967295}` does not. Two
  off, in four files, from exactly the habit this document exists to break.
- **Repro**: `re.compile('a{65536}')`, `a{100000}`, `a{0,65536}`, `a{,65536}`
  and `a{99999999999999999999}` all compile in python 3.14; libpcre2 10.46
  answers error 105 "number too big in {} quantifier" to every one. pcrec
  follows PCRE2 (K5, fixed 2026-08-10).
- **Found**: 2026-08-10, FIX-1, while looking for a corpus home for K5.
- **Impact**: python cannot oracle these, so the seven K5 blocks in
  `tests/base/syntax_errors.rxt` carry `# pcre2-only` and are verified against
  libpcre2 by hand plus `tests/reject/` for the diagnostic. `a{65536,1}` is
  the one exception and needs no marker — python rejects it too, though for a
  different reason (its clamp makes the pair look out-of-order).
- **A second-order hazard worth naming**: the 20-digit form raises
  `OverflowError`, which is NOT an `re.error`, so an unmarked block would
  crash `verify_rxt.py` rather than fail it. The marker also avoids that.

## U6 — python `re`: no whitespace allowed inside `{m,n}` (PCRE2 allows space/tab)

- **Status**: divergence-by-design (a flavour difference). PCRE2 10.46 follows
  Perl 5.34 and skips SPACE and TAB in each of the four gaps inside a repeat
  quantifier; python `re` reads any whitespace there as ending the quantifier,
  so the whole brace becomes literal text.
- **Repro**: `re.compile('a{ 1}').search('a')` → `None`, and it matches the
  five literal characters instead; the PCRE2 oracle answers `match 0 1` for
  the same pattern and subject. Same for `a{1 }`, `a{1, 2}`, `a{1 ,2}`,
  `a{<TAB>1}` and every combination of the four gaps. pcrec follows PCRE2
  (K8, fixed 2026-08-10).
- **Found**: 2026-08-10, R7's spec critic, generating the brace space
  combinatorially rather than listing it.
- **Impact**: python cannot oracle the tolerated forms, so the K8 block in
  `tests/base/bounded_repeats.rxt` carries `# pcre2-only`. The COMPLEMENTARY
  cases — the bytes PCRE2 does not skip, and whitespace inside or in place of
  a number — are where python and PCRE2 agree, so those stay python-verified
  and are the more valuable half: they are the over-reach guard.
- **This is the third instance of one shape**, after `\v` and the POSIX
  collating elements: python agrees with a pcrec bug, so a python-verified
  corpus certifies the divergence instead of catching it. Each time, the thing
  that found it was an instrument that does not use python.

---

Maintenance: add an entry whenever differential tooling implicates another
engine; update status when reported/resolved upstream. Cross-reference from
docs/testing.md (oracle exclusions) and tests/fuzz/README.md.

## python `re` vs PCRE2: `\v` is a different construct in each (2026-08-09)

Not a bug in either engine — a flavour difference, recorded because it defeated
our base-tier oracle.

- **PCRE2**: `\v` is a character TYPE, "vertical white space". Measured against
  libpcre2 10.46 via `tests/fuzz/pcre2_oracle.c`, it matches 0x0a, 0x0b, 0x0c,
  0x0d and 0x85.
- **python `re`**: `\v` is a character ESCAPE for vertical tab, 0x0b alone
  (verified: `re.search(rb'\v', b'\x0a')` is None).

pcrec followed python and decoded `\v` as 0x0B. Because `verify_rxt.py` uses
python `re`, the corpus expectation `pattern \v / m "\v" 0 1` was oracle-VERIFIED
and wrong against the engine pcrec claims compatibility with. Fixed by routing
`\v` to module 'classes' alongside `\V`, which was already routed there.

**Consequence for the oracle strategy, which is the reason this entry exists:**
where python `re` and PCRE2 disagree on what a construct MEANS, a
python-verified corpus certifies the divergence instead of catching it. The
base tier is still the right first oracle — it is fast, dependency-free and
catches the overwhelming majority — but it cannot be the last word on PCRE
semantics. This is a concrete casualty in support of the M7 libpcre2
differential work, and a reason to run `tests/fuzz/fuzz.py` (which uses the
PCRE2 oracle) against any newly supported construct rather than only against
generated patterns.

Other escapes were checked at the same time against libpcre2 and all agree
exactly: `\a` 0x07, `\e` 0x1b, `\f` 0x0c, `\n` 0x0a, `\r` 0x0d, `\t` 0x09.
`\v` was the only divergence in the escape table.

## U7 — python `re`: `[\8] [\9] [\g] [\k]` are "bad escape" (PCRE2: literal fallback)

- **Status**: divergence-by-design (python 3.7+ deliberately made unknown
  escapes of ASCII letters/digits in a class an error; PCRE2's `check_escape`
  falls back to the literal character — `[\8]` matches `8`, `[\k<n>]` is a
  class of `k` `<` `n` `>`).
- **Repro**: `python3 -c "import re; re.compile(r'[\8]')"` → `bad escape \8`;
  libpcre2 10.46 compiles it and matches exactly `8` (measured over all 62
  `[\c]` single-letter/digit probes plus tails and range endpoints,
  tests/probes/probe_fix3.c, 41 cells, zero disagreements). pcrec follows
  PCRE2 since FIX-3 (K13).
- **Impact**: python cannot oracle the literal-fallback class cells →
  `# pcre2-only` blocks in tests/base/class_escape_fallbacks.rxt (their
  oracle is the probe run against libpcre2 directly). The octal cells
  (`[\1]`, `[\12]`, `[\377]`, `[\400]` error) python agrees on and verifies.

## U8 — python `re`: `(?xx)` has no class-interior byte deletion (PCRE2: `xx` deletes SPACE/TAB before range-parsing)

- **Status**: divergence-by-design (python's flag-letter parser treats a
  repeated `x` as ordinary verbose mode, duplicated and harmless — python
  has no concept of a SECOND, stricter extended mode at all; PCRE2 10.43+
  gives `xx` a distinct, documented meaning: inside a character class it
  additionally deletes SPACE and TAB bytes from the class body BEFORE
  range-parsing, which plain `x`/python verbose mode never does).
- **Found**: 2026-08-12, authoring tests/modifiers/xxmode.rxt for module
  `modifiers` (MOD-0.5c corpus half), while deciding which blocks needed
  `# pcre2-only` — checked directly against python3 `re` rather than
  assumed.
- **Repro**: `python3 -c "import re; re.compile('(?xx)[a- ]')"` →
  `re.error: bad character range a-  at position 6` (python parses the
  class body `a- ` unchanged and rejects the descending range a→SPACE);
  libpcre2 10.46 (measured via tests/probes/probe_mod05.c and a throwaway
  scratchpad extension of it, `pcre2_abi.h`-based) COMPILES the identical
  pattern, because `xx` deletes the SPACE from the class body first,
  leaving `[a-]` — members `{a, -}`, dash literal at the end, no range at
  all. This is the D30 §7 hazard docs/dev/plan_completed.md's [MOD-0.5] step names
  directly (R10/C2-11: `[a- ]` is PCRE2 error 108 at options=0, `(?xx)[a-
  ]` compiles at the exact class-range-endpoint spot `3fca0d8` (SPEC-FA)
  had fixed as a silent-wrong-matcher one commit before the panel that
  found it).
- **Isolation**: the divergence is specifically the CLASS-INTERIOR
  deletion, not `xx` generally — OUTSIDE a class the two engines agree:
  `(?xx)a b` matches `"ab"` [0,2) in both python and libpcre2, because
  python's verbose mode and PCRE2's `x`/`xx` share the same
  outside-class whitespace-skip behaviour (python simply never
  distinguishes `x` from `xx` there). The mirrored hazard cells also
  disagree the same way: `(?xx)[a-\ ]` (escaped space, still significant)
  and `(?xx)[\ -a]` (range SP..a) and tab deletion in `(?xx)[a\tb]` all
  compile differently or identically depending on whether the engine
  implements the class-interior deletion at all.
- **Impact**: python cannot oracle ANY of the class-interior `xx` cells →
  tests/modifiers/xxmode.rxt is entirely `# pcre2-only` (every block, not
  just the discriminating one — the file's own header cites this entry).
  Expectations there are measured against live libpcre2 10.46 with a
  throwaway scratchpad oracle patterned on tests/probes/probe_mod05.c and
  probe_mod05b.c (not committed; those two probes remain the canonical,
  reproducible measurement of the hazard). Outside-class `x`/`xx` lexing
  (tests/modifiers/xmode.rxt) stays python-verified as usual, since that
  half is where the two engines actually agree.

## U9 — PCRE2 10.46: no backtrack into a PRECEDING item after a possessive/atomic BOUNDED repeat of a GROUP

- **Found**: 2026-08-15/16, R24 panel (soundness critic F6), sweeping the
  [ENG-BREP] possessification family with possessive spellings against
  both oracles (docs/dev/reviews/2026-08-15-r24-eng-brep.md).
- **Divergence**: `a?(?:b){0,4}+a` on `"a"` — PCRE2 10.46 reports NO
  MATCH; python `re` (and a hand derivation) give (0,1): the possessive
  quantifier should forbid retreat into ITS OWN loop only, not freeze the
  preceding `a?`. Same result for `(a?)(b){0,4}+a` and the atomic-group
  spelling `(a?)(?>(b){0,4})a`.
- **Isolation**: BOTH conditions are necessary — all of these MATCH in
  PCRE2: `a?b{0,4}+a` (character item, not a group), `a?(?:b)*+a`
  (`*+`, not `{m,n}+`), `x?(?:b){0,4}+a` (preceding optional matched
  nothing), `a??(?:b){0,4}+a` (lazy prefix), `(?:b){0,4}+a` (no
  preceding item). The trigger is a possessive/atomic BOUNDED repeat of
  a GROUP with a preceding backtrack point that actually consumed.
- **Impact**: python-possessive and PCRE2-possessive are NOT
  interchangeable oracles for `{m,n}+`-over-group families — a three-way
  sweep over possessive SPELLINGS in that family will report
  disagreements that are not pcrec's. [ENG-BREP]'s possessification is an
  internal rewrite that never emits `+` (and pcrec refuses the spelling
  today, module `atomic-groups`), so §5.1's pcrec-vs-pcrec differential
  is the primary instrument for a measured reason, not just a ruled one.
  These 3 cells were the only "counterexamples" in the critic's 1,889×300
  capture-focused sweep — all PCRE2-side, none analysis-side.
- **Status**: suspected-bug — candidate upstream report to the PCRE2 project
  (classification set by Frank, 2026-08-22: "I think you found an error in
  PCRE2").
- **RULING (D68, Frank, 2026-08-22)**: pcrec KEEPS the derived semantics —
  `a?(?:b){0,4}+a` on "a" is MATCH (0,1), agreeing with python `re` and the
  hand derivation — and DOCUMENTS the deviation from libpcre2 10.46 rather
  than reproducing it. Module `atomic-groups` ([M6.4], shipped the same day)
  is the event that made it reachable. The two cells live in
  tests/atomic_groups/possessive.rxt section 9 beside their three controls,
  python-verified, with a LOUD per-block exclusion from the directory's
  libpcre2 verifier (marker `# pcre2-deviates U9`); they are no longer in
  tests/known_fail (that directory holds pcrec BUGS). A change toward
  libpcre2's answer goes RED in the module's own suite. The compliance page's
  `base:quantifiers-possessive` annotation carries the deviation.

## U10 — python `re`: named-group SPELLING and length-ceiling divergences (module `named-groups`, [M6.3])

- **Status**: two unrelated divergences, filed together because both were
  found authoring the same corpus (tests/named_groups/) and both are
  divergence-by-design rather than bugs on either side.
- **Divergence 1 — SYNTAX, not semantics.** python `re` implements exactly
  ONE of PCRE2's three named-group declaring spellings: `(?P<name>...)`.
  `(?<name>...)` and `(?'name'...)` are simply not python `re` grammar at
  all (`re.error: unknown extension ?` / a literal parse of `(?'` as
  something else entirely — neither is a "python disagrees about what this
  means" case, both are "python cannot parse this text"). This is NOT a
  semantic divergence: all three PCRE2 spellings are the identical
  construct, differing only in which characters delimit the name — same
  numbering, same capture behaviour, same everything but the two
  delimiter bytes — which pcrec's own parser encodes directly
  (`src/parse/mod_named_groups.c` is ONE producer function serving all
  three registry rows, dispatched only on which closing delimiter to scan
  for). So the oracle-verification strategy is a MECHANICAL TRANSLATION
  rather than an exclusion-with-no-evidence: rewrite `(?<name>` to
  `(?P<name>` and `(?'name'` to `(?P<name>` (closing the substitution at
  the matching `'`/`>`), run the TRANSLATED pattern through python `re`,
  and use its verdict as the oracle for the ORIGINAL spelling. Worked
  example: `(?<word>[a-z]+)-(?<num>[0-9]+)` on `"abc-123"` translates to
  `(?P<word>[a-z]+)-(?P<num>[0-9]+)`, which python reports as `(0, 7)`
  with `word` spanning `(0, 3)` and `num` spanning `(4, 7)` — identical to
  the `(?P<...>` spelling's own DIRECTLY-verified block in the same
  corpus file, which is the closest thing to a proof-by-construction that
  the translation changes nothing but delimiters.
- **Divergence 2 — a real ceiling mismatch.** PCRE2 10.46 refuses a named
  group name above 128 bytes (error 148, "subpattern name is too long
  (maximum 128 code units)" — measured, tests/probes/probe_named_groups.c,
  swept 1..2000 bytes of an otherwise-valid name, exact wall at 129).
  python `re` has no such ceiling at all — a 2000-byte group name compiles
  without complaint. So the REFUSING half of this boundary (129 bytes)
  cannot be python-co-verified in either direction; it is pinned in
  tests/reject/'s gated pins instead (which needs no oracle agreement,
  only pcrec's own diagnosis), and the corresponding ACCEPTING half (128
  bytes, which python happily agrees compiles, just without enforcing why
  129 would not) is not separately pinned — the module's own corpus
  exercises ordinary short names throughout, and the 128/129 boundary
  itself is the number worth pinning, not a redundant long-name accept.
- **Also found, not a divergence**: `(?n)` (PCRE2's no-auto-capture
  option) is not a python `re` construct at all (`re.error: unknown
  extension ?n`), so `(?n)`'s interaction with named-group numbering
  — a named group captures even when `(?n)` suppresses a PLAIN group's
  number, measured: `(?n)(a)(?P<x>b)` has `capturecount=1, namecount=1`,
  i.e. the plain group gets no number at all and the named group becomes
  group 1, not group 2 — has no translation available either. Its oracle
  is the probe measurement directly, not python in any form.
- **Impact**: tests/named_groups/named_groups.rxt marks the `(?<name>...)`
  and `(?'name'...)` blocks (and the `(?n)` cell) `# pcre2-only`, each with
  a comment pointing back to this entry; the `(?P<name>...)` blocks are
  NOT excluded and ARE checked live by `verify_rxt.py` on every run — the
  living proof that the translation this entry describes is sound, since
  those blocks assert the SAME spans the translated-and-excluded blocks
  claim. See its CLAUDE.md for the full oracle-split accounting.

## U11 — python `re`: `\Z` IS PCRE2's `\z` (module `assertions`, [M6.2] wave A)

**Found**: 2026-08-18 by the [M6.1] design lane
(`docs/design/assertions_measurements/probes/probe_z_oracle.py`), reproduced
2026-08-19 by the [M6.2] wave A implementation lane over its own 29-pattern
corpus before a single expectation was written.

**The divergence.** PCRE2's `\Z` is "end of subject, OR immediately before a
final newline". python's `\Z` is "end of subject", full stop — which is
PCRE2's `\z`, a construct python 3.14 ALSO spells `\z` (identically to
PCRE2's, checked). So python has TWO spellings of `\z` and NO single escape
for `\Z` at all; the only python expression with PCRE2's `\Z` semantics is
`(?=\n?\Z)`, which needs lookahead — module `lookaround`, which does not
exist.

**MEASURED, libpcre2 10.46 vs python 3.14.4:**

```
pattern   subject     pcre2      python     verdict
b\Z       'ab\n'      (1, 2)     None       *** DISAGREE ***
a*\Z      'aaa\n'     (0, 3)     (4, 4)     *** DISAGREE ***
\Z        '\n'        (0, 0)     (1, 1)     *** DISAGREE ***
b\z       'ab\n'      None       None       agree
b\z       'ab'        (1, 2)     (1, 2)     agree
b$        'ab\n'      (1, 2)     (1, 2)     agree
\A a-cells                                  agree (all, incl. `pos`)
```

Over the implementation lane's own 29 probe patterns × 22 cells, exactly 7
patterns diverge and **all 7 contain `\Z`**; nothing else in the module's
alphabet does.

**Why it matters more than an ordinary exclusion.** Both divergences run in
the SILENT direction: python reports no match where PCRE2 matches, or a
shorter span. An expectation derived from python therefore encodes `\z`, and
a compiler that lowered `\Z` as `\z` would pass it. The oracle would be
agreeing with the bug — this project's recorded check-design failure, arriving
through the oracle rather than through a control.

**Impact**: every block in `tests/assertions/` whose pattern contains `\Z` is
marked `# pcre2-only`, and `tests/assertions/verify_pcre2.py` re-verifies the
whole directory (both marked and unmarked blocks) against libpcre2 on every
`make test`, through `tests/fuzz/pcre2_oracle`. `\A` and `\z` blocks are NOT
excluded and ARE checked live by `verify_rxt.py`, which is the standing proof
that the split is about `\Z` specifically rather than about the module.

The exclusion rule is applied to `\Z` blocks WHOLESALE, not per diverging
cell: a subject added to an unmarked `\Z` block later would silently start
lying, and there is no mechanical way for the corpus to notice.

---

### U11b — python `re`: multiline `^` MATCHES AFTER A FINAL NEWLINE, PCRE2's does not (module `assertions`, [M6.2] wave C)

**Found**: 2026-08-19 by the [M6.2] wave C implementation lane, through
`tests/assertions/run_mline_diff.sh` — a generated subject sweep at
`startpos > 0`, not by reading a manual. **It was a live pcrec defect first
and an oracle divergence second**, and the order matters: pcrec had
implemented the rule the design states, which is python's rule.

**The divergence.** PCRE2's multiline `^` matches at offset 0 and immediately
after an INTERNAL newline; pcre2pattern is explicit that it "does not match
after a newline that ends the string". python's `re` under `MULTILINE` has no
such exclusion. So `(?m)^` and `(?m)$` are NOT mirror images in PCRE2, and
they are in python.

**MEASURED, libpcre2 10.46 vs python 3.14.4:**

```
pattern      subject   startpos   pcre2      python     verdict
(?m)^        'a\n'      1          None       (2, 2)     *** DISAGREE ***
(?m)^        'a\n'      2          None       (2, 2)     *** DISAGREE ***
(?m)^[^c]*   'ac\n'     1          None       (3, 3)     *** DISAGREE ***
(?m)^$       'a\n'      0          None       (2, 2)     *** DISAGREE ***
(?m)^        'a\n'      0          (0, 0)     (0, 0)     agree
(?m)$        'a\n'      any        matches at 1 AND 2 in both   agree
```

**CORROBORATED BY PCRE2's OWN OPTION SURFACE, which this tree had already
surveyed.** `docs/pcre2_options.md`'s `PCRE2_ALT_CIRCUMFLEX` row (RATIFIED
2026-08-14, D38) reads: "under `MULTILINE`, `^` ALSO matches immediately after
a final trailing newline". An option whose entire content is turning that on
is only meaningful if the DEFAULT is off. The fact was in this repository the
whole time, one document away from the design that got it wrong; nobody
composed the two. Worth naming as a process finding rather than only a
semantic one — a survey row is evidence, and this lane found it after the
sweep rather than before.

**Why the corpus could not have caught it and the sweep could.** From
`startpos 0` an earlier match masks the trailing position on almost every
subject — `(?m)^` on `"a\n"` reports `(0,0)` from both — so a corpus that
only searches from 0 is blind to it. It needs a RESUME past the earlier
match, which is what a `startpos > 0` sweep does and what the `.rxt`
corpus's first `(?m)` draft had none of. `(?m)^$` is the single shape that
shows it from `startpos 0`, because no earlier position satisfies both
halves; it is now in the corpus by name.

**Impact**: every block in `tests/assertions/` whose pattern sets `m` AND
contains a `^` is marked `# pcre2-only`, on the same WHOLESALE rule the `\Z`
blocks follow above and for the same reason — a subject or a startpos added
later must not silently start lying. `(?m)$`-only blocks are NOT excluded and
ARE checked live by `verify_rxt.py`, which is the standing proof that this
split is about multiline `^` specifically rather than about `(?m)`.


### U11c — python `re`: `\G` DOES NOT EXIST (module `assertions`, [M6.2] wave D)

**Found**: 2026-08-19 by the [M6.2] wave D implementation lane, in the first
minute of writing the corpus — unlike U11 and U11b this one needs no
measurement to discover, only to record precisely.

**The divergence is TOTAL, which makes it the easiest of the three to handle
and the most important to write down.** U11 is python answering a `\Z` cell
WRONGLY; U11b is python answering a `(?m)^` cell DIFFERENTLY. Neither is
visible without comparing. `\G` is not a python construct at all:

```
>>> import re; re.compile(r'\G')
re.error: bad escape \G at position 0
```

There is no flag, no `re` dialect and no rewriting that expresses it. python's
`re` has no notion of a match's *start offset* being assertable: `pos` exists
as a `search()` argument but nothing in the pattern language can test against
it. (`\A` is offset 0 absolutely, which is a DIFFERENT assertion and the one
`\G` is most likely to be confused with — they coincide only at
`startpos == 0`.)

**Impact**: `tests/assertions/gpos.rxt` is `# pcre2-only` in its ENTIRETY,
block by block, and is verified by `tests/assertions/verify_pcre2.py` against
libpcre2. That is the third place in module `assertions` where the base-tier
oracle cannot answer, after `\Z` and `(?m)^`; `\K` will be the fourth, and
for this same total reason rather than U11/U11b's partial ones.

**The consequence for the wave's INSTRUMENTS is the part worth reading.**
`tests/assertions/run_mline_diff.sh` runs python beside libpcre2 not to judge
pcrec — D26 makes libpcre2 the truth — but to catch the SCRIPT driving the
oracle wrongly, since python shares no code with libpcre2. That arm cannot
run on `\G` patterns at all. `run_gstart_diff.sh` therefore keeps the arm and
points it at the sweep's own `\G`-FREE CONTROL patterns (§0), over the same
subjects, the same startpos values and the same oracle invocation. It is a
strictly weaker instrument than wave C's and it is the strongest one
available: a startpos convention error or a subject that lost a byte still
shows up there, and nothing else in the tree would see it.

### U11d — python `re`: `\K` DOES NOT EXIST (module `assertions`, [M6.2] wave E)

**Found**: 2026-08-19 by the [M6.2] wave E implementation lane. U11c's shape
exactly, one construct over, and recorded separately for the reason U11c is
separate from U11: the four exclusions in this module are four different
FACTS, and a reader who sees one entry covering "some assertions" cannot tell
which constructs are safe to write a python-verified cell for.

```
>>> import re; re.compile(r'a\Kb')
re.error: bad escape \K at position 1
```

**There is no rewriting, and here the reason is deeper than U11c's.** `\G`
is unexpressible because python cannot assert against a search's start
offset; `\K` is unexpressible because python's `re` has no way for a pattern
to move the REPORTED START of its own match at all. A lookbehind gets close
in the cases where the pre-`\K` part is fixed-width (`(?<=a)b` for `a\Kb`),
and it is not the same construct: it is a different assertion with different
backtracking behaviour, it fails on the variable-width shapes that make `\K`
worth having, and it needs module `lookaround`, which does not exist. Writing
a cell that way would encode a translation and check the translation.

**Impact**: `tests/assertions/kreset.rxt` is `# pcre2-only` in its ENTIRETY,
block by block, and is verified by `tests/assertions/verify_pcre2.py` against
libpcre2. That is the FOURTH entry in module `assertions` where the base-tier
oracle cannot answer — `\Z` (U11, WRONG answer), `(?m)^` (U11b, DIFFERENT
answer), `\G` (U11c, no answer) and `\K` (this entry, no answer) — and it
COMPLETES the list. Counted by CONSTRUCT rather than by entry: three of the
module's eight are excluded WHOLLY (`\Z`, `\G`, `\K`) and a fourth PARTLY
(`(?m)`, its `^` half only), while `\A`, `\z`, `\b`, `\B` and `(?m)$` are
python-verified cell for cell at 0 divergences. That asymmetry is the point:
the exclusions are statements about particular constructs — and, for `(?m)`,
about one HALF of one — never about the module.

**The consequence for the wave's INSTRUMENT is U11c's, plus one thing U11c
did not need.** `run_kreset_diff.sh` keeps the python arm on `\K`-FREE
control patterns for U11c's reason. But wave E also needs an oracle for a
question no oracle binary in this tree exposes — "does this pattern match
ANCHORED at offset `sp`", which is what `<prefix>_match`/`_match_caps`
answer — and the answer is to ask libpcre2 about `\G(?:PAT)` at startpos
`sp`. `\G` is exactly "match here and nowhere else", so wave D's construct
becomes wave E's oracle device, from libpcre2's own engine with no arithmetic
of the script's own. That is worth recording beside the exclusion because it
is the shape of the answer whenever an entry point has no oracle flag: find
the PATTERN SPELLING that asks the oracle the same question.

---

## U12 — python `re`: FOUR divergences on backreferences (module `backrefs`, [M6.5.2])

- **Status**: four unrelated divergences, filed together because all four were
  found authoring the same corpus (`tests/backrefs/`) and because together
  they are the largest oracle loss pcrec has met — **of 25 measured spellings,
  20 are accepted by libpcre2 and only 5 also work in python `re`**. Each is
  divergence-by-design rather than a bug on either side, and each is DETECTED
  rather than assumed: `tests/backrefs/gen_corpus.py` drives every cell through
  both oracles in one pass and writes `# pcre2-only` where they disagree, with
  the first disagreement and the cell count recorded in the file.

- **Divergence 1 — SELF- AND FORWARD REFERENCES are python COMPILE ERRORS.**
  `(a\1)`, `^(\1a)$`, `\2(a)(b)` and `(\2(a)|b)+` all COMPILE in libpcre2 and
  are governed entirely by the unset-reference rule (an unset reference FAILS
  at match time; it does not match empty). python `re` refuses every one of
  them at compile time — "cannot refer to an open group", "invalid group
  reference" — so there is no python-derived expectation for any of them.
  MEASURED: 9 cells over 8 distinct patterns (`(\2(a)|b)+` appears twice, on
  `"ba"` and `"baa"`, and answers (0,1) both times).

  **This is the module's largest oracle loss and it lands exactly where the
  module is hardest.** The RE-ENTRY class — `(a|b\1)+` and relatives, a live
  reference INSIDE the group it names — is where the difference between
  publishing a capture at the group's OPEN and at its CLOSE is observable, and
  python cannot express a single cell of it. So `tests/backrefs/selfref.rxt`
  is wholly `# pcre2-only`, and the second oracle for that population is not a
  second regex engine but a SIMULATOR of the emitted model, run in both
  publication disciplines (`docs/design/backrefs_measurements/probes/simvm.py`,
  adopted from the R32 panel rather than written by the implementing lane).

- **Divergence 2 — `\g`, `\k` and `(?J)` DO NOT EXIST in python `re`.** python
  has `\1`, `(?P<n>...)` and `(?P=n)`, and nothing else this module implements:
  `\g1`, `\g{-1}`, `\g{name}`, `\k<n>`, `\k'n'`, `\k{n}` and the `(?J)` letter
  are all "bad escape" / "unknown extension" there. It also rejects the
  `(?<n>...)` declaring spelling (U10 divergence 1), so `^(?<n>a)(?P=n)$` —
  legal PCRE2, and the ONE by-name reference form python does have — is still a
  python compile error as written. `tests/backrefs/dupnames.rxt` is therefore
  wholly `# pcre2-only`, and `spellings.rxt` is all but one block.

- **Divergence 3 — `(?i)` ANYWHERE BUT THE PATTERN START is a python compile
  error**, and it takes the two cells that decide WHERE a backreference's
  caselessness is read. libpcre2 answers `^((?i)a)\1$` and `^(?i)(a)(?-i)\1$`
  cleanly (both NO MATCH on "aA": the compare's caselessness is the option in
  force AT THE REFERENCE, not at the group). python refuses both with "global
  flags not at the start of the expression". So `caseless.rxt` is MIXED — most
  of it is python-verifiable and the two load-bearing cells are not, which is
  the direction R32 C3 found the first test plan getting backwards.

- **Divergence 4 — the CLASS position, already filed as U7, reaches this
  module too.** `[\8]`, `[\9]`, `[\g]` and `[\k]` are the LITERAL characters in
  PCRE2 (and in pcrec, as BASE syntax the module gate never touches), and
  python rejects all four as bad escapes; `[\400]` is a PCRE2 error 151 with no
  python analogue. So 4 of `octal_class.rxt`'s 12 cells have no python oracle —
  and that file's whole purpose is to pin that this module does NOT change the
  class position, so losing the second oracle there is worth naming rather than
  absorbing.

- **What pcrec does about it**: nothing, in the compiler. The corpus records
  the divergences per block with the measured evidence, `gen_corpus.py`
  computes the markings rather than trusting a plan, and libpcre2 10.46 is the
  oracle of record for every cell python cannot arbitrate — which for this
  module is 62 of 112 blocks.

## U13 — libpcre2 VERSION DRIFT 10.46 → 10.48: option-run acceptance (PC-3, found by [MACPORT], 2026-09-04)

**The divergence.** Option runs libpcre2 10.46 ACCEPTS, 10.48 REJECTS with
error 111 ("unrecognised character after (?"): measured probe (ctypes,
2026-09-04) — `(?a:a)`, `(?r)`, `(?aU)a`, `(?aD:x)` all ACCEPTED by 10.46
(2025-08-27, the old box's libpcre2-8-0) and all REJECTED by 10.48
(Homebrew, the Mac dev box); `(?i:a)` accepted by both. pcrec's registry
was measured against 10.46 and agrees with it, so on a 10.48 box PC-3's
"GATED T1 [option runs]" family reads 119 failures that are NOT pcrec
regressions — reproduced deterministically, identical split across runs
([MACPORT]'s report, docs/dev/lanes/macport_report.md, has the discovery;
the classifying probe is in the journal, fifty-third session).

**Disposition.** The reference oracle stays 10.46 (the old box, where the
battery runs). PC-3 red on a 10.48 box is EXPECTED and this entry is the
citable reason; do not "fix" pcrec toward 10.48 without a ruling —
adopting a new reference version is a deliberate re-measurement event
(the pcre2_options.md standing constraint, D26's moving-target clause).
Revisit when: the reference box's libpcre2 upgrades, or Frank rules a
version adoption, or a PC-2 re-survey fires.

## U14 — `tests/harness/verify_rxt.py`'s subject decoder is byte-oriented, not UTF-8-aware (`encoding utf8`, [M5.0] stage 2, found by lane utfprom promoting tests/utf8/)

**Not a divergence in python `re`'s own semantics** — every other entry in
this file is about the regex ENGINE; this one is about the shared
harness's own oracle TOOLING. `verify_rxt.py`'s `decode_subject` maps
every `\xHH` escape to one python `str` character one-for-one (correct for
the project's byte-tier default), while the block's PATTERN text is read
from the `.rxt` file as real UTF-8 and compiled by `re.compile` as a true
Unicode string. Under `encoding utf8` (and, measured, under `encoding
byte` too whenever a LITERAL multi-byte character sits directly in the
pattern source — the byte-decomposition axis1/2/3 mirror files exist to
exercise) a multi-byte UTF-8 sequence therefore compiles or matches as the
WRONG NUMBER of "characters" under python, independent of whether pcrec's
own answer is right.

**Repro**: pattern `α` (one real Unicode character U+03B1, `-e utf8`)
against subject `"\xce\xb1"` (alpha's own UTF-8 bytes) — `re.compile`
compiles a 1-character pattern; `decode_subject` turns `\xce\xb1` into
the 2-character python string `"Î±"`. The two can never align at
the right byte offset, so a correct pcrec answer reads as a python
"failure" that is really a decode-scale mismatch, not a semantic one.
MEASURED at promotion: 211 spurious failures across `tests/utf8/`'s 13
files under the DEFAULT sweep, on cells `tests/harness/run.sh` (the real,
live oracle) answers correctly.

**Impact**: every affected block in `tests/utf8/` carries `# pcre2-only`
(255 blocks marked at promotion) — see that directory's own CLAUDE.md.
`python3 tests/harness/verify_rxt.py tests/utf8` is 100% PASS on what's
left (376/376, 959 skipped for this and the ordinary
`no-python-expression` reason combined).

**Not fixed here**: a UTF-8-aware subject decoder in `verify_rxt.py`
(decode a block's subject as UTF-8 bytes when its `encoding` directive
says `utf8`, and re-encode the pattern to bytes and compile in BYTES mode
throughout — the fix has to touch both sides, not just the subject, since
python's `re` module does not mix `str` patterns with `bytes` subjects) is
shared harness infrastructure outside this lane's `tests/utf8/`-only
scope; filed as the natural next step for whoever builds this corpus's
own libpcre2 differential (`tests/utf8/CLAUDE.md`'s "Maintenance" section)
— that instrument needs UTF-8-aware oracle machinery anyway; teaching
`verify_rxt.py` the same trick may or may not be worth a second
implementation once it exists.

## U15 — libpcre2's OWN property definitions move between versions, and the dlopen shim resolves an OLDER library than anyone thought ([M5.0] stage 3, lane utf8s3, 2026-09-06)

Two findings, filed together because the second is why the first was noticed
at all and neither is a pcrec defect.

### (a) `\p{Xwd}` changed meaning between 10.42 and 10.46

**The divergence.** `Xwd` is a PCRE2 invention with no UCD definition, and
libpcre2 has changed what it denotes:

| libpcre2 | `\p{Xwd}` is |
|---|---|
| 10.42 | `Xan` plus underscore |
| 10.46 (**the reference**), 10.48 | `Xan` plus `Mn` plus `Pc` |

**Measured** (light ctypes probe of the reference box, transcript in the lane
report): 10.46 matches `\p{Xwd}` against U+0300 COMBINING GRAVE ACCENT (`Mn`),
U+005F LOW LINE (`Pc`) and U+203F UNDERTIE (a non-ASCII `Pc`), and does not
match U+0021 (`Po`). `man pcre2pattern` on 10.48 states the newer rule
outright — *"Xwd matches the same characters as Xan, plus those that match Mn
... or Pc"* — so the change is documented, not silent.

The SAME probe found the same shape one property over: `\p{Xps}` on 10.46
matches U+0085 NEXT LINE and U+180E MONGOLIAN VOWEL SEPARATOR, neither of
which is in the `Z` category the man page's `Xps` sentence names. That
sentence is incomplete rather than wrong — the complete rule is `Z` unioned
with PCRE2's own documented horizontal- and vertical-space lists — and pcrec's
generator states it that way with the correction recorded at the definition.

**Disposition.** pcrec follows the REFERENCE (10.46) and therefore ships the
newer `Xwd`. Against an older oracle this shows up as a real, large membership
disagreement — 1,958 code points on the `utf8` arm — which
`tests/uprops/uprops_compare.py`'s `PCRE2_SEMANTIC_DRIFT` tier excuses, and
excuses TIGHTLY: the residue must lie inside `Mn` ∪ `Pc` as pcrec's own sweep
reports them in the same run, so a table bug outside that set still fails and
names its code points. Do not "fix" pcrec toward 10.42. Revisit when: the
reference box's libpcre2 upgrades, or Frank rules a version adoption.

### (b) the dlopen shim resolves macOS's SYSTEM libpcre2, not Homebrew's

**Not a divergence in another engine at all** — like U14, this is about the
shared harness's own oracle tooling, and it changes what several existing
entries in this file are actually describing.

`tests/fuzz/pcre2_abi.h`'s candidate list puts bare SONAMEs first and the
Homebrew absolute paths after. On macOS a bare name resolves through the dyld
shared cache, so **every dlopen-based oracle in this tree — PC-3, PC-4, the
fuzzer, and every module differential built on the shim — loads
`/usr/lib/libpcre2-8.0.dylib` on the Mac dev box.** Measured 2026-09-06 by
dlopening each candidate in turn and reading `pcre2_config`:

| candidate | resolves to | libpcre2 | Unicode |
|---|---|---|---|
| `libpcre2-8.dylib` | `/usr/lib/libpcre2-8.0.dylib` | **10.42** | 14.0.0 |
| `libpcre2-8.0.dylib` | `/usr/lib/libpcre2-8.0.dylib` | 10.42 | 14.0.0 |
| `/opt/homebrew/lib/libpcre2-8.dylib` | Homebrew Cellar | 10.48 | 17.0.0 |
| `/usr/local/lib/libpcre2-8.dylib` | (not loadable) | — | — |

**This is not what the project's own notes say.** `docs/dev/lanes/
BOILERPLATE.md` states "local libpcre2 is 10.48-Homebrew"; the `[MACPORT]`
report's PC-3 escalation is filed above as **U13, "VERSION DRIFT 10.46 →
10.48"** — and the pkg-config/header toolchain IS 10.48, so a probe written
with `#include <pcre2.h>` sees 10.48 while the suite sees 10.42. U13's
classifying probe was of the first kind. **Whether U13's 119 PC-3 failures are
10.48 behaviour or 10.42 behaviour is therefore an OPEN question this entry
re-opens**, and it matters: 10.42 predates 10.43, which is where U2's `{,n}`
change landed, so a pre-10.43 oracle is a materially different reference from
a post-10.46 one. It is also the same shape the `utfprom` lane already hit
from the python side ("oracle provenance is LOCAL 10.37 — the `find_library`
hazard").

**Disposition — a RULING IS OWED, and this lane deliberately did not take
it.** Reordering the candidate list (absolute Homebrew paths first) would
change which oracle the WHOLE suite compares against, on one box, in one line
— a project-wide re-baseline, not a stage-3 edit. What stage 3 did instead:
added `pcre2_abi_unicode_version()` to the shim (`PCRE2_CONFIG_UNICODE_VERSION`
is **10**; 9 is `PCRE2_CONFIG_UNICODE`, a uint32 that reads as an empty string
in a char buffer, which is how the constant was got wrong the first time), and
made `tests/uprops/` read the resolved oracle's version and PRINT it on every
run, so a result can be attributed rather than assumed.
