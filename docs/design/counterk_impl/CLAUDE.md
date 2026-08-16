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
  witness `(?:ab|a){0,2}?b` is already a measured defect in `nfa.c`); the rung shrinks SIZE and not
  FRAMES, so the endgame cell trades a compile-time refusal for a ~512-byte
  runtime ceiling (§3.5); and **§7 has refuted two step-charge proposals, the
  note's own both times** — start there, since it is the section most likely
  to move again.

  **F-1 is RULED** (D47 ADDENDUM): strict §4.5, K stays one per-artifact
  constant, and the CLAMP moved whole to plan row [ENG-CLAMP]. §4.2 is now the
  refutation plus a pointer; acceptance cell 2 is withdrawn; `clamp_arith.py`
  stays here as that row's inherited evidence. **F-2 is WITHDRAWN and
  returning measured**: the engine critic's pass (findings 17-25) blocked the
  first replacement too, because its predicate keyed on PUSHES while its
  justification keyed on POPS and `RX_CUT` charges nothing — so the revdet
  scan, `vm_poss_chain` and counter-K's own possessive arm were all excluded
  from a rule advertising strategy-invariance. §7.4 is the redesign.

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

- **`probes/step_charge.sh`** — the note's §7 measurement, and the probe that
  has now refuted TWO proposals, the note's own both times. It counts three
  populations at their REAL sites in the emitted artifact: `rx_fail:`
  resumptions (charged today), frames discarded by a CUT, and frameless
  span-loop iterations. The last two are the uncharged work, and the rule §7.4
  proposes is defined by exactly them.

  **Four instrument lessons, each of which produced a wrong reading first:**
  (1) the run budget is raised to 10^12 and the default applied on paper
  afterwards, because an artifact that gives up early UNDERCOUNTS the thing
  being counted; (2) THERE ARE TWO SPELLINGS OF A CUT — the `RX_CUT` macro and
  revdet's direct `w->btn = rx_rvN_mk` — and instrumenting only the macro
  reported a confident zero for revdet; (3) the B2 witnesses must have a loop
  REACHABLE AT EVERY START POSITION, and the first draft's `(x)`-prefixed
  patterns never matched their subject, so every row read zero; (4) the
  `sites` column reports how many anchors were instrumented, so "0 discarded"
  is distinguishable from "0 instrumented", which is the distinction that
  produced (2) and (3).

  Round 1's blindness is the standing lesson: its single shape `([a-z]+)9` is
  the possessified CURSOR rung, the one genuinely frameless member of the
  class, so the boundary the rule turned on was invisible to the instrument
  that priced the rule.

- **`probes/clamp_arith.py`** — the clamp, PROVED ARITHMETICALLY before the
  code exists (R25 E1 required this before acceptance). **Kept here after the
  F-1 ruling moved the clamp to plan row [ENG-CLAMP]**: it is that row's
  inherited evidence, and it carries the two results the lane established
  before the deferral — the mechanism is a BOTTOM-UP subtree product (the
  ancestors-only one parks the K22 tower at 2^17 and still refuses), and the
  PRODUCT rule is right where the SHAPE rule over-clamps `(a(b|c)?){0,4000}`.
  It
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
