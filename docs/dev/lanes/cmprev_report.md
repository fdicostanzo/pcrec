# cmprev: `compound_entries.md` revision 2 (report)

Lane `cmprev`, 2026-10-16, opus, from main `7ee8d7ae7` (abi 78). This lane changed design
text only. Nothing under `src/`, `cli/`, `lib/` or `tests/` changed, nothing was built and
nothing was measured. It applies Frank's rulings on revision 1's Q1-Q5 (D163 addendum 7) to
`docs/design/compound_entries.md`.

## What changed (the note's §R2 maps each ruling to its section)

- **§3.0, invariants kept.** I1: every exported entry is a compound controller over parts, and
  the row decides only linkage. I2: E0 comes before I1, and E1 after E0. I3: no
  exported-to-exported call (Q5). I3 is a linkage rule of `entry_rows[]`, not a layout row.
- **§3.2, five DISTINCT pinned policies (Q2).**
  - `−2` `all-shared`: one static body per multi-caller part, with wrappers that forward
    frameless. F-5 is why the forwarding is part of the policy.
  - `−1` `shared-but-inner`: as `−2`, except rank-R3 inner-loop parts are inlined.
  - `0` `as-emitted`.
  - `+1` `hot-inline`: parts ranked ≥ `θ_hot` are inlined; the rest are left as at `0`.
  - `+2` `all-inline`.
  - Hotness is a static EDGE RANK (R3 inner, R2 per-call, R1 conditional, R0 rare), read off
    the combinator in `entry_rows[]`. No profile is used.
  - §3.2.1 names, for each adjacent pair of positions, the part class they disagree on and a
    witness. Populations are owed as an E1 census.
- **§3.3, `θ_hot` (Q1).** It is the one value read from the measurement set. It is a derived
  row with named inputs (`C_part` per rank on the set's reference short-call cell, and the bar
  `y`), and its domain is {R3, R2, R1}, so `+1` ≠ `+2`. When `θ_hot` is absent, `+1` DECLINES
  to `as-emitted` with `_WHY "threshold-unmeasured"`. That is today's state. Revision 1's Ir
  counts are labelled UNMEASURED in set units. Only `+1` moves with a set.
- **§3.4, ONE declared first-match table, L0-L11.** L0 (`0`) comes first, so `0` is
  byte-identical by construction. The constraint rows (label table, computed goto, seam,
  single caller) precede every non-zero position, and each position ends in an unconditional
  row. A side table explains why H4-H7 and members 1 and 4 are not rows: member 1, the VM
  entry chain, keeps its §5.4 cells until its own ruled diff. §3.4.1 lists what a caller
  observes at each position. It proposes a `<PREFIX>_PART_LAYOUT` stamp at non-zero positions
  only, first emitted with the first live cell.
- **§3.5:** Q3 is marked RULED, and the section says where M stays a runtime branch.
- **§3.6:** new checks. Caller counts are checked against an `-O2 -fno-inline` object's
  relocations, ranks against a hand-written per-witness fixture (UNREACHED if no witness),
  plus L8 visibility and totality with K35 counts.
- **§3.7, family lens.** The row is a row of the dial's policy table (D103) that unifies the
  inline/shared family. It is a sibling of `compound_place[]` under `entry_rows[]`. It is not
  an axis (an override spelling is filed to [IFACE-PUSH], U10), not engine selection, and not
  a regime-table row. It shares two edges with the regime tables: M folding, and knowledge
  key A, the set.
- **§3.8:** what `findall_iter.md`'s short revision consumes from the row (§2.2's two-row
  table dissolves into L0+L1, plus the rank of each iterator piece). `findall_iter.md` is not
  edited.
- **§5:** E1/E1′ restated, standing question 3 updated for Q1's ruling, U1 sharpened, U9/U10
  added, Q1-Q5 recorded as ruled (§5.4), and Q6-Q9 added (§5.5).

## Open questions for Frank (in the note, §5.5, each with problem / forces / leaning)

- **Q6.** When the set lacks `θ_hot`, should `+1` decline or refuse? Leaning: decline, with
  the stamped reason (tuning.md §2.21¶3's selection-outcome rule).
- **Q7.** Is a static edge rank enough, or should the analysis object refine conditional
  edges? Leaning: static now, with the exemplar refinement filed as U9 and a trigger.
- **Q8.** At `+1`, are below-`θ_hot` parts left to gcc or shared? Leaning: left to gcc, so a
  speed position never shares more than `0`. The cost is that `+1`'s cold parts still flip
  with `-fPIC`.
- **Q9.** For a position with no corpus population that distinguishes it from its neighbour,
  report it or reshape the policy? Leaning: report it, with a synthetic witness per part
  class (D103's declared-vacuous `+2` is the precedent).

## Also updated

`docs/design/CLAUDE.md` (the note's revision-2 entry) and `docs/dev/lanes/CLAUDE.md` (this
report).

## Validation

No validation runs are owed. This lane changed documents only, so no build, suite or probe
was run, and revision 1's probes are unchanged. Two light doc checks were run on the branch.
`scripts/plan_lint.sh` passed. `make test-spec-history` read 144 passed and 1 failed. The one
failure is `docs/design/findall_iter.md:753`'s line-number citation. It is in the base commit
`7ee8d7ae7`, this lane does not touch it, and main has since fixed it in `b785a6e6a`.
