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
- **possessive_ungreedy.rxt** — K122 (lane langfix2): every possessive suffix under `(?U)` is GREEDY (`(?U)a*+` on "aaa" (0,3)); each block twice, default engine and `engine vm`, beside lazy-under-`(?U)` controls. libpcre2 10.46-generated, `# pcre2-only` (python has no `(?U)`); regenerate with `python3 tests/lib/p2gen.py tests/atomic_groups/possessive_ungreedy.gen.py` (its spec, beside it).
  `{,n}+`. Section 6 is the EQUIVALENCE as cells, each spelling beside its
  group twin. Section 8 is where python `re` diverges and `*+`/`++` do not,
  which is what makes the controls beside it load-bearing. **Section 10
  ([M6.4.4]) is the tier-1 regression** — see "the shape this directory did
  not have" below. Every pattern in it is PAIRED with its one-byte-follow
  twin, which matches: a section of nothing but NO MATCH would pass on a
  compiler that refused the whole family.
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
  only one would not see it. §3 additionally asserts the FOLLOW BARRIER in its
  direction ([M6.4.4]): with a dead cut DELETED the VM artifact carries a
  follow-derived MRL ceiling, with the same cut ALIVE it carries none. §5.4's
  emission-neutrality is still checked, with the length prune removed from
  BOTH arms at the source (`-fno-length-prune`) rather than sed-erased —
  because a live `A_ATOMIC` now legitimately changes the prune, and
  normalising two stamps would have hidden a thirteen-line machinery
  difference behind them.
- **atomic_batch.c**, **atomic_oracle.py** — the batch drivers the sweep needs.
  See "the sweep had to be batched" below.
- **atomic_entries.c** — all three entries of one cut-bearing artifact, side by
  side (H4). The match-here ORACLE is `\G(?:PAT)`, wave D's trick.

`tests/codegen/run_atomic_identity.sh` is this module's byte-identity gate and
lives there by technique. **Since [M6.4.4] it is OPT-IN**, not part of
`make test-atomic` or of `make test`: the design ruled it a one-shot LANDING
gate (§11.2, §14 item 8) and its reference is a pinned pre-module commit, so
every run re-answers the same question about a moment that has passed. Run it
with `make test-atomic-identity`; its archived result is in docs/testing.md,
"The atomic landing gate".

- Rationale sections (THE ORACLE RULE, U9 IS NOT IN THIS DIRECTORY, THE SWEEP HAD TO BE BATCHED, THE SHAPE THIS DIRECTORY DID NOT HAVE ([M6.4.4]), EVERY POPULATION IS ASSERTED, NEVER PRINTED): moved verbatim to NOTES.md.
## Conventions

Blocks carry `features atomic-groups` (plus `assertions`/`modifiers` where the
pattern needs them) — the module is NOT in `std1`, so a bare invocation still
refuses and `tests/reject/`'s rows keep working unchanged. Group expectations
in atomic_caps.rxt are padded to the pattern's real group count, so a group
that did not participate is asserted UNSET rather than omitted.

Maintenance: update this file when files are added or their roles change.

See also NOTES.md in this directory (history, lessons, rationale, moved detail).
