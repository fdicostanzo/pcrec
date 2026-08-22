# tests/atomic_groups — module `atomic-groups` ([M6.4.2])

`(?>...)` and the possessive quantifier suffixes `*+ ++ ?+ {n,m}+` — which are
the SAME CONSTRUCT, not relatives: PCRE2 defines `X*+` as `(?>X*)`, and
`src/parse/parse.c` desugars the suffix to `A_ATOMIC(A_REP(X))` at the
quantifier site. Design: `docs/design/atomic_groups_design.md`, panel-approved
at R31 (`docs/dev/reviews/2026-08-22-r31-atomic-groups-design.md`).

## Files

- **atomic_basic.rxt** — `(?>...)` itself: the cut, alternation priority under
  it, nesting, the empty body (`(?>)` is LEGAL and matches empty), and the
  follow. The alternation-priority PAIR is the cheapest way to see the cut is
  real: `(?>ab|a)b` matches "abb" and `(?>a|ab)b` matches only its first two
  bytes, because each commits to whichever branch its OWN order tried first.
  Swap the branches and the language changes; an implementation that ignored
  the atomicity answers the same thing for both.
- **atomic_quant.rxt** — atomic groups and quantifiers in both directions, and
  THREE of its four sections are carve-outs the emitter must CHECK rather than
  assume. Nullable bodies never take the possessive-rung LIFT (`vm_poss_star`
  emits no empty-iteration guard, licensed by §2.2 refusing nullable bodies —
  a licence a USER-WRITTEN cut deletes, and the failing direction is a HANG,
  not a wrong answer). Lazy bodies never take it either (the possessive rungs
  are greedy-only BY SIGNATURE). And the `(?>a*)a` / `(?>a*)b` pair is the free
  discharge's own boundary: same group, and only the follow decides whether the
  cut costs anything.
- **possessive.rxt** — the four suffix spellings including `{n}+`, `{n,}+` and
  `{,n}+`. Section 6 is the EQUIVALENCE as cells, each spelling beside its
  group twin. Section 8 is where python `re` diverges and `*+`/`++` do not,
  which is what makes the controls beside it load-bearing.
- **atomic_caps.rxt** — CUT-INV as behaviour. `RX_CUT` discards FRAMES and
  deliberately does not rewind the TRAIL, and only ONE of the invariant's two
  halves discriminates: RETENTION (`(?>(a)|ab)` on "ab" is (0,1) with group 1 =
  (0,1)) catches a wrongly-rewinding cut, while UNDO does not — a cut that
  rewinds the trail gets undo trivially right, because it did the undo early.
  The design's own prototype named the undo row as the one the question turns
  on and was wrong.
- **atomic_ceiling.rxt** — the R3a family: patterns whose CUT match ends LATER
  than their UNCUT twin's, which is §4's hazard. It carries BOTH clamp
  populations (R31 C5): `RX_VM_PRUNE_CEILING` is three-valued, and with
  `nclamp == 0` an artifact stamps "none" and has no ceiling to get wrong, so a
  file made only of clamping patterns cannot see a ceiling bug on the other 9%.
- **atomic_case.rxt** — the cut is CASE-BLIND, structurally: pcrec folds case
  into the class bitmap AT PARSE TIME, so `(?i)a*+A` on "aaA" is NO MATCH
  because `a*+` folded to `[aA]*+` and ATE the `A`.
- **atomic_assert.rxt** — `\K`, `\G`, `\b`, `(?m)^`, `(?m)$`, `\Z`, `\z` inside
  and around a cut. `(?>a|a\Kb)b` on "abb" -> (0,2) is the cell worth reading:
  the cut takes branch 1, so the `\K` on branch 2 is NEVER CROSSED. That is the
  intersection of two mechanisms and neither construct's own directory can test
  it.
- **run_atomic_diff.sh** — the behavioural instrument, four sections. Its
  ENGINE arm is the most important thing here: §4's hazard lives in the
  DIFFERENCE between the default hybrid and `--engine=vm`, and a suite running
  only one would not see it.
- **atomic_batch.c**, **atomic_oracle.py** — the batch drivers the sweep needs.
  See "the sweep had to be batched" below.
- **atomic_entries.c** — all three entries of one cut-bearing artifact, side by
  side (H4). The match-here ORACLE is `\G(?:PAT)`, wave D's trick.

`tests/codegen/run_atomic_identity.sh` is this module's byte-identity gate and
lives there by technique; `make test-atomic` runs it.

## THE ORACLE RULE, and why the divergences were DETECTED rather than declared

Every expectation was produced by libpcre2 10.46 through
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`, and python3 `re`
was driven over the SAME cells in the same pass. A block carries
`# pcre2-only` exactly where python disagreed or could not compile the pattern
— measured, never assumed. **13 of 729 generated cells diverge, and they are
EXACTLY the four families the design's Appendix B.3 names**, which is an
independent confirmation of that table rather than a transcription of it:

- `\K` and `\G` — python cannot express them at all;
- the BRACE possessive over a two-exit body — python cuts PER ITERATION and
  PCRE2 cuts at the GROUP EXIT, so `(?:a|ab){2}+` on "aba" is (0,3) in PCRE2
  and NO MATCH in python, while `(?:a|ab)*+` on "aba" is (0,1) in BOTH. The
  divergence runs in the dangerous direction and the `*+`/`++` controls beside
  it are what make it a family rather than a one-off;
- U9 — see below;
- scoped `(?i)` inside a group — python rejects the pattern outright.

## U9 IS NOT IN THIS DIRECTORY, AND THAT IS A RULING SOMEBODY OWES

`tests/known_fail/u9_atomic.rxt` holds the two U9 patterns with LIBPCRE2's
answer, which pcrec does not reproduce: pcrec agrees with python `re` and with
a hand derivation. D26 makes PCRE2 the source of truth, and
`docs/dev/upstream_issues.md` U9 classifies the divergence as PCRE2-SIDE and
names THIS MODULE LANDING as the event that makes it reachable ("pcrec refuses
the spelling today, module `atomic-groups`"). The implementation lane is not
the place to decide which wins, so the ratchet holds it: the cells stay, they
stay loud, and if pcrec is ever changed to reproduce U9 the ratchet FIRES.
The three CONTROLS that each drop one of U9's conjuncts are live and green in
possessive.rxt section 9.

## THE SWEEP HAD TO BE BATCHED, and the number is the argument

`run_atomic_diff.sh`'s first form spawned one `pcre2_oracle` and three
`fuzz_driver` processes PER CELL, over ~120,000 cells. MEASURED: **44 cells per
minute — about eleven hours for one run**, which is not a test anyone runs and
certainly not a sabotage-matrix arm. The oracle side is now ONE python process
(`atomic_oracle.py`, driving the same libpcre2 through the project's committed
ctypes binding) and the pcrec side is one process per (pattern, arm) reading
cells on stdin (`atomic_batch.c`): **~60 seconds**, same cells, same comparison.

`atomic_batch.c` is deliberately NOT a replacement for
`tests/fuzz/fuzz_driver.c` — that file is the fuzzer's own template, compiled
ONCE and linked against every pattern's `gen.o`, which is why it cannot batch.

Because the comparison is POSITIONAL, both batch programs treat an unreadable
input line as a HARD failure, and the driver's output LINE COUNT is asserted
per arm. A driver that dropped a line would shift every later cell against the
wrong answer — the one failure mode the batched shape introduces.

## EVERY POPULATION IS ASSERTED, NEVER PRINTED

A sweep that quietly generated nothing prints the same silence as one that
agreed everywhere, and this project's record is full of that shape. Each
section ends in a floor its own run must clear, and the sharpest is the
NON-VACUITY floor: the cut must MEASURABLY change the answer on at least 15 of
the cut patterns, measured against each one's two-byte UNCUT twin (`(?>` ->
`(?:`, a possessive `+` dropped) rather than inferred from the pattern's shape.
Without it the whole sweep would be green on a compiler that lowered the group
by ignoring the atomicity — which is the trap `src/parse/registry.c`'s own row
comment has warned about since before there was a producer, and sabotage row
S91.

## Conventions

Blocks carry `features atomic-groups` (plus `assertions`/`modifiers` where the
pattern needs them) — the module is NOT in `std1`, so a bare invocation still
refuses and `tests/reject/`'s rows keep working unchanged. Group expectations
in atomic_caps.rxt are padded to the pattern's real group count, so a group
that did not participate is asserted UNSET rather than omitted.

Maintenance: update this file when files are added or their roles change.
