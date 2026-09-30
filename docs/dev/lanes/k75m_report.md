# k75m — K75's measurement (PCRE2 at continuation-byte start offsets)

Lane k75m (sonnet, measurement only, 2026-09-30), branch `lane/k75m` from
`lane/k73utf` (`bd1be543`). Nothing under `src/`/`cli/`/`lib/`/`tests/`; no
`make test`. Memo: `docs/dev/k75_measurement.md`; evidence:
`docs/dev/lanes/k75m_evidence/`.

## Findings

1. **PCRE2 draws no line between a mid-character position and a stray.**
   Without `MATCH_INVALID_UTF` every continuation-byte startoffset is
   `BADUTFOFFSET` (-36); with it every one is advanced to the next
   non-continuation byte. Same for true mid-character (A, 10 cells), stray (B,
   13) and a truncated sequence's continuation (T, 4), anchored or not, 9
   patterns. pcrec refuses all of them (offset 0 aside, K73).
2. **Under `MATCH_INVALID_UTF` the moved start is a chunk boundary**: a
   lookbehind cannot see behind it (`(?<=.)x*` on `c3 a9 78` from 1 answers
   (3,3), not (2,2)), on a well-formed subject too.
3. **K75 is a find-all-loop problem, and the caller can fix it for free.**
   `p = next_pos(s, n, end - 1)` after a non-empty match: over 19,608
   subjects x 11 patterns it takes five patterns from 572 / 2,408 / 2,980 / 2 /
   492 divergences (`a`, `.`, `a|`, `(?<=a)b`, `(?<!a)b`) to 0, never turns an
   agreeing subject into a disagreeing one, and is a no-op on a well-formed
   subject (no abi event, no engine change). The three residual patterns
   (`\B`, `\b`, `(?<=.)x*`) diverge identically before and after: engine never
   attempts at a stray (K74 / [UTF-VALID]).
4. An engine-side change that answers an explicit stray while refusing kind A
   is separable but expensive (backward well-formedness scan at four guard
   sites, abi bump, a ruling on T) and its line would be pcrec-only.

## Recommendation for Frank

Take M1: put the alignment in the §3.1 loop (and `rxt_format.md` `mc`, the
encseam driver, `mc_illformed_utf8.rxtin`, and relay the bench's find-all
formula), keep K50's refusal exactly as it is for A, B and T. Close K75 on
that, not on a guard change. If an explicit stray startpos must someday be
answered, that is M2 and a separate abi event. Ruling owed on K75 remains
Frank's; ruling (a) is untouched.

## Validation and caveats

Complete for what was asked: 3,942 grid cells, 19,608 x 11 find-all cells,
both against local libpcre2 10.48 (Homebrew), NOT the 10.46 reference; the
A/B/T grid was not re-run on the 10.46 box (one light confirmation
recommended before a spec sentence cites it). Scratch in `/tmp/claude-k75m`
(reproduction scripts in the evidence dir carry that path at the top).
