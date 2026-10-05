# Lane `ssrev` — START-SET r4 consolidation + revision 2

Lane `ssrev`, 2026-10-05, opus. Branch `lane/ssrev` off main `08caf4a3`
(abi 61). Design and measurement probes only; nothing under `src/`,
`cli/`, `lib/` or `tests/` changed.

## Delivered

1. **The panel record**, committed verbatim:
   `docs/dev/reviews/2026-10-05-r4-startset/` (ssc-sound + its harness,
   ssc-checks, ssc-cost; own CLAUDE.md).
2. **The consolidation**: `docs/dev/reviews/2026-10-05-r4-startset.md`.
   Every finding id has a disposition, duplicates are merged explicitly
   (6 groups), and the by-id completeness check reads **34/34 ids**
   (sound 10 with F5's five parts as 14 rows, checks 13, cost 10 + the
   unnumbered NOTE as `cost-N1`).
3. **The blocker measurement** (sound-F1): `docs/design/startset/rev2/`
   (instruments, `run.sh`, `out/` transcripts, own CLAUDE.md).
4. **`docs/design/startset.md` REVISION 2**: §R2 "what changed and why",
   keyed to the finding ids; §4.1a, the measured set; §6.2 / §6.3
   rebuilt; §9b, six questions for Frank.

## The blocker measurement (sound-F1)

The six witnesses at the critic's alphabets, maxlen 7, every startpos, the
full capture vector. Local libpcre2 10.48 agreed with base on every cell.

| witness | r3 `S∩E` diffs | (a) `S∩E*` | (b) `S` | (c) |
|---|---|---|---|---|
| `matrix.rxt:1064` | 11,040 | 0 | 0 | declines (0 by construction) |
| `matrix.rxt:2597` | 11,040 | 0 | 0 | declines |
| `matrix.rxt:1122` | 60,430 | 0 | 0 | declines |
| `matrix.rxt:2662` | 60,430 | 0 | 0 | declines |
| `lookbehind.rxt:212` (hybrid) | 11,772 | 0 | 0 | declines |
| `ucp/ctxnode.rxt:400` | 12,264 | 0 | 0 | declines |

**The seeded-machine sweep**:
- **Population**: 94 rows, every seeded byte-class DFA/hybrid census row
  with a necessary `S`. 13,583,325 cells, 3,688,128 matches, 78 rows
  reaching a match. libpcre2 vs base: 0.
- **r3's set**: 322,771 diffs on 20 rows; the static check (`Tdfa ⊆ T`)
  and the start-byte oracle fail on 21 rows.
- **(a), (b), `Tdfa`**: 0 / 0 / 0 on all three counts.
- **(c)**: by construction equals r3's set on the rows it admits.

**Structural finding**: `E*` is all 256 bytes on every seeded machine (94
of 94), so (a) ≡ (b). The machine's own floor `Tdfa` also equals `S` on
94 of 94.

**Mover effect** (bench / corpus):

| option | movers |
|---|---|
| r3 | 18 / 44 (6 unsound; the r3 note itself said 58, counting 14 empty-T rows) |
| (a) = (b) = (c), admitted iff `T ⊊ E` | **18 / 38** |
| (a)/(b), admitted on `\|T\| < \|E\|` | 18 / 53 (+15 corpus-only set SWAPS) |

**Recommendation** (Q-R1): (a), admitted iff `T ⊊ E`. It is sound and
mover-identical to (c).

## The controls built (sound-F2, checks-F2)

- **C-SS\*** (`rev2/control.py`): `Tdfa ⊆ S` on every machine.
  - 864 artifacts read, 170 of them seeded. Baseline: 0 violations.
  - The planted WALK defects fire: `cat-null` 367 (154 seeded),
    `alt-right` 185, `look-eats` 118 (74 seeded), `rep-min0` 23.
  - 1,721 artifacts are counted as unread (no emitted table).
- **The start-byte oracle on the VM hat** (`rev2/vmoracle.py`):
  - at auto, 76 rows / 8.37M cells: 0 violations;
  - forced VM, 2,470 rows / 194.3M cells: 0 violations;
  - the 3 libpcre2 disagreements are the corpus's own U1/U9 rows.

## Questions for Frank (rev 2 §9b)

- **Q-R1** (sound-F1, D148 Q1): the DFA-hat set. Recommend (a)
  `T = S ∩ E*`, admitted iff `T ⊊ E`.
- **Q-R2** (checks-F3/cost-F8/sound-F8, D148 Q7's basis): the forced-VM
  sweep Q7 relied on does not exist. Recommend keeping NO early gate and
  making the `run_axes` product arm and the every-startpos differential
  named stage-2 deliverables, plus a second-subject-class forced-VM read.
- **Q-R3** (sound-F3, extends D148 Q6): name capacity give-ups (FRAMES,
  trail, `_in`). Recommend YES.
- **Q-R4** (cost-F9, D148 Q9): replace stage 4's trigger with a NEED
  trigger, the pre-check-candidate saving on the 4 bench
  `run_present_unbounded` cells. Recommend YES; the regression guard stays
  as a do-not-regress row.
- **Q-R5** (cost-F1/F10, D148 Q1's VM cell): recommend (a), the VM hat
  emits the table form only at stage 2, with MASS admission filed behind
  the dense guard cells.
- **Q-R6** (checks-F1): confirm the stamp's family as both engines
  (`REQ_HANDOFF`'s precedent). Recommend YES.

## Not done / owed

- **`run.sh` was not run end to end.** Every transcript in `rev2/out/` came
  from the same commands, run step by step.
- **Every rev-2 timing is owed.** Linux memchr-form, match-dense,
  short-call and S == REQ_BYTE cells, and F3 at the dense movers: these are
  stage-2/3 alpha items.
- **The census re-run with per-block options** (sound-F4) is stage 1's.
- **Sabotage witnesses marked "verify"** in §6.3 are constructed and need
  confirmation on the build.
- **The oracle arm is local libpcre2 10.48**, not the 10.46 reference.

## For a resuming agent

Start at `docs/design/startset.md` §R2 and §9b. The consolidation table is
the authority on dispositions. `docs/design/startset/rev2/CLAUDE.md` lists
the instruments and the three instrument defects found and fixed during the
run. None of them reached a cited number. The sweep artifacts were
re-verified with the final `estar.py`.
