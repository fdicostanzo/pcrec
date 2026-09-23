# tests/vars/ — the population census, stated before the fact

**[VAR] M10, 2026-09-23.** `variables_roadmap.md` §2.5's first obligation:
*"a population census for the MVP's own axes (K35 applied prospectively) …
enumerate this cross-product with a `gen_corpus.py`-style plan, naming what
gets exhaustive coverage and what gets sampled — K35's shape stated before
the fact rather than found after."*

This is that plan, plus what the three shipped files actually reach. It is a
plan and not a generator: the generator is a NAMED FOLLOW-ON, and §5 says why
it is not built here.

## 1. The axes

Every axis the design's own open questions name, with its values.

| axis | values | where it comes from |
|---|---|---|
| **caseless** | sensitive, `(?i)` | `variables_pattern.md` §6 |
| **encoding** | `byte`, `utf8` | §6.1, and the fold's length-changing case |
| **state** | UNSET, EMPTY, SET | `variables_common.md` §2.2 |
| **operator** | none, `-`, `:-`, `+`, `:+`, `:?` | §1.1's table, as the MVP takes it |
| **position** | bare, under a quantifier, in an alternation, in a lookaround | §9 Q3 |
| **multiplicity** | once, same name twice, two names | §9 Q4 |

The cross-product is 2 × 2 × 3 × 6 × 4 × 3 = **864 cells**, which is the
number this plan exists to cut down honestly rather than to generate.

## 2. What gets EXHAUSTIVE coverage

Three sub-products, chosen because each is where a wrong answer is SILENT —
it changes a match rather than raising anything.

- **state × operator (18 cells).** This is the value model itself, and the
  `:`'s whole job is to move EMPTY from one column to the other. A design
  that folded EMPTY in with SET, or that fired a bare operator on EMPTY,
  would pass every cell of any smaller set. `tests/vars/unset.rxt` covers
  **16 of 18** today; the two missing are `${v+w}` and `${v:+w}` with the
  variable SET-and-non-empty, which are the arms whose answers are the
  same in both and therefore the two least likely to be wrong.

- **caseless × encoding (4 cells), with a length-changing witness in the
  one cell that has one.** `caseless.rxt` covers all four, and the
  `(?i)` × `utf8` cell carries the KELVIN SIGN in BOTH directions (value
  one byte / subject three, and the reverse) plus the 1:1 negative control
  (`ß` does not match `SS`). Complete.

- **position × multiplicity for the SET state (12 cells).** A reference is
  ONE node, so a quantifier or an alternation applies to the whole value —
  which is also the rule the splice oracle's unconditional `(?:…)` wrap
  encodes, so a wrong answer here disagrees with the oracle rather than
  hiding. `basic.rxt` covers **5 of 12**: bare, under `{2}`, in an
  alternation, same-name-twice, two-names. **The 7 not covered are every
  cell whose position is a LOOKAROUND**, and they are not covered because
  a lookbehind containing a variable is REFUSED by construction
  (`pcrec_cwmax` answers unbounded, `mod_lookaround.c`'s fixed-width rule
  refuses) while a lookAHEAD is an ordinary body — so the honest shape is
  ONE refusal row for the behind and ONE match cell for the ahead, not
  seven. **OWED.**

## 3. What gets SAMPLED, and on what rule

Everything else, at **one cell per axis value in combination with the
DEFAULT of every other axis** — the shape `backrefs`' own corpus uses. The
sampling rule is that an axis whose values are answered by DIFFERENT CODE
gets exhaustive treatment above, and an axis whose values are answered by
the SAME code with a different operand gets one cell each.

By that rule `encoding` is exhaustive (two backends, two bodies) and
`position` is sampled (one emit arm, one instruction, whatever surrounds it).

## 4. What is DELIBERATELY not an axis

- **`--no-captures`.** Variables are independent of captures and the two
  features do not interact (`variables_pattern.md` §7). Making it an axis
  would double the product to assert an absence.
- **The `_in` routes.** `frames-buffer=` is orthogonal: the resolution runs
  at the same three `run_state_init` sites whichever entry was called, and
  the harness's own H11/route cross-checks already cover the entry family.
- **`--engine=dfa`.** It is a refusal, not a cell: one reject-table row.

## 5. The GENERATOR is a named follow-on, and D77 is why

`backrefs`' `gen_corpus.py` exists because that module's expectations had to
be driven through libpcre2 BEFORE they were written — its oracle is external
and per-cell. This module's is not: `verify_vars.py` verifies the file AFTER
the fact, over whatever cells the file carries, so a generator would produce
cells a human still has to read and would not remove the step that makes them
trustworthy.

**The trigger for building one, stated so it is checkable:** the first time
this corpus needs more than about a hundred cells — which is phase 2's
operator suite (`#`, `##`, `%`, `%%`, `:off:len`, `^`, `^^`, `,`, `,,`),
where the product genuinely explodes and the per-operator answer is
mechanical. Until then the three hand-written files plus this plan are the
population, and the plan is what makes "what is not covered" a list rather
than a silence.

## 6. OWED, in one place

- The two `+`/`:+` SET-and-non-empty cells (§2).
- The lookaround pair: a refused lookbehind and a matching lookahead (§2).
- The generator, on §5's stated trigger.
