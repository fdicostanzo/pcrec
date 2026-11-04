# SIM lens: span_pick.md rev 1 (frozen copy sha 324aae3a9c5a...), the PICK run as written

Critic round crit-memfn-spanpick, lens SIM (opus). Python only. No compiles, no timing, no make.

Instruments, all in this directory:
- `spick.py` is the pick implemented FROM THE DESIGN TEXT ALONE (written before I opened
  `r33_sim/sim.py`). It covers the candidates (C-meet, core, not full, PARKED verify-YES only, RESEED never
  F0), T-FIND rows by frame validity, the §The pick price formula under P and F, the quadrature band, and
  `pick()` at three levels, with today's answer as each level's default. It also runs a global comparison
  for contrast.
- `cases.py` holds the constructed outcomes C1-C6.
- `units_<tag>.tsv` and `summary_<tag>.tsv` hold one run per interpretation or sensitivity.

Data: R-33's raw sweep (`subject/r33data/sweep.jsonl`, the RTE arm), 3,443 decision units, which is R-33's
population exactly. The one rate table is PRIOR_AUTHORED `a322116b1b87f9f6`.

Constants are Zen 1 `plan_cost.def` (C_MEMCHR 0.06, C_BITMAP 1.16, C_VERIFY 2.5, C_ENTER 20), with R-33's
H_HIT 20 for stream hits.

The ASSUMPTIONS that the text leaves open (each one a finding below):
- c_hit(walk) = 0, as in R-33.
- The Horspool probe costs 3 c. No card exists for it.
- F is read in ppm.
- PAIR is valid only in E-find and E-func frames.

**Noise assumption (stated):** relative 1-sigma A/A noise per card kind:
- find.byte 3 %
- find.hit 10 % (two landing regimes)
- verify.cmp 10 %
- enter 25 % (MEASURED x ASSUMED)

Sensitivity runs: 0 %, 2 % uniform and 10 % uniform.

## Findings

### SIM-1: the design's smp20 and R1 predictions come from R-33's arithmetic, not from the design's own price formula
CONFIRMED. Severity: design/speed. Effort: small (pick one hit model and redo the predictions). Blast radius:
every PAIR price, so every R1/R4 site. Hits: §The pick price formula, and §Robustness "What it predicts".

- The design's formula: `hits_r(S) = m_r(S) (ppm; PAIR: m_r(a) + m_r(b))`. That is the set's mass, NOT doubled
  for two streams.
- R-33's KEY A/B (`r33_sim/sim.py` `score()`): `m * streams * H_HIT`. A PAIR pays twice the hits.

The design's quoted figures are R-33's:
- "under P it wins by 8.6 % under KEY B" is `differ_keyB.tsv` row smp20, 166,634 / 153,476 = 1.086.
- "R1 dense pairs: the walk wins under P" is R-33's gap 0.585 for `cat|dog`.

Under the design's formula (`units_base.tsv`, `--dump smp20`):

| case | plan | P | F |
|---|---|---|---|
| smp20 `(?i)x/1234` | {X,x} PAIR (today) | 144,694 | 295,858 |
| smp20 `(?i)x/1234` | {/} memchr | 153,476 | 147,929 |
| c01979 `(cat\|dog)s`, an E-func site where PAIR is valid | {c,d} PAIR | 1,984,120 | — |
| c01979 `(cat\|dog)s` | {c,d} walk | 2,092,060 | — |

- **smp20:** '/' LOSES under P by 6.1 %, so the pick never departs at H_HIT 20.
- **smp20 sensitivity:** it departs only for c_hit below about 17 c (run h10: 133,724 vs 111,936). It also
  departs if PAIR's hits are doubled (run x1, `--pair-hits r33`: 169,388 vs 153,476).
- **`cat|dog`:** the PAIR is cheaper under P as well, against the design's "the walk wins under P".

Fix: decide whether a PAIR hit costs per member or per stream (the `find.hit` card's "per method"
must say which). Then redo §Robustness's witness predictions with the design's own formula.

### SIM-2: the price formula is dimensionally inconsistent and under-specified in five places
CONFIRMED by reading, plus run `flatraw`. Severity: design/doc. Effort: small. Blast radius: every price.
Hits: §The pick price formula, §The pick step 1.

- **(a) The Horspool scan term is per byte, not per 1e6 bytes.** It reads
  `(c_probe + m_r(S) x verify) / E_r[shift]`.
  - `c_probe / E[shift]` is c per byte, so it is missing the `x 1e6` every other scan term carries.
  - `m_r(S) x verify / E[shift]` is ppm x c per byte, which equals c per 1e6 bytes. That part is correct.
  - Read literally, the probe term is 1e6 times too small, so Horspool is nearly free and wins every
    comparison.
- **(b) "F = flat (`|S|/256` per position)" is a probability, while every other mass is ppm.**
  - The design's own example ("7,812 under F") uses ppm.
  - Read literally (run `flatraw`), F masses are 1e6 times too small and F prices collapse to the scan
    terms. P∧F departures fall from 206 to 2.
  - The rule's outcome depends on a unit the text gets wrong.
- **(c) `E_r[shift]` is never defined.** The text does not say:
  - which window it covers;
  - which position is probed;
  - how `sh[b]` is weighted under F;
  - what the per-candidate offset d means for a method that "replaces find and resume".

  In my implementation the Horspool plan prices identically at every candidate of an alternative
  (`--dump hex8-bounded`: 665,462 at all 8 positions). So it is a property of the alternative, not of a
  (candidate, method) pair.
- **(d) Horspool and lines 2-3 of the formula.** For Horspool, the formula does not say whether the
  `hits x c_hit` and `hits x verify` lines also apply. If they do, verify is counted twice (it is inside the
  scan term already). If they do not, the text does not say so.
- **(e) Units and scale.**
  - "One unit: the target set's scalar-walk per-byte cost" conflicts with a formula written in cycles x
    1e6. The walk card then has to be 1 by definition, and its noise correlates every price.
  - The fixed-point scale (D176 Q5) is not given. The product `m x prod pass` truncates to 0 for rare
    sets in integer ppm, which silently drops the c_enter term.

### SIM-3: the band has no data; with noise absent the rule is maximally aggressive, not conservative
CONFIRMED. Severity: design (seam/abi). Effort: medium (a new channel field and the cards' noise). Blast
radius: every departure. Hits: §Robustness "The margin is measured", §Cost cards "Where they live".

- `mf_measure` (memfn/include/memfn.h:1189-1194) carries `key, value_e6, unit, source`. There is no noise
  field.
- `measure_sets.md` (around lines 948-951 in the review tree) says: "No provenance columns. `abs_ns_e6`,
  `noise_e6`, ... are pcrec's listing's. A kit row that wants noise asks by REQUEST ... No selection reads
  noise today."
- The only committed set, `measure_store/zen4-grid1/1/set.tsv`, has `noise_e6` = `-` on all 68 of its
  kit/pcrec rows.

So the design's "handed to the kit on `mf_art_begin` (`mf_measures`, kit rows only; the existing channel, no
new fact)" is false for the band: the band needs a new fact across the seam, which is an MF abi event.

If absent noise is read as 0, any positive difference departs:
- Constructed case C1: a 0.1 % difference departs.
- Corpus: P∧F departures rise from 206 at the base noise to 244 at zero noise.

The rule must say that a card with no `noise_e6` is UNMEASURED (it cannot challenge), never 0.

### SIM-4: the rule is undefined when the DEFAULT is unpriced
CONFIRMED (C3). Severity: design. Effort: one sentence. Hits: §The pick step 3, §Cost cards "Measured how".

- §Cost cards says "a plan whose method has no card is unpriced and cannot challenge; it may still BE the
  default". But step 3 needs `price_r(default)`.
- Real cases:
  - The Horspool default before a probe card exists (`plan_cost.def` has no Horspool probe row at all).
  - The RESEED KEY's UNPRICED non-memchr candidates.
  - SIMD forms (N12).
- Either "an unpriced default never departs" (it freezes) or "unpriced = +inf" (it departs on anything). The
  text picks neither.

### SIM-5: three-level stickiness at a CHALLENGER candidate hides dominators and departs to P-worse plans
CONFIRMED (C4, C5; data). Severity: design/speed. Effort: small (rule wording). Blast radius: 43 units once
PF frames get PAIR. Hits: §The pick "One rule, three levels" and step 2.

Level (a)'s default at every candidate is T-FIND's first match. At today's stop that is conservative. At any
other candidate it has no "today's answer" claim, yet it is still sticky, so the level above sees only the
sticky plan.

Run `pfpair` (stage 3 item 4's world, PF frames rendering PAIR), base noise: 43 units where 3-level ≠ a
global comparison against today's plan.
- **40 depart to a RESEED PAIR that is P-worse than the same stop's walk, which also dominates today:**
  - bench bounded/ctx-lazy-64/256/1024 and ctx-greedy-256: {a,b} PAIR P 1,578,074 vs walk 1,337,094.
  - bench syntax/alt-two `cat|dog`: {g,t} PAIR P 1,787,990 vs walk 1,359,270.

  The walk beats the PAIR only under P, so the PAIR "stands" at level (a). It then wins level (c) anyway.
- **2 units keep today although a dominator exists:** c00011 `cat|car|cap|dog` and c01624
  `(cat|car|carpet|dog|do)`. The RESEED @1 {a,o} walk dominates today's PARKED {c,d} walk under P and F
  (1,444,568 vs 2,092,060). But level (a) kept {a,o} PAIR, which does not dominate.
- **1 unit** (utf8/alt-cyr-64) picks another alternative than the global comparison would.

Fix:
- either the default sticks only on the default path (today's alternative, stop and method), and elsewhere a
  level takes the priced argmin;
- or the departure test is one global comparison of each complete plan against today's complete plan, and
  the levels only order the trace.

### SIM-6: F does not make a departure "not rest on the prior"; both models agree wrongly on non-ASCII text
CONFIRMED. Severity: design/speed (a known 421x bench row). Effort: medium. Hits: §Robustness "The rule" ("F is
not a guess about text; it is the absence of one").

The case is bench utf8/alt-cyr-64 (Cyrillic alternation, compiled as bytes). R-33 attributed its 421x-off
row to the prior rating {\xd0,\xd1} at 4 ppm. In run `pfpair`, the PAIR beats the walk under BOTH models:

| model | {\xd0,\xd1} PAIR | walk |
|---|---|---|
| P | 120,160 | 1,160,080 |
| F | 432,500 | 1,316,250 |

So the pick departs to two memchr streams on bytes that make up roughly half of Cyrillic UTF-8 text.

F is uniform text, which is itself a rate model. Where real text is far from both uniform text and the prior,
the two models agree, and the robustness rule passes the error through. This holds for UTF-8 lead bytes, for
case-folded letter pairs, and for any dense class the prior under-rates.

The design should either:
- name this class as uncovered (Open question 3 is about smp20 only);
- or add a fact (encoding) or a third, adversarial model (for example, the densest member at the
  per-position max) before stage 3 item 4.

### SIM-7: the alternative level prices PARKED and RESEED with one c_enter; 204 of 206 departures rest on that alone
CONFIRMED. Severity: design/speed. Effort: medium (a per-entry enter card, or PARKED's in-DFA verify priced).
Blast radius: about 200 PF sites. Hits: §The pick ("c_enter is per consumer kind ... every plan of one site
hands to the same consumer, so only passes_r differs"), Staging item 3.

At level (c), the two plans of one site enter differently: a PARKED alternative continues the DFA, and a
RESEED alternative re-seeds it. So the quoted sentence is false there.

In the base run, all 204 P∧F alternative departures are PF sites going from PARKED k0 walk to RESEED walk:
- 181 go to @1, 13 to @2, and the rest to @3, @4, @8 or @9.
- All walks pay the same 1.16 c/B, so the whole difference is that the PARKED plan has no verify chain. Each
  stop hit pays C_ENTER 20 c, against 2.5 c verifies first on RESEED.
- C_ENTER is MEASURED x ASSUMED and enters P and F identically, so F filters none of them.
- 25 % enter noise did not stop them. At 10 % uniform noise, 143 remain.

These are R-33's altwide/loglines "walk to walk" class, which R-33 itself could not support with any timing.

### SIM-8: "PF states one alternative with one candidate" contradicts the data and the design's own stage 3 item 3
CONFIRMED. Severity: doc/design. Effort: small. Hits: §The shape "What is a scenario then", §pcrec-side findings
"PF span 0", Staging item 3.

- In R-33's data, 1,454 of 1,767 PF sites state TWO alternatives (PARKED and RESEED). The RESEED alternative
  has several core positions; for example `\d{4}` has positions 0-3.
- The design says "the kit never picks another stop there". Yet stage 3 item 3 admits RESEED stops on 95 PF
  units.

### SIM-9: whether priced Horspool keeps the D-hors wins (goal 5) depends on two undefined terms, not on measured cards
CONFIRMED under the stated assumptions (runs hp0.5 to hp5, zero noise). Severity: speed (goal 5). Effort: small
(resolve SIM-2 (c)/(d) and c_hit(walk)). Hits: Staging item 2, Goal 5, §Robustness third bullet.

On the five dense D-hors witnesses of job 588 (smp03, smp08, smp13, smp18, smp23) and their corpus twins
(11 units in all), every set is near full, so E[shift] is about 1.0. Horspool vs walk then reduces to
c_probe vs c_byte(walk) = 1.16 c, because the verify and enter terms are identical.

| c_probe | what the pick does |
|---|---|
| ≤ 1 c | keeps Horspool on all |
| 2 c | departs to the walk on 7 units under P∧F (11 under P-only) |
| 3-5 c | departs on 11 units, including all 5 of job 588's dense witnesses |

Only hex8-bounded (and its bench twin and c02934) keeps Horspool on a real shift.

- The departures are measured slower: RTE/DEF 0.57-0.78 is in Horspool's favour.
- With c_hit(walk) = 20 c (the design charges `hits x c_hit(method)` for the walk too, which R-33 did not),
  the walk pays about 20 c x 1e6 per 1e6 bytes on these dense sets and Horspool wins by a mile.

So goal 5 is decided by how SIM-2 (c)/(d) and the walk's hit term are resolved.

### SIM-10: adding a renderer moves the level-(a) DEFAULT outside T-PICK
CONFIRMED (run `pfpair`). Severity: design (D186 gate). Effort: small. Hits: Staging item 4, §The pick step 2,
§Robustness R1 bullet.

- The default is "T-FIND's first match", and T-FIND's validity column is keyed on the frame. When item 4 gives
  PF frames a two-stream renderer, PAIR becomes the first match. The default itself flips from walk to PAIR
  on every PF two-member stop: 269 today-walk units.
- No `T-PICK` row gates a default, so this is a byte-moving choice change outside the gate.
- It also inverts the R1 prediction. "No dominance, the default stands" then means PAIR stands on the 187
  dense units that have no dominance, which is the opposite of the intent.

R1 census (today walk, base noise):

| class | units |
|---|---|
| dense, no dominance | 187 |
| dense, PAIR dominates | 13 |
| dense, walk wins under P only | 3 |
| rare, PAIR dominates | 66 |

The default must stay today's plan until a T-PICK row admits the move, or item 4 must name the flip as its own
choice change.

### SIM-11: smaller gaps in the rule text
CONFIRMED by reading (C6). Severity: doc. Effort: small. Hits: §The pick, Staging.

- **(a) T-PICK rows do not say which level(s) they open.** A row on "candidate set sizes" admits a level-(b)
  departure, but does it also admit level (a) or (c) at that site?
- **(b) "Ties within a band go to the TIE table": whose band?** In C6, two qualifying challengers lie within
  each other's band, and "least P" picks c1 outright before any tie rule applies.
- **(c) The level-(b) default after deletion is undefined.** The KEY rows are "deleted in stage 3 by the first
  choice change", and nothing says what the default is afterwards for PARKED/RESEED alternatives (item 1
  replaces only the no-entry row).
  - The no-entry case is benign on this corpus. Replacing A-mass by a P argmin moves only 3 units with a
    strictly P-cheaper other set: pr09 and `x[\x{e0}-\x{ff}]y`, both F-dominant, and `a[\18]b` within band.
- **(d) The alternative default "MARGIN" is a prior-only (P) price.** So the level-(c) default is itself
  chosen by the prior the rule distrusts.

### Diff of the design text vs R-33's sim.py (step 1)

These are the places where `spick.py` (design text) and `sim.py` (R-33) diverge. Each is either a design
ambiguity or arithmetic the design borrowed.

| # | `spick.py` (design text) | `sim.py` (R-33) | see |
|---|---|---|---|
| 1 | PAIR hits = m(S) | m x streams | SIM-1 |
| 2 | walk pays hits x c_hit(walk) | "the walk's per-hit exit" not modelled | SIM-9 |
| 3 | PARKED candidate set: no definition beyond "verify-YES positions readable" | the AND of the YES spans only (`yset`) | design should say which |
| 4 | verify over Table C's core positions | every stated non-full offset, core or not | — |
| 5 | ties go to the TIE table | ties prefer today's stop | — |
| 6 | Horspool priced (undefined) | today's D-hors, generic and loop priced as the walk | SIM-2, SIM-9 |
| 7 | alternative default = MARGIN | plain least score, no MARGIN | — |
| 8 | P and F dominance plus band | a single-model argmin | — |
| 9 | F masses: undefined | F masses: `len*1e6//256` (ppm) | supports the ppm reading of SIM-2 (b) |

## PROBED-AND-HELD

- **The candidate list contains every stage-1 answer.** My builder located today's (alternative, stop) in its
  candidate list in 3,443 of 3,443 units. The rules were C-meet, core, not full, PARKED verify-YES only and
  RESEED never F0. So the design's candidate definition does not exclude any answer the stage-1 byte identity
  needs.
- **The quadrature band over shared cards is always conservative.** `sqrt(a^2 + b^2) sigma >= |a - b| sigma`
  for one card read by both plans. The band never under-states a correlated difference (algebra).
- **Equal prices keep the default** (C2, strict `>`).
- **The three-level winner always dominates today's plan under both models.** The chained strict wins plus
  the triangle inequality on the bands give this (algebra; not separately counted). SIM-5 is about WHICH dominator, and
  about hidden dominators.
- **The smp20 F half holds.** Under F, '/' beats {X,x} PAIR 2:1 (147,929 vs 295,858), as the design says.
- **The R1 dense-pair conclusion "no departure" holds in count once PF renders PAIR.** 187 of 203 dense
  today-walk units show no dominance at base noise, and all 66 rare pairs are PAIR-dominant ("rare pairs can
  depart"). This rests on SIM-10's default question.
- **D-hors stays the default in stage 1** (T-PICK = {keep}): trivially, 14/14 Horspool units are kept.
- **R4 population at base noise, P∧F:**
  - pr09 `x[Q%]y` departs ({x} memchr P 82,434 vs 130,824).
  - `x[\x{e0}-\x{ff}]y` departs.
  - `a[\18]b` departs only at zero noise.
  - `a[*/]b`, `\B(?<!a)[de]` and smp20 keep.

  This is consistent with "stage 3 item 1's population", except for smp20 (SIM-1).
- **Departure counts.** This is R-33's data with Zen 1 constants and H_HIT 20, today's frames, 3,443 units.

  | run | P-only | P∧F |
  |---|---|---|
  | base noise (3/10/10/25 %) | 315 (alt 292, method 12, pos 11) | 206 (alt 204, pos 2) |
  | zero noise | 375 | 244 |
  | 2 % uniform | 366 | 237 |
  | 10 % uniform | 332 | 145 |
  | with PF PAIR (item 4) | 390 | 279 (alt 200, method 77, pos 2) |

  **So F removes about a third of the P-only departures.** The survivors are dominated by SIM-7's single-card
  alternative flips, not by the rate-driven position picks the design aims F at. Its own target, smp20, never
  departs under its formula (SIM-1).
- **Sensitivity to H_HIT is mild under P∧F:** 206 at H 20, 209 at H 10, 206 at H 40. P-only moves to 794 at
  H 40 (method 496). That is the method level flipping PAIR to walk, all of which F refuses: F does its job on the hit
  constant.

## Summary
- I implemented the pick from the text and ran it over R-33's 3,443 units. P-only departs on 315 units and
  P∧F on 206, but 204 of the 206 are PARKED-to-RESEED walk flips driven by one shared C_ENTER term (SIM-7).
- The design's smp20 and R1 numbers are R-33's doubled-hit arithmetic. Under the design's own formula smp20
  never flips at H 20 (SIM-1).
- The price formula is unit-inconsistent: the Horspool term, F in ppm vs a probability, and an undefined
  E[shift] (SIM-2). The band's noise is not on the seam, and is '-' in the only committed set (SIM-3).
- The sticky defaults at challenger candidates hide dominators or depart to P-worse plans (43 units, SIM-5).
  A renderer addition silently moves the default (SIM-10). F does not catch the UTF-8 prior error
  (alt-cyr-64, SIM-6).
- Goal 5's D-hors outcome hinges on undefined Horspool and walk-hit terms, not on measured cards (SIM-9).
