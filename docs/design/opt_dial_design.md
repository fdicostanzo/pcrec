# [OPT-DIAL] STEP 1 — the speed-vs-size dial: option, policy table, λ

Lane `dialdesign`, 2026-09-16. **REVISION 2 — 2026-09-17, lane `dialfix`,
the r60 fix round.** **REVISION 3 — 2026-09-17, lane `dialgov`, D103's
governance revision** (`docs/dev/decisions.md` D103, Frank's ruling on
the manager's synthesis after his too-complicated/too-unpredictable
challenge to revision 2). **DESIGN ONLY — nothing under `src/`, `tests/` or
`docs/spec/` lands from this lane.** §8 is the spec plan the implementation
lane executes under D80; §9 is the ruling queue.

Inputs, all of them read in full: `docs/dev/plan.md`'s `[OPT-DIAL]` row
(every Frank ruling on this design), `docs/design/opt_dial_inventory.md`
(STEP 0, as revised by this same lane),
`docs/dev/optdial_size_sweep.md` (the merged size sweep),
`docs/dev/cls_tree_study.md` §5 (the sectioning DP, where λ comes from),
`docs/dev/lanes/ccd2_report.md` §9, `docs/dev/reviews/
2026-09-17-r60-opt-dial-design.md` (revision 2's panel), and — for
revision 3 — `docs/dev/decisions.md` D103 itself, the governance ruling
this revision executes rather than argues.

---

## PANEL OUTCOME — r60, and what it moved

Three read-only critics (`docs/dev/reviews/2026-09-17-r60-opt-dial-design.md`):
**6 blockers, 16 must-fix, 8 should, 3 nit.** The λ frontier arithmetic,
~25 sampled numbers and citations, the two-search `abi` plan, the
refusal-set-as-keys rule, the `--unroll` fold and Q6's direction all
SURVIVED attack; the num critic re-derived the entire §4 λ apparatus exact.
The failures concentrated in three places, and a reader who remembers
revision 1 needs all three:

1. **UNIT DISCIPLINE.** §3.2 declared match time as THE unit and then
   treated four THROUGHPUT ratios as already in it; §4.4 bounded PROBE OPS
   with a parameter that bounds MATCH TIME. Both are the same error and
   both are fixed by §3.0's single convention plus §3.2's per-regime
   conversion.
2. **POPULATION HONESTY.** `-fno-anchored-dfa`'s penalty is a
   three-population distribution reported as a point estimate; §6.2's
   refusal check had a population nobody had counted; the refusal analysis
   ran in one direction only.
3. **THE ALLOWLIST APPLIED TO ITSELF.** Two `tuning.md` §2 axes were
   missing from a table headed "twenty-three axes, all of them listed",
   and the count only balanced because three non-§2 rows stood in for
   them.

**REVISION 1's HEADLINE IS WITHDRAWN AND RE-DERIVED** (§0). Two manager
rulings arrived with the panel and are applied here rather than argued:
**S1** (λ becomes a SELECTION, not five constants — §4) and **M16** (the
general explicit-set-provenance form is the recommendation; the tune-only
`PCREC_TUNE_SET` bit is dropped — §1.2). One panel premise is PUSHED BACK
with measurement and marked for the manager (§6.2 — the near-cap
population is not empty, and the reason the panel thought it was is a unit
mismatch of the same class as M7). The finding-by-finding record is
`docs/dev/lanes/dialdesign_report.md` § "r60 fix round".

---

## GOVERNANCE OUTCOME — D103, and what it restructures

Frank found revision 2 too complicated and too unpredictable and issued
D103 on the manager's synthesis. **D103 does not touch a verified number
in this note — it restructures how the table is GOVERNED, and every
verified citation below is unchanged from revision 2.** Four rulings,
applied throughout revision 3:

1. **§3's policy table is now THE PINNED CONTRACT.** A cell changes only
   by an explicit ruled diff — never because a measurement lands. The
   same `--tune=N` therefore never silently produces a different switch
   set across releases, which revision 2's live-conditional cells
   (`†`-marked, moving the day φ arrived) could not promise.
2. **§3.2's threshold rule-shape (the `x`/`y`/`z`/`t_mid` windows, gate 6,
   the sensitivity table) DEMOTES from an assignment rule to THE PROPOSAL
   RUBRIC.** It is kept in full, because it is how a cell proposal is
   argued consistently — the manager applies it to a measurement, Frank
   ratifies the result — and it is explicitly NOT an assignment
   mechanism any more. The per-regime unit discipline and the `φ`
   conversion algebra STAY unconditionally: they are how the rubric
   reads a measurement honestly, and D103's ruling changes who acts on
   the reading, not the reading itself.
3. **`φ` drops from THE BLOCKING MEASUREMENT to ON-DEMAND.** It is
   chartered narrowly only when a specific contested cell needs it — the
   two named customers are `-fno-anchored-dfa`'s `−2` admission and
   `t_mid` before `[CLS-TREE]`'s middle admission. Nothing else in this
   note waits on it.
4. **The allowlist discipline (§3.1) is UNCHANGED.** No cell without a
   cited two-axis measurement — this is the half of revision 2 with the
   proven catch record (STEP 0's `shared` cells, revision 1's
   anchored-dfa point estimate, both caught by citation discipline
   rather than by taste) and D103 does not touch it.

**§9 is restructured to match**: Q1 (φ) closes as ruled-on-demand; Q2,
Q2b and Q3 collapse into ONE ratification item, THE FIRST-BUILD TABLE —
the four decidable positions as the fix round derived them, presented for
one yes/no ratification rather than as three separate numeric asks; Q4
folds into that table's cells. Q6, Q7 and Q8 stand unchanged as separate
items, renumbered. §4 (λ) keeps the verified frontier table and the
selection RULE's arithmetic, and reframes what the arithmetic IS: the
argument that chose five now-PINNED constants, not a live per-class
mechanism. The finding-by-finding record for this revision is
`docs/dev/lanes/dialdesign_report.md` § "D103 revision (rev 3)".

---

## 0. What this note decides, and the one thing it cannot

It decides: the option's spelling and its precedence against D93; the
policy table — **now, under D103, THE PINNED CONTRACT** — across which of
pcrec's twenty-three generation axes the dial may touch and what it sets
them to at each of five positions; how those positions map onto λ, the
class-matcher kit's own currency; the stamp and its `abi` consequence; and
what acceptance means.

**It does not fill the table by running a rule over a measurement, and
that is D103's ruling rather than a missing measurement.** Frank's
rule-shape — *"performance penalty under x% AND size savings over y%"* —
is kept in full below (§3.2) as **THE PROPOSAL RUBRIC**: the argued path
from a citation to a cell, applied by the manager and ratified by Frank,
never itself an assignment mechanism. §3.2's per-regime conversion (every
component row's penalty as `1 + φ·(m − 1)`, one named unknown `φ` per
regime) is how the rubric reads a measurement honestly, and it stays
unconditional; what changes is that `φ` is no longer a blocking
measurement gating the whole table — it is chartered on demand, only when
a specific contested cell needs it (§9). **§9 collapses what would have
been separate numeric asks into ONE ratification item, THE FIRST-BUILD
TABLE**: the four decidable positions, argued by the rubric below and
presented for a single yes/no. Every number in §3 and §4 is marked
**PROPOSED FOR FRANK'S RATIFICATION**; nothing here is a ruling until §9's
table is ratified, and nothing here is presented as measured that is not.

### 0.1 THE HEADLINE — revision 1's is withdrawn, and here is the re-derivation

> **REVISION 1 SAID (and it is wrong):** *"THE FIRST SIZE NOTCH IS EMPTY ON
> EVERY DISCRETE ROW, AND NOT BECAUSE OF THE THRESHOLDS … pcrec's measured
> penalties have a GAP: `--unroll`'s K ladder costs essentially nothing,
> and the next cheapest costs 1.794× … This is a property of the measured
> population, not of the numbers Frank picks."*
>
> **It is a property of a UNIT ERROR.** The "gap" was produced by lining up
> a DFA-scan throughput ratio (1.794×), a per-call-entry ratio (5.06×), a
> whole-match ratio (≈1.99×) and a materiality bar (2×) on one axis as if
> they measured the same thing. They do not. §3.2's conversion puts every
> component row in match time as `1 + φ·(m − 1)`, a CONTINUOUS function of
> an unmeasured share — so there is no hole to fall into.

**THE RE-DERIVED HEADLINE, stated before its derivation so a reader can
check it rather than be walked to it:**

> **THE FIRST SIZE NOTCH IS NOT EMPTY; IT IS UNDECIDED, AND THE THREE
> NUMBERS THAT DECIDE IT HAVE NAMES.** At the proposed `x₁` = 1.10×,
> `-fno-premul-table` sits inside notch `−1` for any `φ_scan ≤ 0.126` and
> `-fno-tiered-entry` for any `φ_entry ≤ 0.0246` — each a falsifiable
> sentence about one measurable share, not a guess. λ's `−1` cell moves
> the same way: it is frontier point 4 for any `φ_cls ≤ 0.161` and the
> middle's 16 otherwise (§4.3).
>
> **And the cell revision 1 thought was safe is the one that fails.**
> `-fno-anchored-dfa` — the largest legitimate size lever the dial has,
> 10.64% of every byte pcrec emits over its own corpus — was admitted at
> `−2` on a point estimate of "≈1.99× against `x₂` = 2.00×". Its ledger
> reports a THREE-POPULATION distribution
> (`opt2_anchored_match_measurement.md:293-295`): **1.161× on
> non-matching subjects, 1.986× on matching subjects overall, and 2.114×
> on the 35 short matching subjects.** A caller does not choose their
> subjects, so §3.1's new gate 6 admits a penalty at its WORST measured
> population — and 2.114× fails a doubling by 5.7%. **At `x₂` = 2.00 the
> min-size column loses its largest row.** It returns at `x₂ ≥ 2.114`,
> which is the number Q2 should put to Frank instead of the word
> "doubling".
>
> Both corrections run the same way: **a point estimate stood where a
> distribution or a conversion belonged.**

**What this leaves for §9's FIRST-BUILD TABLE** (φ unmeasured on demand, λ
unimplemented until `[CLS-TREE]` lands): four distinct positions, not
five, argued by the rubric above and PINNED once ratified rather than
left to move as `φ` arrives. `−2` is the `[ART-SIZE]` ladder's two
parameters plus `-fno-premul-table` denied UNCONDITIONALLY (§3.3 — the
conversion makes that cell safe at every `φ_scan ≤ 1`, which is a
strengthening revision 1 could not see); `−1` is the ladder's two
parameters alone; `0` is today's defaults byte for byte; `+1` is the
entry-chain term's raise; and **`+2` is identical to `+1`**, because M12
removes its one unmeasured cell and the λ row that would separate them is
a reservation. §6.3 states that as the acceptance's own limit rather than
leaving a reader to discover it. **A future measurement of `φ_scan` or
`φ_entry` does not silently move any of these four cells** — it is
evidence for a NEW proposal, argued by the same rubric and ratified as
its own ruled diff (D103 point 1).

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

**The case for file-wins, which this lane finds stronger**, in two parts
(**S2**: revision 1's third argument, "a second exception in a month turns
the rule into a list", is WITHDRAWN — it is a precedent argument where the
other two are reason arguments, and D93's own revisit-when already carries
its content without the rhetoric):

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

**So: the file wins, and a conflict is REPORTED** — non-fatal, on stderr,
naming both sources and both values, in `--engine`'s own wording shape:

```
pcrec: FILE:LINE: target 'PREFIX': CLI --tune=min-size and this file's
`tune speed` disagree; using the file's value (--tune is not the
--engine exception)
```

**M15 — the `--force-tune` sentence is DELETED.** Revision 1's diagnostic
ended `(pass --force-tune to override)`, advertising a flag no section of
this note defines, no spec plan lands, and no implementation would find.
Worse, if it WERE defined it would be D93's own revisit-when shape — *"the
likely shape then is an explicit loud override flag, never a silent
precedence flip"* — which is an answer to Q6 smuggled into a diagnostic
string. If Frank wants an override, D93 already names its shape and Q6 is
where it is asked. Nothing in the diagnostic promises one.

### 1.3 The explicit-set problem, and the general form (M16 — MANAGER-RULED)

The `--engine` exception's spec text records an accepted residual:
`PCREC_ENGINE_AUTO` is both the field's zero-default and `--engine=auto`'s
own value, so an explicitly-typed `auto` is indistinguishable from no
flag, and "no tracking machinery exists to tell the two apart."
`tune`'s default is `0`/`balanced` — exactly the same zero-default
collision.

Revision 1 proposed a `PCREC_TUNE_SET` bit in `pcrec_options.flags`. **The
panel found that this is a per-axis fix for a general defect (M16), and
against the same document's own §5.2 refusal of an `rx_info` mirror on
D77 grounds — opposite standards, one document.** MANAGER-RULED, and
applied here:

> **THE RECOMMENDATION IS THE GENERAL FORM: explicit-set PROVENANCE for
> every D93-composed axis, not a bit for `tune`.** Any axis whose value can
> arrive from a CLI flag, a `config`/`target` row, or a default has three
> sources and today records only the resulting VALUE. The general
> mechanism records WHICH SOURCE wrote it — one enum per composed axis, set
> at the one place each source writes — which makes `--engine=auto`'s
> residual expressible, makes the conflict diagnostic derivable rather
> than hand-written at each site, and costs nothing per new axis.
>
> **THE BUILD IS DEFERRED TO ITS OWN MEASURED TRIGGER (D77).** The trigger
> is named: the SECOND axis that needs the distinction. `--engine` is the
> first and has shipped without it; `tune` is the second and does not need
> it either, because the file-wins recommendation makes an explicitly-typed
> `balanced` and an absent flag behave identically. A third would be the
> measurement.
>
> **The tune-only bit is DROPPED.** Landing it would be building a parallel
> mechanism for a general fact, which is the rule
> `pcrec-general-mechanisms-not-special-cases` names and which §7.1's lens
> exists to catch.

If Frank rules CLI-wins after all (Q6), the general form is what makes
that rule statable without the `auto` ambiguity — and the ruling is then
the trigger.

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
matcher per class; the dial moves the CAP that DP is solved under (§4).
This is why §3's table has fewer moving rows than the inventory has
switches, and why that is a feature.

---

## 3. THE POLICY TABLE

**§3.3's table is THE PINNED CONTRACT (D103, point 1).** A cell changes
only by an explicit ruled diff — never because a measurement lands. The
same `--tune=N` therefore compiles to the same switch set across releases
until Frank rules a diff, whatever `φ` or a later sweep goes on to find.
§3.1's allowlist (no cell without a cited two-axis measurement) is
UNCHANGED and still governs what may EVER be proposed into the contract;
what D103 removes is the idea that a citation, once made, assigns its own
cell automatically. §3.2's threshold rule-shape — the windows, the `x`/
`y`/`z`/`t_mid` parameters, gate 6, the sensitivity table — is kept in
full below, reframed as **THE PROPOSAL RUBRIC**: the documented way a
cell proposal is argued (the manager applies it to a measurement, Frank
ratifies), explicitly NOT the mechanism that assigns a cell. The
per-regime unit discipline and the `φ` conversion algebra inside it STAY
exactly as derived, because they are how the rubric reads a measurement
honestly — D103 changes who acts on a reading, not the reading itself.

### 3.0 SIGN AND UNIT CONVENTIONS, stated once and applied mechanically (M1)

The panel found revision 1 carrying three quantities under two names, with
`-fno-premul-table`'s cost inverted relative to its neighbours' in the same
table. One convention now, and every number in §3 and §4 is in it.

**SIZE — one quantity, `σ`.**

```
σ(switch) = 1 − bytes(denied) / bytes(default),   median over the switch's own movers
```

the SAVING FROM DENIAL as a fraction of the DEFAULT artifact, on
comment-excluded emitted C source bytes. This is
`opt_dial_inventory.md` §3.0's convention verbatim and is reproduced by
the command printed there. **`σ > 0` means the optimization COSTS those
bytes; `σ < 0` means denying it costs bytes** (`-fno-altcls-merge` is the
worked example at `σ = −2.40%`). Revision 1's "+29…33%" for premul was the
reciprocal quantity — bytes as a fraction of the DENIED artifact — and is
the inversion M1 names. Premul's σ is **22…25%**.

**TIME — one quantity, `m`.**

```
m(switch) = time(denied) / time(default)
```

a MULTIPLICATIVE SLOWDOWN OF END-TO-END MATCH TIME. `m > 1` means denying
is slower. **Only one row in this table was ever measured in this unit**
(§3.2); every other row measured a COMPONENT and converts.

**THE PARAMETERS ARE STATED IN THESE TWO QUANTITIES AND IN NO OTHERS.**
Penalty bounds (`x₁`, `x₂`, `t_mid`) and speedup floors (`s`) are `m`
values. Per-switch size bars (`y`, `z_mid`) are `σ` fractions. Two
whole-ARTIFACT size budgets exist and are deliberately spelled with a
capital (`Z₁`, `Z₂`) because they are a different object from `z_mid`: a
budget on the finished matcher, not an admission bar on one optimization.
Revision 1 wrote `z_mid`, `z₁` and `z₂` in one notation and used them for
two objects.

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
> that position.** A row with em-dashes in every non-default column is a
> row the dial never touches at all, and it is listed anyway with its
> REASON CODE, because "we considered it and the number is missing" and
> "we forgot it" must not look the same.

**M13's corollary, which revision 1 wrote around:** a cell whose value
EQUALS the default is an em-dash, not a restatement of the default. A
`0`-column cell states the default; every other column states what the
dial CHANGES. Revision 1 wrote `allow` into `+1`/`+2` cells that change
nothing, which made three flat rows look like moving ones.

That makes an allowlist violation a visibly empty citation rather than a
cross-reference a reviewer has to perform, and §6.1a makes it mechanical a
second time.

**The eligibility gates, in order.** An axis reaches a MOVING cell only if:

- **Gate 1 — the axis is not STRUCTURALLY answer-changing.** This is the
  gate revision 1 wrote circularly ("answer identity, quantified over the
  values the dial can set" — which every admitted axis passes by
  construction, since the dial only sets answer-preserving values). **S3's
  restatement, and it is the content:** the distinction is between an axis
  that is flat TODAY because a number is missing (**CONTINGENTLY FLAT** — a
  measurement can move it) and one that is flat PERMANENTLY (**no
  measurement can**). `-fno-startpos-guard` is permanently flat: its two
  arms disagree about answers on purpose
  (`opt_dial_inventory.md` §2.25), so no exchange rate could ever admit
  it. The panel's coherence critic checked all 23 `tuning.md` §2 entries:
  **nothing else belongs in this bucket.**
- **Gate 2 — the REFUSAL SET does not move**, in either direction (§6.2).
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
- **Gate 5 — the time cost's RANGE is not violent.** `--engine` fails this:
  up to 173,580× on the fail path. A dial position that can turn a 0.2 µs
  answer into a 35 ms one is not a dial position at any size saving.
- **Gate 6 — THE PENALTY IS ADMITTED AT ITS WORST MEASURED POPULATION, NOT
  AT ITS MEDIAN (new, B6).** Where a ledger reports its penalty as a
  distribution over NAMED subject populations, the cell's `m` is the
  MAXIMUM over those populations. A dial position is a promise to a caller
  who does not choose their subjects; a median is a description of a corpus
  the caller never saw. The median is reported beside the maximum, never
  instead of it. **A switch whose distribution STRADDLES a threshold is
  admitted only where its worst population is admitted** — which is exactly
  `-fno-anchored-dfa`'s situation and is why §0.1's headline changed.

**The asymmetry between gate 6 and the SIZE side is deliberate and is
stated so nobody "fixes" it.** The penalty is taken at its worst
population; the saving `σ` is taken at its MEDIAN with its tail reported.
A bound PROTECTS and must hold everywhere; a benefit DESCRIBES and a
median is the honest summary of it. `-fno-offset-skip`'s 27 growers among
491 movers and `-fno-anchored-dfa`'s 39.60% best case are both reported,
neither is the cell's value.

**The REASON CODES for a flat row**, one of seven, and every flat row in
§3.3 carries exactly one:

| code | means |
|---|---|
| **PURE WIN** | measured better on BOTH axes; a dial that could turn it off would have a strictly-worse setting on it (**B3 — this code did not exist in revision 1, which is why two axes were missing from the table**) |
| **GATE 1** | structurally answer-changing; permanently flat |
| **GATE 2** | its deny arm moves the refusal set |
| **GATE 3** | one axis has no number; contingently flat, with the measurement named |
| **GATE 4** | the time cost reverses sign with the workload |
| **GATE 5** | the time cost's range is violent |
| **NOT A RUNG** | a floor, a boundary, a no-op, or a PARAMETER of another row |

### 3.2 THE PROPOSAL RUBRIC, STATED PER REGIME (B5; DEMOTED FROM ASSIGNMENT RULE BY D103)

**This section is now the rubric, not the assignment mechanism (D103
point 2).** Everything below — the windows, `x₁`/`x₂`/`y`/`z_mid`/`t_mid`/
`s`/`Z₁`/`Z₂`, gate 6, the sensitivity table in §3.6 — is the documented,
checkable way a cell PROPOSAL is argued: the manager applies the rubric
to a citation, Frank ratifies the resulting table (§9). No cell in §3.3
is filled by running this rule over a measurement as it lands; a cell is
filled only by an explicit ruled diff. The per-regime conversion below is
kept because it is what makes an argument honest, not because it assigns
anything by itself.

Frank's rule-shape (2026-09-06): *a switch whose measured trade is
"performance penalty under x% AND size savings over y%" becomes a tier-one
size-notch option; the extreme size notch takes "savings above y% AND
penalty under some LARGER bound".* So the rule has three parameters — one
savings floor `y`, and two penalty bounds `x₁ < x₂` — and the positions
NEST: everything `−1` denies, `−2` denies too. The nesting is what makes
the surface an ordinal rather than five unrelated profiles, and it is worth
stating as a required property because it is checkable (§6).

**REVISION 1 DECLARED MATCH TIME AS THE UNIT AND THEN PUT FOUR THROUGHPUT
RATIOS IN IT.** `opt_dial_inventory.md` §3.2 — the same lane, the same day
— says the rows carry four incommensurable units and that no conversion
exists in this repository. Inventory `:823-827` even claims this note
states the rule PER REGIME, which revision 1 did not do (design-20: two
documents disagreeing about what one of them says). It does now.

**THE FOUR REGIMES, and the conversion out of each.** A component that is
a fraction `φ` of match time and whose denial multiplies that component by
`m_c` multiplies TOTAL time by `1 + φ·(m_c − 1)`.

| regime | what the ledger measures | rows | conversion to `m` | the unknown |
|---|---|---|---|---|
| **WHOLE MATCH** | end-to-end `rx_match`/`rx_search` | `-fno-anchored-dfa` | none — it IS the unit | — |
| **DFA SCAN THROUGHPUT** | bytes/s of the DFA transition loop | `-fno-premul-table`, `-fno-scan-edge`, `-fno-offset-skip` | `1 + φ_scan·(m_c − 1)` | **`φ_scan` UNMEASURED** |
| **PER-CALL ENTRY** | ns per `rx_search` call | `-fno-tiered-entry`, `--vm-entry-shape` term | `1 + φ_entry·(m_c − 1)` | **`φ_entry` UNMEASURED** |
| **CLASS MEMBERSHIP** | probe ops per membership test | λ | `1 + φ_cls·(P/P₀ − 1)` | **`φ_cls` UNMEASURED** |

**`φ = (φ_scan, φ_entry, φ_cls)` is the single missing measurement this
whole design turns on**, and it is one measurement rather than three
problems: each component is "what share of a matcher's run time is spent
in X", all three are subject-dependent, and all three are answerable by
the same instrument on the same populations. Revision 1 named two of the
three and put `φ_scan`'s four rows in the wrong unit instead. §9 Q1
charters it, and the panel GRADUATED it from recommended to blocking.

**Until φ exists, an affected cell is stated as a CONDITION rather than as
a value** — which is more useful than a guess, because a condition tells
the measurement what answer would change it, and because a condition is
implementable as an em-dash today and as a cell the day φ lands.

**THE RUBRIC'S OWN PARAMETERS — argued here, none of these is measured,
ratified as part of §9's first-build table rather than one at a time:**

| parameter | quantity | proposed | what it says |
|---|---|---:|---|
| `y` | `σ` | **5%** | a size saving under 5% of the artifact is not worth a dial position |
| `x₁` | `m` | **1.10×** | the first size notch accepts at most a 10% whole-match slowdown |
| `x₂` | `m` | **2.00×** | the extreme size notch accepts at most a doubling — **and §0.1 is why this exact value is the note's single most consequential number** |
| `z_mid` | `σ` | **26%** | a speed optimization may cost at most 26% of the artifact to sit at the MIDDLE |
| `t_mid` | `m` | **1.02×** | a size optimization may cost at most 2% of match time to sit at the MIDDLE |
| `s` | `m` | **1.10×** | a speed notch adopts nothing worth less than a 10% speedup |
| `Z₁`, `Z₂` | artifact multiple | **1.30×**, **2.0×** | the speed notches' WHOLE-ARTIFACT size budgets, against the middle's own matcher |

Two of these moved from revision 1 and both moves are derived, not
retuned. **`z_mid` was "1.20×"**, a multiplier of an artifact the text
never named; in `σ` terms revision 1's own recommendation (i) of "1.35×"
is `1 − 1/1.35` = **25.93%**, so 26% is that recommendation restated in
the one convention, and the agreement is a check that the conversion is
right. **`Z₁` was 2.0×**, and §4.3 measures that 2.0× and 4.0× select the
SAME frontier point, making `+1` and `+2` identical on the λ row; the only
window that separates them is `Z₁ ∈ [1.229, 1.342)`, from the study's own
frontier. 1.30× is inside it.

**The middle's pair is `(t_mid, z_mid)` and the asymmetry Frank named is
the relation between them:** a size optimization pays a far stricter
performance bar at the middle than a speed optimization pays a size bar.
The DIRECTION is Frank's ruling; the ratio is this lane's proposal and
§9 Q2b asks for it as a ratio rather than as two numbers, because the
ratio is the ruled object and the two numbers are not independently
meaningful.

#### 3.2a THE MIDDLE IS PINNED BY RULING; THE WINDOWS ARE A CONSISTENCY TEST ON IT

Frank ruled KEEP THE DEFAULTS (2026-09-04), so the `0` column IS today's
defaults, byte for byte, whatever the windows come out as. Running the
windows over today's shipped defaults as a check is still worth doing,
because their real job is admitting NEW optimizations.

**Window A — `z_mid`: what does each default-ON SPEED optimization cost in
bytes?** (`σ`, §3.0's convention, so a bigger number is a bigger cost.)

| default-ON speed optimization | `σ` | ≤ 26%? | ≤ 20%? |
|---|---:|---|---|
| `-fno-offset-skip` (skip ON) | 1.30% | ✓ | ✓ |
| `-fno-tiered-entry` (tier ON) | 7.48% | ✓ | ✓ |
| `-fno-anchored-dfa` (machine ON) | 15.32% median / **39.60%** worst | ✓ median, **✗ tail** | ✓ median, ✗ tail |
| `-fno-premul-table` (premul ON) | **22…25%** | ✓ (**by 0.93 points**) | **✗** |
| `-fno-scan-edge` (edges ON) | not a fraction: +364…612 B absolute | untestable — §10 | untestable |
| `--vm-entry-shape` term at 4,096 | ≈0 by the term's own contract | ✓ | ✓ |

**Exactly one shipped default fails at 20% and passes at 26%, and it
passes by under one point.** Revision 1 called 1.35× "calibrated so
today's defaults all pass"; in one unit it is calibrated so ONE default
passes with 0.93 points of headroom, and `-fno-anchored-dfa`'s tail fails
at either value. That is a thinner result than revision 1's wording
suggested and §9 Q2b says so.

**Window B — `t_mid`: what does each default-ON SIZE optimization cost in
TIME? (M10 — revision 1 proposed `t_mid` and checked it against nothing,
and it is the strict half of the principle Frank actually ruled.)**

| default-ON size optimization | `m` | ≤ `t_mid` = 1.02×? |
|---|---|---|
| `-fno-cls-fold` (fold ON) | **×1.095** match tier on `ci-256`, forced-VM, against a 1.34% noise floor (`[FORM-CHAR2]`, via `opt_dial_inventory.md` §2.24) | **✗ — by a factor of ≈5** |
| `-fno-counter` (counter rung ON) | no measured throughput cost; the denied build is 206% larger and CPU-budget-killed | ✓ (and it is a floor, not a rung — §3.3) |
| `-fno-size-term` (the `[ART-SIZE]` ladder ON) | throughput advantage "exhausted by K ≈ 16"; `--unroll=1` has no measured cost on nested shapes and 1–3% noise on single-level ones | ✓ within its own noise |

**So BOTH of the middle's windows have exactly one violating shipped
default, and they violate in opposite directions.** `-fno-premul-table`
costs too many bytes for a speed optimization; `-fno-cls-fold` costs too
much time for a size optimization, by ≈5×, which is the larger violation
of the two. Revision 1 asked Frank about the first and never checked the
second. Two qualifications a reader must carry: cls-fold's number is ONE
witness under `--engine=vm`, and the fold is ruled SUBSUMED into
`[CLS-TREE]` (§4.6), so the day the kit replaces it this row's violation is
retired by the same landing that implements λ. **That is not a reason to
leave the window unchecked — it is the reason `t_mid` must be ruled BEFORE
`[CLS-TREE]` lands, since `t_mid` is one of the two numbers the kit's own
middle policy will be admitted under.**

And the general observation stands: **pcrec's shipped defaults are already
speed-leaning** — the project's stated positioning, not an accident — so
the middle sits nearer notch `+1` than a symmetric reading of "balanced"
would suggest, and the speed side of the table is consequently THINNER
than the size side. §0.1's "`+2` is identical to `+1` at the first build"
is that observation arriving as a count.

### 3.3 THE TABLE

**Twenty-three `tuning.md` §2 axes, all of them listed** — revision 1
listed twenty-one and its "twenty-three, all of them listed" balanced only
because three non-§2 rows stood in for the two it dropped (**B3**). The two
dropped were `-fno-start-pinned` (§2.19) and `-fno-alt-island` (§2.20),
and the ROOT CAUSE is that the reason-code set had no **PURE WIN** cell
shape, so the inventory's own first bucket could not be expressed and its
two members had nowhere to go. §3.1's code table now has it.

The arithmetic, stated so it can be checked: **23 §2 axes + λ + 3 rows
that are not §2 axes** (the `[ART-SIZE]` ladder's two parameters, which are
`-fno-size-term`'s sub-parameters and are listed separately because the
dial sets them separately; and the emitted-size caps, which are
`limits.def` boundaries) = **27 rows**.

**A cell is either a value with its citation, or an em-dash meaning the
dial does not touch this axis at that position** (§3.1's M13 corollary:
a cell equal to the default is an em-dash). `†` marks a cell stated as a
CONDITION on an unmeasured `φ` (§3.2). Every value is **PROPOSED FOR
FRANK'S RULING.**

| axis | −2 `min-size` | −1 `size` | 0 `balanced` | +1 `speed` | +2 `max-speed` | why, with citation |
|---|---|---|---|---|---|---|
| **λ** (class kit) | cap `κ(−2)` | cap `κ(−1)` | **cap `κ(0)`** | budget `Z₁` | budget `Z₂` | §4 — the dial sets a CAP and the DP selects λ; today's selections on `\p{L}` are 4 / 4-or-16 `†` / 16 / 64 / 256 (`cls_tree_study.md` §5.2's frontier) |
| `[ART-SIZE]` ladder — bar | `0.95` | `0.85` | **`0.75`** | — | — | `artifact_size_term.md` §3.3; the K curve. Speed side em-dashed: the speed it would buy is ≤3%, below `s` = 1.10 (**M13**) |
| `[ART-SIZE]` ladder — threshold | `40,000` | `80,000` | **`120,000`** | — | — | same; `limits.def:161`. §3.5 carries this row's TWO disclosed dependencies |
| `-fno-premul-table` | **deny** | — `†` | **allow** | — | — | `σ` = 22…25% ≥ `y`; `m` = `1 + 0.794·φ_scan` ≤ `x₂` = 2.00 for **every** `φ_scan ≤ 1`, so `−2` is UNCONDITIONAL; `−1` iff `φ_scan ≤ 0.126` (`artifact_size_census.md` item 2; `premultiplied_dfa_table.md` §13) |
| `-fno-anchored-dfa` | **deny** `†` | — | **allow** | — | — | `σ` = 15.32% on 43.39% reach; `m` is a THREE-POPULATION distribution 1.161 / 1.986 / **2.114** (`opt2_anchored_match_measurement.md:293-295`), so under gate 6 the cell requires **`x₂` ≥ 2.114** and is OUT at the proposed 2.00 (`optdial_size_sweep.md` §2.15) |
| `-fno-tiered-entry` | **deny** `†` | — `†` | **allow** | — | — | `σ` = 7.48% ≥ `y`; `m` = `1 + 4.06·φ_entry`, so `−2` iff `φ_entry ≤ 0.246` and `−1` iff `φ_entry ≤ 0.0246` (`optdial_size_sweep.md` §2.12; `two_tier_entry.md` §1) |
| `--vm-entry-shape` term | — | — | **4,096** | `8,192` | — | §3.4; the raise's measured cheap band tops out at program 6,954 B, which 8,192 covers. `+2` is em-dashed — **M12**: revision 1's 13,312 came from a plan-row RECOMMENDATION PHRASE ("8-13 kB"), not a measurement |
| `--unroll=K` | — | — | — | — | — | **NOT A RUNG** — set BY the ladder rows above, never directly; §3.5 |
| `-fno-offset-skip` | — | — | **allow** | — | — | **GATE 3-adjacent, measured and FLAT**: `σ` = 1.30% median, whole distribution inside a 2% band — **fails `y`** (`optdial_size_sweep.md` §2.14) |
| `-fno-scan-edge` | — | — | **allow** | — | — | fails `y` — and `y` alone; see **N1** below and §10 |
| `-fno-altcls-merge` | — | — | **allow** | — | — | `σ` = **−2.40%**: wrong-signed; **GATE 2** independently (deny arm moves the refusal set, K45) |
| `-fno-altcls-factor` | — | — | **allow** | — | — | `σ` = **−0.56%**: wrong-signed |
| `--engine` | — | — | **auto** | — | — | **GATE 5** (up to 173,580× on the fail path) **AND GATE 2** — `--engine=dfa` refuses captures-default patterns (D44.6), a refusal-set move (**S4**) |
| `-fno-possessify` | — | — | — | — | — | **GATE 3**: size measured (`σ` = −1.69%, wrong-signed), TIME UNMEASURED (`opt_dial_inventory.md` §7.1 item 6) |
| `-fno-revdet` | — | — | — | — | — | **GATE 3**: size measured (a wash, −0.001% of the corpus), TIME UNMEASURED |
| `-fno-prefilter` | — | — | — | — | — | **GATE 3**: measured only through an engine-changing proxy |
| `-fno-atomic-discharge` | — | — | — | — | — | **GATE 3**; and the axis it moves is engine selection |
| `-fno-splice-calls` | — | — | — | — | — | **GATE 4** — sign reverses with the subject population |
| `-fno-prefilter-collapse` | — | — | — | — | — | **GATE 4** — same |
| `-fno-counter` | — | — | — | — | — | **NOT A RUNG** — a correctness-shaped floor |
| `-fno-length-prune` | — | — | — | — | — | **NOT A RUNG** — trades nothing: denial is byte-identical |
| `-fno-start-pinned` | — | — | — | — | — | **PURE WIN** — −3,232 B per pinned artifact AND ×1.985 faster (`opt_dial_inventory.md` §2.19). **The row B3 found missing.** |
| `-fno-alt-island` | — | — | — | — | — | **PURE WIN** — max growth 1.03×, 0 refused, prefix-free islands at 0.140-0.175× of chain time (`opt_dial_inventory.md` §2.20). **The second row B3 found missing.** |
| `-fno-cls-fold` | — | — | — | — | — | **NOT A RUNG — off by RULING** (Frank 2026-09-11); absorbed into λ, §4.6 |
| `-fno-startpos-guard` | — | — | — | — | — | **GATE 1** — the two arms disagree about answers; PERMANENTLY flat |
| `-fno-size-term` | — | — | — | — | — | **NOT A RUNG** — it is the MECHANISM the two ladder rows parameterise |
| emitted-size caps | — | — | — | — | — | **NOT A RUNG** — raise-only refusal boundaries; a dial that lowered one would manufacture refusals |

**Six axes move** (λ, the ladder's two parameters, premul, anchored-dfa,
tiered-entry, the entry-chain term — seven rows). **Twenty rows do not,
and each carries one of seven reason codes** — which is the difference
between an allowlist and a list of things nobody got round to.

**Three cells deserve to be read twice.**

**`-fno-anchored-dfa` at `−2` is OUT at `x₂` = 2.00 and this is the
design's biggest single change from revision 1.** Its ledger's five splits:

| split | n | vs VM (with reverse pass) | vs VM (reverse deleted) | `m` = the cost of denial |
|---|---:|---:|---:|---:|
| ALL | 85 | 2.133× | 1.281× | 1.665× |
| MATCHING | 40 | 2.077× | 1.046× | **1.986×** |
| NON-MATCHING | 45 | 2.301× | 1.981× | **1.161×** |
| matching, short (<256 B) | 35 | 1.207× | 0.571× | **2.114×** |
| matching, long (≥256 B) | 5 | 2.114× | 1.066× | 1.983× |

Revision 1 quoted the MATCHING row's 1.986 as "≈1.99" and admitted the
cell "by a margin of half a percent". Under gate 6 the cell's `m` is
**2.114×** and the margin is −5.7%. One population (non-matching, 1.161×)
sits inside the interval revision 1 called an empty hole; another (matching
short, 2.114×) fails `x₂` outright. **Two carried qualifications, neither
of which changes the direction:** the 1.161× split has `n = 45` against
`n = 35`, so the distribution is not tail-heavy on a small sample; and the
`m` column is a RATIO OF TWO MEASURED COLUMNS in a cost-isolation
experiment, which is the next paragraph.

**AND THIS ROW'S TIME NUMBER HAS NEVER BEEN MEASURED ON THE SHIPPED FLAG.**
`opt2_anchored_match_measurement.md` measured a hand patch DELETING the
`\z` artifact's reverse pass, as a cost isolation, and RECOMMENDED
`[ENG-ABS]`'s unwrapped anchored entry as the lever — which was
subsequently built and is what `-fno-anchored-dfa` denies. The ratio is
therefore a PROXY for the axis, measured on the mechanism's predecessor.
Nobody has run `rx_match` default against `-fno-anchored-dfa` on those 85
subjects. **That A/B is owed (§10) and it is cheap**, and if the shipped
axis measures better than its proxy the `x₂` question in §0.1 may not
arise at all.

**`-fno-anchored-dfa` at `−2` is also safe against gate 2 only because
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
is one that gets removed. §6.3 lists it as not-covered.

**`-fno-scan-edge`'s flat row now rests on ONE argument where revision 1
claimed two (N1).** Revision 1 said the row "fails `y` AND `x₂` — flat on
both counts". Under §3.2's conversion its 2.71-3.03× is a THROUGHPUT ratio,
so its `m` is `1 + (1.71…2.03)·φ_scan`, which exceeds `x₂` = 2.00 only for
`φ_scan ≥ 0.493`. The `x₂` failure is therefore conditional and the row's
flatness rests entirely on `y` — which §10 already flags as this note's
weakest citation, because scan-edge's size cost is quoted absolutely
(+364…612 B per edge-carrying machine) and was never converted to a
fraction. **The independence revision 1 relied on is gone; the row is flat
on an INFERENCE, and it is the only flat row in the table that is.**

### 3.4 The `--vm-entry-shape` row is the TERM, and `+2` is now an em-dash

STEP 0 made this the dial's flagship row. It is the row that changed most
under scrutiny, and `opt_dial_inventory.md` §2.21's REVISION 2 block has
the full re-read. Four consequences land here:

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
3. **`+1` = 8,192 covers the measured band.** The plan row's own figures:
   the cells just above the term (program **5,183 / 5,985 / 6,954** bytes)
   cost **0.061-0.067 bytes per ns/call saved, five times better than the
   next cell up**. 8,192 admits all three with headroom and admits nothing
   beyond them.
4. **`+2` = 13,312 is WITHDRAWN (M12).** That number came from the plan
   row's sentence *"`--tune=speed` should RAISE `VM_INLINE_CHAIN_MAX_BYTES`
   into 8-13 kB"* — a recommendation phrase written before the rate table
   existed, promoted here into a cell of a table built specifically to
   forbid uncited cells. **The citation rule of §3.1 applied to its own
   flagship row.** There is no measured cell above program 6,954 B, so
   there is nothing for `+2` to cite, and the cell is an em-dash. Revision
   1 additionally called the raise "the better-measured rate of the two",
   which contradicts `opt_dial_inventory.md:573-577`: BOTH rungs' rates are
   cross-pair assemblies (`.text`/gcc measured INLINE÷SHARED, run time
   measured INLINE÷PLAIN), so neither is better-measured than the other.
   **What would fill `+2`:** extend ccd2's ladder above 6,954 program bytes
   and find where the 5× rate degradation actually begins. Named in §10.

### 3.5 `--unroll=K` is set by the ladder, and the ladder rows carry two disclosed dependencies

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

**The speed side is em-dashed (M13).** Revision 1 gave `+2` a bar of 0.70
and a threshold of 160,000 — i.e. "shrink less, go faster". On this row's
own citations the speed that buys is at most the 1-3% noise effect, which
fails `s` = 1.10 by an order of magnitude. A parameter proposed in §3.2 and
then applied to nothing is not a threshold; applied here it removes two
cells. The ladder is a SIZE-SIDE-ONLY row, mirroring §3.4's
speed-side-only one.

**One allowlist caveat, stated rather than buried:** the bar's rate is
measured at its ENDS (the K ladder's byte curve; "throughput exhausted by
K≈16") and not per bar VALUE. `artifact_size_term.md` §3.3's own
measurement of the bar is sharper than revision 1 credited — the two
ladder rows either side of 0.75 differ by **0.0073**, so the constant sits
inside a continuum rather than at a gap — which makes the intermediate
values (0.85, 0.95) interpolations along a measured continuum rather than
interpolations across a gap. They are still interpolations. A reviewer is
entitled to call this the weakest citation in §3.3 after scan-edge's, and
§9 Q4 offers Frank the narrower alternative (move only the threshold,
leave the bar at 0.75 everywhere).

#### 3.5a DEPENDENCY 1 — the DECLARED-CAPACITY FLOOR (M14)

**These two rows are admissible only because `artifact_size_term.md` §3.3a
exists, and revision 1 disclosed it nowhere.**

`K` is answer-identical in the LANGUAGE, not in the DEPTH: a smaller `K`
raises the per-iteration frame need, so the same `<PREFIX>_BT_FRAMES`
carries a SHORTER subject. Measured there: `^(a(?1)?b)$`'s
`.subject_ceiling` moves **512 → 341** between `--unroll=8` and
`--unroll=1`, and on a 684-byte subject **five cells** across
`tests/recursion/framebuffer.rxt` and `tests/recursion/d27/sr_depth.rxt`
MATCH at the default `K` and return a FRAMES GIVE-UP under `--unroll=1`,
at the DEFAULT budgets.

What makes the rows admissible is the FLOOR that entry adds: *a rung whose
artifact declares LESS capacity than the default `K`'s — on
`.frame_capacity` OR on `.subject_ceiling` — is not a candidate*, stamped
`capacity-declined`. **Without that floor these two rows would be a
`match → give-up` answer change that no flag asked for**, which is exactly
what §6.1's answer-identity acceptance is for and exactly what an
answer-identity sweep would catch only if its subjects were long enough.

**This is the same treatment §3.3 gives the `[K53-SELRETRY]` dependency,
and the entry itself models it** — which is why revision 1's omission is
a discipline failure rather than an oversight: the note it was citing had
already shown the shape.

#### 3.5b DEPENDENCY 2 — `−2`'s threshold turns a zero-inhabitant pin red for a non-defect (M14)

`artifact_size_term.md` §3.3a's floor is a FORWARD GUARD: over all 2,772
corpus patterns, 69 have a declared capacity that moves with `K` and **none
of the 69 has the counter rung**, so nothing in the corpus reaches the
floor today. `run_size_term.sh` **§7b pins that natural population at 0 and
says so loudly if an inhabitant appears.**

**Lowering the threshold from 120,000 to 40,000 at `−2` is precisely an
"inhabitant appears" event, and it is not a defect.** Measured on the
sweep's own committed baseline table
(`docs/dev/optdial_size_sweep/runs/baseline_size.tsv`, 3,478 rows,
115,198,573 bytes, reproduced by `opt_dial_inventory.md` §3.0's command):
**86 corpus artifacts are at or above 120,000 bytes today, and lowering the
threshold to 40,000 adds 81 more** — the ladder would run on 167 patterns
instead of 86, **a 1.94× population increase**, on shapes it has never run
on. `−1`'s 80,000 is the intermediate step.

Two consequences the implementation lane must not meet as a surprise:

1. **§7b's pin must be per-position, or it must be run at the dial's own
   threshold.** A pin taken at 120,000 is not a claim about a build at
   40,000. This is the check-staleness class `battriage_report.md`
   recorded one manifest over: *a check pinned against a parameter goes
   stale when a new surface moves that parameter, and its own failure
   message names the wrong cause.*
2. **M5 — the trial/abort machinery meets a new population.**
   `artifact_size_term.md` §2.2b's finding R1 is that a ladder attempt's
   refusal needs no `trial` flag, because `ctx_fail` unwinds to the one
   recovery point, `arena_free` runs on every retry path, and trials share
   nothing. **That argument is structural and does not depend on the
   population's size**, which is the honest reason to expect it to hold
   at 40,000. It is not a measurement, and the AST re-publication
   invariant the same section states is a real per-shape dependency. So
   §6.1b makes it a CHECK rather than an assertion: run the ladder's own
   acceptance at `−2`'s threshold over the whole corpus, which is 81
   patterns the ladder has never seen.

### 3.6 SENSITIVITY — re-derived under §3.2's conversion

The point of this section is that Frank's ruling should be informed by
which numbers matter. Under the corrected units, **different ones matter
than revision 1 reported**, and `x₁` is no longer inert.

**M3's fix first:** revision 1's table swept `x₁` to 2.20 while `x₂` sat at
2.00, violating the document's own nesting invariant (`x₁ < x₂`) in the
table built to test it. Every sweep below is capped at its neighbour.

| parameter moved | cells that flip | consequence |
|---|---|---|
| `y` 5% → **2.5%** | **none** | `-fno-offset-skip` (1.30%) still fails; scan-edge has no fraction to test either way |
| `y` 5% → **10%** | **one**: `-fno-tiered-entry` leaves the table entirely | its `σ` = 7.48% is the only one in the 5–10% band |
| `x₁` 1.10 → **1.05** | none, but every `−1` CONDITION tightens: premul `φ_scan ≤ 0.063`, tiered-entry `φ_entry ≤ 0.0123` | `x₁` moves conditions, not cells |
| `x₁` 1.10 → **1.50** (capped below `x₂`) | none, but premul's `−1` condition loosens to `φ_scan ≤ 0.630` and tiered-entry's to `φ_entry ≤ 0.123` | at `x₁` = 1.50 premul's `−1` cell is live for any plausible `φ_scan` |
| **`x₂` 2.00 → 2.12** | **ONE, and it is the largest lever in the table**: `-fno-anchored-dfa` enters `−2` | 10.64% of every byte pcrec emits. **This is the single most consequential threshold value in the note** |
| `x₂` 2.00 → **1.80** | **none** | premul's `−2` survives to `x₂` = 1.794 at `φ_scan` = 1 and below it for smaller `φ_scan`; tiered-entry's condition tightens to `φ_entry ≤ 0.197` |
| `x₂` 2.00 → **4.00** | **none** | a PLATEAU above 2.114: the next penalty up is scan-edge's, which fails `y` anyway |
| `z_mid` 26% → **20%** | none in the table; re-opens §3.2a window A's one inconsistency | see §9 Q2b |
| `t_mid` 1.02 → **1.10** | none in the table; closes §3.2a window B's one inconsistency | cls-fold's 1.095 passes at 1.10 and fails at anything below |
| `Z₁` 1.30 → **1.35** | **one**: λ(+1) becomes 256 = λ(+2), collapsing the speed side's only distinguishing row | §4.3's window is `[1.229, 1.342)` |
| `s` 1.10 → **1.03** | **two**: both `[ART-SIZE]` ladder cells re-enter the speed side | the only parameter that could give `+1`/`+2` a second distinguishing row |

**Four readings a ruling should take from this.**

**(a) `x₂`'s real question is a NUMBER, not a word.** Revision 1 said "the
ruling's real question is not 'what is x₂' but 'is a doubling of match time
acceptable'". Under gate 6 that is exactly backwards: 2.00 and 2.12 give
different tables, and the gap between them is one measured population's
5.7%. Q2 asks for the number.

**(b) `x₁` is NOT inert.** Revision 1 concluded "no value of `x₁` below
1.794 changes anything". That rested on the unit error: under the
conversion `x₁` sets the CONDITION under which two rows enter `−1`, and it
sets it continuously. There is no hole and nothing is inert.

**(c) `y` is still the only parameter whose doubling removes a row**, and
the row is `-fno-tiered-entry`, which is already the conditional one. If
`φ_entry` turns out large, that cell goes anyway.

**(d) The speed side turns on `Z₁` and `s`, and both are unruled.** With
`Z₁` = 1.30 and `s` = 1.10 the speed side has one distinguishing row (λ)
and it is a reservation. That is the whole content of §0.1's "`+2` is
identical to `+1` at the first build".

---

## 4. λ — FIVE PINNED FRONTIER CONSTANTS (D103 point 4; S1's selection rule DEMOTED to the rubric that derived them)

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

**D103's own text**: *"λ becomes five PINNED frontier constants from
cls_tree_study's verified table."* §4.1-§4.3 below are UNCHANGED as
ARITHMETIC — the verified frontier table, the caps, and the worked
selection on `\p{L}` all survive exactly as revision 2 derived them — and
they are reframed as what they now are: **THE RUBRIC that chose the five
constants once, not a live per-class mechanism the compiler runs.** The
five values, pinned:

| position | λ | condition |
|---|---:|---|
| `−2` | **4** | unconditional — λ=0 is dominated at every `φ_cls` (§4.3) |
| `−1` | **16** | pinned CONSERVATIVELY at the middle's own value, since the alternative (λ=4) is admissible only for `φ_cls ≤ 0.161` — an UNMEASURED condition. `−1` and `0` are therefore the SAME pinned constant until `φ_cls` is measured, at which point a change to `−1` alone is its own ruled diff, not an automatic promotion |
| `0` | **16** | unconditional — derived from the size-minimal frontier point alone (§4.4), no `φ_cls` dependency |
| `+1` | **64** | unconditional — a size BUDGET (`Z₁` = 1.30×), no `φ_cls` dependency |
| `+2` | **256** | unconditional — a size BUDGET (`Z₂` = 2.0×), no `φ_cls` dependency |

**One correction §4.1 point 3 needs, now that the constants are pinned
rather than live.** Revision 2 said a cost-model recalibration "discharges
automatically" because the cap test and the objective read the same
model. That is still true of the ARITHMETIC — a recalibration would still
move the argmin the same way it always did — but it is no longer true of
GOVERNANCE: under D103 a recalibration is exactly "a measurement lands",
and a measurement landing must NOT silently move a pinned cell. A future
recalibration is evidence for a NEW proposal, re-argued by this same
rubric and re-ratified as its own diff — never an automatic table update.
The warning revision 1 gave (all five values need hand re-derivation on
recalibration) turns out to have been the right OPERATIONAL answer for
the wrong reason: not because the mechanism cannot re-derive them
automatically, but because D103 says it must not.

### 4.1 What revision 1 did, and why the selection rule was the right ARGUMENT (kept as the rubric, not the mechanism)

Revision 1 assigned **five hard-coded λ constants** (0 / 12 / 16 / 64 /
256), then discovered in its own §4.4 that a constant cannot express a
CAP — the discrete rule's `x₂` refuses a catastrophic switch regardless of
savings, while λ=0 is a pure objective that will accept any number of probe
operations to save one byte — and bolted a cap on beside the constants.
That left the design carrying a constrained-path problem PARALLEL to the
DP, five numbers one of which (12) was not a swept frontier point at all,
and a standing warning that all five must be re-derived by hand if the
study's cost model is ever recalibrated.

**MANAGER-RULED (S1), and it is the general-mechanisms rule applied to
this design's own λ row — READ AS THE RUBRIC THAT PRODUCED THE FIVE
PINNED CONSTANTS ABOVE, not as the live mechanism (D103 point 4 re-pins
this one level up: the same lens that killed a per-axis
`PCREC_TUNE_SET` bit in §1.3 does not exempt λ from D103's own
pinned-contract rule — a position carrying a live cap that reselects on
every recalibration is exactly the "cell moves because a measurement
landed" shape D103 forbids elsewhere in this table):**

> **λ IS NOT A CONSTANT PER POSITION, AND THE SELECTION ARGUMENT BELOW IS
> HOW THE FIVE CONSTANTS ABOVE WERE CHOSEN. A DIAL POSITION CARRIES A CAP,
> AND λ IS SELECTED — per class, by the same DP, over the same swept
> frontier — AS THE POINT THAT BEST SERVES THE POSITION'S DIRECTION
> SUBJECT TO THAT POSITION'S CAP.** Once selected and ratified, the result
> is pinned; a future recalibration re-runs this argument as a NEW
> proposal, not as a live re-selection.

Four things fall out at once, and each of them was a separate open item in
revision 1 — each now describing the RUBRIC's own correctness, not a
runtime property of the compiler:

1. **There is one mechanism, not two.** The cap is not bolted beside the
   DP; the cap is the position and the DP is the solver. Revision 1's §4.4
   ratio test — a coherence check between two mechanisms — is not needed,
   because the mechanisms are now the same shape: *optimise one axis
   subject to a bound on the other*, which is what the discrete rule has
   always been.
2. **λ=0's inversion dissolves, and Q5 with it** (§4.3). A frontier point
   DOMINATED ON BOTH AXES can never be the argmin of either objective, so
   the rubric never PROPOSES it. Revision 1 needed an object-size sweep to
   decide between λ=0 and λ=4; the rubric decides it from data already
   committed — a proposal ratified once, at this revision, into the pinned
   `−2` = 4 above, not a live re-decision on future data.
3. **The recalibration warning is answered by GOVERNANCE, not by
   arithmetic, and D103 is what supplies the governance.** Revision 1
   warned that all five λ values must be re-derived by hand if the study's
   cost model is recalibrated. Under the rubric the cap test and the
   objective read the SAME cost model, so a recalibration would move a
   LIVE selection with it automatically — which is exactly the property
   D103 does not want in a pinned table. A recalibration is instead a new
   measurement that argues a NEW proposal through this same rubric,
   ratified as its own diff. Nothing is hand-derived in the ARGUMENT;
   nothing moves SILENTLY in the CONTRACT.
4. **`−1` stops being a hand-chosen number.** λ = 12 was revision 1's own
   "weakest number on this page" precisely because it was not a swept
   point. There is no λ = 12 any more.

### 4.2 THE CAPS, IN OPS UNITS, DERIVED FROM THE MATCH-TIME BOUNDS (M7)

**This is where revision 1's unit pun lived and it is fixed by
construction.** Revision 1 wrote *"κ is `x₂`, the same parameter"* — but
`κ` bounds PROBE OPS and `x₂` bounds MATCH TIME, and they coincide only at
`φ_cls = 1`. Identifying them silently asked Frank a match-time question
that set an ops cap, and it manufactured `\p{L}`'s "1.91× just inside
2.00×" near-miss out of the identification rather than out of the data.

**The conversion, shown rather than asserted.** Let `P₀` be the middle's
probe-op count for a class and `P` a candidate's. If class-membership
probing is a fraction `φ_cls` of match time, then moving from `P₀` to `P`
multiplies match time by `1 + φ_cls·(P/P₀ − 1)`. Requiring that to stay
inside a match-time bound `x` gives

```
        P / P₀  ≤  κ(x)  =  1 + (x − 1) / φ_cls
```

**Three consequences a reader should check.**

- **`κ ≥ x` always, with equality only at `φ_cls = 1`.** The ops cap is
  LOOSER than the naive identification, never tighter — so revision 1's
  identification was conservative in direction and wrong in kind.
- **The SIZE notches' caps need `φ_cls`; the SPEED notches' do not.** A
  speed notch's cap is a size BUDGET (`Z₁`, `Z₂`), and size is measured in
  bytes on both sides of the comparison. Only the time side needs
  converting. That asymmetry is a property of Frank's rule-shape, which
  bounds time on one side and size on the other.
- **The caps below are PROVISIONAL, pending `φ_cls`.** They are stated at
  `φ_cls = 1`, the TIGHTEST admissible reading (since `φ_cls ≤ 1` only
  loosens them), so a cell that qualifies at the stated cap qualifies at
  every `φ_cls`.

| position | cap | in ops, against `P₀` | provisional value at `φ_cls = 1` |
|---|---|---|---|
| `−2` | `κ(x₂) = 1 + (x₂−1)/φ_cls` | `P ≤ κ·P₀` | `κ ≥ 2.00` |
| `−1` | `κ(x₁) = 1 + (x₁−1)/φ_cls` | `P ≤ κ·P₀` | `κ ≥ 1.10` |
| `0` | — | pinned by ruling; §4.4 | λ = 16 |
| `+1` | `Z₁` | `bytes ≤ Z₁ · bytes(middle)` | 1.30× |
| `+2` | `Z₂` | `bytes ≤ Z₂ · bytes(middle)` | 2.0× |

### 4.3 THE RUBRIC'S RULE, and what it picked on `\p{L}` (the values now pinned at §4's top)

**THE RUBRIC, stated once — this is the argument that produced the five
pinned constants, not a rule the compiler evaluates:**

> At position `p`, over the swept frontier points, λ(p) is:
> - at a SIZE position: **`argmin` total bytes subject to `ops ≤ κ(p)·P₀`**;
> - at a SPEED position: **`argmin` ops subject to `bytes ≤ Z(p)·bytes(middle)`**;
> - at the middle: pinned by ruling (§4.4).
>
> Ties break toward the SMALLER λ. The frontier is the study's own swept
> set — `λ ∈ {0, 4, 16, 64, 256, ∞}` — because those are the λ values at
> which a matcher has actually been BUILT and verified against a reference
> on all 1,114,112 code points. A λ the study never swept is a λ nobody has
> an artifact for.

`cls_tree_study.md` §5.2's frontier for `\p{L}`, reproduced unchanged (the
r60 num critic verified this table exact):

| λ | sections | text | rodata | total bytes | ops |
|---:|---:|---:|---:|---:|---:|
| 0 | 19 | 1,392 | 2,926 | 4,318 | 206 |
| 4 | 17 | 1,168 | 3,028 | **4,196** | 175 |
| **16 (middle)** | 27 | 1,184 | 3,175 | 4,359 | **108** |
| 64 | 25 | 1,076 | 4,283 | 5,359 | 78 |
| 256 | 25 | 1,072 | 4,778 | 5,850 | 72 |
| ∞ | 11 | 688 | 24,308 | 24,996 | 66 |

**Worked, with `P₀` = 108 and `bytes(middle)` = 4,359:**

- **`−2`.** `κ ≥ 2.00` ⟹ cap ≥ 216 ops. Every frontier point qualifies
  (the largest is 206). `argmin` bytes over all six is **λ = 4** at 4,196 B
  / 175 ops. **λ=0 is never selected, at any `φ_cls`, because it is
  dominated** — 4,318 B and 206 ops against 4,196 B and 175 ops. **Q5
  DISSOLVES**: the question "is `−2` 0 or 4?" is answered by the mechanism,
  from the study's own committed table, and re-answered automatically if
  the 3% byte-model error the study names ever moves.
- **`−1`.** `κ = 1 + 0.10/φ_cls` ⟹ cap = `108·κ`. λ=4 (175 ops) qualifies
  iff `108·κ ≥ 175`, i.e. `κ ≥ 1.6204`, i.e. **`φ_cls ≤ 0.161`**. Above
  that share the qualifying set is `{16, 64, 256, ∞}` and `argmin` bytes is
  **λ = 16 — the middle**. So **λ(−1) = 4 if `φ_cls ≤ 0.161`, else the
  middle**: a falsifiable sentence about one measurable share, exactly the
  shape §3.3's `†` cells take, and the λ row's own contribution to §0.1's
  re-derived headline.
- **`+1`.** `Z₁` = 1.30 ⟹ budget 5,667 B. Qualifying: `{0, 4, 16, 64}`
  (256's 5,850 B is over). `argmin` ops = **λ = 64** at 78 ops.
- **`+2`.** `Z₂` = 2.0 ⟹ budget 8,718 B. Qualifying adds 256; ∞'s 24,996 B
  is far over. `argmin` ops = **λ = 256** at 72 ops.

**AND THE SELECTION EXPLAINS WHY `Z₁` MOVED FROM 2.0 TO 1.30.** The
frontier's breakpoints, computed from the table above: λ=64 needs
`Z ≥ 5,359/4,359 = 1.229`; λ=256 needs `Z ≥ 5,850/4,359 = 1.342`; λ=∞
needs `Z ≥ 24,996/4,359 = 5.734`. Revision 1's `Z₁` = 2.0 and `Z₂` = 4.0
both land in `[1.342, 5.734)` and therefore **select the same point**,
making `+1` and `+2` identical on the one row that was supposed to
separate them. The only window that separates them is
**`Z₁ ∈ [1.229, 1.342)`**, which is why `Z₁` = 1.30. That is derived from
the study's frontier, not chosen.

**The ∞ cell excludes itself, which is better than being excluded by
taste.** Revision 1 argued `+2` stops at 256 from a marginal-rate cliff:

| step | Δbytes | Δops | bytes per op |
|---|---:|---:|---:|
| 4 → 16 | +163 | −67 | **2.4** |
| 16 → 64 | +1,000 | −30 | **33.3** |
| 64 → 256 | +491 | −6 | **81.8** |
| **256 → ∞** | **+19,146** | **−6** | **3,191** |

The last step is **39× worse than the one before it for the identical six
operations** (this table is exact and is preserved). Under selection the
argument is no longer needed as a judgment: ∞ costs 5.734× the middle's
bytes, so no `Z₂` below 5.734 admits it, and the cliff table now EXPLAINS
the exclusion rather than performing it. `cls_tree_study.md` §5.3 item 4's
advice — "the dial's speed notches should stop before it" — is a
consequence of the rule instead of an input to it.

### 4.4 The middle is DERIVED, and `t_mid` plays no part in it (M11)

The study calls λ=16 its "mid" policy. That is a name, and a name is not a
derivation. The middle is derived from the DEFAULT-MIDDLE PRINCIPLE plus
the measured frontier, and it lands on the same value — which is worth
saying explicitly, because two routes agreeing is evidence and a name is
not.

**The derivation, under the selection framing** (`argmin` ops subject to a
size budget, against the SIZE-MINIMAL frontier point — λ=4 at 4,196 B,
because "near-free on the axis it spends" means near-free against not
spending at all):

| λ | bytes vs λ=4 | ops vs λ=4 | inside `z_mid` = 26%? |
|---:|---:|---:|---|
| 16 | **+3.88%** | **−38.3%** | ✓ |
| 64 | +27.7% | −55.4% | ✗ |
| 256 | +39.4% | −58.9% | ✗ |
| ∞ | +495.7% | −62.3% | ✗ |

**λ=16 buys 38% of the probe ops for under four percent of the bytes**,
and λ=64 costs 28% of bytes and is correctly not the middle. So **λ(0) = 16
is the ops-minimal frontier point inside the middle's size window**, which
is a derivation, and it agrees with the study's naming, which is a check.

Revision 1 measured this against λ=0 rather than λ=4 (+0.95% bytes for
−47.6% ops). **Both tables are exact and both give λ=16** — the r60 num
critic verified revision 1's — but λ=0 is not the size-minimal point under
the selection rule, so the λ=4 reference is the one this section now uses.
Revision 1's is kept in the record because the agreement of two references
is itself a robustness result.

**M11 — the honest statement about which half of the middle principle did
the work.** Frank's principle has two halves: a speed optimization must be
near-free in SIZE, and a size optimization must be near-free in TIME, with
the second half stricter. **λ(0) = 16 is derived from the FIRST half
alone.** `t_mid` — the strict half — plays no part: any value of `t_mid`
gives the same answer, because nothing in this derivation reads a time
bound. Revision 1 presented the middle's λ as the design's one prospective
application of the whole principle; it is an application of half of it.

**What would complete it:** `φ_cls`. With `φ_cls` measured, λ=16's ops
cost against λ=4 (108 vs 175, a 38.3% REDUCTION) converts to a match-time
SPEEDUP, at which point the middle's λ can be checked against `t_mid`'s own
direction as well — and `-fno-cls-fold`'s ×1.095 (§3.2a window B) becomes
comparable to it, since both are then the same quantity on the same axis.
Until then the λ row is admitted under one half of the principle and says
so.

**λ is still the only row in this design admitted under the middle
principle PROSPECTIVELY rather than grandfathered past it** — every
discrete row's middle cell is today's default by Frank's ruling, and §3.2a
finds that one of them fails each window. That remains true and is the
smaller claim revision 1 should have made.

### 4.5 COHERENCE with the discrete table — what is now structural, and what is not

Revision 1's §4.4 posed a ratio test (`ρ/σ` constant across positions) and
reported a NEGATIVE result at the extremes. **The test is retired and the
result with it**, for the reason S1 gives: the two mechanisms now have the
same shape, so coherence is structural rather than something to measure.
Three specific retractions, because a reader who remembers revision 1 needs
them:

- **M9 is moot.** Revision 1's ratio test computed `ρ(λ=4)` while the
  design proposed λ=12, substituting one frontier point for another
  without saying so. There is no λ=12 and no ratio test.
- **N3 is moot.** Revision 1's `σ(p) = y/(x−1)` gloss ("a min-size caller
  will spend less size to buy time") read backwards — a min-size caller
  spends TIME to buy SIZE. The quantity is gone.
- **M8 is APPLIED, not dissolved, and it runs against this note.**
  Revision 1 claimed "the two halves of the dial agree `−1` is nearly
  empty, and they arrive there INDEPENDENTLY". They do not: **both halves
  read `x₁`.** The discrete rows' `−1` conditions are `x₁`-derived and
  λ(−1)'s cap is `κ(x₁)`, so the agreement is one parameter seen twice.
  **The corroboration claim is WITHDRAWN.** What survives is weaker and
  true: the two halves agree because they are the same rule, which is the
  point of S1 and is not evidence about the population.

**What IS a genuine cross-check, and it is the one revision 1 flagged as
suspicious:** revision 1 observed `\p{L}` at λ=0 landing at 1.91× against a
2.00× cap and `-fno-anchored-dfa` at 1.99× against the same 2.00×, and
declined to treat the agreement as corroboration because the two share no
mechanism. **That instinct was right and the coincidence has evaporated in
both directions**: under §4.2's conversion the λ figure was never a
match-time ratio at all (the 1.91 is `206/108`, an OPS ratio), and under
gate 6 the anchored-dfa figure is 2.114 rather than 1.99. Two numbers that
looked like a pattern were two different quantities, one of them a point
estimate of a distribution. **The lane's own scepticism about its own
result is the thing that held.**

### 4.6 What λ absorbs

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
principle. Under S1 it is stronger still: a new kit member changes what the
SELECTION can choose without changing the dial's surface at all, because
the position carries a cap and not a value.

### 4.7 What the selection COSTS — DISSOLVED FOR THE COMPILER BY D103's PINNING, kept as the rubric's own cost record

**D103's pinning removes this section's live cost from the shipped
compiler.** Everything below describes what a LIVE per-class selection
under a cap would cost, which was the right question while §4.1-§4.3
were a runtime mechanism. Under D103 the compiler never runs the
selection at build time at all: `[CLS-TREE]` reads the pinned constant
for the requested position (§4's table) and solves the DP ONCE, with
that one fixed λ — the same cost as any single-λ build, and no different
from what revision 1's five hard-coded constants would have cost. The
six-frontier-point cost below was the rubric's OWN cost, paid once by
this note (and by whoever re-argues a cell later), never paid per
compile. It is kept for that reason — a future re-argument re-pays
exactly this cost, and it is worth having named.

The selection needs the DP solved at every swept frontier point, not at
one, WHEN RE-ARGUING A CELL. `cls_tree_study.md` §6 measures C discovery
at the middle policy at
**mean 4.19 ms / max 25.86 ms** over the 60 largest property sets, against
the 144 ms `build/pcrec` already spends compiling that one pattern — from
which the study concludes CONSTRAINT 2's pre-analysis cache is NOT
triggered.

**Six frontier points is up to 6× that, and it was the cost of ARGUING the
five constants above — not the cost of using them.** On the worst real
set that argument cost ~155 ms against 144 ms of existing compile time,
paid once by this revision (and payable again, at the same price, the
day a cell is re-argued). Three things, in order, now answered by D103
rather than left open:

1. **The SHAPE that mattered — a position carries a cap, λ is whatever
   satisfies it — is what produced the pinned table, and S1's rule is
   preserved as exactly that argument.**
2. **`[CLS-TREE]`'s per-compile question is no longer "per class or per
   reference set" — it is moot.** Each position now carries ONE fixed λ
   (§4's table), so `[CLS-TREE]` runs the ordinary sectioning DP under
   that one constant, per class, at the SAME cost `cls_tree_study.md` §6
   already measured for the middle policy (mean 4.19 ms / max 25.86 ms) —
   identical to what revision 1's five hard-coded constants would have
   cost, and with none of §4.1's per-class dissolution of the λ=0
   inversion lost, because that dissolution happened once, in the
   argument, not at every compile.
3. **The six-frontier-point measurement stays owed, but to a different
   customer.** It is what a future re-argument of a contested λ cell
   would cost, not a cost `[CLS-TREE]`'s shipped compiler ever pays. It is
   a re-run of an instrument that already exists (`discover.c`), costs one
   lane-hour, and is owed to whichever lane next re-argues a cell — never
   to a compile.

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
on it and §4 has just established that the ordinal is the stable surface
while the λ behind it is selected per class.

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
`tune` is precisely that case, and the rule already covers it.

**M16 removed this section's one inconsistency.** Revision 1 refused the
`rx_info` mirror on D77 (build it when a consumer asks) and in the same
document landed a `PCREC_TUNE_SET` bit with no consumer named — two
standards, one note. The bit is dropped (§1.3) and the two decisions now
rest on the same rule.

### 5.3 `abi`: this IS an event, and the site list is found BY GREP

A new unconditional `#define` in every emitted artifact is emitted
scaffolding, so D76/D94's ritual applies in the same change: **`abi` 25 →
26** (`src/gen/emit_dfa.c:1888` is the value's own site), with the identity
gate's (B) whole-file pin re-pinned, and the site list found by grepping
the tree for the CURRENT number's readers — never a hand-enumerated four
(D94, whose own 2026-09-01 instance missed a fifth reader in
`match_api.md`).

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

#### 5.3a THE SIZING ARGUMENT IS A CHECK BY NAME, NOT A PERCENTAGE (M2, M6)

Revision 1 argued the added line is *"~30 bytes … against a corpus baseline
of 115,198,573 bytes — about 0.00009%. It is far below the artifact-size
tripwire's resolution."* **Two things are wrong with that and the second is
the one that matters.**

**M2 — the digit.** 30 / 115,198,573 = 2.6 × 10⁻⁷, i.e. **0.000026%**, not
0.00009%. The direction is unchanged. But comparing ONE artifact's added
bytes against the WHOLE CORPUS's total is a comparison that cannot fail, so
the honest corpus-wide figure is the one to state: **~30 B × 3,478
artifacts ≈ 104 KB, 0.091% of the baseline.**

**M6 — the argument's SHAPE is the one D94's addendum distrusts.** An
aggregate percentage is exactly what a byte-exact manifest does not care
about. The obligation is a CHECK BY NAME:

- **`tests/codegen/manifests/m5_stage1_stamps.tsv` carries TEN
  `EMITTED_BYTES` rows** (patterns `a`, `abc`, `a(b|c)+d`, `(a)(b)(c)`,
  `[a-z]+@[a-z]+`, `^foo$`, `\bword\b`, `(?i)HeLLo`,
  `cat|dog|cow|calf|camel`, `(\w+)\s+\1`). **All ten move, by exactly the
  stamp's own byte count**, which is computable rather than observable:
  `#define RX_TUNE "balanced"` plus its newline is **27 bytes** at the
  default `rx` prefix, and 23 / 27 / 27 / 24 / 28 across the five tokens
  (`"size"` … `"max-speed"`). The check is therefore a POSITIVE assertion —
  each row moves by the predicted delta — not a re-record, and a row that
  moves by anything else is a finding.
- **`tests/size/check_size_tripwire.sh`'s pins and its unpinned-max guard
  (`MAX_SIZE_BYTES` = 1,400,000)** read `docs/dev/artifact_size_log.tsv`,
  whose per-row counts all move by the same 23-28 B.
- **The two readers may not agree on the delta**, and the implementation
  must compute it per reader rather than once: the size log's count is
  comment-EXCLUDED, and under `[M6-READ]`'s commented-artifact style the
  stamp arrives with a comment line that a comment-INCLUSIVE reader counts
  and a comment-exclusive one does not. *Two byte-count readers with
  different definitions of "byte" is the same class as two surfaces with
  different definitions of "status"* — `docs/CLAUDE.md`'s wave-E entry, one
  quantity over.
- **AND THERE IS A NAMED CORPUS ARTIFACT WITH 75 BYTES OF HEADROOM AGAINST
  A HARD CAP.** §6.2 carries it, because it is the refusal-set check's
  witness rather than the sizing note's, and it refutes the "far below the
  resolution" complacency outright.

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

**AND ANSWER IDENTITY IS BLIND TO A MISWIRED POLICY TABLE** — which is B1,
the panel's first blocker, and §6.1a.

### 6.1a THE MECHANISM-STATE CROSS-CHECK (B1)

**The problem, stated precisely.** Most rows in §3.3 are independently
answer-preserving by construction: that is the allowlist's whole point. So
an artifact built at `−2` that mistakenly denied `-fno-tiered-entry` where
the table says `-fno-premul-table` would pass every answer check in the
tree, at every position, forever. **A sweep that only compares answers
cannot see the table it is sweeping.** Worse, the stamp does not help: the
stamp records what was REQUESTED, and the defect is between the request and
the build.

**The check, in `tests/codegen/run_premul_table.sh` /
`run_search_pinned.sh`'s shape** — recompute the property from the EMITTED
TEXT and compare it against an independently derived expectation:

> **For each of the five positions, compile a witness set and RECOVER each
> moving mechanism's ACTUAL state from the artifact's emitted C, then
> compare the recovered set against the position's promised cell set as
> the SPEC states it.** Never from the stamp, and never from the flag word
> the CLI built — both are upstream of the defect.

The five recoveries, one per moving row, each naming what in the text
carries it:

| row | recovered from the emitted text by |
|---|---|
| `-fno-premul-table` | whether the transition table's entries are multiplied by the row stride — `run_premul_table.sh` already does exactly this |
| `-fno-anchored-dfa` | presence of the SECOND (anchored) machine's transition table and its accessor block |
| `-fno-tiered-entry` | presence of the deep-tier `noinline` function and the two-tier dispatch in `<prefix>_search` |
| `--vm-entry-shape` term | which of the four entry-chain rungs the emitted entry takes (ccd2 §3.4's own object-code properties, read from the source shape) |
| `[ART-SIZE]` ladder bar + threshold | the selected `K`, recovered from the body-copy count, cross-read against `_UNROLL_K_WHY` — and `capacity-declined` must be a legal outcome at `−2` (§3.5a) |

**The expectation side must not share a source with the check.** The
promised cell set is read from `docs/spec/tuning.md` §5's table (the
CONTRACT), not from the `src/` table the compiler consults — otherwise the
check compares the implementation to itself, which is
`docs/dev/learnings.md` §3's standing failure and the exact shape §3.5(a)
of the inventory already caught in this design's own STEP 0.

**Named candidate sabotage rows (checks-6), with what each must break:**

- **SAB-D1 — SWAP TWO ADJACENT POSITION COLUMNS** in the compiler's policy
  table (`−1` and `−2`). Every answer check stays green; the cross-check
  must fire on the `−2` witness's premul state and on both ladder
  parameters. This is the row that proves the check is not vacuous.
- **SAB-D2 — DENY THE WRONG BIT AT ONE POSITION** (`−2` sets
  `-fno-tiered-entry`'s bit where the table says `-fno-premul-table`). Two
  cells wrong at once, in opposite directions, so an arm that counted
  denials rather than identifying them would pass.
- **SAB-D3 — DROP ONE LADDER PARAMETER** (the dial sets the bar and leaves
  the threshold at its default). The two parameters move together by §3.5's
  fold; an arm reading only one of them passes.

Each row is born with its `SAB_REACH` / `SAB_REACH_POP` declarations
verified in BOTH directions, per the house rule — the `[MECH-REACH]`
lesson, and the one this design is most exposed to, since three of its five
witnesses are position-specific.

**N2 — the cheap first half, and it runs before any of the above.**
`<PREFIX>_TUNE`'s value is (a) a member of the closed five-token set and
(b) the token for the position actually requested. That is a two-line arm
with no compile of its own, it catches a whole class of alias-table
defects, and it is a PRECONDITION of the cross-check rather than a
substitute for it: the cross-check reads the position off the stamp to know
which cell set to expect, so a wrong stamp would make it check the wrong
row and pass.

### 6.1b THE `−2` LADDER ARM (M5, §3.5b)

Separate from the cross-check, because it is a population question rather
than a wiring one: **run the `[ART-SIZE]` ladder's own acceptance
(`run_size_term.sh`, including its §7/§7b arms) at `−2`'s threshold of
40,000 over the whole corpus.** The population is 167 patterns against
today's 86 — **81 shapes the ladder has never run on** — and the two things
to watch are named in §3.5b: §7b's zero-inhabitant pin, which may go red
for a legitimate reason, and the trial/abort machinery, whose sufficiency
argument is structural and unmeasured at this population.

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

**The check this needs, and it is not the axes sweep.** The axes sweep
compares ANSWERS on patterns that compile. A refusal-set move is precisely
the thing it routes around via `REFUSAL_PATTERN`. So the dial needs its own
arm: **the set of refusing patterns must be identical across all five
positions, compared as a SET of `file:line` keys and not as a count.** A
count-only comparison passes when one pattern starts refusing and another
stops — and this design has two rows (`anchored-dfa`, the caps) whose
hazards run in OPPOSITE directions, so a count is the one shape of check
that both could slip through at once. The sweep's own `RXTDUMP` already
emits what this needs (`optdial_size_sweep.md` §0 used it for exactly this
cross-check, K35).

#### 6.2a THE POPULATION — a measured PUSHBACK on B2, and B2's fix adopted anyway

**The panel's B2 said this check has an "(almost certainly) EMPTY corpus
population (p99 artifact 14,364 B vs 500K/1M caps)". That premise is a UNIT
MISMATCH of the same class as M7, and the measurement says otherwise.**

`artifact_size_census.md`'s 14,364 B is a **p99 `.o` OBJECT size** over
2,488 artifacts. `PCREC_MAX_EMIT_BYTES` (1,000,000) and
`PCREC_MAX_VM_EMIT_CODE_BYTES` (500,000) are **comment-excluded emitted C
SOURCE bytes** (D84). Comparing them is comparing two quantities that
differ by roughly the object/source ratio. Measured on the same quantity
the caps use — `docs/dev/optdial_size_sweep/runs/baseline_size.tsv`, 3,478
rows, the sweep's own committed baseline:

| statistic | value |
|---|---:|
| median artifact | 23,557 B |
| p99 artifact | 393,733 B |
| ≥ 120,000 B | 86 artifacts |
| **largest artifact** | **999,925 B** — `tests/utf8/axis12_scripts.rxt:296` |
| **headroom against `PCREC_MAX_EMIT_BYTES`** | **75 bytes** |

**One shipped corpus artifact sits 75 bytes below a hard refusal cap, and
the unconditional `RX_TUNE` stamp is 23-28 of them (§5.3a).** That is not a
refusal — 27 bytes leaves 48 — but it is two orders of magnitude away from
"far below the tripwire's resolution", and it is the artifact-size claim
§5.3 should have made.

**B2's FIX IS ADOPTED ANYWAY, and for a better-stated reason than B2 gave:
`n = 1` is not a population.** The one inhabitant is a `dfa` artifact, so
no dial position grows it at the first build (the entry-chain term is a VM
row; λ is a reservation; the ladder's speed side is em-dashed) — which
means the natural population for the GROWTH direction is genuinely empty
even though the near-cap population is not. And its one shrink direction is
already measured: `-fno-anchored-dfa` takes it to 733,131 B.

**THE SYNTHETIC NEAR-CAP FIXTURE FAMILY** (the r53 precedent — *synthetic
ladders are corpus members*), three shapes, each in `tests/size/`:

| fixture | sits | must show |
|---|---|---|
| **F1** | just under `PCREC_MAX_EMIT_BYTES` at `0` | that `+1`/`+2` do NOT push it over — the growth direction, **M4** |
| **F2** | just under `PCREC_MAX_VM_EMIT_CODE_BYTES` at `0`, VM-compiled | the sharper growth case: the entry-chain term's raise is CODE bytes, which is the cap `+1` actually moves |
| **F3** | REFUSES at `0`, compiles at `−2` | the opposite direction — a pattern that GAINS an answer, which §6.2's rule forbids and a count-based check cannot see |

Plus the named real witness above as a non-synthetic control, which a purely
synthetic family would not have.

#### 6.2b M4 — THE GROWTH DIRECTION, AND A RUNG THAT DOES NOT EXIST

Revision 1's refusal analysis ran in ONE direction: it asked whether `−2`'s
denials could make a pattern compile that refuses today. **It never asked
whether `+1`/`+2`'s growth pushes a near-cap pattern OVER a cap** — and
`+1`/`+2` do grow artifacts, by construction: the entry-chain term's raise
admits more inlining (code bytes), and λ's speed notch costs up to 34% of a
class matcher's bytes over the middle (§4.3's frontier).

Naming the population is the obligation and §6.2a does it. **But the
analysis surfaces a mechanism gap that is worth more than the population:**

> **`[K53-SELRETRY]`'s drop ladder has ONE rung and it drops the ANCHORED
> MACHINE. A `+2`-induced code-bytes overflow has no rung at all.** The
> general form of that ladder — *drop an optional contributor and re-emit*
> — covers this case exactly, because the extra inlining a raised term buys
> is optional by the term's own contract ("forward only where it costs
> nothing"). A second rung would back the dial off toward the middle on a
> size-cap refusal, which is the only behaviour consistent with §6.2's
> rule.

**Not built here (D77), and the trigger is named:** fixture F2 going red is
the measurement. `utf8k53_report.md` §1.2 already answers why the ladder
shipped as an ordinal with one rung — a second rung needs an ORDER, and an
order is a measured per-contributor run-time cost that a sample of one
cannot supply. This design would give it its second customer and therefore
its second sample.

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
  reservation.
- **It does not cover the `[K53-SELRETRY]` DEPENDENCY** (§3.3). The
  anchored-dfa `−2` cell's gate-2 safety rests on that ladder existing; no
  check in this plan would notice if the ladder were narrowed.
- **It does not cover the DECLARED-CAPACITY FLOOR dependency** (§3.5a).
  The `[ART-SIZE]` rows' answer identity rests on
  `artifact_size_term.md` §3.3a's floor; the axes sweep's subjects are not
  long enough to reach the give-up boundary the floor guards, which is why
  §6.1b runs the ladder's own acceptance instead.
- **It does not cover a mechanism whose state the emitted text does not
  carry.** §6.1a's cross-check recovers five mechanisms from the text; a
  sixth that left no textual trace would be unreachable by it.

**S6 — THE `−1` ARM SHIPS DECLARED VACUOUS.** At the first build, `−1`
differs from `0` on the two `[ART-SIZE]` ladder parameters and on nothing
else, and the ladder's population below 120,000 bytes is where §3.5b's
81 new patterns live — so the arm is NOT vacuous in the way revision 1
implied. **What IS vacuous is the `+2` arm**: after M12 it is identical to
`+1` on every cell, so its only diff against a `+1` artifact is the
`RX_TUNE` string. It ships DECLARED, on S219's precedent (a check that
ships `UNREACHED` with its derivation, and whose runner fires the day it
becomes reachable) — with the derivation being §3.6(d): `+2` becomes
distinct the day either λ is implemented or `s` is ruled below 1.03.

**And the count revision 1 stated is wrong.** It said the dial's first
build "has five positions of which the discrete rows distinguish three".
It is **FOUR** — `−2`, `−1`, `0`, `+1` — with `+2 ≡ +1`. Revision 1
reached three by treating `+1`/`+2` as one position, which they were not in
its own table (they differed on four cells: the entry-chain term, λ, the
ladder bar and the ladder threshold). Both the old count and its reasoning
were wrong, in opposite directions.

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

The lens bites in three places and this revision answers it at all three.
**(a) λ is the general form and `-fno-cls-fold` is the special case**, and
Frank has already ruled the special case is absorbed rather than dialled
(§4.6). **(b) S1 is this lens applied to the design's own λ row** — five
hard-coded constants beside a bolted-on cap was a parallel mechanism for a
fact the DP already expresses, and the selection replaces it with one rule.
**(c) M16 is this lens applied to `PCREC_TUNE_SET`** — a per-axis bit for a
defect `--engine` has too, replaced by the general explicit-set provenance
form with its build deferred (§1.3).

Where the design could still fail the lens: if a future switch is given a
policy row when it should have been absorbed into λ or into an existing
per-pattern mechanism. §2's statement ("the dial sets the parameters
existing mechanisms spend") is the standing test for that.

### 7.2 Core vs derived

**The dial is DERIVED, completely.** It introduces no new emitted
mechanism, no new analysis, no new IR, no new refusal. Every value it sets
is a value the CLI can already set by hand today — **with five exceptions
the panel found and §9's new question carries** (B4, §7.2a). The dial is a
naming of groups of those values.

The one genuinely core-touching consequence is the `abi` event (§5.3), and
it is core-touching for a scaffolding reason (a new `#define` line) rather
than a semantic one.

**A derived mechanism's characteristic risk is DRIFT**, and this design has
one instance already recorded: the policy table lived in two documents in
STEP 0's shape, and `opt_dial_inventory.md` §3's revision moved it to one.

#### 7.2a B4 — "EXPLICIT FLAGS BEAT THE DIAL" IS UNIMPLEMENTABLE ON FIVE OF THE SEVEN MOVING CELLS

The plan row rules it: *"Explicit per-switch flags override the dial
(explicit beats profile, as D93 file-wins beats the command line)."*
**Revision 1 restated the ruling without checking that the flags exist.
For five of the seven moving cells they do not**, and the gap is honest
rather than fatal:

| moving cell | today's CLI spelling | what "explicit beats the dial" would need |
|---|---|---|
| `-fno-premul-table` | **DENY-ONLY** (no `-fpremul-table`) | a FORCE twin, so a caller at `−2` can keep premultiplication |
| `-fno-anchored-dfa` | **DENY-ONLY** | a FORCE twin |
| `-fno-tiered-entry` | **DENY-ONLY** | a FORCE twin |
| `[ART-SIZE]` ladder — bar | **NO CLI SPELLING AT ALL** (`artifact_size_term.md` §3.3's constant) | a value flag |
| `[ART-SIZE]` ladder — threshold | **NO CLI SPELLING AT ALL** (`PCREC_SIZE_TERM_THRESHOLD`, `limits.def:161`, kind `BUILD_D`) | a value flag or a `--max-*`-shaped override |
| `--vm-entry-shape` term | covered — `--vm-entry-shape=N` "overrides the decision outright" (`limits.def:352`) | nothing |
| λ | covered by construction — no CLI spelling exists and none is proposed; the position IS the surface | nothing |

**The ruled property cannot be quietly narrowed to the two rows where it
already holds.** Three options, with their costs, and **§9's new question
asks Frank which** rather than this lane inventing flags:

1. **Force twins for the three deny-only bits.** The cheapest: three bits
   in the existing deny/force pair shape `-fprefilter`/`-fprefilter-collapse`
   already use, three `tuning.md` §2 sentences, three axes-registry rows,
   and the force arm joins `make test-axes` — which is the real cost, since
   `tests/axes` walks every flag over the corpus and three new force arms is
   ~9 minutes.
2. **Two value flags for the ladder** (`--size-term-bar=`,
   `--size-term-threshold=`). More surface than the twins and it promotes
   two internal constants to contract, which D80 then pins. `limits.def`'s
   `BUILD_D` kind exists precisely to say a constant is NOT a flag, so this
   is a deliberate kind change.
3. **Narrow the ruled property, in the spec, to "where a spelling
   exists"** — and say so in `tuning.md` §5 rather than leaving a reader to
   discover it. Zero implementation cost and it is the option this lane
   would take if the answer is "not yet", because the dial is honest about
   what it does and the flags can arrive when someone needs one.

### 7.3 Applicable vs assumption-changing

**Answer identity is the assumption the dial must not change, and it is
promoted from a property to a GATE** (§3.1 gate 1, §6.2). The design's one
real discovery under this lens is that an axis exists TODAY which would
have quietly broken it: `-fno-startpos-guard`'s two arms disagree about
answers by design. It would have looked like an ordinary `-fno-` flag to a
table-filling exercise.

**And r60 found a second, quieter one:** the `[ART-SIZE]` ladder rows
change `K`, and `K` is answer-identical in the LANGUAGE but not in the
DEPTH (§3.5a). That assumption is held by a floor in another document,
which is a dependency rather than a property — §6.3 lists it.

Two assumptions the dial deliberately does NOT change: the middle is
today's defaults byte for byte (Frank's ruling, and §3.2a keeps it even
where the middle's own windows disagree — now in BOTH windows, §3.2a
window B), and per-pattern decisions stay per-pattern (§2).

One assumption it DOES change, and this is the honest entry: **`tuning.md`
§2's per-axis defaults stop being the whole story.** Today a reader learns
an axis's default from its own section. After the dial, the default is the
`balanced` column and the section is one of five values. §8's spec plan
puts the policy row IN each §2 entry for exactly this reason — the
alternative, a central table the per-axis sections do not mention, is how
two surfaces come to disagree.

### 7.4 Fits architecture vs refactor

**It fits.** The option parser gains one value flag; `pcrec_options` gains
an `int8_t`; one new table maps position to per-axis values and is
consulted once, before any pass runs; the emitter gains one `#define`.
Nothing is restructured. **S1 made this smaller, not larger**: the λ row
is a cap in that same table rather than five constants plus a parallel
constrained-path solver, and the solver it uses is the one `[CLS-TREE]`
was already going to build.

The design deliberately declined the two shapes that WOULD have been
refactors: a per-pattern cost model that picks a POSITION per artifact
(rejected in §2 — it duplicates mechanisms that already exist and would
need `φ` to work at all), and a general "objective function" threaded
through every pass (which is what λ is, correctly, for ONE pass, and which
has no business in the others).

**The one place it presses on the architecture** is §3.5's fold of
`--unroll=K` into the `[ART-SIZE]` ladder's parameters. That is not new
structure — the ladder and the bar both ship — but it does mean the dial's
`−2` position runs the ladder on **81 patterns it has never run on**
(§3.5b), and carries two disclosed dependencies (§3.5a, §3.5b). The
implementation lane should expect that to be where the surprises are, and
§9 Q4 offers Frank the narrower alternative.

---

## 8. SPEC PLAN — what moves in `docs/spec/`, at implementation

D80: a caller-observable change carries its spec hunk in the same change.
This section is the PLAN; no spec file is touched by this lane.

**`docs/spec/tuning.md` — the main body of the work.**

1. **§1 ("What a tuning flag is") gains the PROFILE concept**: that axes
   have a per-position default rather than a single default; the allowlist
   rule in one sentence; and — per B4 — **the honest statement of how far
   "explicit flags beat the dial" reaches**, in whichever of §7.2a's three
   forms Frank rules.
2. **A new §5, "The `--tune` dial"**: the five positions, both spellings,
   the full policy table (this note's §3.3 as the contract), §3.0's sign
   and unit conventions, the seven reason codes, the stamp's token set, and
   the D93 precedence rule as ruled. **The policy table lives HERE — the
   design note is not the contract, and D103 makes that literal: this
   table is THE PINNED CONTRACT, a cell changes only by an explicit ruled
   diff to THIS spec section, never by a later measurement.** §6.1a's
   cross-check reads its expectation side from this table precisely so
   that the check does not share a source with what it checks. The
   design note's §3.2 (the PROPOSAL RUBRIC) is cited by reference for
   HOW a future cell is argued, but the rubric itself does not move into
   the spec — a caller reads the contract, an author proposing a change
   to it reads the rubric.
3. **Every §2 entry gains ONE policy line.** Twenty-three entries, and
   twenty of them say "not on the dial" with which reason code. This is
   deliberate volume: §7.3's lens says a central table the per-axis
   sections do not mention is how two surfaces drift apart.
4. **§2.10 (`--unroll=K`) and §2.16 (`-fno-size-term`) gain the fold**:
   the dial sets the bar and the threshold, K is derived per pattern —
   **plus the declared-capacity floor as a stated precondition** (§3.5a),
   which `tuning.md` does not carry today.
5. **§2.21 (`--vm-entry-shape`) gains the term's per-position values** and
   the statement that the dial names the term and never a rung.
6. **§2.19/§2.20 gain the PURE WIN reason code**, which is the spec-side
   half of B3: the two axes that fell out of revision 1's table fell out
   because no vocabulary existed for them.
7. **§2.22 (`-fno-cls-fold`) and §2.23 (`-fno-startpos-guard`) gain their
   exclusion reasons** — a ruling and gate 1 respectively, and they are
   different kinds of "no", which the entry should say.
8. **§3/§3.1 (the stamp sections) gain `<PREFIX>_TUNE`.**
9. **§4 (`pcrec_options` mirror) gains `tune`** — and, per M16, **no
   `PCREC_TUNE_SET` bit**, with the general explicit-set-provenance form
   recorded as the recommendation and its trigger named.

**`docs/spec/cli.md`.** `--tune=N` in the flag table with both spellings
and the `=`-form requirement for negatives; the `tune` config-block
directive; and — in the file-wins section that currently carries
`--engine` as its ONE named exception — a sentence confirming `tune` is
NOT a second exception, with the conflict diagnostic's wording (and
without `--force-tune`, M15). That sentence is worth its space: the
section's structure invites a reader to assume new axes join the exception
list.

**`docs/spec/match_api.md`.** The `abi` 25 → 26 event and its row in the
abi history; §6's stamp inventory gains `<PREFIX>_TUNE`; the explicit
statement that there is NO `rx_info` mirror and why (§5.2), so the absence
is a recorded decision rather than a gap.

**`docs/spec/limits.md`.** `VM_INLINE_CHAIN_MAX_BYTES` and
`PCREC_SIZE_TERM_THRESHOLD` become dial-dependent; their entries state the
per-position values, and `PCREC_SIZE_TERM_THRESHOLD`'s notes that its
`BUILD_D` kind means no CLI override exists (B4). The emitted-size caps'
entries gain the sentence that the dial never lowers them — **and §6.2b's
finding that a `+2`-induced overflow has no drop-ladder rung**, as a
recorded gap rather than a promise.

**`docs/spec/rxt_format.md`.** The `tune` config directive in the config
vocabulary, with its value grammar.

**`docs/guide/`** points at `tuning.md` §5 and does not restate the table.

**S7 — THE CHECKS GET NAMES, IDS AND OWNERS IN THE SPEC PLAN**, because a
check described in a design note and never named is a check nobody builds:

| id | what | home | sabotage |
|---|---|---|---|
| **DIAL-S1** | `<PREFIX>_TUNE` well-formedness: closed token set, token matches requested position (N2) | `tests/codegen/` | folded into SAB-D1 |
| **DIAL-S2** | the mechanism-state cross-check, five recoveries × five positions (B1, §6.1a) | `tests/codegen/`, `run_premul_table.sh`'s shape | **SAB-D1, SAB-D2, SAB-D3** |
| **DIAL-S3** | the refusal set as a SET of `file:line` keys, identical across five positions (§6.2) | `tests/axes/`, riding `RXTDUMP` | one row: make one position's refusal set differ by one key |
| **DIAL-S4** | the near-cap fixture family F1/F2/F3 + the named real witness (§6.2a) | `tests/size/` | F3 IS the sabotage in the gaining direction |
| **DIAL-S5** | the `[ART-SIZE]` ladder's own acceptance re-run at `−2`'s threshold (§6.1b, M5) | `tests/codegen/run_size_term.sh`, per-position | existing §7/§7b arms, re-based |
| **DIAL-S6** | nesting: everything `−1` denies, `−2` denies too; the five positions are monotone in every row (§3.2) | `tests/codegen/` | swap two cells so one row is non-monotone |

---

## 9. THE FRANK QUEUE

**RESTRUCTURED BY D103.** The r60 revision left five live asks (Q1, Q2,
Q2b, Q3, Q4) plus a dissolved one (Q5) and three unrelated ones (Q6, Q7,
Q8). D103 point 3 collapses the five into two: Q1 CLOSES as
ruled-on-demand, and Q2/Q2b/Q3/Q4 COLLAPSE into ONE ratification item —
**THE FIRST-BUILD TABLE**, presented below for a single yes/no rather
than as four separate numeric asks. Q5 stays dissolved (S1, unaffected by
D103). Q6, Q7 and Q8 survive unchanged and are renumbered to follow.

**1 — `φ = (φ_scan, φ_entry, φ_cls)`: CLOSED AS RULED-ON-DEMAND (D103
point 3), not chartered as a blocking lane.** What fraction of a
matcher's run time is (a) the DFA scan loop, (b) per-call entry cost, and
(c) class-membership probing, on the populations that matter, is real
evidence for a future proposal — but nothing in the table below waits on
it. `φ` is chartered narrowly, and only, the day a specific contested
cell needs it: `-fno-anchored-dfa`'s `−2` admission (below, EXCLUDED for
now) and `t_mid` before `[CLS-TREE]`'s middle admission. No lane is asked
for here.

**2 — THE FIRST-BUILD TABLE, for ONE ratification (D103 point 3, folding
in the r60 revision's Q2, Q2b, Q3 and Q4).** The four decidable positions,
exactly as the fix round derived them, presented as one table rather than
as separate numeric questions:

| position | ships with |
|---|---|
| `−2` (`min-size`) | `[ART-SIZE]` ladder bar **0.95**, threshold **40,000**; `-fno-premul-table` **denied** (unconditional at every `φ_scan ≤ 1`, §3.3); `-fno-anchored-dfa` **EXCLUDED** — its worst measured population (2.114×) fails the working `x₂` = 2.00 by 5.7%, and rather than ratify a specific `x₂` between 2.00 and 2.114 now, the cell is left OUT pending its own on-demand A/B (item 1) |
| `−1` (`size`) | `[ART-SIZE]` ladder bar **0.85**, threshold **80,000**; nothing else — the three `φ`-conditional cells (premul, tiered-entry, λ) stay em-dashed until their own on-demand measurement |
| `0` (`balanced`) | **today's defaults, byte for byte** (Frank's keep-the-defaults ruling; unaffected by any of the above) |
| `+1` (`speed`) | `--vm-entry-shape` term raised to **8,192** |
| `+2` (`max-speed`) | **DECLARED VACUOUS**, identical to `+1` on every cell — the day either λ lands (`[CLS-TREE]`) or `s` is ruled below 1.03 (§3.6) is its become-reachable condition, and the table says so rather than leaving a reader to discover it |

Two things this table deliberately does NOT ask for, because ratifying
the table does not need them. **The `x₂`/`x₁`/`y`/`s`/`Z₁`/`Z₂` numbers
behind it** (2.00, 1.10×, 5%, 1.10×, 1.30×, 2.0×) are the rubric's own
working parameters (§3.2), not separately ruled — a future re-argument of
any cell above reopens them, ratified with that cell, not before. **The
middle's asymmetry ratio** (the r60 revision's Q2b, `t_mid` against
`z_mid`) stays an open rubric detail rather than a blocking ask: both
windows already have exactly one violating shipped default in opposite
directions (`-fno-premul-table` against `z_mid`, `-fno-cls-fold` against
`t_mid` by ≈5×, §3.2a), neither of which this table's five cells touch,
and `t_mid` is owed against `-fno-cls-fold`'s number before `[CLS-TREE]`
lands regardless of how the ratio is eventually ruled. `[ART-SIZE]`'s own
disclosed dependencies (§3.5a's declared-capacity floor, §3.5b's 167-vs-86
population and §6.1b's ladder arm) are the table's stated price, not a
separate ask.

**3 — the D93 precedence ruling (§1.2) — RULED (Frank, 2026-09-16, sixty-sixth session; decisions.md D93 addendum 2026-09-16): the FILE WINS, with the loud non-fatal conflict diagnostic; no `--force-tune`; the `--engine` exception stays unique.** The recommendation below was adopted as written and stays as the record of the argument.
Does an explicit CLI `--tune` beat a target's `tune` row?
**Recommendation: NO — the general D93 rule stands, the file wins, with a
loud non-fatal conflict diagnostic.** Two arguments, and revision 1's third
("a second exception in a month turns the rule into a list") is withdrawn
as a precedent argument standing beside two reason arguments: (2) D93's
H11 support is vacuous for an answer-preserving axis, leaving the
DEFINITION argument, which says the file wins; (3) `--engine`'s exception
had a forcing reason — it is a comparability facility and it can cause a
refusal — that `tune` lacks. If Frank rules the other way, **D93's own
revisit-when names the right shape (an explicit loud override flag, never a
silent precedence flip)**, and that ruling is also the trigger for §1.3's
general explicit-set-provenance form.

**4 — the force-pair / CLI-spelling question (B4) — RULED (Frank, 2026-09-16): option (3) now, option (1) when someone needs a flag — the ruled property narrows in the spec to "where a spelling exists", force twins arrive on demand.** The option analysis below stays as the record.
"Explicit flags beat the dial" is RULED and is unimplementable on **five of
the seven moving cells** — `-fno-premul-table`, `-fno-anchored-dfa` and
`-fno-tiered-entry` are deny-only with no force twin, and the `[ART-SIZE]`
ladder's bar and threshold have no CLI spelling at all (§7.2a). **Which
of the three options?** (1) three force twins (cheapest; the real cost is
~9 minutes added to `make test-axes`); (2) two value flags for the ladder
(promotes two internal constants to contract, and `limits.def`'s `BUILD_D`
kind exists to say they are not flags); (3) narrow the ruled property in
the spec to "where a spelling exists". **Recommendation: (3) now, (1) when
someone needs one** — the dial should be honest about what it does rather
than grow five flags nobody has asked for (D77).

**5 — the solo battery — RULED (Frank, 2026-09-16): YES, the dial's implementation merge gets its own validation battery (D102's escape hatch), not the nightly batch.**
D102's risk-tier escape hatch lets the manager demand one for an
emitter-touching merge. This carries an `abi` event plus four new
answer-identity axes. **Recommendation: yes, solo** — and this is the
manager's call rather than Frank's; it is listed here so the queue is
complete.

**Q5, for the historical record, DISSOLVED by S1 and untouched by D103.**
Revision 1 asked whether λ's `−2` should be 0 or 4, given that λ=0 is
dominated on both axes by λ=4 on `\p{L}`, and proposed resolving it with
an object-size sweep of the frontier over several sets. Under the
rubric's own selection rule a dominated frontier point can never be the
argmin of either objective, so it is never proposed (§4.3) — the answer
is 4, and it is one of the five constants §4 now pins. The object-size
sweep is no longer needed to decide this cell; it remains worth having as
a cost-model improvement, and it belongs to `[CLS-TREE]`.

---

## 10. WHAT THIS NOTE DOES NOT SETTLE

Named, not hidden, in the house's style.

- **`φ` is unmeasured** (Q1), and after r60 it is BLOCKING rather than
  merely missing: four of the six moving rows carry conditional cells
  because of it, and λ's caps are provisional.
- **`-fno-anchored-dfa`'s time number has never been measured on the
  shipped flag** (§3.3). It is a ratio of two columns in a cost-isolation
  experiment on the mechanism's PREDECESSOR. The A/B — `rx_match` default
  against `-fno-anchored-dfa` on `opt2`'s own 85 subjects — is cheap and is
  the single owed measurement most likely to change a cell.
- **`+2`'s entry-chain cell has no measurement to cite** (§3.4, M12). What
  would fill it: extend ccd2's ladder above program 6,954 B and find where
  the 5× rate degradation begins.
- **No end-to-end dial measurement exists** (§6.3). Every rate in §3.3 is a
  per-switch measurement from its own ledger; nobody has built one artifact
  at `−2` and at `0` and compared them. The composition of individually
  correct rates can still be wrong.
- **λ's row is a reservation until `[CLS-TREE]` lands**, and the first
  build has four distinct positions, not five (§6.3).
- **λ's frontier numbers come from ONE set (`\p{L}`)** at the per-set
  resolution, with population-wide section shares as the only cross-check.
  §4.3's selections and §4.4's derivation both rest on that single set.
  **D103 WIDENS this limitation rather than narrowing it, and this is a
  correction against S1's own claim.** S1 said a PER-CLASS selection
  confines the one-set limitation to the caps' calibration, because each
  class would solve its own frontier and the pinned VALUES would not be
  the one-set concern. Under D103's pinning there is no per-class
  selection any more — the five constants are fixed once, from `\p{L}`'s
  frontier alone, and applied to EVERY class `[CLS-TREE]` ever sections.
  The one-set limitation therefore applies to the pinned λ VALUES
  themselves, not only to their derivation, until a second real set is
  swept and the constants are re-argued.
- **§4.7's six-frontier-point argument cost is estimated, not measured**:
  ~155 ms worst-case against a 25.86 ms single-policy discovery, paid once
  by this revision and again by any future re-argument — NOT a per-compile
  cost (§4.7 corrects this from the pre-D103 framing). Owed to whichever
  lane next contests a cell, not to `[CLS-TREE]`'s build.
- **`-fno-scan-edge`'s size cost is never converted to a fraction**, and
  after r60 the row's flatness rests on that inference ALONE (§3.3, N1).
  It is cited absolutely (+364…612 B per edge-carrying machine) because the
  sweep did not cover it. Revision 1 claimed an independent `x₂` failure;
  under §3.2's conversion that failure is conditional on
  `φ_scan ≥ 0.493`, so the independence is gone.
- **The `−1` column's population is measured on today's corpus**, which has
  two throughput sweeps owed against it
  (`opt_dial_inventory.md` §7.1 item 6). If `-fno-possessify` turns out
  cheap on time, it lands in exactly the interval §0.1 describes — though
  its `σ` is wrong-signed today, so it would enter as a flat row unless the
  size half moves too.
- **A `+2`-induced size-cap overflow has no drop-ladder rung** (§6.2b).
  Named, not built; fixture F2 going red is the trigger.
- **Two dependencies carry moving cells and no check covers either**
  (§6.3): `[K53-SELRETRY]`'s drop ladder for `-fno-anchored-dfa` at `−2`,
  and `artifact_size_term.md` §3.3a's declared-capacity floor for both
  `[ART-SIZE]` rows.
