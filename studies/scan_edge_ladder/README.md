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

## D112: emitted comments are off by default (read this before re-running)

D112 (2026-09-19, abi 26 -> 27) flipped emitted comments OFF BY DEFAULT.
The `[OPT-5] SCAN EDGE` comment marker BOTH census points in this harness
read (`rungs`'s and `run_ladder.sh`'s own re-check of `a_after_$k.c`;
`floorcells`'s and `run_floor.sh`'s own check of `e_${fam}_$m.c`) is exactly
the comment class the flip removes.

The two census sites are affected DIFFERENTLY, because only one of them
reads an artifact built by the compiler under test:

* The **ladder's** rung census reads `a_after_$k.c`, built by the OLD
  `after` reference compiler (`b048fa61`, git-archive'd from before D112
  existed). That compiler always emits comments unconditionally and has
  no `-fcomments` flag to pass (passing one would itself be a hard CLI
  error on that old binary). `step11` (the compiler under test) shares
  `scanedge.c`'s edge-taking decision with `after` by the ladder's own
  design precondition, so `after`'s topology stands in for it — no fix
  needed on this side.
* The **floor's** census reads `e_${fam}_$m.c`, built by `$PCREC` itself —
  there is no old-reference stand-in. `floorcells` and `run_floor.sh` now
  pass `-fcomments` on that one build. This is proven byte/behaviour-
  neutral for the machine under test (D108; `emitverb_report.md`'s own
  `.o`-identity proof and its AUTO-rung-selection fix for the one place a
  raw-byte-including-comments comparison could have picked a different
  rung) — it changes only what the CENSUS can see, not what is measured.

If a future compiler removes the `[OPT-5] SCAN EDGE` marker itself (rather
than just gating it behind the comments axis), both census points break
again and need a structural stamp instead — see the finding recorded in
`docs/dev/lanes/edgefix_report.md`.

## Failure semantics

A rung or cell that measures nothing FAILS the run (non-zero exit, with the
reason printed) — it never merely prints a message and exits 0. This
applies to: a `pcrec`/`gcc` build failure, a wrong forward-edge count, a
cell/rung with zero valid rounds, and (floor only) the median/IQR summary's
own "no valid rounds" case. `make ladder`/`make floor`/`make rungs`/
`make floorcells` all propagate this.

## The floor's median/IQR summary

`run_floor.sh` now prints a `median / IQR summary` block (median and a
linear-interpolated IQR, per `m` x family, over every ACCEPTED round) at
the end of its own output. This did not exist before 2026-09-21: the
2026-09-04 report's medians/IQR were computed by hand, from an interactive,
never-saved `python3` one-liner run against the raw per-round lines the
script already printed — which is why re-running the harness never
reproduced a summary block on its own.

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
