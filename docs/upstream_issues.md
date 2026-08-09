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

---

Maintenance: add an entry whenever differential tooling implicates another
engine; update status when reported/resolved upstream. Cross-reference from
docs/testing.md (oracle exclusions) and tests/fuzz/README.md.
