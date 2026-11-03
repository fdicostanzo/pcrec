# Review 2026-11-02 rN: memfn-spanpick (design): span_pick.md rev 1, the kit's one "find the span" choice mechanism

DRAFT by the coordinator (crit-memfn-spanpick). Every disposition below is PROPOSED; the launcher rules.
(The round number N is the launcher's to assign.)

## Subject

- `docs/design/memfn/span_pick.md` rev 1 (PROPOSED) on lane/memfn-spanpick, frozen at the doc's last
  commit 61b7afec1 (= branch head; the branch adds only this file and one index line). Copy in
  `$PCREC_TMPDIR/scratch/crit-memfn-spanpick/subject/`, sha256 324aae3a9c5a471d… (re-checked OK
  after the round; branch head unchanged).
- Build-landing commit: main HEAD 884996ef6 (= the branch's merge base). The subject's code cites are
  "re-read at main 34c8ed620"; between 34c8ed620 and 884996ef6 only memfn/docs/requests.md changed.
  Review tree `worktrees/crit-memfn-spanpick` built once (`nice make -j2`, unlocked, rc 0), plus one
  scratch MF_TRACE build in the round dir so critics could read today's selections. The worktree is
  removed after the round; the trace build stays in the round's scratch dir (`tracebuild/`).
- Evening hold (20:00-01:00): no make by critics, no timing, no queue; single compiles only (OWNER 0,
  PREMISE 4, SLOT 0, SIM 0, MEAS 3, verifier 3). R-33's raw sweep (5,492 lines) was copied read-only
  into the round dir as the population for SIM, SLOT and PREMISE.
- No earlier review of this subject. Not a re-check.

## Lenses as run

| lens | model | its one question | why chosen |
|---|---|---|---|
| OWNER (owner criteria + goals) | opus | Grade the subject on the owner's criteria in force at the freeze, in his order (the 11-02 direction, D186, D176, D157, D147); are the ranked goals checkable and served in order; are the open questions the right ones | the launcher named the owner's criteria; the goals lens folded in |
| PREMISE | opus | Name and test every assumption, especially every "today X does Y" and every stage-1 byte-identity claim, against the review tree | a new mechanism + tables; stage 1 rests on byte identity |
| SLOT (slot tracing + ruling check) | opus | Trace every decision to its one table; is the "six + one" count true; is anything decided twice; does each relied-on ruling agree, with what consequences. Carried the two STANDING QUESTIONS (sibling of a family; general form + unlocks) | a table/mechanism design that claims "one table per question"; many rulings relied on |
| SIM (simulate) | opus | Implement the pick from the TEXT first, then diff against R-33's sim.py; drill constructed outcomes (the design's own predictions first); run it over R-33's 3,443 units | a selection rule with predicted outcomes and a corpus to run it on |
| MEAS (measurement + cost and overlap) | sonnet | docs/design/CLAUDE.md's standing questions on cards, rate models, controls, regeneration; and each stage's cost, buy, trigger (D77) and overlap (D153, A-PLAN) | measured quantities + a staged build proposal |
| verifier | opus | Re-check 33 groups of CONFIRMED findings that would change the design | judgment-heavy arithmetic and code reads |

Not run: adversary (no trust boundary), soundness (no answer-identity-by-proof claim beyond stage 1's
byte identity, which PREMISE covered), fix-induced (not a re-check). A D27 spec-first test author is
NOT recommended for this design: its contract (the plan reply) is internal to the kit; G2 and the
pcrec-side byte-identity sweep are the right controls. Revisit at the first stage-3 row if it exposes a
caller-observable deny or stamp.

## Which lens caught what

| consolidated item | OWNER | PREMISE | SLOT | SIM | MEAS |
|---|---|---|---|---|---|
| A1 pricing revived ahead of D186's trigger | 1 | 11 | 12 | | 9 |
| A2 smp20 (D186's own witness) waits for stage 3 and may not close | 2 | | | 1 | 9 |
| A3 default-wins tie route vs D176 Q5 | 5 | 10 | 5 | 11(b) | |
| A4 open questions mis-aimed | 6 | | | | |
| A5 prior fix has no independent evidence | 3 | | | | |
| A6 A-PLAN point 1 answered as settled; A-PLAN go assumed | 4 | | | | 10 |
| B1 stage-1 byte identity fails on named items | | 2, 3, 4, 5, 6, 12 | 3 | | |
| B2 frame "fixed fact" is the kit's plan-dependent Table E | | 1 | 6 | | |
| B3 Goal 3's count and check | 9 | | 1, 2, 9, 10 | | |
| B4 unbuilt prerequisites (unbounded spans, D176 Q4 fold, PAIRSTOP) | 7 | 9 | 10 | | 10 |
| B5 abi wording and stage-1 witness arms | | 14 | 15 | | 8 |
| C1 price formula does not reproduce the design's predictions; units | | | | 1, 2 | |
| C2 band has no data or channel | | | | 3 | 1, 6 |
| C3 three-level stickiness / default moves / unpriced default | | | 4, 11 | 4, 5, 10, 11 | |
| C4 one c_enter across PARKED/RESEED drives ~200 departures | | 15 | | 7 | 5 |
| C5 F does not catch UTF-8 / dense prior errors | | | | 6 | |
| C6 Horspool's priced outcome hinges on undefined terms | | | | 9 | |
| C7 SIMD forms can move the scalar plan (D147) | 8 (wording) | | 7 | | |
| C8 finder crossover rows vs cards: two representations | | | 8 | | |
| C9 pricing machinery in stage 1 ahead of need | | | 16 | | |
| D1 stamp moves on first consult | | 8 | | | 3 |
| D2 no target-class input | | 7 | 14(c) | | 4 |
| D3 one method per set; new id vs new rev; step-0 gate | 7 | | | | 2 |
| D4 drop-F sabotage cannot reach smp20; validation = motivation | | | | | 7 |
| D5 cards are per-byte, the bar is per-call | | | | | 5 |
| E1 stage-3 item 3/4 renderer gaps; "PF one candidate" | | 13 | | 8, 10 | |
| E2 D153 miscited; D174/D80 for new denies | | | 13, 14 | | |
| E3 stage 1 sized as one change | | | | | 9 |
| F standing questions | | | SQ | | |

Overlap was high on the ruling items (A1 and A3 found by four and three lenses independently); the
behavioural items (C1-C6) were SIM's alone, and the code-level stage-1 items (B1) PREMISE's alone.

## Findings, by consolidated id, with PROPOSED dispositions

No ANSWER-level finding: the subject is a design, stage 1 is a no-mover by its own bar, and no lens
found a path from it to a wrong match. SPEED-level items are C1, C4, C5, C6, C3 (SIM-5/10) and A2.
Verifier verdicts in brackets; detail in `review/verify.md`.

### A. Owner criteria and rulings

**A1 (OWNER-1, SLOT-12, PREMISE-11, MEAS-9) — stage 3 is card pricing, which D186 and [PRICE-BAKEOFF]
(both 2026-11-02) defer until hand-written rows conflict; the design never asks.** [HOLDS] Stage 3's
first row replaces the no-entry KEY with a priced key (cards, two rate models, bands, three levels),
while §The pick still says pricing's trigger lies ahead ("when T-PICK rows start conflicting").
Mitigation all four lenses note: architecture.md permits "an optimizer inside one row's action", and
the subject's authority is the owner's 11-02 direction ("cost cards ... robust to the prior") plus
D176 Q1/Q3. No D-row reconciles the two. MEAS-9's cost table makes it concrete: item 1 reaches about 6
units (sign-only estimate), against a card stage that is grid-sized (D3).
**PROPOSED: DOC + owner question** (the gating question before any build go): put it in plain words
("price inside the row now, or hand-written rows first and prices only when rows conflict?"), with
the D186-literal alternative for item 1 (a hand row on stated facts: no entry, candidates differ in
member count, prefer one stream; 588 evidence) beside the priced form and its cost. Correct the
§The pick trigger sentence either way. If the owner picks pricing, record it as a D186 addendum.

**A2 (OWNER-2, SIM-1, MEAS-9) — the shipped smp20 loss (1.58-4.03x, D186's own witness) is Goal 5,
waits behind stages 1-2, and by the design's own formula does not close.** [HOLDS] Under the subject's
price formula (PAIR hits = m(S), not doubled) and Zen 1 constants, '/' LOSES to {x,X} PAIR by 6.1 %
under P (144,694 vs 153,476); the "wins by 8.6 % under KEY B" is R-33's doubled-hit arithmetic (C1).
D186's remedy for a losing row ("a losing regime narrows the row's condition") applied to S3's
shipped cover row is absent.
**PROPOSED: PLAN + owner question**: offer an interim D186 narrowing of S3's cover row for smp20's
class (its own deny and 588 evidence), independent of stages 1-3, as smp04 already is; restate Goal 5's
rank relative to D186's bar (a shipped loss under D186 is a Goal-2 matter).

**A3 (OWNER-5, PREMISE-10, SLOT-5, SIM-11(b)) — "otherwise the default stands" changes D176 Q5's ruled
tie route without citing it; and "least P price wins" among qualifiers lets P alone decide.** [HOLDS]
D176 Q5: "prices within the measurement-noise band tie, decided by the existing declared tie rows".
`wf_ties` has no row returning "the default" and none for the new levels.
**PROPOSED: FIX-NOW (design text)**: declare "default within band" as a `wf_ties` row (and per-level
rows), choose among qualifying challengers by a declared rule on both models, and cite D176 Q5 + D186
as the reason; owner question only if the manager reads it as amending a ruled answer.

**A4 (OWNER-6) — the open questions need rebuilding.** [not separately verified; reading] Q1 is
already answered by D186; Q4 (offset-0 stops: soundness + one timing) and Q5 (a unit change; overlaps
[MEMFN-PAIRSTOP], D176 Q6) are manager/kit calls; Q2 is ahead of need (D77) and uses ids the owner
cannot track. Missing owner-level questions: A1, A2, A6.
**PROPOSED: FIX-NOW (doc)**: rebuild around A1, A2, A6 in plain words; answer Q1/Q4/Q5 in the design as
the manager's or kit's calls; drop or defer Q2.

**A5 (OWNER-3) — Open question 3's "fix the prior" names no evidence independent of job 588, which is
also item 1's validation site.** [PARTLY: the subject's no-fitting sentence is about cards, and Q3
does ask for "its own evidence"; the source is unnamed.]
**PROPOSED: DOC**: name a rate source that shares no subject with 588, or demote the leaning in favour
of A2's narrowing row.

**A6 (OWNER-4, MEAS-10) — A-PLAN open point 1 is answered as settled ("one plan, prices only in the
trace") against §0a's "opaque entries with prices", and "the split and stage 1 are one change" takes
A-PLAN's step, whose prerequisites are the kit's agreement and the first stream step touching search
sites (no go).** [HOLDS] The landmark end state ("pcrec reads the kit's price") contradicts the
no-prices reply.
**PROPOSED: DOC + owner question**: keep point 1 open ("settled at the split / by the bake-off"), or
mark one-plan as stage 1's interim; say explicitly whether stage 1 IS A-PLAN's step and, if so, take
the roadmap's ratchet accounting and its go.

### B. Stage 1: the byte-identity claims and the one-table count

**B1 — named stage-1 items cannot be byte-identical as written.** [all HOLD; PREMISE-5 one cite
misattributed]
- PREMISE-2: precheck's memchr (N9) is a PRESENCE test with its own three texts; asked as a FIND on
  the VM route, T-FIND's first match is D1w (walk). N9 belongs under T-PRES's rendering.
- PREMISE-3: generic.c's per-byte RUN compares (U8) never match runcmp's rows (memcmp/overlap/words);
  U8 is a unit change, and T-CMP keeps two deciders after stage 1.
- PREMISE-4: the 381 OFS sites state site_kind UNSTATED and every FIND row reads the kind, so T-FIND
  answers nothing there; the RESEED KEY must restate `scan_ok` itself and `fn_rows` BODY stays a
  decider (its cube condition is not PAIR's) until pcrec states a kind on OFS sites (a pcrec-side
  fact, an MF_SITE_ABI event, unlisted).
- PREMISE-5: Table C is a cumulative 7-step list, not a first-match `kit_table`; C-table/C-own are
  booked under both T-VERIFY and T-SETTEST; PARKED readability is a T-VERIFY output (C-pin sets
  reseed), not a step-2 fact.
- PREMISE-12: U5 needs a NEW `wf_ties` row (pattern order then byte); U4's `window_mass` under the
  NONE rate is one floor over the total, not a sum of floors (62,500 vs 62,496).
- PREMISE-6: U9 "plan_cost.def reads limits.def" crosses the kit boundary (memfn/CLAUDE.md:28).
- SLOT-3: Table A has five rows; the KEY table three. RESEED -> A-floor on 1,420 alternatives (77 %
  of RESEED) and A-empty have no KEY row.
**PROPOSED: FIX-NOW (design)**: per item, state the real stage-1 action (keep the decider, move to a
unit change, add the row, or name the pcrec-side prerequisite), and add the A-floor/A-empty rows.

**B2 (PREMISE-1, SLOT-6) — the frame is not "a fixed fact chosen by pcrec's NEXT row": the
validity-relevant frame (the E row) is the kit's Table E, which reads the PLAN; T-FIND's validity
column "declared beside the renderer table it mirrors" is a copy.** [PREMISE-1 PARTLY (pcrec does
state form/handoff, per window_site); SLOT-6 HOLDS] On R-33's data the E row is a pure function of
(form, handoff, site_kind, wfloor), so stage 1 holds in practice but not by construction.
**PROPOSED: FIX-NOW (design)**: choose one: Table E becomes a plan-time question whose answer the emit
face reads, or the validity column READS Table E's row contracts (one source). Say the effective key
is the stated consumer kind (REPORT) rather than "no row reads a label".

**B3 (SLOT-1, SLOT-2, SLOT-9, SLOT-10, OWNER-9) — Goal 3's "six question tables plus one admission
table" is not the stage-1 inventory, and Goal 3 has no check.** [SLOT-1/2 HOLD] Stage 1 also keeps the
KEY table, Table M/MARGIN, `wf_ties`, Table E as renderer selector, vrun's KA/KB, and `run_member` (a
second position decider: stop and run member differ on 31 replies). T-RESUME re-reads T-FIND's answer
(SLOT-9). The "presence price" has no reader and D176 Q4's fold has no slot (SLOT-10).
**PROPOSED: FIX-NOW (doc)**: state the true inventory, give `run_member` and KA/KB homes, fold T-RESUME
into T-FIND's action column, place the presence fold as a T-PRES row, and name a decider/reach census
per table as Goal 3's check.

**B4 (PREMISE-9, OWNER-7, SLOT-10, MEAS-10) — unbuilt prerequisites.** [HOLD] "Presence states
unbounded spans" is [MEMFN-UNBOUNDED-SPANS] (STATE:not-started, an MF_SITE_ABI event); today presence
is the finder's PRES slot. Stage 3 item 4 needs [MEMFN-PAIRSTOP] (not-started).
**PROPOSED: FIX-NOW (doc)**: say presence keeps its PRES entry in stage 1 ("seven scenarios" becomes
six until the row lands), and list both rows as prerequisites.

**B5 (PREMISE-14, SLOT-15, MEAS-8) — abi wording.** [PREMISE-14/MEAS-8 PARTLY, SLOT-15 HOLDS] Growing
the reply is a certain MF_SITE_ABI (+ MF_CLASS_V) event; per window_site §5.2 a byte-identical seam
change carries NO pcrec abi event, so Goal 2's "but for the abi digits" is the wrong sentence. MEAS-8's
other part holds: window_site §5.2's stage witness is emit_sweep on EVERY arm (default, each deny,
`--engine=vm`, both SIMD layers), stamps and movers manifests included; the subject names main vs
branch only. Two cost systems (plan_cost.def integers, walk-relative ratios) coexist from stage 2.
**PROPOSED: FIX-NOW (doc)**: "stage 1 = one MF_SITE_ABI (+ MF_CLASS_V) event, no pcrec abi event,
zero movers on every arm", copy window_site §5.2's witness list, state which cost system wins.

### C. The pick as written (SIM's simulation over R-33's 3,443 units, Zen 1 constants)

**C1 (SIM-1, SIM-2) — the price formula does not produce the design's own predictions, and its units
are inconsistent.** [HOLDS; SIM-2(b) doc severity] smp20 and `cat|dog` predictions are R-33's doubled
PAIR hits; under the text's formula '/' loses (A2) and PAIR beats the walk on `cat|dog` under P. The
Horspool probe term lacks x1e6; F is defined as a probability but used in ppm; E_r[shift], whether
Horspool also pays the hit/verify lines, and the fixed-point scale are undefined.
**PROPOSED: FIX-NOW (design)**: decide per-member vs per-stream hits (in the `find.hit` card's
definition), fix the units, define E[shift] and the scale, and redo §Robustness's predictions with the
design's own formula.

**C2 (SIM-3, MEAS-1, MEAS-6) — the band has no input: `mf_measure` has no noise field, the one committed
set has `noise_e6` '-' on all 68 kit rows, and measure_sets.md says no selection reads noise.** [HOLDS]
With noise read as 0 the rule is maximally aggressive (0.1 % departs). The band also omits model error
(R4.6's bound, which no stage measures) and every surviving band is under the UNMEASURED 3 % gate.
**PROPOSED: FIX-NOW (design)**: a missing noise is UNMEASURED (cannot challenge), never 0; put the noise
channel (a kit request, an MF abi event, spec hunks) and a noise rule for derived rows in stage 2;
say "no constant except the card gates".

**C3 (SIM-4, SIM-5, SIM-10, SIM-11(a,c,d), SLOT-4, SLOT-11) — the three-level default rule.** [HOLD on
the checked cases]
- SIM-5: stickiness at a CHALLENGER candidate hides dominators and departs to P-worse plans (43 units
  once PF renders PAIR; e.g. ctx-lazy-64 picks {a,b} PAIR, P-worse than the same stop's walk; c00011
  keeps today although a RESEED walk dominates).
- SIM-10: adding a renderer moves the level-(a) default (T-FIND first match) on ~269 units outside
  any T-PICK row; and inverts the R1 "default stands" reading.
- SLOT-4: item 1 replaces a KEY row, i.e. the DEFAULT, so its deny no longer returns today's answer;
  the KEY rows' fate is stated four ways.
- SIM-4: the rule is undefined when the default itself is unpriced (Horspool before a probe card;
  UNPRICED RESEED candidates; SIMD forms).
- SIM-11: T-PICK rows do not say which levels they open; the post-deletion default is undefined; the
  alternative default MARGIN is a P-only price.
- SLOT-11 (SUSPECTED): a level's default can carry a price of a method that will not render.
**PROPOSED: FIX-NOW (design)**: the default is TODAY's complete plan, sticky only on the default path;
elsewhere a level takes its priced argmin (or one global comparison of complete plans against today's,
with the levels ordering only the trace); KEY rows stay defaults until a census shows no class reads
them; a renderer addition that flips a first match is its own choice change; unpriced default = keep;
T-PICK rows name their levels.

**C4 (SIM-7, PREMISE-15, MEAS-5's enter half) — 204 of the 206 P-and-F departures are PARKED -> RESEED
walk flips resting on one shared C_ENTER term** (MEASURED x ASSUMED), which F cannot filter. [HOLDS;
checked on pr01] The subject's "every plan of one site hands to the same consumer" is false at level
(c). Today MARGIN 2x (ARGUED) is what holds these; stage 3 item 3 deletes it. R-33 could not time this
class.
**PROPOSED: FIX-NOW (design)**: key the `enter` card by entry fact (PARKED resume vs RESEED) or argue
equality; keep MARGIN until that card exists.

**C5 (SIM-6) — F does not make a departure prior-independent where real text is far from both:
utf8/alt-cyr-64 departs to {\xd0,\xd1} PAIR under both models (a known 421x bench row) once PF renders
PAIR.** [HOLDS]
**PROPOSED: PLAN**: name the class (UTF-8 lead bytes, case-folded pairs, dense classes the prior
under-rates) as uncovered, and gate stage 3 item 4 on a fix (an encoding fact or a third adversarial
rate model). Not FIX-NOW: it bites only at item 4.

**C6 (SIM-9) — whether priced Horspool keeps the D-hors wins (Goal 5) is decided by c_probe and
c_hit(walk), two terms the text leaves undefined**, not by measured cards: at c_probe >= 3 c the pick
departs from Horspool on all five dense 588 witnesses, which are measured faster with Horspool.
[HOLDS under the stated assumptions]
**PROPOSED: FIX-NOW (design)**, folded into C1: define both terms and name their cards.

**C7 (SLOT-7, OWNER-8) — SIMD forms at level (a) can move the stop and alternative (D147: SIMD is a
layer, never a different plan); the card table keys "per method x layer" while §Cost cards says the
layer "never" changes a cost.** [SLOT-7 HOLDS, forward-looking]
**PROPOSED: FIX-NOW (doc)**: levels (b)/(c) price scalar forms only; SIMD forms compete as rungs inside
the scalar plan; fix the layer wording.

**C8 (SLOT-8) — the finder's crossover-key rows (R8/R3a/R3b/R4/R1/R2) and the new `find.*` cards are
two representations of one fact; the rows' reach is provably zero.** [HOLDS] N14's validity column
will not retire R1/R3a/R4 (they pick a renderable walk).
**PROPOSED: PLAN**: delete the six on the zero-reach proof (or derive their keys from the cards) as a
stage-1 deletion; say so in N14.

**C9 (SLOT-16, SUSPECTED) — stage 1 ships "pick at three levels" and a trace with "both prices and
bands" while T-PICK = {keep} and no card exists: pricing built ahead of a reader (D77).**
**PROPOSED: FIX-NOW (doc)**: say stage 1 builds the levels' defaults and the trace only; pricing lands
with the first stage-3 row.

### D. Cards, sets, stamps, controls

**D1 (PREMISE-8, MEAS-3) — the `<PREFIX>_MEASURES` stamp is "" today and becomes `id@rev:digest` on
first consult, so every site in a stage-3 row's class moves bytes even where `keep` results, and again
on each card rev; finder_check.py checks D and F encode "no row reads a key" and break at the first
row.** [HOLD; extent depends on the price/gate order]
**PROPOSED: FIX-NOW (design)**: test the T-PICK condition before any card lookup; count stamp-only
movers as their own census class; list checks D/F's replacement in stage 3.

**D2 (PREMISE-7, MEAS-4, SLOT-14(c)) — no compile can declare a target class (only `idk`); "chosen by
the target" works only with `--measures=NAME`.** [HOLD]
**PROPOSED: DOC + PLAN**: say an unnamed compile prices with DEFAULTS (zen4) as a conscious choice, and
file the class-declaring option under [IFACE-PUSH].

**D3 (MEAS-2, OWNER-7) — a set names ONE method@ver, so `kit-span@1` cards cannot share a set with
`kit-grid@1` keys; D176 Q3 rules "a new revision of the box's set" gated on the step-0 census, the
subject says "a new set id per box per run" and omits the gate.** [MEAS-2 PARTLY: one-method rule
holds; "re-read unavailable" and the finder-mover consequence REFUTED (a new rev is the re-read path;
the pay rule runs only behind inert rows)]
**PROPOSED: FIX-NOW (doc)**: span cards as quantities of the successor grid method (or argue a
multi-method set), new rev not new id, the step-0 gate, and the job's true size.

**D4 (MEAS-7) — the "drop F flips smp20" sabotage plant CANNOT reach: at smp20 F already favours the
challenger 2:1, so with or without F the test reduces to P.** [HOLDS, stronger than stated] F was also
motivated by smp20, item 1's validation site.
**PROPOSED: FIX-NOW (doc)**: witness at a site where F refuses a P winner (an R1 dense pair); name a
held-out class for item 1 or an owner exception.

**D5 (MEAS-5) — cards are long-subject per-byte; the cited losses and the bar include search_short and
match (per-call) regimes, with no per-call term in the price.** [SUSPECTED by the critic; not verified]
**PROPOSED: PLAN**: state the pick is a long-subject pick with per-regime row evidence, or add a
per-call term with its card before stage 3.

### E. Stage 3 specifics and doc slips

**E1 (PREMISE-13 PARTLY, SIM-8) — stage 3 item 3 prices RESEED stops "with PAIR/walk cards" on R-33's
R2 population, which is PF / E-stmt, where PAIR has no renderer (the gap item 4 names, unnamed for item
3); "PF states one alternative with one candidate" is false on 1,454 of 1,767 PF sites.** [PREMISE-13's
"OFS/FUNC frame" claim REFUTED: R2 is PF/E-stmt; SIM-8 HOLDS]
**PROPOSED: FIX-NOW (doc)**: name the E-stmt PAIR renderer as item 3's prerequisite (or restrict item 3
to the walk), and correct the PF scenario statement.

**E2 (SLOT-13, SLOT-14(a,b)) — D153 does not say "refactors are no-movers" (it says in-flight refactors
come first and opt rows touching them sequence after, which would sequence smp04's unit change after
stage 1); stage-3 denies spelled `--memfn=no-<row>` need D174 behaviour names and their spec home is
tuning.md/cli.md/registry.md, not only measures.md.** [HOLD]
**PROPOSED: FIX-NOW (doc)**.

**E3 (MEAS-9) — stage 1 is the justified part (simplification qualifies alone) but is sized as one
change over ~9,300 kit lines and 24 items; it splits into independent byte-identity units (primitives
U4/U5/U9; kit-only U2/U6; dead code N3; the planning core U3/U10/N1/N6).** [facts HOLD]
**PROPOSED: PLAN**: rev 2 orders stage 1 as separable units, each with its own sweep.

### F. Standing questions (SLOT)

- **Sibling of a family:** three members of "an admission table whose rows carry a priced argmin with a
  declared default": pcrec's landmark walk (`lmwalk_conj[]` + `lc_rarity`, `LMWALK_K_HIT_UNMEASURED`),
  [PRICE-BAKEOFF]'s expected "rules, then pricing within them" shape, and this design's T-PICK + pick.
  **PROPOSED: PLAN** (file a row proposing one idiom across the D157 boundary, trigger: the first
  stage-3 row or the bake-off's revisit). Other siblings (Table E vs validity column, crossovers vs
  cards, pcrec's `dominated` presence drop vs T-PRES) are B2, C8, B3.
- **General form + unlocks:** facts -> candidate lattice -> per-candidate tables -> nested
  conservative-dominance pick over a declared SET of rate models -> admission table. Unlocks with
  triggers: a caller-stated exemplar (`--analysis` bundle) as a third rate model (trigger: an analysis
  bundle whose rates differ from the prior on a mover site, e.g. smp20); the same pick per stretch with
  engines as a fourth level (trigger: [STREAM] crossing prices measured); per-class arms for a target
  SET (trigger: a second class's set committed); lmwalk's k_hit and the crossovers derived from cards
  (trigger: stage 2's first card set). **PROPOSED: NOTED.**

## Overall assessment (proposed)

The shape (facts -> candidates -> per-question tables -> pick last, scenarios as data) holds up: no lens
challenged it, the candidate builder contains every stage-1 answer on all 3,443 R-33 units (SIM), D157
and D147's core are respected, and every cited code location holds in the review tree. Rev 1 is NOT
ready for a build go:
1. The owner-level question A1 (pricing inside rows vs D186's hand-written rows first) is unasked, and
   the answer changes stages 2-3 entirely. A2 and A6 belong beside it.
2. Stage 1's "byte-identical, one table per question" claim fails on named items (B1-B5); each has a
   small, stated fix, mostly "keep this decider" or "this is a unit change".
3. The pick rule as written does not reproduce its own predictions (C1), has no band data (C2), and its
   level defaults misbehave on the corpus (C3, C4).
A rev 2 that answers A1 first (with the owner) and then fixes B and C is the proposed next step; stage 1
re-scoped as separable units (E3) could proceed on the simplification benefit alone once B is fixed,
independent of the A1 answer.

## PROBED-AND-HELD (by lens; detail in review/)

- OWNER: D186 row discipline for stage 3 rows (deny, per-regime 588 evidence, movers census, own abi
  event); D176 Q1 details (5 items), Q2, standing rule; D157 (3 checks); D147 (3 checks); roadmap §0a's
  "emit decides nothing a card covers"; four quoted numbers (smp20 1.58-4.03x, 1,097/4,154 ppm, 8.6 %,
  0.981); goal order for the design's own changes; build-go discipline.
- PREMISE: no code drift 34c8ed620..884996ef6; 20+ cited locations hold (B-fn off by one line,
  trivial); U1's two smp20 stops; inert finder rows provably unreachable; PAIR only via fd_find (101
  REPORT) vs walk elsewhere (279); Horspool admission; N3/N12 reach; U2's run-member agreement; U4's
  cube identity; U9 values (4 = 4); prior numbers; card channel; DEFAULTS; seven scenarios exist.
- SLOT: 17 cited locations; KEY entry-keying reproduces Table A on PARKED 1,857/1,857 and NONE
  1,432/1,432; U3's two method deciders (28 sites fire both); MARGIN/M-one/M-parked/D-hors populations;
  D157, D167, D147 add. 9, D176 Q1-Q3, D76/D94/D80, one set per compile, architecture.md's priced
  argmin.
- SIM: candidate list contains today's answer on 3,443/3,443 units; quadrature band conservative for a
  shared card (algebra); equal prices keep the default; the three-level winner always dominates today
  under both models; smp20's F half (2:1); R1 dense pairs "no departure" in count (187/203) once PF
  renders PAIR; R4 population behaviour; departure counts across 6 sensitivity runs; F removes about a
  third of P-only departures; H_HIT sensitivity mild under P-and-F (206/209/206).
- MEAS: price unit = the set's walk unit row; no host probe in the set loader; DEFAULTS/spec agree; card
  shape checks exist; MAX_SET duplicate real; R-33's constants match plan_cost.def (7 rows); stamp ""
  on 3 compiles; unmeasured-and-visible rule consistent with measure_sets §4.3; re-measure ritual
  consistent with D76/D94; no D153 conflict with a started remodel row.
- Verifier: 0 refuted outright; 5 PARTLY (PREMISE-1, PREMISE-13, PREMISE-14/MEAS-8, MEAS-2, OWNER-3),
  each with its refuted part named.

## By-id completeness

| lens | ids | consolidated into |
|---|---|---|
| OWNER | 1-9 | A1, A2, A5, A6, A3, A4, B4/D3, C7, B3 |
| PREMISE | 1-15 | B2, B1 (2, 3, 4, 5, 6, 12), D2, D1, B4, A3, A1, E1, B5, C4 |
| SLOT | 1-16 + standing | B3 (1, 2, 9, 10), B1 (3), C3 (4, 11), A3 (5), B2 (6), C7, C8, A1 (12), E2 (13, 14), B5 (15), C9 (16), F |
| SIM | 1-11 | C1 (1, 2), A2 (1), C2 (3), C3 (4, 5, 10, 11), C5 (6), C4 (7), E1 (8), C6 (9), A3 (11b) |
| MEAS | 1-10 | C2 (1, 6), D3 (2), D1 (3), D2 (4), D5/C4 (5), D4 (7), B5 (8), A1/A2/E3 (9), A6/B4 (10) |

Every id has a disposition through its consolidated item.

## Lessons for the guide (proposed)

1. **A simulate lens should recompute the design's quoted predictions with the design's OWN formula,
   not only run the rule.** SIM found the smp20 and `cat|dog` predictions were borrowed from the
   evidence study's arithmetic (doubled PAIR hits) and do not follow from the text's formula. Proposed
   text for the lens table's simulate row: "... and recompute every outcome the design quotes from its
   OWN formula; a number borrowed from an evidence study's different arithmetic is a finding (2026-11-02
   spanpick: smp20's 8.6 % was R-33's doubled hits)."
2. **Give a premise critic the evidence study's raw data, not only its report.** PREMISE, SLOT and SIM
   all counted populations from R-33's sweep.jsonl (OFS 381/381, A-floor 1,420, run member 31, PF
   two-alternative 1,454); the report alone would not have shown them. Proposed for §5's COMMON
   template: "when the subject's evidence includes a sweep with committed raw data, copy it read-only
   into the round dir and name it as the population."
3. **For a design whose sabotage plant names a witness, check the witness reaches the plant by the
   design's own arithmetic** (D4: drop-F cannot move smp20 because F already agrees there). This is
   [MECH-REACH] applied to a design's proposed control; the measurement lens caught it as "may not",
   the verifier proved "cannot".

## Meta (summary; full record in .coord/process.md)

Five critics launched 20:59 in one message; all wrote complete files with a passing lanecheck by 21:12
(4-13 min each); none needed a resend or nudge; no final replies reached the coordinator (all
"ended without SubagentHandback") but the file protocol made that irrelevant. One verifier 21:16-21:24
over 33 groups. Draft 21:30. Total about 35 minutes of wall time.

## RULINGS (kit manager, 2026-11-02)

All PROPOSED dispositions are ACCEPTED as drafted, with these notes:
- **A1, A2 and A6 go to the owner** (plain words, via the kit manager, recorded by main) BEFORE rev 2:
  - A1: price inside rows now, or hand rows first and prices only when rows conflict. The owner's 11-02 "costs within the kit" direction came AFTER D186; the kit reads it as answering A1 for within-site choices, but four lenses flagged the conflict, so the owner confirms it and main records a D186 addendum.
  - A2: an interim D186 narrowing of S3's cover row for smp20's class (a hand row on stated facts, its own deny, job 588 as evidence), independent of stages 1-3. Kit leaning: yes.
  - A6: stage 1 IS A-PLAN's next step (the plan call + emit call, byte-identical); take the roadmap's ratchet accounting; the go is the owner's.
- **FIX-NOW** (A3, A4, B1-B5, C1, C2, C3, C4, C6, C7, C9, D1, D3, D4, E1, E2) is done in rev 2 by a fresh design lane, after the owner's answers. E3 (stage 1 as separable units) is adopted in rev 2.
- **Lessons 1-3** are ACCEPTED: the skill's simulate row and COMMON note, plus docs/dev/guide/critics.md, in this commit.
