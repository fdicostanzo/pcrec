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
