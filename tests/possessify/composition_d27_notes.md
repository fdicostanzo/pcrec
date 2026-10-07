# composition_d27 -- notes (D27-blinded author, 2026-10-07)

Corpus: `tests/possessify/composition_d27.rxt`. Oracle: libpcre2 10.46 (2025-08-27, 8-bit,
interpretive `pcre2_match`, no JIT, no UTF/UCP) compiled with `PCRE2_NO_AUTO_POSSESS`
(0x4000), plus `PCRE2_CASELESS` for blocks carrying `flags i`.

## Size

- 676 pattern blocks, 7,412 cases (3,874 `m`/`ms` matches, 1,590 `gp` capture lines,
  the rest `n`/`ns`), of which 1,348 are `ms 1|2` (startpos) cases on the block's longest subject.
- 103 blocks are caseless. Roughly 9-11 subjects per pattern: the empty string (about 70% of
  blocks), a two-letter base string, `base base`, `-base-`, and random strings built from the
  pattern's own literal letters plus separators (space, `-`, `_`, digit, `.`, `,`), with random
  case swaps in caseless blocks.

## How it was generated

1. A seeded (27) Python generator composed patterns from templates, 13 families (counts are
   blocks kept in the file):

   | family | what | blocks |
   |---|---|---|
   | A | atom x quantifier (`* + ? *? +? {1,3} {2,} {0,2}? {1,2} {2} {1,3}? {0,}?`) followed by an optional/empty gate continuation (`(?:\b\|)`, `(?:\B\|)`, `(?:\|\b)`, `(?:(?=a)\|)`, `(?:(?!a)\|)`, `(?:\b\|a)`, `(?:\B)*`, `(?:(?<=a)\|)`, `(?:\b)??`, `(?=a)?`, `(?:\b){0,2}`, ...) and a terminal | 108 |
   | B | atom x quantifier followed directly by one of 27 zero-width gates (`\b \B`, +/- lookahead and lookbehind, bodies that can match empty such as `(?=a*)`, `(?=a\|)`, `(?!a*)`, variable-alternative `(?<=a\|bc)`, `(?=\b)`, `(?<!\B)`, anchors) and a terminal | 110 |
   | B0 | classic possessify-adjacent controls (`a*b`, `\w+\b`, `\W*\B`, `a*(?!a)b`, ...) | 35 |
   | C | `(body)q mid backref`: 23 group bodies (gates, empty-able, lazy, alternation with empty arm), 10 group quantifiers, numbered/`\g{1}`/`\g{-1}` backrefs, quantified and gated backrefs; 25% caseless | 85 |
   | C2 | the same with a named group and `\k<n>`, `\k{n}`, `\k'n'`, `\g{n}` | 35 |
   | C3 | hand-written multi-group / unset-group / looping-capture backref cases | 35 |
   | H | captures inside lookarounds and empty-able groups, referenced later | 24 |
   | D | subroutine calls and recursion (`(?1)`, `(?&n)`, `(?R)`) into gate-bearing or empty-able groups, balanced-paren recursion | 54 |
   | E | nested and enclosing loops, loops over gate/empty alternatives, atomic groups and explicit possessives | 71 |
   | F | caseless focus (case-pair gates, backrefs, recursion) | 27 |
   | I | `\b`/`\B`/anchors/`\G` stacked, with quantifiers | 36 |
   | J | lazy and bounded quantifiers followed by empty alternatives | 34 |
   | K | lookbehind interacting with a preceding quantifier | 22 |

2. Subjects were generated per pattern (second seed, 2701) as described above.
3. All (pattern, subject, startpos) triples were sent over ssh to the Linux box and run by a
   Python/ctypes driver over `libpcre2-8.so.0` (script and data via stdin; scratch in
   `/tmp/posscomp-$$`, deleted at the end of each run). The driver ran every pattern twice,
   with and without `PCRE2_NO_AUTO_POSSESS`, and recorded the full ovector (all groups).
4. **Driver check:** 183 random cells (whole-match text, caseless and not) were replayed through
   `pcre2test` with the `no_auto_possess` modifier; 0 disagreements.
5. The .rxt was emitted from the NO_AUTO_POSSESS column only. `gp` (not `g`) is used for every
   capture line, so a group beyond what an artifact delivers is pending rather than a hard fail.
6. Every block is marked `# pcre2-only` (python `re` is not this corpus's oracle) and carries
   `features all`; the file head has `oracle pcre2/10.46`. `pcrec --list-source` parses it (rc 0).

## Combination census (regex-approximate; a block can count in several rows)

| feature present in the pattern | blocks |
|---|---|
| `\b` | 292 |
| `\B` | 128 |
| lookahead positive / negative | 124 / 49 |
| lookbehind positive / negative | 65 / 37 |
| capture group (numbered or named) | 194 |
| backreference (`\1`, `\g{}`, `\k<>`) | 202 |
| named group | 47 |
| subroutine / recursion | 57 |
| lazy quantifier | 219 |
| bounded `{m,n}` quantifier | 213 |
| quantified group | 180 |
| empty alternative (`(?:x\|)`, `(?:\|x)`, `(?:)`) | 106 |
| atomic group / explicit possessive | 15 |
| anchors (`^ $ \A \z \Z \G`) | 105 |
| caseless | 103 |

Cross-combinations: gate (`\b \B` or any lookaround) with no backref and no subroutine 380;
gate + backref 154 (3 of them also with subroutines); gate + subroutine 33 (plus the 3);
`\b`/`\B` + backref 112; `\b`/`\B` + subroutine/recursion 30; empty alternative + lazy
quantifier 62; no gate at all 109.

## Default (auto-possess ON) vs NO_AUTO_POSSESS: differences

**None.** Over the 676 corpus patterns (7,412 cells) the match/no-match verdict, the whole-match
span and every capture span were identical with and without `PCRE2_NO_AUTO_POSSESS`. To look
harder than the corpus I also ran two throwaway grammar-fuzz batches of the same shape (random
atoms, 20 gates, 14 quantifiers incl. possessive, alternation with empty arms, captures,
numbered backrefs, atomic groups, lookarounds; 18,000 patterns, 139,696 cells, 20% caseless):
again 0 differences (1 cell hit a PCRE2 error, excluded). So there are no "interesting cells"
to list; the expected answer everywhere is the NO_AUTO_POSSESS one, which equals the default.
(What auto-possess does change in PCRE2 is match-limit consumption and callout/verb behaviour,
which this corpus does not exercise.)

## Exclusions

- **12 patterns rejected by PCRE2** (error 109, "quantifier does not follow a repeatable item"):
  every pattern with `\b?` / `\B?` applied directly to an assertion (e.g. `[^a]?\b?\b`,
  `-+?\b?-`). `(?:\b)?` and `(?:\b)??` are accepted and are in the corpus.
- **24 cells dropped** where PCRE2 itself errored (recursion loop / match limit), all in
  `(?:a|\b(?R))+`, `a*(?R)?b`, `^(a|\b(?1)b)` -- the other subjects of those patterns are kept.
- **1 pattern excluded because pcrec refuses it** (checked with the cell's `build/pcrec
  --features all`, a refusal only, answers not consulted): `(?<=(a?))x`, "variable-length
  lookbehind is not implemented" (PCRE2 accepts it: a capturing lookbehind that can match 0..1
  characters). It is a gap in the format of this corpus, not a possessify finding. Of 689 generated patterns, 12 were PCRE2-rejected, 1 pcrec-refused, 676 kept; all 676 compile under
  `--features all`. Note `(?(1)..)` conditionals
  are refused by pcrec and were deliberately not generated.

## DISCLOSURE

- At spawn, text from outside the cell was injected into my context without my reading it: the
  project's root `CLAUDE.md` (project instructions), the user's auto-memory index, and a git
  status/recent-commit snapshot. I did not use any of it to design or tune patterns or choose
  expectations.
- I read only `docs/spec/rxt_format.md` and `docs/spec/tuning.md` (a grep for "possessif") from
  the cell, plus the cell's `build/pcrec --list-syntax` / `--help` / `--list-source` outputs.
  I did not open `docs/testing.md` or `docs/pcre2_compliance.md` beyond a `grep` for "features"
  that surfaced module-gating lines.
- `build/pcrec` was used only for (a) `--list-syntax` module names, (b) compile-or-refuse checks
  with `--features all`, (c) `--list-source` parsing of the delivered file. Expected answers
  come solely from libpcre2.
- Housekeeping: one probe compile wrote `/tmp/x.c` on the Mac (outside the scratchpad); it was
  deleted immediately. All other scratch lives in a `mktemp -d` directory under `$TMPDIR` and is
  removed at the end. On the Linux box only `/tmp/posscomp-$$` was used, each run deleting it.
