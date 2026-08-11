# tests/parse — checks on the parser's own reported facts

Checks on things `src/parse/parse.c` COMPUTES but does not emit. Behaviour of
the generated matcher is the .rxt corpus's job (tests/base, tests/harness);
optimization signatures are tests/codegen's. This directory exists for parser
outputs that no generated C can show.

## Files

- **branch_count_check.c** — PARSE-1's top-level branch count. Links
  `build/libpcrec.a` and calls `pcrec_parse_info` directly, the way
  tests/registry/registry_check.c calls the registry: the subject is internal
  and the CLI cannot see it.
- **run_parse_tests.sh** — builds and runs the above, runs its three sabotages,
  and runs the generated AST-identity pairs.

## Why the branch count needs a check of its own

PARSE-1 adopted a design that deliberately leaves the AST unchanged, so **no
output-shaped test can observe it.** Measured on the tree before PARSE-1
landed: `(a|b)|c`, `((a|b)|c)|d`, `(a)|b`, `a|(b|c)` and `(a|a)|a` were already
byte-identical to their flat forms. A codegen check asserting that identity is
therefore passed by a build containing NONE of PARSE-1 — and cannot tell a
correct count from one that always returns 1, because nothing consumes the
count yet. The count and the emitted C are on orthogonal axes.

## The control, and why it is not a self-join

Checking pcrec's count against pcrec's parser proves nothing. So:

1. **An independent REFERENCE counter** lives in branch_count_check.c as a
   deliberately different algorithm — a flat byte scan tracking paren depth,
   against the parser's recursive descent. It is not a transcription of
   `p_alt`.
2. **libpcre2 arbitrates the reference.** Two thresholds are functions of this
   number alone, measured over 928 generated probes on 2026-08-11:
   `(a)(?(1)BODY)` is error 127 iff BODY has more than TWO top-level branches;
   `(?(DEFINE)BODY)` is error 154 iff it has more than ONE. **pcrec implements
   neither construct, and that is the point** — libpcre2 stands in for the
   module PARSE-1 does not have yet, exactly as PC-3 checked the registry
   before the modules it describes existed. Two different thresholds mean a
   reference uniformly off by one fails one of them.

Measured at PARSE-1 close: 16,384 generated bodies, pcrec agreed with the
reference on all of them, and libpcre2 arbitrated the reference 32,768 times
with zero disagreements.

**SKIPPING IS LOUD AND IS NOT A PASS.** Without libpcre2-8-0 the arbitration
stage prints a SKIP banner and the pcrec-vs-reference comparison still runs, so
a stranger's `make test` stays green without the outside authority silently
disappearing.

## Sabotage, because an unsabotaged green check is worth nothing

`PCREC_BC_SABOTAGE={class,escape,off-by-one}` corrupts the REFERENCE; the
runner requires each to FAIL and fails if one passes. Separately, and this is
the stronger control, **three sabotages of the real subject** — `p_alt` made to
always report 1, to stop incrementing, and to over-increment — were each
verified to be caught, 12,288 failures apiece, before PARSE-1 was committed.

## Read the AST-identity check's claim carefully

It asserts `(a|b)|c` and `a|b|c` still emit identical C. That property held
BEFORE PARSE-1, so it is **not evidence PARSE-1 was built or is correct**. It is
a regression net pointing FORWARD: a later edit adding a group wrapper to the
AST without pricing it — the candidate-A shape PARSE-1 rejected, which would
cost 7-15x compile time on alternations wrapping a proper sub-run — trips it.
That is the only direction it has power in. Its pairs are GENERATED across
branch counts and group positions rather than hand-listed, because a hand-listed
pair is how a check quietly narrows.

## Two properties this directory deliberately does NOT assert

Stated in the runner's output on every run, so a green result is not mistaken
for coverage:

- **depth balance across a doorway that RETURNS** — every doorway is `noreturn`
  today (zero `return` statements on any path in ext.c), so no input can reach
  the unbalanced path. First observable at MOD-0.2+.
- **caseless save/restore around a group body** — nothing writes `cx->caseless`
  yet, so save == restore on every pattern. First observable when `modifiers`
  lands (MOD-0.5).

These are SKIP-shaped (loud, exit 0), NOT `check_tail_precedence`-shaped
(exit 1). The distinction is load-bearing: `check_tail_precedence` fails the
suite when its subject vanishes because the property WAS live and going dead is
a regression a maintainer caused. These two were never live — they need code
that does not exist yet — so wiring them to `bad()` would leave `make test`
permanently red from PARSE-1 until MOD-0.2. `pcre2_check.c`'s loud-SKIP is the
right precedent.

Maintenance: update this file when files are added/removed or their roles change.
