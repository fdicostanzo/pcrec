# tests/lookaround — module `lookaround` ([M6.6.2])

`(?=X)` `(?!X)` `(?<=X)` `(?<!X)` and the two non-atomic spellings `(?*X)`
`(?<*X)`. Design: `docs/design/lookaround_design.md`, panel-approved at R33.

**ALL SIX CONSTRUCTS ARE BUILT AS OF WAVE D.** Wave B+C landed the lookahead
half and DECLINED the three `(?<` tails at `WANT_RESULT`, which is what kept
their registry rows `unbuilt`; wave D landed the back-step seam entry, deleted
the decline, and added the five lookbehind files (`lookbehind.rxt`,
`lookbehind_widths.rxt`, `startpos.rxt`, `nonatomic_behind.rxt`,
`workbudget.rxt`). Wave E adds `prefilter.rxt`, wave F `alpha_spellings.rxt`.
`gated.rxt` carried the split's own three enabled-but-unbuilt cells and wave D
RETIRED them — they would now be pinning a lie, and `lookbehind.rxt` asserting
the same three spellings compile and match is the control that says the count
going down is the module landing.

## The files, and every expectation in them is GENERATED

- **gen_corpus.py** — the generator, and it exists FOR THE `# pcre2-only`
  MARKING rather than for convenience. Every cell is driven through libpcre2
  10.46 (the committed ctypes binding at
  `docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`) AND through
  python3 `re` in the same pass; the expectation is libpcre2's (D26), and a
  block is marked `# pcre2-only` exactly where python diverged or could not
  compile it, with the first divergence and the cell count written above the
  marking. **It never asks pcrec anything** — an expectation derived from the
  compiler under test is not an expectation.

  **WHY COMPUTED RATHER THAN DECLARED, and this module is the case that
  proves it.** Design §7 catalogues two expectations a hand-marking would
  have written in and that MEASUREMENT REFUTES: python compiles all fourteen
  quantified lookaround forms and agrees on all nine behavioural cells (G8),
  and the two oracles agree on all 27 capture cells INCLUDING captures in a
  negative lookahead (G9). Marking either family `# pcre2-only` by hand would
  have thrown a working oracle away — R32 C3's finding, which is exactly what
  the backrefs module's generator was built to remove.
- **lookahead.rxt** — `(?=` and `(?!`: bodies, contexts, degenerate forms.
  Carries §3.2.1's two witnesses BY NAME (`(?=(a+)b)a+b` on "aab" is (0,3)
  g1=(0,2); `(?!(a+)b)a+b` on "aab" is NOMATCH), §2.2's atomic discriminator
  `(?=(a|ab))\1$`, and the CAPTURE-FREE `(?=a)b` cell sabotage row S126
  needs — capture-free on purpose, because `(a)(?=b)c` keeps the VM whatever
  the row's `engines` mask says and would mask it.
- **captures.rxt** — the four polarity/outcome combinations with `g` lines:
  retention inside a positive assertion, the undo when a positive one fails,
  the discard inside a negative one, and the trailing-unset control
  `(?!(a)x)(a)` that proves the answer is READ rather than truncated.
- **quantified.rxt** — `(?=a)*` and family, including §2.6's five
  empty-iteration cells. They are here BECAUSE THEY MUST TERMINATE:
  `vm_nullable` answers true for `A_LOOK`, and if it did not the star would
  lose its empty-iteration guard. The failure is NOT a hang — every VM
  artifact carries a step budget, so the lost guard BURNS it and returns
  `PCREC_ERR_STEPS`, which a span-comparing harness scores as an error rather
  than as a mismatch.
- **nonatomic_ahead.rxt** — `(?*` only, and `# pcre2-only` IN ITS ENTIRETY
  (python has no `(?*` at all, G5) — computed, not declared, ten blocks of
  ten. Carries §2.2's non-atomic half and §3.2.1's row 3, which is the arm an
  implementer following "the atomic shape MINUS the cut" is most likely to
  lose the follow-scoping in.
- **lookbehind.rxt** — `(?<=` and `(?<!` with FIXED bodies and SAME-length
  alternatives, which is what keeps the file python-verifiable: python's rule
  is narrower than "same width" (it accepts `(?<=ab|cd)x` and rejects
  `(?<=a|bc)x`), so the divergence is about DIFFERING widths and not about
  alternation at all (G10). Carries design §3.4's B5 guard cells by name
  (`(?<=a)b` on "b" is NOMATCH where `(?<!a)b` is (0,1)), the two
  fixed-width-quantifier cells F3 measured (`a{3}` and `(?:ab){2}` — both are
  `A_REP`s that take a cursor rung whose MRL literal moves with the follow,
  which is why the lookbehind's body is scoped too), captures inside a
  lookbehind, both nesting orders, and the assertion family's own three bodies
  (`\w`, `\n`).
- **lookbehind_widths.rxt** — DIFFERENT-length branches, `# pcre2-only` in its
  entirety (G1). **It carries §2.4's preference-order measurement, which is the
  sharpest cell in the module**: `(?<=(a)|(aa))c` on "aac" answers g1=(1,2) and
  `(?<=(aa)|(a))c` answers g1=(0,2) — top-level branches in WRITTEN order,
  never by length, and an implementation that ordered them by width would get
  exactly one of the two right. It also carries the three ZERO-WIDTH-branch
  cells that FOUND A DEFECT: width 0 is a legal fixed width, and the emitted
  guard for it was `scan_position < 0` — an always-false `size_t` comparison
  the harness's `-Werror` generated build refuses.
- **startpos.rxt** — `ms`/`ns` cells over a lookbehind, and **the axis a
  startpos-blind corpus would miss entirely**. A lookbehind READS SUBJECT BYTES
  BEFORE `startpos` (§3.8, measured in both oracles: `(?<=a)b` on "ab" at
  startpos 1 MATCHES, `(?<!a)b` does not), which is a contract question rather
  than a syntax one. Sabotage row S135 clamps the guard to
  `scan_position - startpos < k`; without this file it could not go red. Every
  block pairs its `ms` cells with startpos-0 controls, because the file is
  about the WINDOW and not about the pattern.
- **nonatomic_behind.rxt** — `(?<*`, `# pcre2-only` (G5), carrying §3.6's
  measured witness `(?<*(a)|(ba))c\2` on "bacba" BY NAME **and its atomic
  control `(?<=(a)|(ba))c\2` in the same file**. That pair is the one thing
  that goes red if the per-branch retry frames are cut: (2,5) with g2=(0,2)
  against NOMATCH, on one subject, from one character's difference in the
  spelling. In the atomic form those frames are discarded by the cut; here they
  are LOAD-BEARING.
- **workbudget.rxt** — §3.7's long-subject LEADING multi-branch lookbehind
  (R33 C1-6), so the `n·Σk_i` charge shape is MEASURED rather than reasoned
  about. Every branch is width 2 so python verifies it. The subjects are 1000
  bytes: the budget itself is only reachable at ~50 MB, which a corpus cannot
  carry, so this file measures the SHAPE and the short cells beside it are the
  control that the answer does not depend on the length.
- **refused.rxt** — the `perr` cells: §2.5's VARIABLE-WIDTH family (and their
  libpcre2 verdicts are NOT one verdict — pcrec AGREES with PCRE2's err 125 on
  the unbounded bodies and refuses what PCRE2 COMPILES on the bounded ones,
  which the generator records per block), §2.7's `\K`-in-lookaround refusal
  (including the three nested spellings an immediate-children check would
  miss) and the unterminated forms. **Every block records BOTH oracles'
  verdicts**, because the agreement here is not agreement: libpcre2 refuses
  `(?=a\K)x` because `\K` is not allowed in a lookaround, python refuses it
  because it has no `\K` AT ALL (design §7, G6).
- **gated.rxt** — the module gate and D65's `built` column, cell by cell:
  the closed gate, the wrong module, the three lookbehind rows'
  enabled-but-unbuilt refusal (the split's own measurement), R33 C2-5's
  masking cell (`(?=a\K)x` WITHOUT `assertions` is refused by the assertions
  gate and never reaches §2.7's check at all), and the control that no row
  outside this module moved. **It opens with a block that must MATCH**: a
  file of nothing but `perr` passes just as well on a compiler that refuses
  everything, which is precisely the state a half-landed module gate puts the
  compiler in.
- **run_lookaround_diff.sh** — the behavioural instrument, `make
  test-lookaround`, four sections. See its own header; two things about it are
  worth knowing before adding to it.

  **ITS SUBJECT SET GREW AT WAVE D, 19 -> 26**, and that is not a detail: the
  sweep is only as sharp as the subjects it runs over, and a differing-width
  lookbehind needs a subject on which ONE branch fits and the other does not
  (`ax`, `bcx`, `cx`), §2.4's preference-order cells need `aac`/`ac`/`c` to
  tell branch 1 from branch 2 by its captures, and §3.6's F4 fourth row is
  measured on `baca` specifically. Growing it re-derives every per-pattern cell
  count in the same change — including §2's, whose disagreement total the
  additions happened to leave at 13.

  **ITS POPULATION GUARDS ARE EXACT NUMBERS AND ONE HAS ALREADY GONE STALE**
  — during the wave that wrote it, when three `\K` cells were added to
  `lookahead.rxt` after §1's count was taken (python has no `\K` at all, so
  all three computed as `# pcre2-only` and the population went 11 to 14). The
  guard FIRED, loudly, which is what it is for; the lesson is the one
  `tests/reject/CLAUDE.md` records about hand-copied figures, and the remedy is
  the same: when a cell is added, re-derive the number from a run and change it
  DELIBERATELY. **Do not relax it to a floor.** A floor would let the
  population SHRINK, and the cells this section exists for are exactly the ones
  no other check in the tree can see.

  **§2 IS THE ONLY ARM IN THIS TREE WHOSE POPULATION MUST DISAGREE WITH
  ITSELF.** `(?=` and `(?*` differ in exactly one emitted line, so a compiler
  that cut BOTH or cut NEITHER answers them identically — and an arm that only
  checked agreement with libpcre2 per pattern would go green on both
  sabotages. It asserts the EXACT number of disagreeing cells (13 of 137 at
  this wave, every one the atomic form saying NOMATCH where the non-atomic
  form matches, never the reverse).

  **IT REUSES `tests/backrefs/bref_oracle.py` AND `bref_batch.c` RATHER THAN
  COPYING THEM.** Design §10.2 asks for `la_oracle.py` "modelled on" those
  two; modelled-on would have been a THIRD copy of one mechanism
  (`tests/atomic_groups/` already holds the second), and D24 is the standing
  rule against a second home for one fact. Neither file is backref-specific in
  behaviour.

## Every block names `lookaround` in its `features` line

R33 V-10, and it applies to this directory AND to every sabotage row's
detector. `std1` is a FROZEN named set, `{classes, modifiers}`, so it does not
contain this module: a cell that forgot the feature would pass BY REFUSAL, on
a correct compiler and on a sabotaged one alike. That is S108's masking shape
applied to a whole file. Blocks needing `assertions` (the `\K` cells),
`backrefs` (the discriminator), `classes` (the `\w` lookbehind bodies) or
`atomic-groups` (`(?=a)*+`) name those too.

## Census at the wave D landing

Read it from a run — `python3 tests/lookaround/gen_corpus.py` prints the table
and `tests/harness/verify_rxt.py tests/lookaround` prints the python-side one —
rather than from here, for the reason `tests/reject/CLAUDE.md` records about
hand-copied figures. At wave B+C's landing it was **81 blocks / 118 cells / 18
`# pcre2-only` / 16 `perr`**, 166 harness cases, 1,022 pcre2-only cells
re-verified by §1. At wave D's it is **175 blocks / 335 answer cells / 48
`# pcre2-only` / 40 `perr`**, 451 harness cases, 302 python-verified cases, and
§1's pcre2-only population went **14 -> 44 answer-bearing blocks / 4,268
cells** — the biggest single move that guard will ever see, because
`lookbehind_widths.rxt` and `nonatomic_behind.rxt` are `# pcre2-only` in their
entirety.

## What this directory does NOT hold

- **The byte-identity gate** is `tests/codegen/run_lookaround_identity.sh`,
  opt-in as `make test-lookaround-identity`, on the ruling
  `test-atomic-identity` and `test-backrefs-identity` have.
- **The `\K`-refusal's module attribution** and the six rows' closed-gate
  diagnostics live in `tests/reject/`: a `perr` block asserts only THAT a
  pattern is rejected, never WHY, and for a module boundary the why is the
  point.
- **`(?=(?i))*`**, which libpcre2 accepts and pcrec refuses. It is not a cell
  here because it is not this module's question: pcrec refuses `((?i))*` and
  `(?>(?i))*` the same way, and `src/parse/parse.c`'s A_CAP arm records the
  pre-existing question. Giving the lookaround its own cell would be giving
  one question two homes.

## `run_expansion_diff.sh` + `expand_corpus.py` — THE SUBSTITUTION DRIVER (wave E2)

**A different KIND of instrument from `run_lookaround_diff.sh`, not more of
it** (design §10.1a). That one runs the module's OWN corpus — every spelling,
every body shape, the refusals, the alpha forms, `ms` startpos, the prefilter
witness — and is a BREADTH instrument. This one re-expresses
`tests/assertions/`'s corpus as lookarounds and is a DEPTH instrument on
exactly ONE body shape: the assertion family's, which is one class or one
literal. Neither substitutes for the other and §11's landing bar asks for both.

**WHAT IT DOES.** Every assertion module `assertions` ships has a lookaround
DEFINITION (§6.1). Replacing each assertion in that module's corpus by its
definition turns 468 blocks / 10,120 libpcre2-verified cells into a lookaround
corpus for free — 263 blocks / 8,260 cells of it — whose expectations are not
this module's guesses, because they were written for a module that already
ships. **It is a CORPUS GENERATOR, not a product mechanism** (Frank,
2026-08-23; design §6.4): it emits PATTERN TEXT the compiler sees as an
ordinary user-written lookaround. Nothing under `src/` changed for it, and the
product-side substitution is [DD-14]'s, on the subroutine-call primitive.

**THE THREE-WAY CHECK, per cell, and both halves are required.** `A` is the
expanded pattern compiled by pcrec, `B` the folded pattern compiled by pcrec,
`C` libpcre2 on the expanded pattern. `A == B` is D66's SELF-ORACLE — pcrec's
two lowerings of one language must agree, which needs no external oracle at
all. `A == C` is what stops `A == B` passing because BOTH lowerings are wrong
the same way. Measured at the wave: **887 generated patterns / 29,063
three-way comparisons, 0 disagreements**, match span AND every group span.

**FIVE THINGS KEEP IT FROM BEING A TAUTOLOGY**, and they are the part to read
before changing anything here, because every check this project has written
that FAILED, failed by sharing a source with the thing it controls:

1. **The expansion table is LITERAL** (`expand_corpus.py`), transcribed from
   §6.1 / D66 / [DD-11] and never derived from the compiler. Read out of
   `src/parse/mod_assertions.c` it would make `A == B` two spellings of one
   source agreeing with themselves. **If [DD-11] later rewrites the assertions
   to their definitions on the [DD-14] primitive, this table and the
   compiler's must remain TWO SOURCES.**
2. **§0 re-verifies the table against libpcre2 before a row of it is used** —
   42 patterns (7 expandable rows × 6 tails) / 2,646 cells, both arms carrying
   the same option state, 0 disagreements. §6.5 records why that last clause
   is not a detail: the first version of this measurement put `(?m)` on the
   folded arm only and reported 3 disagreements that were the measurement's.
3. **§0 CARRIES ITS OWN FAILING DIRECTION** — the VACUITY GUARD. `\A|(?<=\n)`,
   the D66 expansion with its `(?!\z)` term dropped, is asserted to DISAGREE on
   **exactly 16** cells. A table check that could only report agreement would
   report agreement for a table of nine identity rows.
4. **The `--policy=none` CONTROL ARM** — the same pipeline with no
   substitution, so the generated pattern IS the original and every cell must
   come out trivially equal. It is a SEPARATE compile of the same text, not a
   reuse of arm B's artifact. **And its converse**: §2/§3 assert that their
   patterns are textually DIFFERENT from their source and count how many
   INSERT a lookaround (199 of P1's 263, 248 of P2's 361). A substitution that
   silently became the identity would pass every comparison in the file.
5. **§1c the CELL-FIDELITY GUARD** — arm B against `tests/assertions/`'s OWN
   stated expectations, all 8,260 cells. The corpus's expectations are the one
   input no arm of this driver produced, and without this guard a bug in the
   subject decoding would feed the same wrong subject to all three arms, they
   would agree, and the driver would be green while measuring nothing.

**THE SIX QUALIFICATION RULES ARE PARSERS, NOT SUBSTRING TESTS** (R33 C3-1,
C3-2), and each carries the reason it exists at its own site. Q3's class walk
consumes one literal `]` after `[` or `[^` (PCRE2's literal-first rule), so
`[]\b]` is a class containing `]` and a backspace; Q4 finds every `(?` followed
by a modifier LETTER SET (optional `-`, second set) terminated by `:` or `)`
and exempts only a bare LEADING `(?m)`, because `^`/`$` mean different things
under different multiline states.

**THE POPULATION NUMBERS ARE GUARDS, NOT DECORATION**, and they are EXACT: 468
/ 10,120 / 67 for the whole corpus, 263 / 8,260 / 13 qualifying, and the
per-rule table Q1 87/0, Q2 87/754, Q3 0/0, Q4 31/1,106, Q5 0/0, Q6 0/0 —
re-counted on HEAD at the wave with **zero delta** against design §6.3. A
qualification rule that quietly stopped firing would SHRINK this population,
and a smaller population is the one failure mode a green run cannot show. When
the assertions corpus grows, re-derive from a run and change the literals
DELIBERATELY; **never relax one to a floor**, the lesson `tests/reject/
CLAUDE.md` and this file's own §1 guard already record.

**THE IDENTITY ROWS ARE ACCOUNTED FOR, NOT TOLERATED.** `\A` and `\z` are
PRIMITIVES in §6.1 — the floor of the definition chain — so an
occurrence-level substitution of one of them is the identity: 56 of P1's 263
patterns and 84 of P2's 361, and that 84 is asserted to equal the `\A` (37) +
`\z` (47) occurrence count rather than merely tolerated. They are excluded
from the headline "cells that compared two lowerings".

**BOTH ARMS COMPILE WITH ONE FEATURE SET** — the block's own plus
`lookaround`, `classes` (for `\w` in `\b`/`\B`'s bodies) and `assertions` (for
the `\z` INSIDE `(?=\n?\z)`, which a block needing no module at all needs after
substitution). A wider set on arm A would be a SECOND difference between the
two lowerings, and a disagreement could then not be attributed to the
substitution. §1b is the failing-direction control on that: the five expansion
shapes are REFUSED without module `lookaround` and accepted with it, so arm A
is the lookaround path and not the assertions path wearing different text.

**IT REUSES `tests/backrefs/bref_oracle.py` AND `bref_batch.c`**, the same two
files `run_lookaround_diff.sh` reuses, for the same D24 reason — this would
have been the FOURTH copy of one mechanism. One oracle invocation per BLOCK
covers all of that block's generated patterns.

**RUNTIME AND WIRING.** `make test-lookaround` runs it beside
`run_lookaround_diff.sh`; it parallelizes internally on `PROCS` (default
`nproc`) and MEASURED 40s warm / 1m43s cold at PROCS=12 on the project box.
`--policy=P1|P2|none` runs one arm alone. It SKIPS LOUDLY without libpcre2,
and the skip banner says explicitly that `A == B` alone is not the check.
