# [OPT-DIAL] STEP 1 — the speed-vs-size dial: option, policy table, λ

Lane `dialdesign`, 2026-09-16. **DESIGN ONLY — nothing under `src/`,
`tests/` or `docs/spec/` lands from this lane.** §8 is the spec plan the
implementation lane executes under D80; §9 is the ruling queue.

Inputs, all of them read in full: `docs/dev/plan.md`'s `[OPT-DIAL]` row
(every Frank ruling on this design), `docs/design/opt_dial_inventory.md`
(STEP 0, as revised today by this same lane),
`docs/dev/optdial_size_sweep.md` (last night's merged size sweep),
`docs/dev/cls_tree_study.md` §5 (the sectioning DP, where λ comes from),
and `docs/dev/lanes/ccd2_report.md` §9.

---

## 0. What this note decides, and the one thing it cannot

It decides: the option's spelling and its precedence against D93; which of
pcrec's twenty-three generation axes the dial may touch and what it sets
them to at each of five positions; how those five positions map onto λ, the
class-matcher kit's own currency; the stamp and its `abi` consequence; and
what acceptance means.

**It cannot fix the thresholds numerically, and the reason is a missing
measurement rather than a missing opinion.** Frank's rule-shape is stated
in one unit — *"performance penalty under x% AND size savings over y%"* —
and the inventory's rows carry their penalties in four different ones
(`opt_dial_inventory.md` §3.2). Two of the rows measure a COMPONENT of
match time rather than match time, and nothing in this repository says what
share of match time those components are. §3.2 converts the component rows
exactly, with one unknown per row, and §9 names the measurement. Every
number in §3 and §4 below is marked **PROPOSED FOR FRANK'S RULING**;
nothing here is a ruling and nothing here is presented as measured that is
not.

**The headline finding, stated before its derivation**, because a reader
should be able to check it rather than be walked to it:

> **THE FIRST SIZE NOTCH IS EMPTY ON EVERY DISCRETE ROW, AND NOT BECAUSE
> OF THE THRESHOLDS.** Among the axes whose DENIAL SAVES BYTES — the only
> ones a size notch could ever want — pcrec's measured penalties have a
> GAP: `--unroll`'s K ladder costs essentially nothing, and the next
> cheapest costs **1.794×** (`-fno-premul-table`); the rest run 1.99×,
> 2.00×, 2.71-3.03× and 5.06×. So for any tier-one bound below 1.794 the
> notch-`−1` column is identical to the middle on every discrete row, and
> the only rows that distinguish them are λ and the `[ART-SIZE]` ladder.
> **This is a property of the measured population, not of the numbers Frank
> picks**, and it will not be fixed by moving x.
>
> The qualifier is load-bearing and a reader should check it. There IS a
> measured penalty inside the gap — `-fno-altcls-merge`/`-fno-altcls-factor`
> at 7.61% throughput, i.e. 1.082× — and it is not a candidate, because
> denying those two also makes the typical artifact BIGGER
> (`opt_dial_inventory.md` §2.6). A switch that is worse on both axes is not
> a trade, so it never enters the distribution a size notch draws from.

---

## 1. THE OPTION

### 1.1 Spelling

**`--tune=N`, an ordinal `N ∈ {-2,-1,0,+1,+2}`, `0` the default middle,
with five mnemonic aliases accepted on equal terms:**

| N | alias | meaning |
|---:|---|---|
| −2 | `min-size` | smallest artifact the measured rates justify |
| −1 | `size` | size-leaning |
| 0 | `balanced` | **today's defaults, unchanged, byte for byte** |
| +1 | `speed` | speed-leaning |
| +2 | `max-speed` | fastest the measured rates justify |

This is the manager's pre-ruling and this lane adopts it. STEP 0
recommended three NAMED profiles and its argument for names over numbers
was good — a closed token set is what `RX_ENGINE_SEL` is, a typo is an
error rather than a silent neighbour, and it extends without renumbering.
Frank's 2026-09-06 direction then ruled FIVE settings, and at five the
argument weakens on its own terms: the fourth and fifth names
(`size`/`min-size`, `speed`/`max-speed`) are not natural language, they are
ordinal positions wearing words. Accepting both spellings keeps the closed
set for the stamp (§5) and Frank's own framing ("a dial of N") for the
command line, and costs one alias table.

**Two mechanical points the implementation must not discover late.**

1. **A negative value needs the `=` form.** `--tune -2` is two tokens and
   the second begins with `-`; every argv parser in this CLI would have to
   special-case it. The `=` form (`--tune=-2`) is unambiguous. The
   recommendation is to REFUSE the separated form for negative values with
   a diagnostic naming the `=` spelling, rather than accept it by
   look-ahead — and to document the aliases as the preferred spelling
   precisely because they have no leading dash.
2. **Out-of-range values are refused, never clamped.** `--tune=3` is an
   error naming the range. A clamp would let a caller believe they had
   asked for something the artifact does not have, and the whole point of
   the stamp is that an artifact says how it was built.

### 1.2 The `tune` config line, and D93

A `tune` line in an `.rxt` `config`/`target` block takes the identical
vocabulary — both numeric and alias — per D93's own framing that a config
block's directives are the format's named axes.

**THE PRECEDENCE QUESTION IS A RULING AND §9 CARRIES IT. This lane's
recommendation is the GENERAL D93 RULE UNCHANGED — the file wins — plus a
conflict diagnostic.** The reasoning, with the case against stated first
because it is the stronger-feeling one:

**The case for a CLI-wins exception** is the `--engine` precedent, ruled
2026-09-15 and now in `docs/spec/cli.md`: an explicit non-default CLI
`--engine=` beats a target's `engine` row, non-fatally, with both sources
and values named on stderr. Frank's operative principle there was that
*silence is not acceptable*. And `tune` feels more like ambient user
preference than `engine` does: it is `-Os`, and `-Os` is a command-line
thing — "my target device is small" is a fact about the build environment,
not about the artifact's identity.

**The case for file-wins, which this lane finds stronger**, in three parts:

1. **D93's first leg applies and its second does not, and the difference
   cuts toward the file.** D93 rests on two supports: a target is the
   artifact's DEFINITION ("you wouldn't change a C function name via cli
   options"), and letting an ambient flag reshape a target breaks H11's
   free identity control. The second support is VACUOUS for `tune`,
   because `tune` is answer-preserving by its own acceptance criterion
   (§6), so H11's control survives either precedence. That leaves the
   definition argument alone — and it is the one that says the file wins.
2. **`--engine`'s exception had a forcing reason that `tune` lacks.**
   `--engine` is a comparability facility: a caller types `--engine=vm`
   precisely to compare two builds of one pattern, and silently getting
   the file's engine defeats the purpose of the invocation. It can also
   make a pattern REFUSE (`--engine=dfa` on a captures-default pattern).
   `tune` can do neither. An exception needs a reason, and copying the
   shape of the last exception is not one.
3. **A second exception in a month turns the rule into a list.** D93's
   own revisit-when already names the expected shape of the answer: *"the
   likely shape then is an explicit loud override flag, never a silent
   precedence flip."* If the size-constrained-builder scenario is real,
   the answer is a spelling that says so, not a reordering.

**So: the file wins, and a conflict is REPORTED** — non-fatal, on stderr,
naming both sources and both values, in `--engine`'s own wording shape:

```
pcrec: FILE:LINE: target 'PREFIX': CLI --tune=min-size and this file's
`tune speed` disagree; using the file's value (--tune is not the
--engine exception; pass --force-tune to override)
```

**And one defect this axis should decline to inherit.** The `--engine`
exception's spec text records an accepted residual: `PCREC_ENGINE_AUTO` is
both the field's zero-default and `--engine=auto`'s own value, so an
explicitly-typed `auto` is indistinguishable from no flag, and "no
tracking machinery exists to tell the two apart." A NEW axis gets to not
have that problem. `tune`'s default is `0`/`balanced`, which is exactly the
same zero-default collision — so the option's storage carries an explicit
**`PCREC_TUNE_SET`** bit in the `pcrec_options.flags` word beside the
`int8_t tune` value (D43.2's one-representation rule: booleans are bits in
the flags word). It costs one bit and makes "the caller explicitly asked
for balanced" expressible on the day anyone needs it. If Frank rules
CLI-wins after all, this bit is what makes that rule statable without the
`auto` ambiguity.

---

## 2. What the dial is FOR, stated once

A dial position is a claim about the CALLER's preference, not about the
pattern. It is not a per-pattern predicate and it must not become one: the
places where pcrec should decide per pattern (which engine, which rung,
which K) already have their own mechanisms, and a dial that second-guessed
them would be a parallel mechanism for a general fact (memory
`pcrec-general-mechanisms-not-special-cases`).

Concretely, the dial sets the PARAMETERS that existing per-pattern
mechanisms then spend. `[ART-SIZE]`'s ladder still chooses K per pattern;
the dial moves its materiality bar. The sectioning DP still chooses a class
matcher per class; the dial moves λ. This is why §3's table has fewer rows
than the inventory has switches, and why that is a feature.

---

## 3. THE POLICY TABLE

### 3.1 The allowlist, made MECHANICAL

STEP 0's §6 ruled that the policy table is an allowlist: **the dial may
never set a switch that has no measured rate.** STEP 0's own draft table
then violated it, naming rung `shared` in two cells while the same document
said the shared rung's run time was unmeasured
(`opt_dial_inventory.md` §3.5(a)). The rule was in one section and the
table in another, and nothing checked one against the other.

So the rule is restated as a property of HOW the table is written, not as
something a reader applies afterwards:

> **Every non-default cell in §3.3's table carries, in the cell itself, the
> citation of the measurement that justifies it. A cell with no citation is
> an em-dash, and an em-dash means the dial does not touch that axis at
> that position.** A row with em-dashes in every column is a row the dial
> never touches at all, and it is listed anyway, because "we considered it
> and the number is missing" and "we forgot it" must not look the same.

That makes an allowlist violation a visibly empty citation rather than a
cross-reference a reviewer has to perform, and §6's check plan makes it
mechanical a second time (a structural check that every set cell's stamp
has a citation in the spec).

**The eligibility gates, in order.** An axis reaches the table only if:

- **Gate 1 — ANSWER IDENTITY, quantified over the values the dial can
  set.** `-fno-startpos-guard` fails this outright: its two arms disagree
  about answers on purpose (`opt_dial_inventory.md` §2.25), so no
  measurement can ever admit it. This gate is checked FIRST because it is
  the only one that cannot be discharged by measuring harder.
- **Gate 2 — the REFUSAL SET does not move**, which is gate 1 in its weaker
  form: a pattern whose answer becomes "refused" is not answer-identical.
  `-fno-altcls-merge`'s deny arm moves it (K45); the axis is therefore
  admissible only with that arm unreachable, which §3.3 gives it.
- **Gate 3 — a MEASURED two-axis rate exists**, on a stated population.
- **Gate 4 — the time cost's SIGN is stable across workloads.**
  `-fno-splice-calls` and `-fno-prefilter-collapse` fail this
  (`opt_dial_inventory.md` §4): each is faster for some subjects and slower
  for others, and "I want speed more than bytes" does not select between
  them. Note the contrast with `-fno-tiered-entry`, whose MAGNITUDE varies
  with the workload while its sign does not — sign-stable and
  magnitude-regime-dependent is dial-holdable, sign-reversing is not.
- **Gate 5 — the time cost's RANGE is not violent.** `--engine` passes
  every other gate and fails this one: up to 173,580× on the fail path.
  A dial position that can turn a 0.2 µs answer into a 35 ms one is not a
  dial position at any size saving.

### 3.2 THE THRESHOLD RULE, in ONE unit, with the conversions made explicit

Frank's rule-shape (2026-09-06): *a switch whose measured trade is
"performance penalty under x% AND size savings over y%" becomes a tier-one
size-notch option; the extreme size notch takes "savings above y% AND
penalty under some LARGER bound".* So the rule has three parameters — one
savings floor `y`, and two penalty bounds `x₁ < x₂` — and the positions
NEST: everything `−1` denies, `−2` denies too. The nesting is what makes
the surface an ordinal rather than five unrelated profiles, and it is worth
stating as a required property because it is checkable (§6).

**THE UNIT IS THE MULTIPLICATIVE SLOWDOWN OF END-TO-END MATCH TIME**, on
the population the switch reaches. Penalties are written as factors
(`1.794×`), savings as a fraction of the artifact's comment-excluded
emitted bytes, median over the switch's own movers.

**A row whose ledger measured a COMPONENT converts exactly, with one
unknown.** If a component is a fraction `φ` of match time and denying the
switch multiplies that component by `m`, total time multiplies by
`1 + φ·(m − 1)`. Two rows need this:

| row | component | measured `m` | its `φ` |
|---|---|---:|---|
| `-fno-tiered-entry` | per-call entry path | 5.06× (233.8 ns → 46.2 ns/call) | `φ_entry` — **UNMEASURED** |
| λ (the class kit) | class-membership probing | in probe ops, not time | `φ_cls` — **UNMEASURED** |

**`φ = (φ_entry, φ_cls)` is the single missing measurement this whole
design turns on**, and it is one measurement rather than two problems: both
components are "what share of a matcher's run time is spent in X", both are
subject-dependent, and both are answerable by the same instrument. §9 item
Q1 names it. Until it exists, the affected cells are stated CONDITIONALLY —
which is more useful than a guess, because a conditional cell tells the
measurement what answer would change it.

**PROPOSED VALUES — FOR FRANK'S RULING, none of these is measured:**

| parameter | proposed | what it says |
|---|---:|---|
| `y` | **5%** of the artifact | a size saving under 5% is not worth a dial position |
| `x₁` | **1.10×** | the first size notch accepts at most a 10% slowdown |
| `x₂` | **2.00×** | the extreme size notch accepts at most a doubling |
| `z_mid` | **1.20×** size | a speed optimization may cost at most 20% of the artifact to sit at the MIDDLE |
| `t_mid` | **1.02×** time | a size optimization may cost at most 2% of match time to sit at the MIDDLE |
| `s` | **1.10×** | a speed notch adopts nothing worth less than 10% |
| `z₁`, `z₂` | **2.0×**, **4.0×** size | the speed notches' size budgets |

**The middle's pair is `(t_mid, z_mid)` and the asymmetry Frank named is
the ratio between them: 2% against 20%, a factor of ten.** A size
optimization pays a ten-times stricter performance bar at the middle than a
speed optimization pays a size bar. The factor of ten is this lane's
proposal and is the most arbitrary number on this page; what is NOT
arbitrary is its direction, which Frank ruled.

**THE MIDDLE IS PINNED BY RULING AND THE WINDOWS ARE A CONSISTENCY TEST ON
IT, NOT A GENERATOR.** This matters and is easy to get backwards. Frank
ruled KEEP THE DEFAULTS (2026-09-04), so the `0` column IS today's
defaults, byte for byte, whatever `t_mid` and `z_mid` come out as. Running
the windows over today's shipped defaults as a check gives:

| default-ON speed optimization | its size cost | ≤ `z_mid` = 1.20? |
|---|---:|---|
| `-fno-offset-skip` (skip ON) | +1.30% | ✓ |
| `-fno-scan-edge` (edges ON) | +364…612 B | ✓ |
| `-fno-tiered-entry` (tier ON) | +7.48% | ✓ |
| `-fno-anchored-dfa` (machine ON) | +15.32% median, +39.60% worst | ✓ on the median, ✗ on the tail |
| `-fno-premul-table` (premul ON) | **+29…33%** | **✗** |
| `--vm-entry-shape` term at 4,096 | ≈0 by the term's own contract | ✓ |

**Exactly one shipped default clearly fails, and it fails by a lot.**
`-fno-premul-table` costs about 30% of a DFA-scan-bearing artifact's bytes
for 1.794×, which is not "near-free on the axis it spends" under any
reading. Two resolutions, and §9 Q2 asks Frank which:

- **(i) `z_mid` = 1.35, calibrated so today's defaults all pass.** The
  window becomes DESCRIPTIVE of revealed preference rather than
  prescriptive — which is a perfectly good thing for it to be, because its
  real job is admitting NEW optimizations, and for that job "what have we
  already accepted" is the right reference. **This lane recommends (i).**
- **(ii) `z_mid` = 1.20, and `-fno-premul-table`'s default is recorded as
  one notch mis-set**, to be revisited on its own merits independently of
  the dial.

Either way the `0` column does not move, because the keep-the-defaults
ruling is not conditional on the windows agreeing with it. And the
general observation is worth stating plainly: **pcrec's shipped defaults
are already speed-leaning** — which is not an accident but the project's
stated positioning — so the middle sits nearer notch `+1` than a
symmetric reading of "balanced" would suggest, and the speed side of the
table is consequently THINNER than the size side. §3.4 is where that shows.

### 3.3 THE TABLE

Twenty-three axes, all of them listed, plus λ. **A cell is either a value
with its citation, or an em-dash meaning the dial does not touch this axis
here.** `†` marks a cell whose evaluation depends on an unmeasured `φ`
(§3.2). Every value in this table is **PROPOSED FOR FRANK'S RULING.**

| axis | −2 `min-size` | −1 `size` | 0 `balanced` | +1 `speed` | +2 `max-speed` | why, with citation |
|---|---|---|---|---|---|---|
| **λ** (class kit) | `0` | `12` | **`16`** | `64` | `256` | §4; `cls_tree_study.md` §5.2's frontier |
| `[ART-SIZE]` ladder — bar | `0.95` | `0.85` | **`0.75`** | `0.75` | `0.70` | `artifact_size_term.md`; the K curve |
| `[ART-SIZE]` ladder — threshold | `40,000` | `80,000` | **`120,000`** | `120,000` | `160,000` | same; `limits.def` |
| `-fno-premul-table` | **deny** | — | **allow** | allow | allow | −22…25% bytes at 1.794×; ≤ `x₂`, > `x₁` (`artifact_size_census.md` item 2; `premultiplied_dfa_table.md` §13) |
| `-fno-anchored-dfa` | **deny** | — | **allow** | allow | allow | −15.32% on 43.39% reach at ≈1.99×; ≤ `x₂` **by 0.5%** (`optdial_size_sweep.md` §2.15; `opt2_anchored_match_measurement.md`) |
| `-fno-tiered-entry` | **deny** `†` | — | **allow** | allow | allow | −7.48% at 5.06× of ENTRY; denied iff `φ_entry ≤ 0.246` (`optdial_size_sweep.md` §2.12; `two_tier_entry.md` §1) |
| `--vm-entry-shape` term | — | — | **4,096** | `8,192` | `13,312` | §3.4; the raise's 0.061-0.067 B per ns/call (plan row `[OPT-DIAL]`, ccd2's ladder) |
| `--unroll=K` | — | — | — | — | — | **set BY the ladder rows above, never directly** — §3.5 |
| `-fno-offset-skip` | — | — | **allow** | — | — | −1.30% median, whole distribution inside a 2% band: **fails `y`** (`optdial_size_sweep.md` §2.14) |
| `-fno-scan-edge` | — | — | **allow** | — | — | fails `y` AND `x₂` (2.71-3.03×) — flat on both counts |
| `-fno-altcls-merge` | — | — | **allow** | — | — | median +2.40%: **wrong-signed**; deny arm also moves the refusal set (gate 2) |
| `-fno-altcls-factor` | — | — | **allow** | — | — | median +0.56%: wrong-signed |
| `--engine` | — | — | **auto** | — | — | **gate 5** — up to 173,580× on the fail path |
| `-fno-possessify` | — | — | — | — | — | gate 3: size measured, TIME UNMEASURED |
| `-fno-revdet` | — | — | — | — | — | gate 3: size measured (and a wash), TIME UNMEASURED |
| `-fno-prefilter` | — | — | — | — | — | gate 3: measured only through an engine-changing proxy |
| `-fno-atomic-discharge` | — | — | — | — | — | gate 3; the axis it moves is engine selection |
| `-fno-splice-calls` | — | — | — | — | — | **gate 4** — sign reverses with the subject population |
| `-fno-prefilter-collapse` | — | — | — | — | — | **gate 4** — same |
| `-fno-counter` | — | — | — | — | — | a correctness-shaped floor, not a rung |
| `-fno-length-prune` | — | — | — | — | — | trades nothing: denial is byte-identical |
| `-fno-cls-fold` | — | — | — | — | — | **off by RULING** (Frank 2026-09-11) — absorbed into λ, §4.4 |
| `-fno-startpos-guard` | — | — | — | — | — | **gate 1** — the two arms disagree about answers |
| `-fno-size-term` | — | — | — | — | — | not a rung; it is the MECHANISM the two ladder rows parameterise |
| emitted-size caps | — | — | — | — | — | raise-only refusal boundaries; a dial that lowered one would manufacture refusals |

**Six axes move. Seventeen do not, and the table says which of five
distinct reasons applies to each** — which is the difference between an
allowlist and a list of things nobody got round to.

**Two cells deserve to be read twice.**

**`-fno-anchored-dfa` at `−2` qualifies by a margin of half a percent.**
Its penalty is 1.99× against `x₂` = 2.00×. It is simultaneously the largest
legitimate size lever the dial has (10.64% of all the bytes pcrec emits
over its own corpus) and the cell most sensitive to a threshold nobody has
ruled. §3.6 quantifies that.

**And `-fno-anchored-dfa` at `−2` is safe against gate 2 only because
`[K53-SELRETRY]` exists.** K53 established that the optional anchored
machine's bytes count toward `PCREC_MAX_EMIT_BYTES`, so its presence can
REFUSE a pattern that compiles without it. That would make denying it a
refusal-set move in the favourable direction — and gate 2 does not care
about the direction, since a pattern that refuses at `0` and answers at
`−2` is not answer-identical either. What closes it is that
`[K53-SELRETRY]`'s drop ladder ALREADY drops the machine on a size-cap
refusal, so the refusal set at `0` is the same as at `−2` today.
**This row's admissibility is a DEPENDENCY on that ladder, not a property
of the row**, and if the ladder is ever removed or narrowed this cell must
be re-derived. It is recorded here because a dependency nobody wrote down
is one that gets removed.

### 3.4 The `--vm-entry-shape` row is the TERM, and the size side is empty

STEP 0 made this the dial's flagship row. It is the row that changed most
under scrutiny, and `opt_dial_inventory.md` §2.21's REVISION 2 block has
the full re-read. Three consequences land here:

1. **The dial names the TERM (`VM_INLINE_CHAIN_MAX_BYTES`), never a rung.**
   Rung `shared` has no measured run time, so the allowlist forbids naming
   it; rung `forward`'s run time is established STRUCTURALLY (no entry
   frame, no canary, no out-of-line chain symbol — ccd2 §3.4) and not
   measured. The term is the object with a measured rate on both sides.
2. **The size side is empty and the reason is the term's own contract.**
   Below 4,096 bytes of program the INLINE/SHARED `.text` ratio is already
   1.01× — the default term exists precisely to take forwarding only where
   it costs nothing. There is nothing for a size notch to recover.
   **Frank's 2026-09-04 keep-the-defaults ruling and the DEFAULT-MIDDLE
   PRINCIPLE are the same fact on this row**, one derived from the other,
   which is why the plan row calls that ruling the principle's existing
   instance.
3. **The speed side has the better-measured rate of the two.** The plan
   row's own figures: the cells just above the term (program 5,183 / 5,985
   / 6,954) cost **0.061-0.067 bytes per ns/call saved, five times better
   than the next cell up**. `+1` = 8,192 covers them; `+2` = 13,312 is the
   top of the measured cheap band, and above it the rate degrades by that
   same 5×. Frank already ruled this raise belongs to the speed profile.

### 3.5 `--unroll=K` is set by the ladder, not by the dial

STEP 0 gave `--unroll=K`, the size-term bar and the caps a row each, while
its own note under the table said the three "address emitted size through
the same `[ART-SIZE]` mechanism" and "a policy table has to say they move
together." The table's shape contradicted its own note.

**They are folded.** The dial sets the ladder's two parameters — the
materiality bar and the threshold above which the ladder runs at all — and
`[ART-SIZE]`'s existing per-pattern mechanism derives K. Three reasons,
and the third is the one that decides it:

1. A dial cannot set K inconsistently with the bar if it does not set K.
2. It is per-pattern where a direct K row would be global.
3. **A direct K row cannot be evaluated against the threshold rule at all**,
   because K=1's penalty has two different values on two populations: no
   measured throughput cost on NESTED bounded-repeat shapes (where it is
   75-79% smaller) and a 1-3% noise effect on single-level large-count ones,
   with a byte curve that is NON-MONOTONE in K
   (2,449/2,469/1,334/1,635/498/262 nodes at K=8/6/4/3/2/1). A global row
   would have to pick one population and be wrong on the other. The ladder
   already decides per pattern, on bytes it measures rather than models.

**One allowlist caveat, stated rather than buried:** the bar's rate is
measured at its ENDS (the K ladder's byte curve; "throughput exhausted by
K≈16") and not per bar VALUE. The intermediate bar settings (0.85, 0.95)
are therefore interpolations, not measurements. They are admissible because
the mechanism they feed re-measures bytes per pattern and cannot select a K
that does not pay — but a reviewer is entitled to call this the weakest
citation in §3.3, and §9 Q4 offers Frank the narrower alternative (move
only the threshold, leave the bar at 0.75 everywhere).

### 3.6 SENSITIVITY — which cells flip if x or y moves by a factor of two

The point of this section is that Frank's ruling should be informed by
which numbers matter. Most of them do not.

| parameter moved | cells that flip | consequence |
|---|---|---|
| `y` 5% → **2.5%** | **none** | `-fno-offset-skip` (1.30%) still fails; `-fno-scan-edge` would enter on savings and still fails `x₂` |
| `y` 5% → **10%** | **one**: `-fno-tiered-entry` leaves the table | the 7.48% row is the only one in the 5-10% band |
| `y` → **1.3%** | one: `-fno-offset-skip` enters — **but only if `x₂` ≥ 2.00 too** | needs BOTH thresholds moved; a genuine knife edge on two axes at once |
| `x₁` 1.10 → **0.55**/**2.20** | down: none. up: **two** — premul and anchored-dfa move from `−2` to `−1` | at `x₁` ≥ 1.80 the first notch stops being empty; below 1.794 nothing changes at all |
| `x₂` 2.00 → **4.00** | **none** | a PLATEAU: the next penalty up is `-fno-scan-edge`'s 2.71-3.03×, which fails `y` anyway |
| `x₂` 2.00 → **1.00** | **two** — premul and anchored-dfa both leave | the min-size column collapses to λ and the ladder only |
| `z_mid` 1.20 → 1.35 | none in the table; resolves §3.2's one middle inconsistency | see §9 Q2 |

**Three readings a ruling should take from this.**

**(a) `x₂` has a plateau above and a cliff below.** Anywhere in [2.00, 2.70)
gives the identical table. Below 1.99 the dial loses `-fno-anchored-dfa`,
its largest legitimate lever. So the ruling's real question is not "what is
x₂" but "is a doubling of match time acceptable at the extreme size notch",
and if the answer is yes at all, the exact value barely matters.

**(b) `x₁` is nearly inert, and §0's headline is why.** Among size-SAVING
axes the measured penalties jump from 1.00× to 1.794×. No value of `x₁`
below 1.794 changes anything; the first value that does is 1.80, and it
makes notch `−1` identical to notch `−2` on the discrete rows. **There is
no `x₁` that makes `−1` a distinct, non-empty, non-extreme column on
today's measurements.** Two honest responses, and §9 Q3 asks Frank which:
accept that `−1` differs from the middle only on λ and the ladder (this
lane's recommendation — it is true, it is stated, and the population will
fill in as the owed throughput sweeps land), or re-define `−1` by a RATE
test rather than a threshold test, which would place premul (22-25% per
0.794 excess = 28% per unit) above anchored-dfa (15.32% per 0.99 = 15%) and
give `−1` a single member.

**(c) `y` is the only parameter whose doubling removes a row**, and the row
is `-fno-tiered-entry`, which is already the conditional one. If `φ_entry`
turns out large, that cell goes anyway.

---

## 4. λ — THE MAPPING, AND WHY IT IS THE HARD PART

`docs/dev/cls_tree_study.md` §5.1 chooses a class matcher's sectioning by
minimising, over contiguous partitions,

```
best[j] = min over i of  best[i] + rodata(i..j) + text(i..j) + λ·ops(i..j)
```

λ prices **one probe operation against one byte**. Frank has ruled that
`[CLS-TREE]`'s kit is selected by this DP priced by λ, and the study's own
words are that λ **is** `[OPT-DIAL]`'s dial "arrived at from the algorithm
rather than fitted to it". This section is the seam: the `[CLS-TREE]`
design note, which follows this one, consumes it.

### 4.1 The proposed mapping

| position | λ | `\p{L}` at that λ: total bytes / probe ops |
|---|---:|---|
| −2 `min-size` | **0** | 4,318 / 206 |
| −1 `size` | **12** | (between the study's 4 and 16 rows; see §4.3) |
| 0 `balanced` | **16** | 4,359 / 108 |
| +1 `speed` | **64** | 5,359 / 78 |
| +2 `max-speed` | **256** | 5,850 / 72 |
| — never — | `∞` | 24,996 / 66 |

Four of the five are the study's own swept frontier points, which is
deliberate: they are the λ values at which a matcher has actually been
BUILT and verified against a reference on all 1,114,112 code points. A λ
the study never swept is a λ nobody has an artifact for.

### 4.2 The middle is DERIVED, not inherited from the study's naming

The study calls λ=16 its "mid" policy. That is a name, and a name is not a
derivation. The middle is derived instead from the DEFAULT-MIDDLE
PRINCIPLE plus the measured frontier, and it lands on the same value —
which is worth saying explicitly, because two routes agreeing is evidence
and a name is not.

Against the λ=0 baseline, on `\p{L}`:

| λ | bytes vs λ=0 | probe ops vs λ=0 | inside `z_mid` = 1.20? |
|---:|---:|---:|---|
| 4 | **−2.8%** | −15.0% | ✓ |
| 16 | **+0.95%** | **−47.6%** | ✓ |
| 64 | +24.1% | −62.1% | ✗ |
| 256 | +35.5% | −65.0% | ✗ |
| ∞ | +479% | −68.0% | ✗ |

**λ=16 buys nearly half the probe ops for under one percent of the bytes.**
That is the default-middle principle's own definition — "applies only
optimizations that are near-free on the axis they spend" — satisfied with
two orders of magnitude of headroom. λ=64 costs 24% of bytes and is
correctly not the middle. **So λ(0) = 16 is the LARGEST frontier point
inside the middle's size window**, which is a derivation, and it agrees
with the study's naming, which is a check.

**And λ is the first row in this whole design admitted UNDER the middle
principle prospectively rather than grandfathered past it** (§3.2: every
discrete row's middle cell is today's default by ruling, and one of them
fails the window). That is a small thing and it is the only place the
principle has done predictive work.

### 4.3 The extremes, and where the mapping is NOT clean

**`+2` = 256 and never ∞, and the reason is a measured cliff rather than
taste.** The realized marginal rate along the frontier — bytes paid per
probe op removed, between adjacent points — is:

| step | Δbytes | Δops | bytes per op |
|---|---:|---:|---:|
| 4 → 16 | +163 | −67 | **2.4** |
| 16 → 64 | +1,000 | −30 | **33.3** |
| 64 → 256 | +491 | −6 | **81.8** |
| **256 → ∞** | **+19,146** | **−6** | **3,191** |

The last step is **39× worse than the one before it for the identical six
operations.** The study's §5.3 item 4 says the dial's speed notches should
stop before it; this is that statement as an exchange rate. `+2` is the
last frontier point before the cliff.

**`−2` = 0 is proposed WITH a named residual the study itself flags.** On
`\p{L}`, λ=0 (4,318 B / 206 ops) is DOMINATED on both axes by λ=4 (4,196 B
/ 175 ops) — smaller *and* fewer ops. A frontier point dominated on both
axes is a modelling error, and the study says so: its byte term is accurate
to about 3%, and at the extreme size end 3% is enough for two adjacent
policies to invert. Population-wide λ=0 is genuinely the smallest (812
sections against the middle's 1,168; `PAGE64` 24.0% and `RANGES` 20.7%,
both absent or near-absent elsewhere), so the inversion looks like a
one-set artifact. **But this lane will not resolve a modelling question by
asserting it**: §9 Q5 names the measurement — a real object-size sweep of
the frontier, replacing the model's `.text` estimate, on more than one set.
If the inversion survives that, `−2` becomes 4 and `−1` moves down with it.

**`−1` = 12 is the weakest number on this page and is marked as such.** It
is not a swept frontier point. It is chosen by the ops-cap argument of §4.4
below, which places it just under the middle — and that makes notch `−1`
nearly inert on this row too, exactly as it is on the discrete rows (§3.6
(b)). **The two halves of the dial agree that `−1` is nearly empty, and
they arrive there independently**, which is either a confirmation or the
same population showing through twice. This lane reports it as the former
with the caveat that it cannot distinguish them from one set.

### 4.4 CONSISTENCY — how the DP and the discrete table answer the same question

This is the section the brief calls the design's hardest original content,
so the structure is stated before the result.

**The test.** At position `p` the discrete table accepts a size-for-time
trade at some marginal rate `σ(p)` — fraction of bytes paid per unit of
relative slowdown — and the DP accepts a size-for-ops trade at λ(p) bytes
per op. Putting the DP in the same relative units: for a matcher of `B`
bytes and `P` ops, λ's implied relative rate is `ρ = λ·P/B`. The two are
consistent iff `ρ(p) / σ(p)` is **the same constant across positions** —
and that constant is *time per probe op*, i.e. `φ_cls` again. **So
consistency is a RATIO TEST that can be checked TODAY without knowing the
constant.** That is the useful part: the calibration is unmeasured, the
COHERENCE is not.

**The result, and it is a negative one at the extremes.** The discrete
rule's marginal accepted rate at a size notch is `y/(x−1)`:
`σ(−1) = 0.05/0.10 = 0.50` and `σ(−2) = 0.05/1.00 = 0.05` — decreasing
toward min-size, correctly (a min-size caller will spend less size to buy
time). λ's ρ on `\p{L}`: `ρ(λ=4) = 4·175/4,196 = 0.167`, and
**`ρ(λ=0) = 0` exactly.** The ratios are 0.334 at `−1` and 0/0.05 = **0**
at `−2`. Not constant. The mapping is NOT ratio-consistent at the extreme.

**The cause is structural and worth more than the discrepancy.** The
discrete rule's `x₂` is a HARD CAP — a safety bound that refuses a
catastrophic switch regardless of how many bytes it saves. λ=0 is a pure
objective with no safety term at all: at λ=0 the DP will accept ANY number
of probe operations to save one byte. **The two mechanisms have different
shapes at the boundary, and no choice of λ fixes it, because the problem is
that λ alone cannot express a cap.**

**The repair: give the DP the same shape, by adding the cap the discrete
rule already has.** The min-size position is not "λ=0"; it is

```
minimise rodata + text   subject to   ops ≤ κ · ops(middle)
```

and **κ is `x₂`, the same parameter.** Checked on the study's own worst
case: `\p{L}` at λ=0 is 206 ops against the middle's 108 — **1.91×, just
inside a 2.00× cap**. So the proposed `−2` survives its own cap, with the
same order of margin as `-fno-anchored-dfa`'s 1.99-against-2.00 in §3.3.

Two independent rows landing within 5% of the same bound is either a
pleasing coincidence or a sign that 2.00 is doing more work than a
proposed number should. **This lane flags it as the latter and declines to
treat the agreement as corroboration**: one is a measured throughput ratio
and the other is a DP output on a single set, and they have no mechanism in
common. §9 Q3 puts `x₂` in front of Frank with both dependencies named.

**And the cap is what fixes `−1` too.** With `x₁` = 1.10 the constraint is
`ops ≤ 118.8` against the middle's 108 — and the frontier's next point up
(λ=4) is 175 ops, far outside. So λ(−1) must sit just below 16, which is
where the proposed 12 comes from and why §4.3 calls it weak. It is a
derivation from a cap, not a measurement, and it inherits `x₁`'s
arbitrariness exactly.

**One property of λ the implementation must not lose.** λ's absolute
numbers are meaningful only against the study's own cost model, whose
`.text` coefficients were calibrated two ways that disagreed (OLS 117
bytes/section for `RANGES` against the direct route's 52). **If the cost
model is ever recalibrated, all five λ values must be re-derived.** The
stable surface is the ORDINAL; λ is an implementation detail behind it.
This is the argument for §5's stamp recording the position and never λ.

### 4.5 What λ absorbs

`-fno-cls-fold` is the worked example and it is already ruled: Frank,
2026-09-11, subsumed it into the `[CLS-TREE]` design note, with no
standalone dial placement, because its end state is the `m = 0x20` one-cube
instance of the kit's general cube form. The study measures why the general
form is the right object — the cube test reaches **8 of the 41 byte classes
in this tree's corpus where today's fold classifier sees only 4**
(`cls_tree_study.md` §4.3).

The structural point for this design: **λ ABSORBS axes rather than sitting
beside them.** Any future class-representation switch arrives as a kit
member priced by λ, not as a new policy row. So the dial's row count does
not grow with the tree the way the inventory's switch count does — which is
the general-mechanisms rule showing up as table structure rather than as a
principle.

---

## 5. THE STAMP, the `rx_info` question, and the `abi` consequence

### 5.1 `<PREFIX>_TUNE`, a closed token, unconditional

```c
#define RX_TUNE "balanced"
```

Tokens: `"min-size"`, `"size"`, `"balanced"`, `"speed"`, `"max-speed"` —
the alias spelling, never the number. A closed token set is what D82 wants
for a selection and what `RX_ENGINE`/`RX_DFA_SCAN`/`RX_ENGINE_SEL` already
are: a consumer can bucket on it, a typo is an error rather than a silent
neighbour, and the set extends without renumbering. **The number is
deliberately not the stamp's value**, because a number invites arithmetic
on it and §4.4 has just established that the ordinal is the stable surface
while the values behind it are not.

**UNCONDITIONAL — emitted on every artifact, including at `balanced`.**
The tempting alternative (stamp only when non-default, so today's artifacts
stay byte-identical and there is no `abi` event) is the anti-pattern
`ccdiff1` recorded when it ruled `RX_DFA_UNIFORM_FOLDS` ships: *this tree
has twice had to remove a check reading a fact off a macro's absence.*
Absence would mean "built at balanced" and "built by a pcrec too old to
have a dial" identically.

### 5.2 The `rx_info` mirror: RECOMMEND NO

`rx_info` is the run-time reflection surface. Nothing at run time behaves
differently because of the dial — that is what answer identity means — so a
mirror would be a field no consumer can act on. The precedent is
`RX_DFA_TABLE`, which has no mirror on exactly this reasoning (D77: build
it when a measured consumer asks), against `search_form`, which got one
because Frank approved a specific consumer. **No consumer has been named
for `tune`.** A build system wanting to verify how an artifact was built
reads the compile-time macro, which is where a compile-time fact belongs.

**Nor does `tune` belong in `rx_info.flags`.** `docs/spec/tuning.md` §2.23
states the existing mask rule while explaining why `-fno-startpos-guard` is
the one exception to it: every other member changes an emitted SHAPE for
one language, so stamping it would make two identically-behaving artifacts
differ in their reflection surface over a knob with no observable effect.
`tune` is precisely that case, and the rule already covers it. Recording
this explicitly matters because the `PCREC_TUNE_SET` bit of §1.2 lives in
`pcrec_options.flags`, which is a different word from `rx_info.flags`, and
an implementer skimming will conflate them.

### 5.3 `abi`: this IS an event, and the site list is found BY GREP

A new unconditional `#define` in every emitted artifact is emitted
scaffolding, so D76/D94's ritual applies in the same change: **`abi` 25 →
26**, with the identity gate's (B) whole-file pin re-pinned, and the site
list found by grepping the tree for the CURRENT number's readers — never a
hand-enumerated four (D94, whose own 2026-09-01 instance missed a fifth
reader in `match_api.md`).

**And the grep must be widened, per `battriage_report.md`'s 2026-09-15
finding.** A grep for the literal old abi number finds every reader that
CITES it and structurally cannot find a reader whose content merely
DEPENDS on the scaffolding — `tests/codegen/run_cpset_structure.sh`'s CHECK
3 manifest is the recorded instance: its `EMITTED_BYTES` rows name no abi
digit at all and their VALUES move anyway. So the ritual's site list for
this change is two searches, not one:

1. every reader of the number `25` (the `.abi` stamp, test expectations,
   every spec sentence, the gate's (B) pin);
2. every pinned BYTE COUNT or manifest of emitted text, whose values move
   because the scaffolding grew by one line.

`make test-codegen` before delivering, per the situation index.

**One sizing note for the implementation lane.** The added line is ~30
bytes of source per artifact (`#define RX_TUNE "balanced"` plus its
newline, and one byte more or fewer per token) against a corpus baseline of
115,198,573 bytes — about 0.00009%. It is far below the artifact-size
tripwire's resolution and it is NOT below the byte-exact manifests', which
is the whole point of (2).

---

## 6. ACCEPTANCE

### 6.1 The bar: answer identity across all five positions

`[OPT-DIAL]`'s charter makes this the acceptance, and the mechanism already
exists: `make test-axes` (`tests/axes/run_axes.sh`) sweeps every
optimization-axis deny/force flag plus the engine axis over the whole
corpus and requires answer-identity with the default. **The dial is a fifth
kind of axis on that same sweep** — five values of one option, each
answer-identical to `0` over the corpus — and it is testable the day it
exists, which is the charter's own claim and is true.

Scope: 5 values × the 3,478-row corpus. The axes sweep's measured cost is
~175 s per axis (`tt12_step0_profile.md`), bottlenecked on one 3,065-case
`.rxt` file rather than on a `PROCS` cap, so four new non-default axes is
roughly **12 minutes** added to `make test-axes`. It does not ride
`make test`.

**Where it runs: the NIGHTLY CHECKPOINT BATTERY, not per merge** (D102,
2026-09-16). `make test-axes` is a battery stage, individual merges take
`make test` + targeted suites + `make strict`. An emitter-touching change
like this one MAY demand a solo battery at the manager's discretion under
D102's risk-tier escape hatch, and this lane recommends it does: the
implementation carries an `abi` event, and D102 names emitter-touching
merges as the category that can.

### 6.2 The K45-class interaction: a refusal-set move IS an identity break

`tests/axes/run_axes.sh` already carries a `REFUSAL_PATTERN` table, because
some deny flags legitimately make some patterns refuse — `-fno-altcls-merge`
is the documented instance (`tests/size/size_term.rxt:32`'s nested-repeat
tower, above the 131,072-node emitted cap without the merge). That
mechanism is right for an AXIS SWEEP, whose job is to exercise a flag in
both arms including arms nobody ships.

**It is wrong for the dial, and the rule is one sentence: NO DIAL POSITION
MAY SELECT A SWITCH VALUE THAT MOVES THE REFUSAL SET, in either direction.**
A pattern that compiles at `0` and refuses at `−2` has lost its answer. A
pattern that refuses at `0` and compiles at `−2` has gained one — and that
is equally a break, because "refused" is an answer a caller can observe and
depend on, and because a dial whose positions accept different LANGUAGES is
not a tuning knob.

Three consequences, all of them already visible in §3.3:

- `-fno-altcls-merge` gets a flat row. It was already flat on the
  measurement (wrong-signed); this makes it flat for a second, independent
  reason, which is the stronger position to be in.
- The emitted-size caps stay a boundary and never a row. Lowering a cap
  manufactures refusals by construction, which is exactly what raise-only
  exists to prevent.
- `-fno-anchored-dfa`'s `−2` cell is admissible **because of
  `[K53-SELRETRY]`'s drop ladder**, not in spite of K53 — §3.3's dependency
  note is the load-bearing half of that cell's argument.

**The check this needs, and it is not the axes sweep.** The axes sweep
compares ANSWERS on patterns that compile. A refusal-set move is precisely
the thing it routes around via `REFUSAL_PATTERN`. So the dial needs its own
arm: **the set of refusing patterns must be byte-identical across all five
positions**, compared as a SET of `file:line` keys and not as a count. A
count-only comparison passes when one pattern starts refusing and another
stops — and this design has two rows (`anchored-dfa`, the caps) whose
hazards run in OPPOSITE directions, so a count is the one shape of check
that both could slip through at once. The sweep's own `RXTDUMP` already
emits what this needs (`optdial_size_sweep.md` §0 used it for exactly this
cross-check, K35).

### 6.3 What the acceptance does NOT cover, named

- **It does not check that a position is FASTER or SMALLER.** Answer
  identity is the correctness bar; the performance claim is §3.3's
  citations, and those are per-switch measurements, not an end-to-end
  dial measurement. Nobody has measured an artifact built at `−2` against
  the same artifact at `0`. **That measurement is owed at implementation**
  and it is the one that would falsify the table: if `min-size` does not
  measurably shrink the corpus, the rates were composed wrongly even
  though each was cited correctly.
- **It does not check the λ row at all**, because λ has no implementation
  until `[CLS-TREE]` lands. Until then the λ column of §3.3 is a
  reservation, and the dial's first build has five positions of which the
  discrete rows distinguish three (`−2`, `0`, `+1`/`+2`). Shipping a
  five-position dial whose `−1` does nothing is honest only if the stamp
  says `size` and the spec says what `size` currently sets — §8's spec plan
  makes that an explicit per-position table rather than prose.

---

## 7. THE FOUR STANDING LENSES

Frank's 2026-09-04 evaluation lenses, one subsection each, answered rather
than gestured at.

### 7.1 Specific vs general

**The dial is the general form of a decision pcrec has been making one
switch at a time.** Every `-f` flag's default was chosen at its own landing
by whoever landed it, against whatever that lane cared about. The dial does
not add a mechanism; it makes an existing, distributed, undocumented policy
explicit and consistent.

The lens bites in one place and this design answers it there: **λ is the
general form and `-fno-cls-fold` is the special case**, and Frank has
already ruled the special case is absorbed rather than dialled (§4.5). The
measured argument is `cls_tree_study.md` §4.3's count — the general cube
test reaches 8 of 41 corpus byte classes where the shipped fold classifier
sees 4. A dial with a `cls-fold` row would have been the parallel mechanism
this lens exists to catch.

Where the design could still fail the lens: if a future switch is given a
policy row when it should have been absorbed into λ or into an existing
per-pattern mechanism. §2's statement ("the dial sets the parameters
existing mechanisms spend") is the standing test for that.

### 7.2 Core vs derived

**The dial is DERIVED, completely.** It introduces no new emitted
mechanism, no new analysis, no new IR, no new refusal. Every value it sets
is a value the CLI can already set by hand today; the dial is a naming of
groups of those values. This is the lens the design passes most cleanly,
and it is why the implementation is small relative to the design.

The one genuinely core-touching consequence is the `abi` event (§5.3), and
it is core-touching for a scaffolding reason (a new `#define` line) rather
than a semantic one.

**A derived mechanism's characteristic risk is DRIFT**, and this design has
one instance already recorded: the policy table lives in two documents in
STEP 0's shape, and `opt_dial_inventory.md` §3's revision moved it to one.

### 7.3 Applicable vs assumption-changing

**Answer identity is the assumption the dial must not change, and it is
promoted from a property to a GATE** (§3.1 gate 1, §6.2). The design's one
real discovery under this lens is that an axis exists TODAY which would
have quietly broken it: `-fno-startpos-guard`'s two arms disagree about
answers by design. It would have looked like an ordinary `-fno-` flag to a
table-filling exercise.

Two assumptions the dial deliberately does NOT change: the middle is
today's defaults byte for byte (Frank's ruling, and §3.2 keeps it even
where the middle's own windows disagree), and per-pattern decisions stay
per-pattern (§2).

One assumption it DOES change, and this is the honest entry: **`tuning.md`
§2's per-axis defaults stop being the whole story.** Today a reader learns
an axis's default from its own section. After the dial, the default is the
`balanced` column and the section is one of five values. §8's spec plan
puts the policy row IN each §2 entry for exactly this reason — the
alternative, a central table the per-axis sections do not mention, is how
two surfaces come to disagree.

### 7.4 Fits architecture vs refactor

**It fits.** The option parser gains one value flag; `pcrec_options` gains
an `int8_t` and a flags bit; one new table maps position to per-axis values
and is consulted once, before any pass runs; the emitter gains one
`#define`. Nothing is restructured.

The design deliberately declined the two shapes that WOULD have been
refactors: a per-pattern cost model that picks a position per artifact
(rejected in §2 — it duplicates mechanisms that already exist and would
need `φ` to work at all), and a general "objective function" threaded
through every pass (which is what λ is, correctly, for ONE pass, and which
has no business in the others).

**The one place it presses on the architecture** is §3.5's fold of
`--unroll=K` into the `[ART-SIZE]` ladder's parameters. That is not new
structure — the ladder and the bar both ship — but it does mean the dial's
`−2` position changes the ladder's behaviour on patterns below today's
120,000-byte threshold, which is a population the ladder has never run on.
The implementation lane should expect that to be where the surprises are,
and §9 Q4 offers Frank the narrower alternative.

---

## 8. SPEC PLAN — what moves in `docs/spec/`, at implementation

D80: a caller-observable change carries its spec hunk in the same change.
This section is the PLAN; no spec file is touched by this lane.

**`docs/spec/tuning.md` — the main body of the work.**

1. **§1 ("What a tuning flag is") gains the PROFILE concept**: that axes
   have a per-position default rather than a single default, that explicit
   per-switch flags beat the dial, and the allowlist rule in one sentence
   (the dial never sets an axis with no measured rate — which is why most
   §2 entries' policy rows read "not on the dial").
2. **A new §5, "The `--tune` dial"**: the five positions, both spellings,
   the full policy table (this note's §3.3 as the contract), the stamp's
   token set, and the D93 precedence rule as ruled. The policy table lives
   HERE in the spec — the design note is not the contract.
3. **Every §2 entry gains ONE policy line.** Twenty-three entries, and
   seventeen of them say "not on the dial" with which gate. This is
   deliberate volume: §7.3's lens says a central table the per-axis
   sections do not mention is how two surfaces drift apart.
4. **§2.10 (`--unroll=K`) and §2.16 (`-fno-size-term`) gain the fold**:
   the dial sets the bar and the threshold, K is derived per pattern.
5. **§2.21 (`--vm-entry-shape`) gains the term's per-position values** and
   the statement that the dial names the term and never a rung.
6. **§2.22 (`-fno-cls-fold`) and §2.23 (`-fno-startpos-guard`) gain their
   exclusion reasons** — a ruling and a gate respectively, and they are
   different kinds of "no", which the entry should say.
7. **§3/§3.1 (the stamp sections) gain `<PREFIX>_TUNE`.**
8. **§4 (`pcrec_options` mirror) gains `tune` and `PCREC_TUNE_SET`.**

**`docs/spec/cli.md`.** `--tune=N` in the flag table with both spellings
and the `=`-form requirement for negatives; the `tune` config-block
directive; and — in the file-wins section that currently carries
`--engine` as its ONE named exception — a sentence confirming `tune` is
NOT a second exception, with the conflict diagnostic's wording. That
sentence is worth its space: the section's structure invites a reader to
assume new axes join the exception list.

**`docs/spec/match_api.md`.** The `abi` 25 → 26 event and its row in the
abi history; §6's stamp inventory gains `<PREFIX>_TUNE`; the explicit
statement that there is NO `rx_info` mirror and why (§5.2), so the absence
is a recorded decision rather than a gap.

**`docs/spec/limits.md`.** `VM_INLINE_CHAIN_MAX_BYTES` and
`PCREC_SIZE_TERM_THRESHOLD` become dial-dependent; their entries state the
per-position values. The emitted-size caps' entries gain the sentence that
the dial never lowers them.

**`docs/spec/rxt_format.md`.** The `tune` config directive in the config
vocabulary, with its value grammar.

**`docs/guide/`** points at `tuning.md` §5 and does not restate the table.

---

## 9. THE FRANK QUEUE

Everything this note could not settle, with the recommendation and what
would change the answer. Q1 is the one that unblocks the most.

**Q1 — `φ`, the component-share measurement (blocks the most).** What
fraction of a matcher's run time is (a) per-call entry cost and (b)
class-membership probing, on the populations that matter? Not a ruling but
a lane: it is what converts `-fno-tiered-entry`'s 5.06× into a whole-match
number and what calibrates λ against the discrete rows in units rather than
by ordinal. **Recommendation: charter it before implementation.** It is
cheap (both components are isolable by the hand-twin method
`form_char_step0.md` and `ccdiff_step0_evidence/` already use) and every
other open number is downstream of it. Without it the `−2` column carries
one conditional cell and λ's calibration stays ordinal.

**Q2 — the threshold values `y`, `x₁`, `x₂`, `z_mid`, `t_mid`, `s`, `z₁`,
`z₂` (§3.2).** Proposed: 5%, 1.10×, 2.00×, 1.20× (or 1.35× — see below),
1.02×, 1.10×, 2.0×, 4.0×. The sensitivity table (§3.6) says most of them do
not matter: `x₂` has a plateau from 2.00 to 2.70 and a cliff below 1.99,
and `y`'s only live boundary is at 10%. **The substantive question is one
sentence: is a doubling of match time acceptable at the extreme size
notch?** If yes, the table is as printed; if no, the min-size column loses
both `-fno-premul-table` and `-fno-anchored-dfa` and collapses to λ plus
the ladder.

**Q2b — `z_mid` = 1.20 or 1.35 (§3.2).** At 1.20, exactly one shipped
default (`-fno-premul-table`, ~30% of bytes for 1.794×) fails the middle's
own window. **Recommendation: 1.35**, calibrated so today's defaults pass,
making the window descriptive of revealed preference — its predictive job
is admitting NEW optimizations, and for that job "what have we already
accepted" is the right reference. The alternative is to record premul's
default as one notch mis-set and revisit it on its own merits.

**Q3 — is a nearly-empty `−1` acceptable (§0, §3.6(b))?** On today's
measurements no value of `x₁` makes `−1` a distinct, non-empty,
non-extreme column on the discrete rows: the penalty distribution has a
hole between 1.00× and 1.794×. **Recommendation: accept it.** It is true,
it is stated, the λ and ladder rows still move there, and the population
fills in as the owed throughput sweeps land — which is Frank's own
2026-09-04 framing that "the dial is a theoretical at this point and will
look better with more options". The alternative is to define `−1` by a RATE
test rather than a threshold test, which gives it exactly one member
(`-fno-premul-table`, at 28% of bytes per unit of excess slowdown against
anchored-dfa's 15%).

**Q4 — the `[ART-SIZE]` ladder fold (§3.5).** The dial sets the
materiality bar and the threshold; K is derived per pattern. The bar's
intermediate values (0.85, 0.95) are interpolations rather than
measurements, and `−2`'s lowered threshold runs the ladder on a population
it has never run on. **Recommendation: take the fold, and the narrower
variant if the interpolation worries him** — move only the THRESHOLD
per position, leave the bar at 0.75 everywhere. That keeps every dialled
value measured at the cost of a smaller size lever.

**Q5 — λ's `−2` value, and the frontier inversion (§4.3).** λ=0 is
dominated on both axes by λ=4 on `\p{L}`, which the study names as a ~3%
byte-model artifact at the extreme size end. **Recommendation: keep `−2` =
0 provisionally and resolve it with a real object-size sweep of the
frontier over several sets** rather than the model's own `.text` estimate —
the study calibrated that estimate two ways that disagreed by better than
2× on two forms. If the inversion survives, `−2` becomes 4.

**Q6 — the D93 precedence ruling (§1.2).** Does an explicit CLI `--tune`
beat a target's `tune` row? **Recommendation: NO — the general D93 rule
stands, the file wins, with a loud non-fatal conflict diagnostic.** The
`--engine` exception had a forcing reason (`--engine` is a comparability
facility and can cause a refusal) that `tune` lacks, and D93's own
revisit-when names an explicit override FLAG as the right shape if the
scenario turns out to be real. Whichever way this goes, §1.2's
`PCREC_TUNE_SET` bit should land, so this axis does not inherit the
`--engine=auto`-is-indistinguishable-from-unset residual.

**Q7 — does the dial's landing demand a SOLO battery (§6.1)?** D102's
risk-tier escape hatch lets the manager demand one for an
emitter-touching merge. This carries an `abi` event plus four new
answer-identity axes. **Recommendation: yes, solo** — and this is the
manager's call rather than Frank's; it is listed here so the queue is
complete.

---

## 10. WHAT THIS NOTE DOES NOT SETTLE

Named, not hidden, in the house's style.

- **No end-to-end dial measurement exists** (§6.3). Every rate in §3.3 is a
  per-switch measurement from its own ledger; nobody has built one artifact
  at `−2` and at `0` and compared them. The composition of individually
  correct rates can still be wrong.
- **λ's row is a reservation until `[CLS-TREE]` lands.** The dial's first
  build has five positions of which the discrete rows distinguish three.
- **`φ` is unmeasured** (Q1), so one cell is conditional and λ's
  calibration is ordinal rather than exact.
- **λ's frontier numbers come from ONE set (`\p{L}`)** at the per-set
  resolution, with population-wide section shares as the only cross-check.
  §4.3's inversion and §4.4's 1.91× both rest on that single set.
- **The `−1` column's emptiness is measured on today's population**, which
  has two throughput sweeps owed against it
  (`opt_dial_inventory.md` §7.1 item 6). If `-fno-possessify` turns out
  cheap on time, it lands in exactly the gap §0 describes.
- **`-fno-scan-edge`'s size cost is never converted to a fraction.** It is
  cited absolutely (+364…612 B per edge-carrying machine) because the sweep
  did not cover it; the claim that it fails `y` is therefore an inference
  from artifact sizes rather than a measurement. It also fails `x₂`
  independently, so the row's flatness does not rest on it — but the cell
  is weaker than the others and should not be quoted as if it were not.
