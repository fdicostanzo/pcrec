# scan_edge_ladder — [OPT-EDGE]'s two owed measurements

The 1/2/3/4 EDGE LADDER and the MINIMUM-CHAIN FLOOR that `[OPT-EDGE]` STEP 1
left owed. Written by lane edge2 (2026-09-04) and committed here because a
harness that dies with a session cannot be re-run against the next compiler.

Nothing here is built by pcrec's own `make`, and no check reads its output.

## The ladder, and why edge1's design was wrong

STEP 1 replaced a per-edge `if (state == HEAD && …)` on the scan loop's
generic path with ONE shared sentinel test, so the entry cost went from
O(edges) per byte to O(1). The ladder is meant to split the FIXED per-artifact
cost from the PER-EDGE one by fitting `t(k) = a + b·k` over machines carrying
1, 2, 3 and 4 forward edges.

edge1 built it by SUBTRACTING the `-fno-scan-edge` arm, and the entry cost came
out NEGATIVE at every rung. That is the design being wrong, not the compiler
being fast: `-fno-scan-edge` is a **different machine** — its chain interiors
are not deleted — so the difference carries the scan collapse's own per-byte
win as well as the entry cost, and the collapse dominates.

The isolation that works is **BEFORE against AFTER on the same machine**: same
states, same edges, only the dispatch differing.

| arm | compiler | what it is |
|---|---|---|
| `before` | `9d8401a` | the per-edge `if` chain on the generic path |
| `after` | `b048fa61` | the shared-sentinel dispatch (STEP 1) |
| `step11` | `$(PCREC)` | the compiler under test (STEP 1.1 and later) |
| `noedge` | `after` + `-fno-scan-edge` | a CONTROL, printed and never subtracted |

## The floor

Precondition (5) admits chains of `m >= 2`. On the O(1) dispatch the length at
which an edge PAYS is a different number from the old loop's — the row's own
SEQUENCING ruling — so the floor is measured on the NEW loop only. Here the
`-fno-scan-edge` arm IS the right control, because the question is "is the edge
worth taking at this length", which is exactly the two-machine comparison.

The floor is placed INSIDE a measured gap: a length where the arms are
separated by more than the per-round range at BOTH neighbours. No gap, no move
(D77).

## Three refusals, and they are the point

Each is a lesson edge1 paid for, spelled as a refusal rather than a caveat.

1. **`load1 >= 0.5` refuses the whole run**, and a round whose load rose is
   DISCARDED rather than reported. edge1's ladder ran at 0.84-1.01.
2. **A rung whose FORWARD edge count is not `k` is refused by name.** The count
   is read from the artifact's own `[OPT-5] SCAN EDGE` markers, attributed by
   the state variable each block tests — never from `RX_DFA_SCAN_EDGE`, which
   names axis I's BODY form and reads identical when a machine goes from two
   edges to one.
3. **A rung whose subject never ENTERED the chain is dropped**, not reported.
   Two of edge1's three attempts died exactly there: a subject the pattern
   cannot engage reads ~0.04 ns/byte and measures nothing. `ENTRY_FLOOR`
   (0.15 ns/byte) is the tripwire.

Method for both: 256 KB near-miss subjects, `taskset`-pinned, arms INTERLEAVED
inside each round, the ratio taken per round from that round's own pair,
15 rounds × 10 sweeps, medians reported WITH the per-round range.

## Running it

```
make refs        # build the two reference compilers from git archive
make rungs       # regenerate + verify the four rung artifacts
make ladder      PCREC=../../build/pcrec
make floorcells
make floor       PCREC=../../build/pcrec
```

`PCREC` has no default on purpose: a study that silently measures whatever is
in `../../build` is how a number ends up attributed to the wrong commit.
Everything generated lands in `out/`, which is gitignored.
