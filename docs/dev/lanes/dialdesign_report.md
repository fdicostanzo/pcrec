# lane `dialdesign` — [OPT-DIAL] STEP 1, the DESIGN

2026-09-16, opus, branch `lane/dialdesign`. **Design only** — nothing under
`src/`, `tests/` or `docs/spec/`. Two deliverables:

- **A.** `docs/design/opt_dial_inventory.md` REVISION 2 — the size sweep
  folded into §2, §3 reshaped from a draft policy table into a rate table,
  §7's items closed.
- **B.** `docs/design/opt_dial_design.md` — the STEP 1 design note: the
  option, the policy table, λ, the stamp, acceptance, the four lenses, the
  spec plan, the ruling queue.

A D6 panel reviews B. This report is what the work FOUND, not a summary of
what it says — the notes say what they say.

---

## 1. The three findings a reviewer should attack first

### 1.1 The first size notch is empty, and no threshold fixes it

The dial has five positions because Frank ruled five. Filling them from the
measured rates, notch `−1` comes out **identical to the middle on every
discrete row**, and the cause is not the thresholds:

Among the axes whose DENIAL SAVES BYTES — the only ones a size notch can
want — the measured penalties are 1.00× (`--unroll` K=1), then **1.794×**
(`-fno-premul-table`), then 1.99×, 2.00×, 2.71-3.03×, 5.06×. **There is
nothing between 1.00 and 1.794.** So every tier-one bound below 1.794 gives
`−1` the middle's column exactly, and the first bound that does anything
(1.80) makes `−1` equal to `−2` instead. There is no `x₁` that makes `−1` a
distinct, non-empty, non-extreme column.

One qualifier, because it is the thing to check: there IS a measured
penalty inside the gap — altcls-merge/factor at 7.61% (1.082×) — and it is
not a candidate because denying those also makes the typical artifact
BIGGER. A switch worse on both axes never enters the distribution a size
notch draws from.

**The λ row reaches the same conclusion independently** (§4.3, §4.4): with
`x₁` = 1.10 the ops cap admits nothing between the middle's 108 probe ops
and the frontier's next point at 175, so λ(−1) must sit just under λ(0).
Both halves of the dial say `−1` is nearly inert, and they get there by
different routes. I report that as a confirmation with the caveat that one
set is all the λ evidence there is, so it could be the same population
showing through twice.

Recommendation (Q3): accept it, say it in the spec, and let the owed
throughput sweeps fill the gap.

### 1.2 The four-units problem, and collapsing it to one unknown

`opt_dial_inventory.md` §3.2 is the revision's real finding. Frank's
threshold rule is stated in ONE unit; the inventory's rows carry penalties
in four — % throughput, whole-match multiplier, **per-call ENTRY**
multiplier, and a materiality-bar ratio on a named shape — plus λ's fifth,
probe ops. The rule cannot be evaluated across them.

The design note's answer is not a normalisation constant. It fixes the unit
as the whole-match multiplier and converts a component row EXACTLY:
`total = 1 + φ·(m − 1)`. That turns a guessed threshold into a falsifiable
sentence:

> **`-fno-tiered-entry` belongs in the min-size column if and only if
> per-call entry cost is at most 24.6% of match time on the population it
> reaches.**

`φ = (φ_entry, φ_cls)` is ONE measurement, not two problems — both are
"what share of run time is spent in X", both are subject-dependent, both
are isolable by the hand-twin method `form_char_step0.md` and
`ccdiff_step0_evidence/` already use. It is Q1 and it unblocks the most.

I record the near-miss: an earlier draft of this design invented a second
"per-call-entry regime" with its own `x₁`/`x₂` and a guessed cross-regime
factor `c`. It produced the same table and hid the unknown inside `c`.
The `φ` formulation is the same arithmetic with the guess named — and the
difference is that `c` was untestable while `φ ≤ 0.246` tells a measurement
exactly what answer would change the cell.

### 1.3 λ and the discrete table are NOT consistent at the extreme, and the reason is structural

§4.4 is the brief's hardest ask and the answer is negative before it is
positive, which is worth knowing.

The consistency test is a ratio test and — this is the useful part — it is
**checkable today without the calibration constant**: the DP's implied
relative rate is `ρ = λ·P/B`, the discrete rule's marginal accepted rate is
`σ = y/(x−1)`, and the two are consistent iff `ρ/σ` is constant across
positions (that constant being `φ_cls`). Computed: 0.334 at `−1`, and
**exactly 0** at `−2`.

The cause is not a bad λ value. **`x₂` is a hard SAFETY CAP — it refuses a
catastrophic switch no matter how many bytes it saves — and λ=0 is a pure
objective with no safety term at all**: at λ=0 the DP will accept any
number of probe operations to save one byte. The two mechanisms have
different shapes at the boundary and no choice of λ repairs it, because λ
alone cannot express a cap.

The repair gives the DP the cap the discrete rule already has:
`minimise rodata+text subject to ops ≤ x₂ · ops(middle)` — **the same
parameter, not a new one.** On `cls_tree_study.md`'s own worst set, λ=0
lands at 206 ops against the middle's 108: **1.91× against a 2.00× cap**.

And then a caution I want on the record rather than in the win column:
`-fno-anchored-dfa` qualifies at `−2` by 1.99 against 2.00, and the λ cap
is satisfied at 1.91 against 2.00. **Two rows landing within 5% of the same
proposed bound is suspicious, not corroborating.** They share no mechanism
— one is a measured throughput ratio, the other a DP output on one set —
so the agreement is most likely coincidence, and if it is not, `x₂` is
doing more work than a proposed number should. Q2 puts it to Frank with
both dependencies named.

---

## 2. What the revision found wrong in STEP 0, none of it a moved number

### 2.1 The draft policy table violates STEP 0's own allowlist rule

`opt_dial_inventory.md` §3.5(a). The draft table names rung `shared` in two
cells. §2.21 of the same document says the shared rung's run time is "NOT
YET MEASURED ... the number the whole rung turns on", and §7 item 1 lists
it as blocking. §6's last paragraph rules that the dial may never set a
switch with no measured rate.

**The rule was in §6 and the table in §3, and nothing checked one against
the other.** That is the same shape as a check whose control shares a
source with what it controls (`learnings.md` §3), one document earlier in
the pipeline — a rule and its application in one file, with no mechanism
tying them.

The design note's response is not a warning. §3.1 makes conformance a
property of how the table is WRITTEN: every set cell carries its citation
IN the cell, and a cell with no citation is an em-dash. An allowlist
violation becomes a visibly empty citation rather than a cross-reference a
reviewer has to perform.

### 2.2 The `--vm-entry-shape` row — the dial's flagship — is measured on two different pairs of rungs

No new measurement; a re-read of the two the entry already cites, prompted
by trying to fill five columns from them (`opt_dial_inventory.md` §2.21,
REVISION 2 block):

- the `.text` and gcc table is **INLINE ÷ SHARED**;
- the run-time number (isl1 §12.2's flat 16-23%) is the `always_inline`
  ATTRIBUTE's, i.e. **INLINE against PLAIN**.

There is no cell in which one pair is measured on both axes. So "16-23% for
2.7-6.2× bytes" — the charter's own framing, and §5's — is a ratio
assembled from two different comparisons.

Worse for the row: **the rung the DEFAULT selects has no measured run time
at all.** `forward` is established on size (ccd2 §3.4, 20 artifacts, no
exception) and on time only STRUCTURALLY — no entry frame, no canary, no
out-of-line chain symbol, therefore it should run like inline. That is a
good argument and it is not a measurement.

The consequence is in the design note §3.4 and it is tidier than the
problem: the dial moves the TERM and never names a rung, the speed side has
the genuinely measured rate (0.061-0.067 B per ns/call at the cheap cells),
and **the size side is empty because the term's own contract already IS the
min-size answer** — "forward only where it costs nothing", at 1.01× below
1,786 bytes of program. Frank's keep-the-defaults ruling and the
default-middle principle turn out to be the same fact on this row.

### 2.3 Two axes were never inventoried at all

`-fno-cls-fold` (bit 24) and `-fno-startpos-guard` (bit 25) landed in
`docs/spec/tuning.md` after STEP 0 was written, so the headline's
denominator had moved from twenty-one to twenty-three and nobody had
counted. New §2.24/§2.25.

The second one matters beyond the count: **`-fno-startpos-guard` is the one
axis in `tuning.md` that is not answer-identity-preserving, by its own
declaration and on purpose.** A table-filling exercise would have treated
it as an ordinary `-fno-` flag. It introduces a bucket STEP 0 did not have
— STRUCTURALLY INELIGIBLE, where UNMEASURED means "no number yet" and this
means "no number can ever admit it", since the dial's acceptance IS answer
identity.

### 2.4 `-fno-anchored-dfa`'s "pathological population" framing was an artefact of its witness

The sweep's own headline, restated here for the mechanism rather than the
number: STEP 0's size figure came from one hand-picked 30,000-count shape
(+50%). The corpus says **43.39% reach, monotone, median −15.32% of the
artifact, and 10.64% of every byte pcrec emits over its own test corpus.**
An entry whose only size number comes from a hand-picked witness will
describe the witness. §7 item 3 asked for exactly this replacement, and it
is worth recording that the request was right and the expected answer was
too small.

---

## 3. Findings the brief did not anticipate

**(a) `-fno-anchored-dfa`'s min-size cell is admissible only as a
DEPENDENCY on `[K53-SELRETRY]`.** K53 established that the optional
anchored machine's bytes count toward `PCREC_MAX_EMIT_BYTES`, so its
presence can refuse a pattern that compiles without it — which would make
denying it a refusal-set move, and §6.2's rule does not care that the
direction is favourable (a pattern that refuses at `0` and answers at `−2`
has *gained* an answer, which is equally not identity). What closes it is
that K53-SELRETRY's drop ladder already drops the machine on a size-cap
refusal, so the two refusal sets coincide today. **This is a property of
the ladder, not of the row.** Recorded in the note because a dependency
nobody writes down is one that gets removed.

**(b) The K45 check the dial needs is one the axes sweep structurally
cannot be.** The axes sweep compares ANSWERS on patterns that compile and
routes around refusals via `REFUSAL_PATTERN`. The dial needs the refusing
SET compared across positions — **as a set of `file:line` keys, never as a
count**, because this design has two refusal hazards running in OPPOSITE
directions (`anchored-dfa` can only remove refusals, a lowered cap could
only add them) and a count is the one shape of check both could slip
through at once. The sweep memo's own `RXTDUMP` cross-check (K35) already
emits what this needs.

**(c) The middle's own windows disagree with one shipped default.** Running
the default-middle principle over today's defaults as a consistency test,
exactly one fails and it fails by a lot: `-fno-premul-table` costs ~30% of
a DFA-scan-bearing artifact's bytes for 1.794×, which is not "near-free on
the axis it spends" under any reading. `-fno-anchored-dfa` passes on the
median (15.32%) and fails on the tail (39.60%).

The resolution I recommend (Q2b) is to calibrate `z_mid` to 1.35 so the
defaults pass, and to say plainly what that makes the window:
**descriptive of revealed preference rather than prescriptive.** That is
the right thing for it to be, because its real job is admitting NEW
optimizations and for that job "what have we already accepted" is the
correct reference. The general observation underneath: **pcrec's shipped
defaults are already speed-leaning**, which is the project's stated
positioning and not an accident, so the middle sits nearer `+1` than a
symmetric reading of "balanced" suggests — and the speed side of the table
is consequently thinner than the size side.

**(d) λ ABSORBS axes rather than sitting beside them.** `-fno-cls-fold` is
the first and is already ruled that way (Frank, 2026-09-11). Any future
class-representation switch arrives as a kit member priced by λ, not as a
policy row. So the dial's row count does not grow with the tree the way the
inventory's switch count does — the general-mechanisms rule showing up as
table structure rather than as a principle.

**(e) `--unroll=K` should not be a dial row at all**, and the decisive
reason is not tidiness: **a global K row cannot be evaluated against the
threshold rule**, because K=1's penalty has two values on two populations
(no measured throughput cost on nested bounded-repeat shapes where it is
75-79% smaller; 1-3% noise on single-level large-count ones) with a
non-monotone byte curve. A global row would pick one population and be
wrong on the other. The `[ART-SIZE]` ladder already decides per pattern on
bytes it measures rather than models, so the dial sets the ladder's bar and
threshold and K is derived. STEP 0's own note under its table
("THREE ROWS ARE ONE ROW'S PARAMETERS") was right and its table's shape
contradicted it.

---

## 4. Method note: where the percentages came from

The sweep memo reports absolute byte deltas plus three summary ratio
columns; the threshold rule needs RELATIVE savings. Rather than estimate
them from the memo's few cited before/after pairs, I recomputed the full
distributions directly from the sweep's own committed per-pattern tables
(`docs/dev/optdial_size_sweep/runs/*_size.tsv`). **The reproduction command
is in `opt_dial_inventory.md` §3.0**, over committed inputs, needing no
build — because a number in a design note with no reproduction is a number
an adversarial panel is right to distrust, and this lane's numbers are not
in the memo it cites.

What that produced beyond the memo: per-mover percentage distributions
(p10/p25/p50/p75/p90 and the full range), the count of movers clearing each
of several savings thresholds, and **the whole-corpus aggregate**, which is
where `-fno-anchored-dfa`'s 10.64% comes from and which no prior document
carries.

**One denominator choice is a judgement and is flagged as one.** The same
switch reads very differently on the two available denominators —
`-fno-tiered-entry` is 7.48% per reached artifact and 0.559% of the corpus;
`-fno-offset-skip` is 1.30% and 0.126%. The threshold rule uses the
**per-mover** denominator, on the argument that the dial is a per-
compilation setting and a caller compiling one pattern cares what happens
to THAT artifact, not to a corpus they do not have. The corpus aggregate is
the right number for "how much does this matter to the project" and is
reported beside it, never instead of it.

---

## 5. Validation

Docs-only lane. `timeout 300 make strict CC=gcc-16` is the standing bar and
is a formality here — no file this lane touched is compiled by anything.
**Result: see §5.1.** The real check on this work is citation discipline,
and the shape of it is:

- every figure carries its source section;
- every figure this lane computed rather than quoted carries its
  reproduction command (§4);
- every threshold is marked **PROPOSED FOR FRANK'S RULING** and appears in
  the queue (`opt_dial_design.md` §9);
- every Frank ruling cited is distinguished from this lane's proposal in
  the sentence that cites it.

`opt_dial_design.md` §10 is the note's own list of what it does not settle,
headed by: **no end-to-end dial measurement exists.** Every rate is a
per-switch measurement from its own ledger; nobody has built one artifact
at `−2` and at `0` and compared them. The composition of individually
correct rates can still be wrong, and that measurement is owed at
implementation.

### 5.1 `make strict`

**GREEN.** `timeout 300 make strict CC=gcc-16`, run at `ce0c9671` in this
worktree: `strict: whole tree compiles clean with -Werror -Wshadow`, rc 0,
well inside the 300 s bound. Nothing owed.

---

## 6. The Frank queue, in one place

Full statements with recommendations and what would change each answer are
`opt_dial_design.md` §9. In brief:

| id | question | recommendation |
|---|---|---|
| **Q1** | `φ` — what share of match time is per-call entry cost, and class-membership probing? | **Charter the lane before implementation.** It unblocks the most and is cheap. |
| **Q2** | the thresholds `y`, `x₁`, `x₂`, `s`, `z₁`, `z₂` | 5%, 1.10×, 2.00×, 1.10×, 2.0×, 4.0×. The substantive question is one sentence: **is a doubling of match time acceptable at the extreme size notch?** |
| **Q2b** | `z_mid` = 1.20 or 1.35 | **1.35**, calibrated so today's defaults pass; the window is descriptive of revealed preference and that is correct for its job. |
| **Q3** | is a nearly-empty `−1` acceptable? | **Accept it**, state it in the spec. The alternative is a rate test, which gives `−1` exactly one member. |
| **Q4** | fold `--unroll=K` into the `[ART-SIZE]` ladder's parameters? | **Take the fold.** Narrower variant available: move only the threshold, leave the bar at 0.75 everywhere. |
| **Q5** | λ's `−2` value, given the frontier inversion | **Keep 0 provisionally**; resolve with a real object-size sweep over several sets, not the model's `.text` estimate. |
| **Q6** | does an explicit CLI `--tune` beat a target's `tune` row (D93)? | **NO — the file wins**, with a loud non-fatal diagnostic. `--engine`'s exception had a forcing reason `tune` lacks. Either way, land the `PCREC_TUNE_SET` bit. |
| **Q7** | solo battery for the implementation merge (D102)? | **Yes, solo** — `abi` event plus four new answer-identity axes. Manager's call, listed for completeness. |

## 7. Commits

| commit | contents |
|---|---|
| `ad4a444e` | inventory revision 2 — the sweep folded into §2; §2.24/§2.25 added |
| `9a36ac7d` | inventory §3 reshaped to a rate table; §3.5 what STEP 0 got wrong; §7.1 items closed |
| `ce0c9671` | `opt_dial_design.md` — the STEP 1 design note; `docs/design/CLAUDE.md` entry |
| (this) | the two claim corrections §1.1 names, and this report |

Nothing is owed except the `make strict` line in §5.1 and the queue above.

---

# r60 fix round

2026-09-17, lane `dialfix`, opus, same branch. Against
`docs/dev/reviews/2026-09-17-r60-opt-dial-design.md` — 6 blockers, 16
must-fix, 8 should, 3 nit, every finding FIX-NOW. Docs only; nothing under
`src/`, `tests/` or `docs/spec/`.

This section is the finding-by-finding record (§R1), then what the fixes
REVEALED that the review did not anticipate (§R2), then the one place this
lane PUSHED BACK with measurement (§R3).

## R1. Finding by finding

### Blockers

| id | what moved |
|---|---|
| **B1** | `opt_dial_design.md` §6.1a, the MECHANISM-STATE CROSS-CHECK. Five mechanisms recovered from EMITTED TEXT (premul's stride, the anchored machine's second table, the deep-tier `noinline` function, the entry rung's shape, the selected `K`) × five positions, in `run_premul_table.sh`'s shape. **The expectation side reads `docs/spec/tuning.md` §5's table and never the `src/` table the compiler consults** — otherwise the check compares the implementation to itself, which is the shape §3.5(a) of the inventory already caught inside this design's own STEP 0. Three named sabotage rows, SAB-D1 (swap two adjacent position columns), SAB-D2 (deny the wrong bit at one position — two cells wrong in opposite directions, so a denial COUNT passes), SAB-D3 (drop one ladder parameter — the two move together by §3.5's fold). N2's stamp well-formedness arm is folded in as its PRECONDITION rather than its cheap substitute, because the cross-check reads the position off the stamp to know which cell set to expect. |
| **B2** | §6.2a. **PUSHED BACK with measurement (§R3) and ADOPTED ANYWAY.** The population is named and counted on the caps' own quantity; the synthetic F1/F2/F3 family lands, with the named real near-cap artifact beside it as a control. |
| **B3** | §3.1 gains the **PURE WIN** reason code, which is the ROOT CAUSE the review named — the inventory's own first bucket had no cell shape in this table, so its two members (`-fno-start-pinned`, `-fno-alt-island`) had nowhere to go and silently left. Both rows restored with their citations. Arithmetic restated so it can be checked: **23 `tuning.md` §2 axes + λ + 3 non-§2 rows = 27**. The seven reason codes are now a table, and every flat row carries exactly one. |
| **B4** | §7.2a. No flags invented. All five affected cells enumerated with today's spelling and what "explicit beats the dial" would need (three deny-only bits with no force twin; the `[ART-SIZE]` bar and threshold with no CLI spelling at all — `PCREC_SIZE_TERM_THRESHOLD` is `limits.def:161` kind `BUILD_D`, which exists precisely to say a constant is not a flag). Three options costed, including the ~9 minutes three force arms add to `make test-axes`. New queue item **Q7**; this lane recommends option (3) — narrow the ruled property IN THE SPEC — with (1) when someone needs a flag. |
| **B5** | §3.2 restated PER REGIME: four regimes, one threshold set in §3.0's two quantities, conversion `1 + φ·(m_c − 1)` per regime. **φ is three components, not two** — revision 1 named `φ_entry` and `φ_cls` and silently left `φ_scan`'s four rows in the wrong unit. §0's headline re-derived (§R2.1). |
| **B6** | §3.1 **gate 6** — a penalty is admitted at its WORST measured population, never its median, because a dial position is a promise to a caller who does not choose their subjects. `-fno-anchored-dfa`'s cell carries all five splits from `opt2_anchored_match_measurement.md:292-296`; §3.6's sensitivity re-derived off the distribution. The asymmetry with the SIZE side (median, tail reported) is stated deliberately so nobody "fixes" it: a bound protects and must hold everywhere, a benefit describes. |

### Must-fix

| id | what moved |
|---|---|
| **M1** | §3.0, new. ONE size quantity (`σ`, the inventory §3.0 convention verbatim) and ONE time quantity (`m`), applied mechanically. Premul's "+29…33%" was the reciprocal of its neighbours' quantity and is now `σ` = 22-25% like everything else. `z₁`/`z₂` are respelled **`Z₁`/`Z₂`** because they are a whole-ARTIFACT budget, a different object from `z_mid`'s per-optimization admission bar — a conflation revision 1 carried in one notation. |
| **M2** | 0.00009% → **0.000026%**, with the note that comparing one artifact's bytes against the whole corpus's total is a comparison that cannot fail; the corpus-wide figure (~104 KB, 0.091%) stated beside it. |
| **M3** | §3.6 no longer sweeps `x₁` past `x₂`. Every sweep is capped at its neighbour and the nesting invariant is stated as the cap's reason. |
| **M4** | §6.2b, the growth direction, with the population named — and a mechanism gap the review did not ask for (§R2.3). |
| **M5** | §6.1b, the `−2` ladder arm, with `artifact_size_term.md` §2.2b's finding R1 CITED and its sufficiency argument marked STRUCTURAL rather than measured. |
| **M6** | §5.3a. The aggregate percentage is replaced by a check BY NAME: `tests/codegen/manifests/m5_stage1_stamps.tsv`'s **ten** `EMITTED_BYTES` rows (all ten listed), each moving by a COMPUTABLE 23-28 B, asserted POSITIVELY. Plus the tripwire's pins and `MAX_SIZE_BYTES` guard, plus the finding that the two readers may not agree on the delta (§R2.2). |
| **M7** | Fixed by construction under S1: §4.2 derives `κ = 1 + (x−1)/φ_cls`, shows the arithmetic, names `φ_cls` as its unknown, marks the caps PROVISIONAL at `φ_cls = 1` (the tightest reading, so a qualifying cell qualifies everywhere), and records that `κ ≥ x` always — the identification was conservative in direction and wrong in kind. |
| **M8** | **APPLIED, and it runs against this note.** The "two halves agree independently" claim is WITHDRAWN in §4.5: both halves read `x₁`. What survives is weaker and true — they agree because they are the same rule. |
| **M9**, **N3** | Moot with §4.4's retirement (S1 removes the ratio test). Both retractions are recorded in §4.5 rather than deleted, because a reader who remembers revision 1 needs to know the quantity is gone. |
| **M10** | §3.2a **window B**, new: `t_mid` checked against three default-ON size optimizations for the first time. `-fno-cls-fold` fails it at ×1.095 against 1.02 — **by a factor of ≈5, the larger of the middle's two violations** — with both qualifications carried (one witness, forced-VM; and the fold is subsumed into `[CLS-TREE]`, which is why `t_mid` must be ruled BEFORE the kit lands rather than after). |
| **M11** | §4.4 states plainly that λ(0) = 16 is derived from ONE HALF of the middle principle and that any `t_mid` gives the same answer, and names `φ_cls` as what would complete it. Revision 1's claim that λ is the design's one prospective application of the whole principle is reduced to the true, smaller claim. |
| **M12** | §3.4. **`+2` = 13,312 WITHDRAWN** — it came from the plan row's phrase "into 8-13 kB", a recommendation written before the rate table existed, promoted into a cell of a table built to forbid uncited cells. `+1` = 8,192 stands and covers the measured band (program 5,183 / 5,985 / 6,954). Revision 1's "better-measured rate of the two" is corrected against `opt_dial_inventory.md:573-577`: both rungs' rates are cross-pair assemblies. The measurement that would fill `+2` is named. |
| **M13** | `s` is applied rather than proposed: the `[ART-SIZE]` ladder's speed side is EM-DASHED (the speed it buys is ≤3%, an order of magnitude below `s` = 1.10), making it a size-side-only row mirroring §3.4's speed-side-only one. And §3.1 gains the corollary that a cell EQUAL to the default is an em-dash — revision 1 wrote `allow` into `+1`/`+2` cells that change nothing, which made three flat rows look like moving ones. |
| **M14** | §3.5a and §3.5b, both new. The DECLARED-CAPACITY FLOOR is disclosed, cited (`artifact_size_term.md` §3.3a), quantified (`.subject_ceiling` 512 → 341; five corpus cells flip match → FRAMES give-up under `--unroll=1` on a 684-byte subject), and added to §6.3's not-covered list — mirroring the `[K53-SELRETRY]` treatment §3.3 already models, which is why the omission was a discipline failure rather than an oversight. §3.5b quantifies the zero-inhabitant-pin hazard from the sweep's own committed baseline (see §R2.4). |
| **M15** | `--force-tune` DELETED from the §1.2 diagnostic. It advertised a flag no section defined, and had it been defined it would have been D93's own revisit-when shape — an answer to Q6 smuggled into a diagnostic string. |
| **M16** | MANAGER-RULED, applied. §1.3: the general explicit-set-provenance form is the recommendation, its build DEFERRED with the trigger named (the second axis that needs the distinction; `--engine` is the first and has shipped without it), and the tune-only bit DROPPED. §5.2 records that this removes the section's own inconsistency — revision 1 refused the `rx_info` mirror on D77 and landed a consumer-less bit in the same note. |

### Should / nit

**S1** — MANAGER-RULED, adopted; §4 rewritten (§R2.5 is what it turned out
to buy beyond what the ruling promised). **S2** — Q6's argument 1 withdrawn
in §1.2 and §9; the note says WHY (a precedent argument standing beside two
reason arguments). **S3** — gate 1 restated as PERMANENTLY-flat vs
CONTINGENTLY-flat, with the critic's finding that nothing but
`-fno-startpos-guard` belongs in the first bucket recorded as part of the
gate. **S4** — `--engine` cites gate 2 as well as gate 5, in both
documents. **S5** — subsumed by B5; the inventory's own claim is corrected
in place with the original quoted (§R2.6). **S6** — the `+2` arm ships
DECLARED vacuous on S219's precedent with its become-reachable condition
stated; §6.3's distinct-position count corrected to **FOUR**, and the
correction notes that revision 1's "three" and its reasoning were wrong in
opposite directions. **S7** — six checks (DIAL-S1..S6) get ids, homes and
sabotage rows in §8. **N1** — scan-edge's flat row now rests on the `y`
INFERENCE alone, because under the conversion its `x₂` failure is
conditional on `φ_scan ≥ 0.493`; the independence revision 1 relied on is
gone and §10 says so. **N2** — folded into §6.1a as the cross-check's
precondition.

### The Frank queue

§9 rewritten to the review's REFRAMED shape. Q1 (φ) graduates to THE
blocking measurement chartered before implementation. Q2 asks for a NUMBER
(`x₂` ≥ 2.114?) instead of the word "doubling", with the proxy caveat as a
rider. Q2b asks for the middle's RATIO and runs `t_mid` against cls-fold
first. Q3 is reframed with its corroboration withdrawn — the question is no
longer "is an empty notch acceptable" but "does `−1` ship before φ". Q4
gains its two disclosed dependencies. Q5 DISSOLVES. Q6 stands on arguments
2-3. Q7 is NEW (B4). Q8 (solo battery) is revision 1's Q7 renumbered.

## R2. What the fixes revealed

### R2.1 The re-derived headline inverts which cell is in trouble

The review expected §0's empty notch to repopulate under the corrected
units, and it does — `-fno-premul-table` enters `−1` for any
`φ_scan ≤ 0.126`, `-fno-tiered-entry` for any `φ_entry ≤ 0.0246`, λ's cell
for any `φ_cls ≤ 0.161`. **What the re-derivation also produced, and the
review did not predict, is that the conversion makes premul's `−2` cell
UNCONDITIONAL** (`1 + 0.794·φ_scan ≤ 2.00` for every `φ_scan ≤ 1`), so the
min-size column gains a row it did not securely have — while gate 6 takes
away the biggest one it thought it had. The honest summary is that **both
of revision 1's errors ran the same way: a point estimate stood where a
distribution or a conversion belonged**, and correcting them moved cells in
both directions rather than only tightening the table.

### R2.2 Two byte-count readers with two definitions of "byte"

M6 asks for a check by name, and writing it surfaced that the two readers
of this change's byte delta do not count the same bytes.
`docs/dev/artifact_size_log.tsv`'s counts are comment-EXCLUDED;
`m5_stage1_stamps.tsv`'s `EMITTED_BYTES` are not obviously so, and under
`[M6-READ]`'s commented-artifact style the new `#define` arrives with a
comment line. **So the delta must be computed PER READER, not once.** This
is `docs/CLAUDE.md`'s wave-E class one quantity over: *two surfaces with
different definitions of one word, where the word looks like it can only
mean one thing.* The design states it as a requirement on the
implementation rather than guessing which reader is which.

### R2.3 A `+2`-induced size-cap overflow has no drop-ladder rung

Answering M4 in the growth direction surfaced a mechanism gap neither
document names. `[K53-SELRETRY]`'s drop ladder has ONE rung and it drops
the ANCHORED MACHINE. The extra inlining a raised entry-chain term buys at
`+1`/`+2` is ALSO an optional contributor — optional by the term's own
contract, "forward only where it costs nothing" — so the ladder's general
form covers it and the ladder itself does not. Under §6.2's rule a `+2`
build that refuses where `0` compiles is an acceptance FAILURE, so the only
consistent behaviour is a second rung that backs the dial toward the
middle. **Not built (D77), and the trigger is named: fixture F2 going
red.** `utf8k53_report.md` §1.2 already explains why the ladder shipped
with one rung — a second needs an ORDER, and an order is a measured
per-contributor cost that a sample of one cannot supply. This design would
give it its second sample.

### R2.4 `−2`'s threshold nearly doubles the ladder's population

M14's second half asked whether `−2`'s 40,000 threshold can turn
`run_size_term.sh` §7b's zero-inhabitant pin red for a non-defect. Counted
from `docs/dev/optdial_size_sweep/runs/baseline_size.tsv` (3,478 rows, the
sweep's own committed baseline, reproduced by `opt_dial_inventory.md`
§3.0's command): **86 artifacts sit at or above 120,000 bytes today; 81
more sit in [40,000, 120,000)**, so `−2` takes the ladder from 86 patterns
to **167, a 1.94× population increase**, on shapes it has never run on.
That is what makes M5's trial-machinery question a CHECK (§6.1b) rather
than an argument, and it is the sharpest concrete number the round
produced about the `[ART-SIZE]` fold.

### R2.5 S1 bought more than the ruling promised

The ruling's stated prizes were dissolving Q5 and §4.3's inversion. Two
more fell out while writing §4:

1. **The recalibration warning discharges for free.** Revision 1 warned
   that all five λ values must be re-derived by hand if
   `cls_tree_study.md`'s cost model is recalibrated. Under selection the
   cap test and the objective read the SAME model, so a recalibration moves
   the selection with it. Nothing is hand-derived and nothing goes stale —
   which is a property of the mechanism, not a claim about the numbers.
2. **`Z₁` moved from 2.0× to 1.30× on a DERIVATION.** Solving the
   selection at revision 1's proposed budgets shows that `Z₁` = 2.0 and
   `Z₂` = 4.0 select the SAME frontier point (λ = 256), making `+1` and
   `+2` identical on the one row that was supposed to separate them. The
   frontier's breakpoints are 1.229 (λ=64), 1.342 (λ=256) and 5.734 (λ=∞),
   so **`Z₁ ∈ [1.229, 1.342)` is the only window that separates them** and
   1.30 is inside it. Revision 1 could not have found this, because with
   five hard-coded λ constants the budgets were decorative.

And one thing S1 costs, named rather than absorbed: a per-class selection
needs the DP solved at all six frontier points, up to 6× the study's
measured 25.86 ms worst-case discovery, against `build/pcrec`'s existing
144 ms on that pattern. §4.7 states the number, names the cheaper
reference-set variant and what it gives up, and hands the measurement to
`[CLS-TREE]` — because nothing here is implementable until the kit is.

### R2.6 One lane, one day, two documents that disagreed about each other

S5's finding is worth keeping as a shape. `opt_dial_inventory.md`:823-827
asserted that `opt_dial_design.md` §3.2 "states the rule PER REGIME, with
two regimes and two threshold pairs". Revision 1 of that note stated it
per-regime nowhere and had one threshold set. **Both documents were written
by this lane on 2026-09-16, and the inventory described the design from
INTENT rather than from text** — the author's memory of what the sibling
was going to say, committed as a claim about what it does say. The
correction keeps the original sentence quoted, because the failure mode is
invisible to a grep (nothing is misspelled) and to an inverse walk (the
design has a §3.2 and it is about units). *A cross-document claim is only
as good as the last time somebody OPENED the other document* — which is
`w23implfix_report.md`'s citation-provenance class arriving at the level of
a whole section instead of a `file:line`.

## R3. The one PUSHBACK, with its measurement — FOR THE MANAGER

**B2's premise is wrong; B2's fix is right and is adopted anyway.**

B2 states that §6.2's refusal-set check has an "(almost certainly) EMPTY
corpus population (p99 artifact 14,364 B vs 500K/1M caps)" and calls it
K35. The 14,364 B is `artifact_size_census.md`'s **p99 `.o` OBJECT size**
over 2,488 artifacts. `PCREC_MAX_EMIT_BYTES` and
`PCREC_MAX_VM_EMIT_CODE_BYTES` are **comment-excluded emitted C SOURCE
bytes** (D84, and both notes say so). Comparing them is comparing two
quantities that differ by roughly the object/source ratio — **a unit
mismatch of exactly the class the panel's own M7 names**, arrived at from
the other side.

Measured on the caps' own quantity, from the sweep's committed baseline:

| statistic | value |
|---|---:|
| rows | 3,478 |
| median artifact | 23,557 B |
| p99 artifact | 393,733 B |
| **maximum** | **999,925 B** — `tests/utf8/axis12_scripts.rxt:296` |
| **headroom against `PCREC_MAX_EMIT_BYTES`** | **75 bytes** |

**One shipped corpus artifact sits 75 bytes below a hard refusal cap**, and
the unconditional `RX_TUNE` stamp this design adds to every artifact is
23-28 of them. That does not refuse it — 27 leaves 48 — but it retires
§5.3's "far below the artifact-size tripwire's resolution" outright, and it
is the reason §5.3a is a check by name rather than a percentage.

**B2's fix stands and is taken**, for a better-stated reason than B2 gave:
`n = 1` is not a population, and the one inhabitant is a `dfa` artifact
that no dial position grows at the first build (the entry-chain term is a
VM row, λ is a reservation, the ladder's speed side is now em-dashed) — so
the GROWTH direction's natural population is genuinely empty even though
the near-cap population is not. §6.2a therefore lands the synthetic F1/F2/F3
family **with the named real artifact beside it as a control**, which is
strictly better than either alone: a synthetic family proves the check can
fire, and the real witness proves the cap is reachable by something
somebody actually shipped.

One residual, stated because it bounds the claim: the sweep's `size_bytes`
and the cap's own post-emission counter are both comment-excluded source
bytes and are believed byte-identical (`docs/testing.md`, the `[ART-SIZE]`
census's own classifier), but this lane did not cross-check them
byte-for-byte. If they differ the headroom is not exactly 75; it is not
large under any reading, which is what the finding turns on.

## R4. Commits and validation

| commit | contents |
|---|---|
| `1cc8912f` | `opt_dial_design.md` REVISION 2 — every r60 finding |
| `b00c39dc` | `opt_dial_inventory.md` REVISION 2.1 (§2.15a, §2.11, §3.1, §3.2, §7.1 item 7 + new item 8) and both `docs/design/CLAUDE.md` entries |
| (this) | this section |

**SCOPE NOTE.** The brief scoped this round to `opt_dial_design.md`,
`opt_dial_inventory.md` and `docs/dev/lanes/`. `docs/design/CLAUDE.md` was
also touched — the directory index entry for the two files in scope — because
leaving it would have published revision 1's WITHDRAWN headline as the
directory's summary of the note. Flagged rather than assumed.

**VALIDATION: `timeout 300 make strict` — GREEN, rc 0, "strict: whole tree
compiles clean with -Werror -Wshadow".** This round is docs-only and no
build input moves, so `make strict` confirms the tree is unchanged rather
than that it works — the appropriate bar for a design-only change.

---

# D103 revision (rev 3)

2026-09-17, lane `dialgov`, sonnet, same branch. Executes
`docs/dev/decisions.md` D103 — Frank's ruling on the manager's synthesis
after his too-complicated/too-unpredictable challenge to revision 2.
Docs only; nothing under `src/`, `tests/` or `docs/spec/`. **This is a
GOVERNANCE change, not a re-derivation**: no verified citation, number,
or measurement in revision 2 is touched. What moves is who is allowed to
fill a table cell and when.

## What moved

**§3 (the policy table) becomes THE PINNED CONTRACT.** A governing
sentence states it directly at the top of §3: a cell changes only by an
explicit ruled diff, never because a measurement lands. §3.1's allowlist
(no cell without a cited two-axis measurement) is UNCHANGED — it still
governs what may ever be PROPOSED — but a citation no longer assigns its
own cell automatically.

**§3.2 (the threshold rule-shape) DEMOTES from assignment rule to
PROPOSAL RUBRIC.** Retitled in place: "THE PROPOSAL RUBRIC, STATED PER
REGIME (B5; DEMOTED FROM ASSIGNMENT RULE BY D103)". Every number and every
line of algebra in it survives unchanged — the windows, `x₁`/`x₂`/`y`/
`z_mid`/`t_mid`/`s`/`Z₁`/`Z₂`, gate 6, the per-regime conversion
`1 + φ·(m_c − 1)`, §3.6's sensitivity table — because D103 point 2 keeps
the per-regime unit discipline and the `φ` algebra exactly as derived: it
is how the rubric reads a measurement honestly. What changed is the
framing sentence at the top of every subsection that used to say "this
assigns a cell" — it now says "this is how a cell proposal is argued."

**`φ` drops from THE BLOCKING MEASUREMENT to ON-DEMAND.** §0's "It cannot
fix the thresholds numerically… the reason is a missing measurement"
paragraph is rewritten: the note no longer waits on `φ` at all. `φ` is
chartered narrowly, only when a specific contested cell needs it — the
two named customers are `-fno-anchored-dfa`'s `−2` admission and `t_mid`
before `[CLS-TREE]`'s middle admission (D103 point 3, verbatim). §9's
former Q1 ("THE BLOCKING MEASUREMENT, CHARTERED BEFORE IMPLEMENTATION")
closes as item 1, "CLOSED AS RULED-ON-DEMAND" — no lane is asked for.

**§4 (λ) reverses S1's OWN reversal.** Revision 2's S1 ruling replaced
revision 1's five hard-coded constants with a live per-class selection
under a cap, on the general-mechanisms lens. D103 point 4 reverses that
one level up: λ becomes **five PINNED frontier constants** again — but
now DERIVED BY THE SAME RUBRIC S1 built, rather than chosen by hand as
revision 1 did. The five values, computed at `φ_cls = 1` (the
conservative reading — see §4.2's own "provisional… a cell that qualifies
at the stated cap qualifies at every `φ_cls`" argument, which now decides
a PINNED value rather than a live one):

| position | λ | why |
|---|---:|---|
| `−2` | 4 | unconditional — λ=0 is dominated at every `φ_cls` |
| `−1` | 16 | pinned CONSERVATIVELY at the middle's value; the alternative (4) needs `φ_cls ≤ 0.161`, unmeasured — `−1` and `0` are the same pinned constant until that measurement re-argues `−1` as its own diff |
| `0` | 16 | unconditional — the size-minimal frontier point, no `φ_cls` dependency |
| `+1` | 64 | unconditional — a size budget (`Z₁` = 1.30×) |
| `+2` | 256 | unconditional — a size budget (`Z₂` = 2.0×) |

Three consequences this lane found while writing the pin, none of them
anticipated by the brief:

1. **§4.7's six-frontier-point compile-cost concern DISSOLVES for the
   shipped compiler.** Under a live selection, `[CLS-TREE]` would have had
   to solve the DP at all six swept points to know which one wins; under
   pinning it reads ONE fixed constant per position and solves the DP
   once, at the SAME cost `cls_tree_study.md` §6 already measured for the
   middle policy (mean 4.19 ms / max 25.86 ms) — identical to what
   revision 1's hard-coded constants would have cost. The six-point cost
   is real, but it is the RUBRIC's own argument cost, paid once by this
   revision and again by any future re-argument, never by a compile. §10's
   corresponding bullet is corrected to say so.
2. **D103 WIDENS §10's one-set (`\p{L}`)-only limitation rather than
   narrowing it, reversing what S1 claimed.** S1 said a per-class
   selection confines the one-set limitation to the CAPS' calibration,
   because each class would solve its own frontier and the pinned values
   would not be single-set-dependent. Under pinning there is no per-class
   selection left — the five constants are fixed once, from `\p{L}`
   alone, and applied to every class `[CLS-TREE]` ever sections. The
   limitation now covers the VALUES, not only their derivation, until a
   second real set is swept.
3. **§4.1 point 3's "recalibration warning discharges automatically" needed
   a correction, not a deletion.** The arithmetic claim is still true (the
   cap test and the objective read the same cost model, so a live
   selection would move with a recalibration); the GOVERNANCE claim is
   now false, because a recalibration is exactly "a measurement lands,"
   and D103 forbids a pinned cell moving on that event. Revision 1's own
   warning turns out to have been the right operational answer for the
   wrong reason.

**§9 collapses five asks into two, per D103 point 3.** The r60 revision's
Q1/Q2/Q2b/Q3/Q4 become:

- **item 1** — `φ`, CLOSED as ruled-on-demand (above).
- **item 2** — **THE FIRST-BUILD TABLE**, ONE ratification rather than
  four separate numeric asks:

  | position | ships with |
  |---|---|
  | `−2` (`min-size`) | `[ART-SIZE]` ladder bar **0.95**, threshold **40,000**; `-fno-premul-table` **denied** (unconditional); `-fno-anchored-dfa` **EXCLUDED** — its worst measured population (2.114×) fails the working `x₂` = 2.00 by 5.7%, and the cell is left OUT pending its own on-demand A/B rather than ratifying a specific `x₂` between 2.00 and 2.114 now |
  | `−1` (`size`) | `[ART-SIZE]` ladder bar **0.85**, threshold **80,000**; nothing else — the three `φ`-conditional cells (premul, tiered-entry, λ) stay em-dashed until their own on-demand measurement |
  | `0` (`balanced`) | today's defaults, byte for byte |
  | `+1` (`speed`) | `--vm-entry-shape` term raised to **8,192** |
  | `+2` (`max-speed`) | DECLARED VACUOUS, identical to `+1` — becomes distinct the day either λ lands or `s` is ruled below 1.03 |

  Two things this table deliberately does not ask for: the rubric's own
  working parameters behind it (`x₂`=2.00, `x₁`=1.10×, `y`=5%, `s`=1.10×,
  `Z₁`=1.30×, `Z₂`=2.0×) are not separately ruled — a future re-argument
  of any cell reopens them with that cell, not before — and the r60
  revision's Q2b (the middle's asymmetry as a ratio) stays an open rubric
  detail rather than a blocking ask, since neither of this table's five
  cells touches it.

Q5 stays dissolved (S1, untouched by D103 — it is now simply "the λ`−2`
row above reads 4"). Q6 (D93 file-wins), Q7 (the force-pair question) and
Q8 (solo battery) survive unchanged, renumbered to items 3, 4 and 5.

**§0/§8 and both `docs/design/CLAUDE.md` entries (this file and
`opt_dial_inventory.md`'s own governance-forced correction) are updated to
the D103 shape** — the headline no longer promises a filled table pending
one measurement; it promises a pinned contract, a rubric, and one
ratification-ready table.

## What deliberately did NOT move

- **No number in §3.2's rubric, §3.3's citations, §3.4's term ladder,
  §3.5's `[ART-SIZE]` fold, or §4.2-§4.4's caps/middle derivation was
  re-derived.** Every verified measurement this revision cites is
  revision 2's, unchanged.
- **§6 (acceptance) is UNCHANGED, verbatim, checked directly**: a grep of
  the acceptance section for `φ` (literal and `φ_scan`/`φ_entry`/`φ_cls`)
  returns zero hits, so D103's "§6 unchanged except φ references" clause
  has nothing to apply to. The mechanism-state cross-check, the sabotage
  candidates (SAB-D1/D2/D3), the near-cap fixtures (F1/F2/F3), and S6's
  declared-vacuous `+2` arm all stay exactly as revision 2 built them —
  they check the pinned table, which D103 does not change the CONTENT of.
- **`opt_dial_inventory.md` was touched at exactly ONE site** — §7.1
  item 7's "GRADUATED… to the blocking measurement… (§9 Q1)" sentence,
  which D103 makes factually wrong by cross-reference (φ is no longer
  blocking, and §9's Q1 no longer exists under that name). Annotated in
  place, house style, rather than rewritten: the measurement's own value
  is unchanged, only its governance status. No other inventory content —
  the rate table, the verdicts, the STEP 0/2.1 revision history — was
  touched, per the brief's "only if a cross-reference forces it."
- **The four decidable positions' CONTENT is unchanged from what revision
  2 already concluded** (§0.1's "what this leaves at the FIRST BUILD" and
  §3.3's table already said `−2` excludes anchored-dfa and denies premul
  unconditionally, `−1` moves only the ladder, `0` is the untouched
  defaults, `+1`/`+2` collapse). D103's table in §9 packages that
  conclusion for ratification; it does not change it.

## The final ratification-ready §9 item list

1. `φ = (φ_scan, φ_entry, φ_cls)` — CLOSED as ruled-on-demand; no lane
   asked for.
2. **THE FIRST-BUILD TABLE** — one yes/no ratification (table above).
3. The D93 precedence ruling (§1.2) — does an explicit CLI `--tune` beat
   a target's `tune` row? Recommendation: NO, file wins, loud non-fatal
   diagnostic.
4. The force-pair / CLI-spelling question (B4) — which of three options
   for "explicit flags beat the dial" on the five cells with no force
   twin or CLI spelling? Recommendation: narrow the ruled property in the
   spec now, add flags when someone needs one.
5. Does the dial's landing demand a SOLO battery? Recommendation: yes —
   manager's call, listed for completeness.

## Validation

`timeout 300 make strict` — GREEN, rc 0, "strict: whole tree compiles
clean with `-Werror -Wshadow`". This round is docs-only and no build
input moves, so `make strict` confirms the tree is unchanged rather
than testing the change; there is nothing here `make test` could observe.
