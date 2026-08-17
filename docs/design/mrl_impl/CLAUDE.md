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

- `probes/throughput.sh` — what the bound COSTS on the forward path, which is
  D18's mandate and D51 ruling 1's adoption bar (<= 2% at full clamp density).
  THREE arms, and the third is the point: pruned, denied
  (`-fno-length-prune`), and a PLACEBO — the pruned artifact with its two MRL
  macros redefined so the bound is computed with the same instruction shape
  and can never bind. `clamp` is pruned-vs-placebo, `layout` is
  placebo-vs-denied.

  **The placebo is not symmetry for its own sake, and this probe learned that
  the hard way.** Its first version ran two arms and reported +27.8% on
  `(\d{3})-(\d{4})b` — a 12 ns measurement on a digit-free subject, where the
  DFA prefilter answers and the VM is never entered at all, so not one MRL
  instruction executes. That number is entirely what inserting any code does
  to the layout of a translation unit, which is exactly the attribution
  k23_design.md §6 built its own placebo for. The row is KEPT rather than
  replaced, because a demonstration that the instrument needs its control is
  worth more than a tidier table.

- `probes/dfadiff.py` — **the LANDING PANEL's own instrument, adopted here.**
  Not written by this lane: it is what the soundness lens used to reach its
  ~285,000-cell verdict, and it is kept because an instrument built by someone
  ATTACKING the change is worth more than one built by the person who wrote
  it. The build lane's own differential compares two pcrec builds that share
  every line of the analysis; this one uses pcrec's OWN DFA ENGINE
  (`--no-captures`) as an independent oracle — MRL-free, terminating,
  capture-blind, and therefore able to referee exactly the SPAN an over-large
  bound would delete. Three arms: default hybrid, pure DFA, and `--engine=vm`
  to separate the window ceiling from the bound.

  Adopted verbatim in mechanism, with two changes and no third: its hardcoded
  session paths are generalised, and its companion driver is INLINED so the
  file stands alone (a probe that depends on an uncommitted sibling is a probe
  that stops running). NOT battery-wired, deliberately — it generates random
  patterns and builds three artifacts each, so its population is a seed rather
  than a fixture. The narrower form of the same idea IS wired: `run_mrldiff.sh`
  uses a `--no-captures` referee arm for the excused cells specifically.

- `out/` — archived probe OUTPUT. Evidence, never an oracle: no check reads
  it. `dfadiff.txt` is the panel's own run against this branch (74 patterns x
  1,305 subjects, 0 span divergences), archived with its provenance stated in
  the header rather than left to be inferred from the numbers.

## The one thing worth knowing before re-running any of it

**The step figures are BOUNDS, not counts, and the unpruned arm's bound is a
power of two.** `≤16,777,216` on the exemplar is 2²⁴, the first power of two
above the design note's exactly-measured 10,621,636 — the two agree, and the
note's figure is the precise one. The pruned arm's `≤1` is exact for a
different reason: 1 is the smallest budget the doubling search tries.

Maintenance: update this file when files/subdirectories are added or removed
or their roles change.
