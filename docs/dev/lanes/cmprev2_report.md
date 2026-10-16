# cmprev2 — `compound_entries.md` revision 3 (panel r3)

Lane `cmprev2`, opus, 2026-10-16, branch `lane/cmprev2` from main `74ac73f7f` (abi 78).
Design text only: nothing under `src/`, `cli/`, `lib/` or `tests/` changed, and nothing was
measured beyond one two-line gcc probe (below).

## Delivered

- `docs/design/compound_entries.md` revision 3. Read its §R3 first: it maps all 27 r3
  findings to sections.
- `docs/dev/reviews/2026-10-16-r3-compound-entries.md`, copied in from the main tree.
  Every disposition now reads ACCEPTED (manager 2026-10-16), and a "Revision 3 discharge"
  section at its end maps each finding to the section and fix.
- `docs/dev/reviews/CLAUDE.md`: an entry for the review, in the r1-measure-sets shape.
- `docs/design/CLAUDE.md`: the note's entry now records revision 3.

## The blockers, and how they were discharged

All three had one root: revision 2's table ignored attributes the emitters already write.
- **CE-1.** `+1`'s decline is now artifact row T1, evaluated before any part row, so it
  gives the `0` object exactly. [OPT-1]'s `_deep` `noinline` is OWNED (row P1) and kept at
  every position. The single-caller row P3 keeps the `0` layout and adds no attribute.
- **CE-2.** The VM entry chain is OWNED by P1. The two dial rows are "co-resident, not
  unified", with disjoint subjects, and §3.6 checks that.
- **F3.** New invariant I4: the `0` layout is the owning design's. T0 leaves every
  attribute alone. `findall_iter.md` §2.2 is KEPT as the `0` cell's content, and P2 keeps its
  explicit `static noinline` on label-table bodies.

## Majors of note

- **LK-1.** `entry_rows[]` does not exist, so E0a ADDS a rank column. It is a shape
  predicate per part reference, written by hand, with a hand fixture that is a precondition
  of E1.
- **LK-2.** `forwardable(w)` plus the W2 `adapt` fallback.
- **LK-3.** P2, P4 and P6 write `noclone`, and a clone-symbol check backs it.
- **F1.** The honest recount finds one built decision (the VM chain), one designed (§2.2),
  four fixed writers and the kit's helpers. The "past the unification threshold" argument is
  DROPPED.

## Measured in this lane

gcc 15.2 `-O2 -Wall` on a two-line probe (lane scratch, `build/probe/`, not committed):
`noinline` together with `always_inline` gives "ignoring attribute 'noinline' because it
conflicts with attribute 'always_inline'" [-Wattributes], rc 0 without `-Werror`. This is
the detector named for proposed row S1000.

## Not discharged, or discharged by statement only

Every finding is addressed. Two rest on a statement and the note says so:
- **LK-3.** No cloning was observed in the panel's test, so the clone check carries the
  proof.
- **LK-4.** The zero population of gcc's other refusal causes (`alloca`, `setjmp`, variadic,
  recursion) is a grep at `74ac73f7f`, held by E1's census.

## Open for Frank

Q6-Q9 (§5.5), updated with the panel's notes, in discussion form:
- **Q6.** Decline vs refuse. Leaning: decline, keeping T1's "threshold-unmeasured" and T2's
  "no-material-rank" distinct.
- **Q7.** Static rank. Leaning: static, with U9 for the exemplar.
- **Q8.** Cold parts at `+1`. Leaning: the `0` layout. The F3 tension is resolved by I4.
- **Q9.** Empty populations. Leaning: report with hand-written synthetic witnesses. Three
  of the four adjacent pairs are now UNWITNESSED or declared-coincident.

## For the manager

- Sabotage ids S999-S1008 in §3.6 are PROPOSALS, to be allocated by the manager.
- No validation suite applies to a docs-only change. No `make` was run.
