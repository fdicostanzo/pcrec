# docs/design/counterk_impl — the [ENG-BREP] COUNTER-K lane's design and measurements

The lane that builds `../eng_brep_design.md` §4's COUNTER RUNG — one body copy
(or K) plus an iteration counter, replacing the frames rung's full replication
of bounded repeats. Its own design note, probes and archived outputs, kept
separate from `../eng_brep_measurements/` (the design lane's territory),
`../possessify_impl/` and `../rungselect_impl/` (the two earlier rung lanes')
so the four are never confused — the same separation `possessify_impl` was
created for.

Everything here is COMMITTED AND RE-RUNNABLE. R24 M-F4's lesson: a number that
cannot be re-run is not a measurement.

## Files

- **`counterk_design.md`** — the emitted-shape design note, written before the
  code on this project's design-first precedent (the manager reviews direction
  from it, and the D6 panel reviews it before any engine code is written).
  Its four structural loads, for a reader deciding what to check first:
  the counter must be a TRAILED slot rather than a frame field or a local
  (§2.2, with the `(a|b){0,4}c` counterexample); a counter LOOP is preference-
  equivalent to `vm_opt_chain`'s NESTED optional chain and not to a chained one
  (§3.3, whose witness `(?:ab|a){0,2}?b` is already a measured defect in
  `nfa.c`); K needs a CLAMP or it does nothing at all for K22 (§4.2); and the
  owed E-5 step charge is REFUTED — see §7, which started as a cost estimate
  for it and became the measurement that killed it.

## Probes

- **`probes/measure_baseline.sh`** — every MEASURED claim in the note,
  reproduced from the committed tree in one run, in the note's own order:
  §1.2's possessified-repeats-still-replicate table (which is why counter-K
  must cover the possessive arm), §2.2's frame-padding measurement (the
  cheaper mechanism the note refutes is FREE, and refuting a free alternative
  needs the argument to be structural), §8.1's rung census over candidate
  endgame bodies, §8.5's acceptance cells as they behave TODAY, and the
  stamped capacities the trail arithmetic is predicted against.

  Its own recorded instrument note, because the first draft got it wrong: a
  mandatory-phase cell MUST use a body that declines the reverse-deterministic
  rung too. `((a)|bc){4000}` compiles today in 299 lines and would have read
  as "counter-K already works"; `(a|ab)` is the body that declines both
  earlier rungs.

- **`probes/step_charge.sh`** — the note's §7 measurement, and the one that
  REFUTED the fix it was written to size. It counts, in the EMITTED ARTIFACT
  and at the two real charge sites rather than at proxies for them, what the
  budget is charged today (`rx_fail:` resumptions) beside what the owed
  E-5 entry charge would ADD (visits to the label `--emit-ir`'s RUNGS rows
  name for each quantifier). They are the SAME NUMBER at every size, which is
  the refutation. Three blocks: A what the charge would cost on legitimate
  linear work, B the blind spot with `-fno-possessify` as the control that
  shows where the number needs to land, C whether the pathology is reachable
  on the DEFAULT path at all (it is not).

  Two instrument notes worth keeping. The run budget is raised to 10^12 and
  the DEFAULT budget applied on paper afterwards, because an artifact that
  gives up early UNDERCOUNTS the thing being counted. And a DFA-only artifact
  legitimately has no quantifier rows and no fail label, so the probe reports
  zero there rather than calling its own instrumentation broken — while any
  OTHER count mismatch is a hard failure, since a probe that silently
  instruments nothing is the check-design failure this project has recorded
  twice.

- **`probes/bench_k.sh`** — the K sweep of `../eng_brep_design.md` §4.4, with
  this note's §4.4 additions (a real counter loop at K = 1, and the three
  subject regimes rather than only the satisfied-at-maximum one). Scaffolded
  during the design phase and INERT until the counter rung exists: with no
  `--unroll` in the compiler it reports the axes it cannot yet walk instead of
  printing numbers that are secretly about something else. It is a
  measurement, never a gate (D18).

## Archived outputs

- **`measure_baseline.txt`** / **`step_charge.txt`** — one run of each probe
  above, with its own source header (repo, commit, gcc, date). Stable-named so
  a re-run diffs against them, D35's shape. Evidence for the panel, never an
  oracle: no check reads them.

  `step_charge.txt`'s 1 MB `--engine=vm` quadratic row is absent on purpose and
  its absence is the finding — the row exceeded a 120 s wrapper during
  development and extrapolates to ~213 s from the 100 KB row, against the
  possessify lane's independently measured 228.5 s. A timeout is a recorded
  finding, never a reason to re-run longer (D45's posture).

Maintenance: update this file when files are added/removed or their roles
change.
