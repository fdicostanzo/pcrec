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
  owed E-5 step charge has to be strategy-INVARIANT or it turns the lane's
  primary differential red by construction (§7.2).

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

- **`probes/bench_k.sh`** — the K sweep of `../eng_brep_design.md` §4.4, with
  this note's §4.4 additions (a real counter loop at K = 1, and the three
  subject regimes rather than only the satisfied-at-maximum one). Scaffolded
  during the design phase and INERT until the counter rung exists: with no
  `--unroll` in the compiler it reports the axes it cannot yet walk instead of
  printing numbers that are secretly about something else. It is a
  measurement, never a gate (D18).

Maintenance: update this file when files are added/removed or their roles
change.
