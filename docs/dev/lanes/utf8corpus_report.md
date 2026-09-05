# [M5.0] D27 blinded UTF-8 corpus — author's report

Written by the D27-blinded author (denied `src/`, `tests/`, and everything
in `docs/design/utf8_design.md` beyond the extract at
`docs/design/utf8_d27_extract.md`), working entirely inside
`worktrees/utf8corpus-cell/`. Deliverables: `d27/*.rxt` (13 files, listed
below) and this report.

## 0. Disclosure — injected/ambient files beyond the cell

Per the brief's disclosure requirement, everything the harness put in front
of me at spawn time beyond the cell's allow-listed contents:

- The project root `CLAUDE.md` (pcrec's top-level conventions doc) was shown
  in full in a `<system-reminder>` before the manager's task message.
- The user's memory index, `MEMORY.md` (one-line pointers to ~20 memory
  files: process preferences, project status, check-design lessons, box
  concurrency rules, etc.), was shown alongside it.
- Both arrived as background context, not as part of the cell's own
  allow-listed file set. I did not open, follow, or act on any file
  `MEMORY.md` merely points to (I have no path to them and did not seek
  one), and nothing in either document changed anything about how this
  corpus was built — the task brief and the extract were the only inputs
  that shaped the corpus content. I am naming them here only because the
  brief requires listing every injected file, not because either carries
  implementation detail relevant to UTF-8.
- No other file, directory listing, or tool output outside
  `worktrees/utf8corpus-cell/` was read at any point. No `ssh`, no `make`,
  no access to the main repository tree.

## 1. What shipped

Thirteen `.rxt` files under `d27/`:

| file | blocks | perr | real | future-case comments | oracle-checked real cases |
|---|---:|---:|---:|---:|---:|
| axis01_encoded_length.rxt | 64 | 64 | 0 | 256 | 0 |
| axis01_encoded_length_byte.rxt | 64 | 16 | 48 | 0 | 144 |
| axis02_class_boundary.rxt | 24 | 24 | 0 | 96 | 0 |
| axis02_class_boundary_byte.rxt | 24 | 10 | 14 | 0 | 42 |
| axis03_invalid_utf8.rxt | 27 | 27 | 0 | 108 | 0 |
| axis03_invalid_utf8_byte.rxt | 27 | 0 | 27 | 0 | 108 |
| axis04_p_categories.rxt | 148 | 148 | 0 | 506 | 0 |
| axis05_p_refusals.rxt | 34 | 34 | 0 | 34 | 0 |
| axis06_caseless_fold.rxt | 48 | 48 | 0 | 192 | 0 |
| axis07_caseless_1ton.rxt | 11 | 11 | 0 | 22 | 0 |
| axis08_lookbehind_varwidth.rxt | 24 | 24 | 0 | 78 | 0 |
| axis09_nextpos_findall.rxt | 20 | 20 | 0 | 80 | 0 |
| axis10_surrogate_witness.rxt | 9 | 9 | 0 | 27 | 0 |
| **TOTAL** | **524** | **435** | **89** | **1,399** | **294** |

Primary (utf8-encoded) arm alone, excluding the three `_byte.rxt` mirror
files: **409 blocks / 1,399 future cases**, against the extract's own
sizing table of **423 blocks / ≈1,559 cases** (§8.3). Gap: 14 blocks / 160
cases, entirely accounted for by three disclosed, documented shortfalls
(§4 below) — not an omission nobody noticed.

Every `.rxt` file passes `python3 d27_scratch/check_rxt.py` today: 524
blocks parse cleanly under an independent, from-scratch parser, and every
one of the 294 real (non-`perr`) cases independently re-verifies against
that checker's own fresh `python re` call — a SEPARATE python process, a
separate decoder, zero shared code with the generator (§5).

## 2. Why (almost) everything is `perr` today, and why that is the honest, live-testable form

Measured live against the prebuilt `build/pcrec` before writing a single
block (commands and output kept in `d27_scratch/`):

- `-e utf8` refuses **every** pattern, unconditionally, today:
  `pcrec: encoding 'utf8' arrives with milestone M5 (an engine axis, not a
  module: no --features name enables it)`. This is [M5.0] stage 2, and only
  stage 1 (an internal IR refactor, per the git log at session start) has
  landed. Verified per-block (every one of the 409 primary-arm blocks
  independently confirmed this refusal against its own exact pattern text,
  not just once) — zero surprises.
- `\x{...}` and `\p{...}`/`\P{...}` refuse as `requires module
  'unicode-props'`, regardless of `--features unicode-props` (tried; makes
  no difference — the module is "unbuilt" per `--list-syntax`'s own `built`
  column) and regardless of encoding (`-e byte` refuses identically).
- A lookbehind (`(?<=...)`/`(?<!...)`) refuses as `requires module
  'lookaround'`, and a named-group call `(?&g)` refuses as `requires module
  'named-groups'` — both discovered live while building axis 8, not
  assumed; see the correction noted in that axis's generator header (an
  early draft of axis 8 checked the wrong gate for `\p{L}`-bodied blocks and
  a live run caught it — kept in the code as a documented fix, not silently
  smoothed over).

Given that, the only honest, live-testable shape for a utf8/unicode-props
-gated block today is exactly this project's own established convention
(`docs/spec/rxt_format.md`'s "expected-unsupported policy",
`tests/recursion/gen_corpus.py`'s worked example): a `perr` block pinning
today's real refusal, with the oracle-driven **future** answer for each
subject kept as a comment in ready-to-promote `m`/`n`/`ms`/`ns` syntax
directly above the `pattern` line. Landing the module becomes "delete the
`perr` line, uncomment the case lines, re-run" — not a rewrite.

**The byte-encoding mirror arm is different and often genuinely live.**
Three axes (encoded-length, class-boundary, invalid-UTF-8) have primary
patterns that are largely literal multi-byte characters with no
`\x{}`/`\p{}`, and those compile FINE under `-e byte` today. Two outcomes
were found, both real and LIVE-verified (pcrec's own byte-mode output
cross-checked against python's bytes `re` engine before being recorded —
294 cases, zero disagreements):

1. A **bare, unwrapped** literal multi-byte sequence matches identically to
   a byte-literal reading (e.g. `alpha` on `alpha` matches `(0,2)` under
   `-e byte` too — two literal bytes, matched in sequence).
2. A literal **wrapped** in a class/quantifier/range/alternation compiles
   under `-e byte` but is **byte-decomposed**: `[alpha]` under byte encoding
   is a class containing the two BYTES `0xCE` and `0xB1` as independent
   alternatives (matches either byte alone!), and `alpha+` is the literal
   byte `0xCE` followed by `(0xB1)+`. This is neither a refusal nor an
   identity match with the utf8-encoded promise — it is exactly the reason
   the utf8 encoding module needs to exist at all, and axis 3's mirror file
   captures the sharpest instance of it: `a.+a` under `-e byte` MATCHES
   through an "ill-formed" byte sequence (a byte engine has no notion of
   ill-formed UTF-8), where the utf8-encoded promise is explicitly NO MATCH
   (extract Sec 2.6).

Axes 4–10 do not have a byte-mirror file. This is a real, disclosed scope
cut, not an oversight — see Sec 4.

## 3. Oracle provenance — and a correction to the brief's own version claim

**The brief said the local libpcre2 would be 10.48 (Homebrew). It is not.**
Measured: `ctypes.util.find_library("pcre2-8")` — the fallback
`pcre2_ctypes.py`'s loader reaches after its two literal `.so` names fail
(this is macOS; those are Linux sonames) — resolves to
`/Users/fdicostanzo/miniconda3/bin/../lib/libpcre2-8.dylib`, **libpcre2
10.37 (2021-05-26)**. A newer copy, **10.48**, sits on this same machine at
`/opt/homebrew/Cellar/pcre2/10.48/lib/libpcre2-8.dylib` (installed via
Homebrew) but is never reached: the loader's search order finds the
Miniconda copy first, and dlopen never fails, so the brief's own documented
fallback ("set the library path env it documents if the dlopen fails") never
triggers — there is no failure to trigger it. I did not modify the loader
or force the Homebrew copy; every measurement in this corpus is against
**10.37**, not 10.46 (project reference) and not 10.48 (what the brief
expected). This is disclosed rather than silently absorbed because it is a
BIGGER and DIFFERENT drift than the brief itself anticipated.

**Before trusting 10.37 for anything not explicitly in the extract's own
tables, I ran a targeted validation sweep** (`d27_scratch/verify_drift.py`)
reproducing every literal measured cell the extract states for 10.46:
Sec 1.3's construct-table refusals, Sec 2.6(b)/(c)'s ill-formed-subject
barrier cells, Sec 2.6.1.1's full mid-character-startpos table (all four
rows, THREE different columns), Sec 4.1's 0-of-11 simple-folding finding,
Sec 4.2's closure triples and the two dotted/dotless-I non-folds,
Sec 4.2(c)'s `[a-z]` vs KELVIN/LONG-S, Sec 4.3's fold-before-negate cells,
Sec 5.6's eight-body lookbehind population, and Sec 7.1.1's UCP-split
arbitrating-oracle table (including the one discriminating cell, `\b`
between ASCII and Greek, and the one cell that fails for a unit reason,
`\W` over Greek). **Every single one reproduced exactly** on this cell's
10.37, with one narrow, disclosed exception: the two truncated-UTF-8 error
CODE NUMBERS the extract states for 10.46 (-8/-9) came back as -3/-4 on
10.37 (same semantic kind — "N bytes missing at end" — different numeric
code; see axis 3's generator header). Given that level of agreement, I
judged 10.37 usable as this corpus's oracle for cells the extract doesn't
itself tabulate, with the truncation-code drift called out at its one point
of use and nowhere else assumed to propagate.

**Every oracle-checked assertion carries its options word**, per the
brief's own rule — every future-case comment line ends in
`# oracle=PCRE2_UTF` / `PCRE2_MATCH_INVALID_UTF` / `PCRE2_UTF|PCRE2_CASELESS`
etc. (rendered by `u8_oracle.opts_name`, never hand-typed), and the four
mid-character-startpos blocks in axis 9 are explicitly marked
`pcre2-ARGUED (no oracle produces this)` since they encode pcrec's own
design POSITION (extract Sec 2.6.1.1's fourth column) rather than any
single library's measured answer — the other three measured columns are
kept alongside as context, explicitly labelled NOT the expected value.

**Python** is `python3.11.4`; `flags i` (nowhere used in this corpus's
directives, but relevant to the checker) maps to `re.ASCII | re.IGNORECASE`
per `rxt_format.md`'s own rule.

## 4. Design choices and disclosed deviations from a literal reading of Sec 8.3's table

The extract's population-sizing table gives DERIVATIONS ("4 lengths x 4
contexts x 4 shapes"), not literal non-overlapping recipes — several of its
own context/shape names overlap by construction (no reading makes "class"
a distinct axis from itself, named as both a context and a shape). Every
place I resolved that ambiguity is called out in the corresponding
generator's own header comment (`d27_scratch/axis_*.py`), not only here.
Summary:

- **Axis 1** (64/256, exact): implemented as 16 genuinely distinct pattern
  shapes (bare/class/negated/quantified x literal/escaped/range/bounded x
  alternation forms) x 4 byte-widths, rather than trying to force a literal
  non-overlapping 4x4 context/shape grid.
- **Axis 2** (24/96, exact): 12 shapes x 2 boundary pairs (the exact
  U+007F/U+0080 length boundary, and the extract's own worked example
  `a`/alpha) rather than a literal 6-shape x 4-spelling grid.
- **Axis 3** (27/108, exact): the "9 measured ill-formed kinds" are MY OWN
  live measurement against 10.37 (the extract states codes, not byte
  sequences), reproducing 6 of the extract's stated codes exactly (-22, -23,
  -17, -16, -15, -13) with one disclosed drift (truncation codes -3/-4 here
  vs -8/-9 there).
- **Axis 4** (148/506, target ~150/600): delivers the exact 37x2x2=148 the
  extract's own arithmetic derives, not the stated "rounded" 150 — I chose
  not to pad two arbitrary filler blocks onto a number the extract itself
  calls a rounding. `\p{Cs}` (surrogates) structurally has zero reachable
  members in this corpus's own candidate pool, because a surrogate scalar
  has no valid UTF-8 encoding — that absence is itself the correct
  measurement, not a generator failure (flagged live, not silently
  swallowed).
- **Axis 5** (34/34, exact): straightforward; all 34 spellings confirmed
  live as error 147 under BOTH `options=0` and `PCRE2_UTF`.
- **Axis 6** (48/192, target ~60/240): the extract's own row text
  ("6 pairs + 2 non-folds + 4 closure shapes + 3x4 fold-before-negate ≈ 60")
  does not reconcile to 60 under any factoring I could reconstruct from the
  included material alone — I believe the excluded Sec 5.6.1-adjacent
  resolution style (or an excluded internal reference) supplies the missing
  multiplier. I delivered the fully-justified 48 (6 pairs x 4 case/escape
  spellings + 2 non-folds x 4 spellings + 4 closure shapes, unmultiplied + 3
  fold-before-negate shapes x 4 spellings) and disclosed the gap rather than
  padding to hit a number I could not derive. **This axis's sibling (axis 7)
  caught a real generator bug live**: the first draft's four
  "precomposed-vs-decomposition" 1:n candidates were typed to *look*
  decomposed in source but a combining-character sequence renders
  identically to its precomposed glyph in a text editor — the oracle
  immediately flagged all four as "UNEXPECTEDLY MATCHED" (a pattern
  trivially matching itself is not a 1:n candidate), and the fix (explicit
  `\uXXXX` escapes, never a literal glyph) is kept in the generator with the
  bug's own history documented in a comment.
- **Axis 7** (11/22, exact): "match + reverse direction" is not literally
  realizable as two DIFFERENT patterns inside one `.rxt` block (a block has
  exactly one `pattern` line); I read it as (1) a vacuity-guarding positive
  control — the literal still matches itself caseless — and (2) the actual
  0-of-11 assertion. Disclosed as an interpretation, not asserted as the
  extract's own intended meaning.
- **Axis 8** (24/78, target 24/96): "call-bearing" is excluded-section
  vocabulary; read here as a lookbehind body reached through a subroutine
  call (`(?&g)`), which LIVE-measurement showed hits a further, independent
  module gate (`named-groups`) — itself a disclosable fact. The 78-vs-96
  shortfall is the live-classification pool occasionally finding only 1
  member/non-member for a body (e.g. `[\x{0}-\x{10FFFF}]` has essentially no
  non-members in a small pool), same graceful-degradation shape as axis 4's
  thin categories.
- **Axis 9** (20/80, exact): `.rxt` has no native find-all/next_pos
  directive (confirmed against `docs/spec/rxt_format.md`); the 16
  boundary-walk blocks are a proxy — one `ms` case per character boundary
  of the subject, the exact sequence of positions a real find-all loop
  would visit. The 4 mid-character-startpos blocks are the extract's own
  Sec 2.6.1.1 table, verbatim, including its "ARGUED" fourth column.
- **Axis 10** (9/27, exact): straightforward; every surrogate encoding is,
  correctly, ill-formed UTF-8 with no valid scalar, so its oracle is the
  same `MATCH_INVALID_UTF` barrier axis 3 uses.

**Byte-mirror coverage is a real, disclosed scope cut.** I built the mirror
for axes 1–3 (409 -> 115 mirror blocks, 294 live-double-oracle-verified real
cases) because it surfaced genuinely new, informative behaviour (the
byte-decomposition finding above). I did not build mirrors for axes 4–10:
axes 4–5 are `\p`-gated regardless of encoding (a mirror would just be
`perr` under the identical gate, near-zero incremental information); axis 8
is additionally `lookaround`-gated regardless of encoding (same reasoning).
Axes 6, 7, 9, and 10, however, use plain literal/class patterns that likely
WOULD compile under `-e byte` today and would very likely show the same
byte-decomposition divergence axes 1–3's mirrors found — **this is a real
gap left by time, not by design**, and is the top item in "open questions"
below.

## 5. The independent checker

`d27_scratch/check_rxt.py` — written from scratch against
`docs/spec/rxt_format.md`'s own text, importing NONE of
`common.py`/`shared.py`/`axis_*.py` (the generator's own modules). It:

1. Implements its own line-level `.rxt` parser (block boundaries, the
   `perr`/`m`/`n`/`ms`/`ns`/`g`/`gp`/`encoding`/`flags` grammar, the
   7-escape subject decoder, the `g`/`gp`-must-follow-`m`/`ms` rule, the
   `-1 -1` RX_UNSET symmetry rule).
2. For every REAL (non-`perr`) case, makes its OWN fresh call to python's
   `re` (bytes engine — every real case in this corpus is `encoding byte`,
   checked and enforced, not assumed) and compares the result to the file's
   recorded expectation.
3. Additionally sanity-checks the SYNTAX of this corpus's own "future case"
   comment convention (so a corrupted future value cannot silently survive
   to promotion day even though it is inert today).

**Failing-direction-tested against FIVE planted corruptions** (exceeds the
>=4 the brief asks for), each in its own scratch copy of a real corpus file,
each independently confirmed DETECTED by a fresh run
(`python3 d27_scratch/check_rxt.py --selfcheck`):

```
=== SELFCHECK: planted-corruption detection ===
  [DETECTED] wrong-span-value             ...:15: expect...
  [DETECTED] match-vs-nomatch-flip        ...:17: e...
  [DETECTED] invalid-escape-sequence      ...:15: ...
  [DETECTED] case-line-inside-perr        ...:16: '...
  [DETECTED] unterminated-quote           ...:15: expe...
=== SELFCHECK PASSED: 5/5 corruptions detected ===
```

**Real run against the delivered corpus** (`python3 d27_scratch/check_rxt.py`,
full transcript kept in `d27_scratch/`): 524 blocks parse with zero
structural errors; 294 real cases independently re-verified against the
checker's own python `re` call; **zero mismatches**.

## 6. Population counts per Sec 7.1.1's oracle-marking convention

`docs/spec/rxt_format.md` documents exactly ONE oracle-tier comment
convention today: `# pcre2-only` immediately before a `pattern` line, for a
block correct-for-PCRE2 but not python-verifiable. **This corpus contains
zero `# pcre2-only` marks**, for a structural reason, not because the
question doesn't arise: every primary-arm block is `perr` today, and a
`perr` block has no `m`/`n`/etc. case for `# pcre2-only` to ever qualify —
the marking convention applies to a REAL case, and none of this corpus's
409 primary-arm blocks have one yet.

Where Sec 7.1.1's oracle predicate DOES matter is inside the future-case
comments themselves (the value a promoted case will carry). Since the
format has no comment convention for "this future value is pcre2-only" (the
extract's own Sec 7.1.1 flags this as an open question — see below), I
recorded provenance a different way for every one of the 1,399 future-case
lines: an explicit `# oracle=<options-word>` trailer naming exactly which
library configuration produced the value (`PCRE2_UTF`,
`PCRE2_MATCH_INVALID_UTF`, `PCRE2_UTF|PCRE2_CASELESS`, or the explicit
`pcrec-ARGUED (no oracle produces this)` for axis 9's four design-position
cells). A future reader promoting a block can see, cell by cell, exactly
what produced the value and whether any oracle beyond libpcre2 could ever
confirm it — which for every UTF-tier cell in this corpus is "no, python
cannot express this syntax" (Sec 7.1's own PCRE2-ONLY verdict for `\p`,
`\x{}`, class ranges over non-ASCII, quantified multi-byte characters, and
ill-formed subjects — i.e., essentially this entire corpus). I did not
invent a new `.rxt`-level comment KEYWORD for this, to avoid the format
mistaking it for a real directive; every marking stays inside an existing
`#`-comment line, per the lexical rule that only column-1 `#` is a comment
and anything else is data.

## 7. Open questions / flagged for the manager

1. **Byte-mirror coverage gap (axes 6, 7, 9, 10)** — see Sec 4. I believe
   these would show the same byte-decomposition divergence axes 1–3's
   mirrors found, but did not build and live-verify them; flagging rather
   than guessing at their content.
2. **Axis 6's arithmetic** — the extract's own "≈60" does not reconcile to
   60 under any factoring reconstructable from the included material; I
   suspect an excluded section supplies the missing multiplier. If the
   manager can name it, axis 6 is extendable to the target count
   mechanically.
3. **Sec 7.1.1's own flagged gap, inherited**: the extract's cutter noted
   (its own "Sentences I was unsure about") that the source design ties the
   oracle predicate to "a future `.rxt` oracle value... not yet
   implemented," and deliberately left me unsure whether to be told that no
   such third oracle value exists today. Having now built the corpus, I can
   confirm from the format side: it doesn't, and the `# oracle=` comment
   convention in Sec 6 above is my own stand-in, not a claim that
   `rxt_format.md` grew a new keyword.
4. **`\p`'s pairing with encoding**: the construct table states `\p` "works
   without `PCRE2_UTF`," but every category member above U+00FF has no
   representation under pcrec's byte encoding (which only sees 0-255).
   Axis 4's future-case values are computed under `PCRE2_UTF` throughout
   (documented in that file's own header) since that is the only pairing
   under which most category members are even reachable, but whether a
   real `\p` block should REQUIRE `encoding utf8` once landed, or degrade
   gracefully under byte to only its 0-255 members, is unresolved here —
   the extract's own Sec 5's resolution sections are excluded, and I did
   not guess.
5. **Axis 8's "call-bearing" reading** — see Sec 4; a different, equally
   defensible reading might have been intended by the excluded material.

## 8. File manifest

- `d27/axis01_encoded_length.rxt` + `_byte.rxt`
- `d27/axis02_class_boundary.rxt` + `_byte.rxt`
- `d27/axis03_invalid_utf8.rxt` + `_byte.rxt`
- `d27/axis04_p_categories.rxt`
- `d27/axis05_p_refusals.rxt`
- `d27/axis06_caseless_fold.rxt`
- `d27/axis07_caseless_1ton.rxt`
- `d27/axis08_lookbehind_varwidth.rxt`
- `d27/axis09_nextpos_findall.rxt`
- `d27/axis10_surrogate_witness.rxt`
- `d27/REPORT.md` — this file

Generator and checker source (not part of the delivered corpus, kept for
audit/promotion tooling): `d27_scratch/common.py`, `shared.py`,
`axes_1_2_3.py`, `axis_4_5.py`, `axis_6_7.py`, `axis_8_9_10.py`,
`check_rxt.py`, plus three one-off measurement probes
(`verify_drift.py`, `probe_invalid_utf8.py`, `probe_p_refusals.py`) and
`stats_final.json`/`warnings.log` (the generation run's own transcript —
every WARNING line in `warnings.log` traces to one of the two bugs this
report documents being caught and fixed live, Sec 4).
