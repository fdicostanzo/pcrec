# docs/design/mrl_impl/ — the [M4.6d] MRL BUILD lane's own measurements

The lane that BUILT minimum-remaining-length pruning (K23's fix of record,
D51 ruling 1). Kept separate from `../k23_impl/` — the DESIGN lane's territory
— for the same never-confuse-the-lanes reason `possessify_impl/`,
`rungselect_impl/` and `counterk_impl/` are separate from
`eng_brep_measurements/`: the design lane's numbers come from prototypes that
patch already-emitted C, and this lane's come from the shipped compiler. A
number from one is not evidence about the other.

Nothing here is built or run by pcrec's `make`. The lane's PERMANENT checks
live in `../../../tests/mrl/`, which is where a number that has to keep being
true belongs (R24 M-F4: a number that cannot be re-run is not a measurement,
and one nobody re-runs is not a check).

## Files

- `probes/mrl.py` — the lane's one instrument, three subcommands over the same
  two artifacts (the shipped compiler with pruning, and with
  `-fno-length-prune`):
  - `steps PATTERN SUBJECTS` — the step count for both arms, by DOUBLING the
    emitted step budget until the artifact stops returning `RX_ERR_STEPS`.
    It reports the smallest power of two ABOVE the true count and is labelled
    as a bound, because there is no step counter to read out of a shipped
    artifact and adding one would measure a different binary.
  - `diff CASES.tsv` — a three-way differential (pruned / unpruned / python
    `re`) on the FULL capture vector. Superseded as the lane's primary
    instrument by `tests/mrl/run_mrldiff.sh`, which is committed, swept over
    both ceilings and part of `make test`; kept here because it is the form
    that also consults python, which the committed one does not.
  - `sizes PATTERN` — emitted-C size, both arms.

  `LC_ALL=C` is set for every subprocess (R24 M-F1's collation defect).

- `out/` — archived probe OUTPUT. Evidence, never an oracle: no check reads
  it.

## The one thing worth knowing before re-running any of it

**The step figures are BOUNDS, not counts, and the unpruned arm's bound is a
power of two.** `≤16,777,216` on the exemplar is 2²⁴, the first power of two
above the design note's exactly-measured 10,621,636 — the two agree, and the
note's figure is the precise one. The pruned arm's `≤1` is exact for a
different reason: 1 is the smallest budget the doubling search tries.

Maintenance: update this file when files/subdirectories are added or removed
or their roles change.
