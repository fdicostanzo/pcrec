# tests/counterk — the [ENG-BREP] COUNTER rung's differential

The rung's PRIMARY validation instrument (`docs/design/counterk_impl/counterk_design.md`
§8.1): the counter build against its own `-fno-counter` build, compared on span,
every capture slot and the failure surface.

`-fno-counter` is the GROUND TRUTH, not merely a control. Denying the rung
leaves a bounded repeat on the frames rung, which for `{m,n}` is literal
replication — `{m,n}` unrolled, which is what ships today — so the denied build
is the semantic definition and any disagreement is a bug by construction. That
is the same role `-fno-revdet` plays one rung up, and the reason D47.3 made the
family DENY rather than FORCE.

## Files

- **`run_counterkdiff.sh`** — the harness. Adapted from
  `../rungselect/run_rungdiff.sh` and reusing `../possessify/possdiff_driver.c`
  through the same `-DDIFF_A_LABEL`/`-DDIFF_B_LABEL` seam both earlier rungs
  reuse, because the comparison is identical for every member of the deny family
  and only the words in the divergence report differ.

  Three things specific to this rung:

  **It sweeps subjects to 28 bytes where the revdet suite stops at 12.** That
  suite's counts top out at 8; this one's reach 24, and a bounded loop must be
  walked across 0, 1, m−1, m, m+1, n−1, n, n+1 iterations. A sweep that cannot
  reach its own family's upper boundary is not measuring the boundary.

  **It raises BOTH run clocks (`GENCPU` 45 s, `GENRUNTIMEOUT` 90 s), and the
  measurement is why.** The sweep is ~4,200 cells per pattern against the revdet
  suite's few hundred, and the nullable high-count members (`(a?){0,17}b`,
  `(|a){9,17}b`) need 10.2 s of CPU for 4,201 cells — MEASURED, and measured
  AGREEING at 0 divergences. The shared 10 s default clipped them by two tenths
  of a second and reported a wall timeout as a divergence. Raising one clock
  alone just moves which one reports the same clipping; that is what the first
  attempt did. The budgets exist to catch a HANG, and a sweep four times larger
  needs a proportionally larger ceiling or the budget stops measuring hangs and
  starts measuring sweep size.

  **Do-or-die is asserted from the ARTIFACT'S STAMP** (D47.3): the denied build
  must not stamp the COUNTER bit, and the non-vacuity control fails the run if
  NO pattern took the rung — an instrument comparing two identical artifacts
  agrees on everything and measures nothing.

- **`patterns.txt`** — the population, and its counts are chosen for their
  RESIDUE MOD K rather than for roundness.

  **This is the file R26 E1/E2 is about.** That review found an unsound clamp
  blessed by an 855-cell differential that could not have seen it: single-byte
  bodies, so no stride > 1 rung ever ran, and no residue axis at all. This rung
  has the same exposure class from its own structure — the trip guard is
  `stv[ctr] + K > count` and the tail is `count mod K` copies, so every boundary
  it computes lives on that lattice. The lane reproduced the blindness in
  miniature before this file existed: an ad-hoc sweep over counts whose residues
  mod 8 were {4,4,1,1} reported 576 green cells.

  So the file walks every residue 0..K−1 on the optional phase AND the mandatory
  phase AND both at once, plus the K−1/K/K+1 boundary where the loop first runs;
  bodies with stride > 1 so a nested cursor rung runs inside the counter loop
  (also §7.4's only division, and §8.1's [R25 E16] nested cell); nullable bodies
  at `{0,12}` and above rather than `{0,4}`, because below K no counter is
  emitted and the cell would be checking replication's termination; possessified
  shapes reached through the PASS rather than through `+` (that spelling needs
  module `atomic-groups`, which has no producer); and §3.3's named preference
  witness `(?:ab|a){0,2}?b` beside a counter-selecting sibling.

  **THE COUNTS ALL STAY UNDER 64.** The denied build is the one that replicates
  and is refused above `PCREC_MAX_VM_REPEAT_COPIES`, so a higher count would
  compile on the rung and have no ground truth. §8.1's blindness above the
  replication knee is real; it is covered by §8.5's acceptance cells and the
  oracle sweep, never by pretending this instrument reaches it.

- **`run_counterk_tests.sh`** — the STRUCTURAL checks and §8.5's ACCEPTANCE
  CELLS: the things the differential and the corpus structurally cannot see.
  24 checks (23 + [TT-10]'s K32 pin, below). Selection asserted from the stamp at both sides of the K boundary
  (7 declines, 8 selects — R25 E3's strictness as a row rather than a
  sentence), D47.3's do-or-die, byte-identity below K, and every §8.5 cell.

  **[TT-10], 2026-08-25: it also carries a LOAD-AWARE compile-cost pin for
  K32** (`docs/dev/known_issues.md` K32 — the DFA prefilter Thompson-
  replicates a bounded repeat, so `X{n}` compiles in O(n²) even though the
  VM's counter rung is already constant-size). `counterk.rxt`'s own
  `((a)|ab){4000}c` block (28 dependent m/n/g assertions off one compile) is
  the ANSWER oracle and is untouched; this file's own compile of the same
  pattern, under `scripts/watchdog -c 20 -s 60 -m 256m`, is a SECOND,
  purpose-built instrument for what that compile COSTS — `tests/resource`'s
  own shape, since this directory and that one are the two places in the
  tree asserting a compile's cost rather than a pattern's answer. Sources
  `tests/lib/load_guard.sh`: a watchdog CPU/wall kill (123/124) is reported
  **INCONCLUSIVE** rather than FAIL when the 1-min load average / `nproc`
  exceeds `LOAD_GUARD_RATIO` (default 2.0) at the moment it fires — see that
  file's header and `docs/testing.md`'s "The load guard" section for the
  measurement and threshold. This pin is INDEPENDENT of the shared corpus
  harness's own D45 budget, which the `.rxt` block still rides unchanged —
  see `docs/testing.md`'s note on why both exist.

  **The acceptance cells are CHECKS here rather than numbers in the note**, per
  R24 M-F4: a number that cannot be re-run is not a measurement. Cell 1 asserts
  the endgame's stamped ceiling AND that a subject above it gives up with
  `RX_ERR_FRAMES` rather than answering wrongly — writing it as "the pattern the
  cap refused now compiles" would be true and would hide the trade. Cell 3
  covers all three `{4000}` spellings, and the third of them is why the file
  exists: `{4000,}` was still refused after the other two compiled, and writing
  the row is what surfaced it.

  **Its own byte-identity row failed on its own filenames first**, reporting
  seven failures that were entirely the check's: the generated `.c` carries
  `#include "<basename>.h"`, so emitting the two sides as `ia.c` and `ib.c`
  makes every artifact differ on that one line. Verified before fixing, not
  after — with matched basenames the same seven pairs are byte-identical. The
  two sides now share a basename in different directories, and the comment says
  why.

## The sabotage rows this suite catches, and their MARGINS

`tests/mech/sabotages/S53..S57`, run through the `counterkdiff` arm. All five
DETECTED, 0 undetected, 0 anomalies (mech at `bf4f567`). The margins are worth
recording because they are not equal, and a thin margin is a maintenance fact
rather than a pass:

| row | what it breaks | margin |
|---|---|---|
| S53 | the counter slot made untrailed | 1 fail / 58 pass |
| S54 | the residue tail deleted | 32 fail / 27 pass |
| S55 | the greedy preference inverted | 30 fail / 29 pass |
| S56 | an empty-iteration guard ADDED | 1 fail / 58 pass |
| S57 | a nested untrailed local across a trip | 1 fail / 58 pass |

**The three narrow rows are narrow BY CONSTRUCTION, not by accident**, and each
names its own requirement: S53 needs a body with an internal choice point *and*
a resume that lands inside it; S56 needs a NULLABLE body above K; S57 needs a
nested loop inside a counter loop. Those are small populations in any honest
corpus — but small is one deletion away from zero. **If a future edit removes
the nullable cells, or the stride cells, or the alternation bodies from
`patterns.txt`, the corresponding row goes UNDETECTED while the file still looks
well populated.** That is the failure mode to watch here, and it is why those
cells carry comments in `patterns.txt` naming what depends on them.

S54 and S55 are broad because a deleted residue and an inverted preference are
wrong on most subjects of most patterns. Breadth is not virtue here — it just
means those two would be caught by a weaker instrument too.

## Why the possessive block earns its place

It caught a SILENT CAP. The first version of the possessive cost arm copied the
frames rung's `max(mandatory, loop)` frame peak, and `((a)|bc){9,20}d` returned
`RX_ERR_FRAMES` where replication matched: the two phases' peaks ADD, because
the cut mark sits below the mandatory copies and nothing cuts between them, so
they are all still live during the first optional iteration.

Reaching it needs a mandatory phase at or above K AND an optional phase — the
residue axis alone does not produce it and the possessive block alone does not
either. That is the argument for sizing a differential by the axes the MECHANISM
has rather than by how many rows it can be made to print.

Maintenance: update this file when files are added/removed or their roles change.
