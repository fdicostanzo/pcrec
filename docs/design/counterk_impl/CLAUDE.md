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
  code on this project's design-first precedent. **PANELED R25
  (`../../dev/reviews/2026-08-16-r25-counterk.md`): four blockers and nine
  majors, all applied IN PLACE.** Read the PANEL OUTCOME block at the top
  before any section.

  Its structural loads, for a reader deciding what to check first: the counter
  must be a TRAILED slot (§2.2 — a plain local is a correctness failure with
  `(a|b){0,4}c` as the witness, a per-frame field is CORRECT at one nesting
  level and dies on the depth-shaped vector nesting would need, and the first
  draft conflated the two); a counter LOOP is preference-equivalent to
  `vm_opt_chain`'s NESTED optional chain and not to a chained one (§3.3, whose
  witness `(?:ab|a){0,2}?b` is already a measured defect in `nfa.c`); K needs a
  CLAMP or it does nothing at all for K22, and the clamp needs a BOTTOM-UP
  subtree pass rather than the ancestors-only product the first draft specified
  (§4.2, proved by probe); the rung shrinks SIZE and not FRAMES, so the endgame
  cell trades a compile-time refusal for a ~512-byte runtime ceiling (§3.5);
  and the owed E-5 step charge is REFUTED — see §7, which started as a cost
  estimate for it and became the measurement that killed it.

  Two questions are open with Frank and the sections say so: F-1 (may K vary
  per quantifier at all — `../eng_brep_design.md` §4.5 says no and this note
  self-authorized the exception) gates §4.2; F-2 (§7.3's replacement charge and
  its SHIFT) gates §7.3.

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

- **`probes/clamp_arith.py`** — §4.2's clamp, PROVED ARITHMETICALLY before the
  code exists, which R25 E1 required before the design could be accepted. It
  models the emitted-copy count and the nesting-path product rather than
  compiling, because the pass does not exist and a compile today would measure
  replication. Reads `PCREC_MAX_*` out of `limits.h` rather than copying the
  numbers — a constant transcribed into a check is a control sharing a source
  with the thing it controls. Carries the `{1,2}` tower as a MUST-STILL-REFUSE
  row and fails if it compiles: a probe that shows only its own successes is
  not evidence.

- **`probes/census_default.sh`** — R25 E10's owed census: quantifiers by rung
  and by possessification, on the DEFAULT routing (what ships) and under
  `--engine=vm`, read from `--emit-ir`'s RUNGS section so it cannot drift from
  the emission. It exists because §1.2 argued the possessive arm's necessity
  over a `-fno-revdet` table — a population the default path never reaches —
  and exhibited no member of the cell it was arguing about. `LC_ALL=C` is set
  explicitly for R24 M-F1's collation reason, as the possessify lane's census
  does.

- **`probes/bench_k.sh`** — the K sweep of `../eng_brep_design.md` §4.4, with
  this note's §4.4 additions. **The K axis is inert until `--unroll` exists;
  the harness is not** [R25 C2]: it carries a real throughput driver (subject
  built in memory, min-of-N-trials ns/search) and the THREE subject regimes —
  loop satisfied at maximum, satisfied well below it, and FAILING after
  maximal consumption, which is where backtracking runs and where K should
  matter most. Every cell validates its verdict before any time is reported,
  so a wrong subject fails loudly instead of producing a meaningless number.
  It runs end to end today with the K column collapsed to "shipped". It is a
  measurement, never a gate (D18).

  One body was dropped when the harness became real: `(a(b|(c|d)))` stamps
  `VM_RUNGS 0x8`, the reverse-deterministic rung, so it would have measured
  rung-select under counter-K's name. Replaced by `((a)|a(b|c))`, verified
  `0x2` at every N in the sweep.

## Archived outputs

- **`measure_baseline.txt`** / **`step_charge.txt`** / **`clamp_arith.txt`** /
  **`census_default.txt`** — one run of each probe above, with its own source
  header (repo, commit, gcc, date). Stable-named so a re-run diffs against
  them, D35's shape. Evidence for the panel, never an oracle: no check reads
  them.

  `step_charge.txt`'s 1 MB `--engine=vm` quadratic row is absent on purpose and
  its absence is the finding — the row exceeded a 120 s wrapper during
  development and extrapolates to ~213 s from the 100 KB row, against the
  possessify lane's independently measured 228.5 s. A timeout is a recorded
  finding, never a reason to re-run longer (D45's posture).

Maintenance: update this file when files are added/removed or their roles
change.
