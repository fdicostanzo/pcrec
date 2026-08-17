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
  stays here as that row's inherited evidence.

  **F-2 is RULED too** (D47 SECOND ADDENDUM, 2026-08-17): **settlement 4** —
  the frameless forward work §7.4 meters gets its OWN bound beside frames and
  trail, with its own `rx_info` field and its own `RX_ERR_*` code, because the
  meter must see the FULL work. The step budget does not move (same meaning,
  same unit, every pin untouched), so §7.4's `PCREC_STEP_SCALE` apparatus is
  DELETED rather than retuned and R25 finding 27 evaporates; finding 29's
  measured ~16:1 work ratio survives with a changed job, as the exchange rate
  that prices a candidate default. Three proposals were refuted before this
  one — the E-5 entry charge (§7.2), the engine critic's target (§7.3, whose
  predicate keyed on PUSHES while its justification keyed on POPS, so the
  revdet scan, `vm_poss_chain` and counter-K's own possessive arm were all
  excluded from a rule advertising strategy-invariance), and the corrected
  predicate (finding 26, which double-billed the non-possessified cursor
  rung). §7.4 is the surviving redesign.

  **What is still owed is §10.5**, and it is the first thing a reader should
  check for staleness: the new bound's DEFAULT VALUE (held back by the ruling
  itself, returning to Frank as a one-liner at implementation), the SECOND
  ADDENDUM's pre-release ABI rider (a recommendation, not a decision — the
  lane recommends `<prefix>_match` carry the same distinct negative codes as
  its siblings), and PROPOSED spellings for the new surface. Nothing in §10.5
  is ruled and no frozen document is edited by it.

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

  **The column-adjacency lesson, recorded four times now: READ ACROSS THE
  CONTROL ROWS.** Finding 26's refuting number (the same 50,005,000 under
  `steps` and under `scan`) and finding 29's deriving numbers (the seconds
  column, which prices a resumption at ~16 scan iterations) were BOTH already
  sitting in rows this note quoted. Neither needed a new measurement — only
  reading two columns of an existing row against each other.

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

- **`probes/bench_k.sh`** — the K sweep of `../eng_brep_design.md` §4.4.
  Records PER-BODY-KIND series (alternation, group-with-capture) rather than
  one aggregate curve, on counter-K's own reasoning: K is ONE dial for every
  body under F-1, this sweep is what picks its value, and a knee sitting in
  different places for different body shapes would be averaged into
  invisibility by a single curve. **The K axis is inert until `--unroll` exists;
  the harness is not** [R25 C2]: it carries a real throughput driver (subject
  built in memory, min-of-N-trials ns/search) and the THREE subject regimes —
  loop satisfied at maximum, satisfied well below it, and FAILING after
  maximal consumption, which is where backtracking runs and where K should
  matter most. Every cell validates its verdict before any time is reported,
  so a wrong subject fails loudly instead of producing a meaningless number.
  It runs end to end today with the K column collapsed to "shipped". It is a
  measurement, never a gate (D18).

  Two findings came out of building it rather than running it. One body was
  dropped: `(a(b|(c|d)))` stamps `VM_RUNGS 0x8`, the reverse-deterministic
  rung, so it would have measured rung-select under counter-K's name (replaced
  by `((a)|a(b|c))`, verified `0x2` at every N). And a SINGLE-CLASS body is not
  in this rung's population at all — `([a-c]){0,N}c` stamps `0x1`, the cursor
  rung, at every N — so the harness reports that kind EXCLUDED with the verify
  command instead of substituting a body that would measure elsewhere.

  A pragma-unroll comparison cell and every citation of `studies/simd1` were
  added at one point and then RETRACTED under the scalar-first directive; the
  file carries no external-study input.

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
