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
