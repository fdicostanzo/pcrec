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
