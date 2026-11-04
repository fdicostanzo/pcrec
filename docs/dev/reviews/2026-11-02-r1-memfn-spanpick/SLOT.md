# SLOT lens: slot tracing + ruling check, span_pick.md rev 1 (frozen 324aae3a9c5a...c56c39)

Critic: SLOT (opus), read-only. Review tree worktrees/crit-memfn-spanpick @ 884996ef6. No compiles
run (none were needed); evidence is the subject's text, the cited code, the guide, the D-rows and
R-33's raw sweep (`r33data/sweep.jsonl`, 5,492 lines, 10,356 site records), read with `python3 -I`.
"Line N" = the frozen subject's line.

## Findings

### SLOT-1 — Goal 3's count "six question tables plus one admission table" is not true in stage 1
CONFIRMED. Severity: design (the goal is the design's own check and it cannot pass as written).
Effort: small (re-state the count). Blast radius: Goal 3, §The tables, §The pick. Subject: lines 27-30, 136.
Every decider the design keeps in stage 1, with where it lives:
| slot | decider in stage 1 | subject line |
|---|---|---|
| method | T-FIND (first match) | 121 |
| verify plan | T-VERIFY | 122 |
| resume | T-RESUME (but see SLOT-9) | 123 |
| set test | T-SETTEST | 124 |
| compare | T-CMP | 125 |
| presence members | T-PRES (but see SLOT-10) | 126 |
| departure admission | T-PICK = {keep} | 173-178 |
| stop position (Q1) | the KEY table, 3 rows keyed on entry | 180-187 |
| alternative (Q2) | Table M / MARGIN ("today's MARGIN row keeps") | 151-152, 321 |
| ties | `wf_ties` (6 rows today, window.c:85-100) + "default stands" (SLOT-5) | 133-134, 155 |
| renderer availability | T-FIND's validity column (a second key on T-FIND, mirroring Table E) | 323, 341-343 |
| renderer / frame text | Table E + B's renderers + `fn_rows` + compose `arms[]` as renderers, order kept | 131, 312, 324, 330 |
| run member of R | `run_member` (window.c:763), untabled (SLOT-2) | 311 |
| SIMD positions KA/KB | vrun's `rank_pos[1]` rule, KEPT | 316, 329 |
So stage 1 has ten declared tables (6 + T-PICK + KEY + M + TIE) plus a validity column, a renderer
selector and two untabled position answers. Q1 still has two deciders (KEY + `run_member`, plus vrun's
KB under SIMD), against Goal 3's "exactly ONE per question". Fix: state the true inventory in Goal 3
("six question tables, two pick-default tables that stage 3 retires, one tie table, one admission table,
one renderer selector") and give `run_member` and KA/KB a named home.

### SLOT-2 — the run MEMBER is a position decider with no slot in the design
CONFIRMED. Severity: design/maintenance. Effort: small. Blast radius: Q1, T-VERIFY. Subject: line 311 (U2).
`run_member` (memfn/src/window.c:763-797) is a least-mass argmin with its own tie row
(`T_MASS_STRETCH`) that `c_plan` (:975-977) runs before Table C; its answer travels in the reply
(`out->run_member`, :1046). R-33's sweep: 483 replies state a run; in 31 the reply's stop and run member
DIFFER (30 RESEED, e.g. `\bcat\b` stop 1 / member 0, `a{ , }` stop 1 / member 5,
`\b(github_pat_[0-9a-zA-Z_]{82})\b` stop 6 / member 10; 1 mass). U2 only unifies its spelling ("one tie
rule"); no table or pick level owns it, so after stage 1 the kit still answers "which position" in two
places. Fix: make it a T-VERIFY output (the C-pin/C-run grouping already reads it) or a pick-level
attribute, and say which in §The tables.

### SLOT-3 — the KEY table drops Table A's floor rows; 1,420 RESEED alternatives fall through it
CONFIRMED. Severity: design (an unassigned case; no-silent-defaults). Effort: small. Subject: lines 128-130, 180-187.
Table A today is five first-match rows on structural facts (window.c:638-647): A-empty, A-parked,
A-model, A-mass, A-floor. The KEY table names three rows keyed on the entry fact. Cross-tab of R-33's
traces (each stated alternative against the wfA row it took): PARKED -> A-parked 1,857/1,857; NONE ->
A-mass 1,432/1,432; RESEED -> A-model 415 and **A-floor 1,420**; A-empty 0. So the RESEED KEY row
("prefix_k's model_cost ... candidates whose T-FIND answer is not memchr are UNPRICED") has no stated
answer for the 77 % of RESEED alternatives with no `scan_ok` walked span (today: no stop, MARGIN cannot
hold, M-parked). The design must say the level-(b) default for "no priced candidate" (today's A-floor:
no stop) and where A-empty (C-meet's floor clause) lives; otherwise the builder invents it. A-empty also
has no population in the sweep ([MECH-REACH]).

### SLOT-4 — stage 3 item 1 is a DEFAULT edit, not a T-PICK row; the KEY rows' fate is stated four ways
CONFIRMED (text). Severity: design (D186 bar cannot be applied as written). Effort: medium.
Subject: lines 180, 278-284, 310, 320-321, 327.
- line 180: the KEY rows are "deleted in stage 3 by the first choice change" (all three);
- line 283: item 1 replaces "the no-entry KEY row" only;
- line 310 (U1): "stage 3 item 1 replaces both" A-model and A-mass;
- line 320 (N1, the RESEED key) and 321 (MARGIN): stage 3 item 3; line 327 (N8, PARKED key): no item.
And line 279 says every stage-3 difference is "one T-PICK row, its deny", while item 1 replaces a KEY row,
i.e. the DEFAULT. Consequences: (1) the item's deny (`--memfn=no-<row>`) returns the default, which is now
the priced key, so "RTE vs the row denied" no longer compares against today's answer, which D186's
per-regime evidence needs; (2) the robustness rule anchors on a conservative default (§Robustness: "keep
the choice that is never badly wrong"); a priced default removes that anchor for the no-entry class, and
under which rate model the "priced key" prices is unstated. Fix: keep every KEY row as the default
until the last stage-3 item; each item is a T-PICK row admitting a departure; delete a KEY row only
when no class still reads it (a census), as its own no-mover step.

### SLOT-5 — ties are decided by two mechanisms, and D176 Q5 says one
CONFIRMED (text + code). Severity: design (ruling disagreement). Effort: small. Subject: lines 133-134, 153-155, 243.
D176 Q5: "prices within the measurement-noise band tie, decided by the existing declared tie rows."
The pick instead decides every default-vs-challenger near-tie by an undeclared rule ("Otherwise the
default stands"), and sends only challenger-vs-challenger near-ties to `wf_ties`. `wf_ties` (window.c:85-100)
holds rows keyed on today's RULES (T_MASS_STRETCH, T_MASS_SET, T_MODEL, T_CMODEL, T_MARGIN, T_WINDOW),
none for the new levels (method, position, alternative under a band). Also "the least P price wins"
among qualifying challengers lets the prior alone decide between two plans that both beat the default
under both models, which §Robustness says P alone must not decide. Fix: declare "default within band"
as a `wf_ties` row (e.g. `T_BAND -> TIE_DEFAULT`), add per-level rows, and pick among challengers by a
declared rule on BOTH models (e.g. the least worst-case, or default-like ordering), so ties have one home
and D176 Q5 holds; or record a D176 amendment.

### SLOT-6 — the frame slot is circular and the validity column is a copy of Table E
CONFIRMED (text + data). Severity: design. Effort: medium. Blast radius: T-FIND validity, Q8, N4, N11,
window_site phase 1. Subject: lines 52, 109-111, 130-131, 323, 330, 341-346.
The design makes "frame class" a step-1 fixed fact read by T-FIND's validity column, "chosen by pcrec's
NEXT row from the reply". But (a) window_site §0 makes the NEXT row's frame a phase-2 statement, after the
reply, and phase 1 "reads no frame fact" (window_site.md lines 94-96); (b) which renderer serves a STMT
site is decided by the kit's Table E, first match, legacy first (window_site §2.6; window.c:1440-1449), and
E-find's own predicate reads B's method decision. R-33 data: STMT-form sites (form 1) split E-stmt 1,887
vs E-find 1,021 vs E-func 200 (E-func also takes all 381 FUNC-form sites); PAIR renders via `fd_find` only under E-find (101
sites) and via `fn-pair` under E-func/E-find (61); 28 smp05-shape sites fire BOTH `fd:PAIR` and
`fn:fn-pair`. So "a two-stream renderer exists" is not a function of any frame class pcrec states: it is a
function of Table E's choice, which runs after the plan. The column can only be filled by re-evaluating
Table E's predicates at plan time; line 342 calls it "declared beside the renderer table it mirrors": a
mirror is the private copy architecture.md "One table per slot" forbids. Fix: either (i) the plan call
chooses the renderer row (Table E becomes a plan-time question whose answer is an output fact the emit face
reads; pcrec states only form/op), or (ii) the validity column is a READER of Table E's row contracts (one
source), and the design says which. Line 110's "the renderer table's declared contract read at plan time"
is (ii); line 342 is a copy; pick one.

### SLOT-7 — SIMD forms at level (a) can move the stop and the alternative (D147, D155 seam)
CONFIRMED (text). Severity: design (ruling disagreement). Effort: small (restrict). Subject: lines 121, 195, 215.
T-FIND's SIMD forms apply at `-fmemfn-simd`; `find.byte` is carded "per method x layer"; level (a)'s winner
per candidate feeds levels (b) and (c). Hence a SIMD-on compile can pick a different STOP or ALTERNATIVE
than SIMD-off. D147: the scalar layer IS "the algorithm: what is searched, the plan, handoffs"; SIMD is a
layer on top, "never a substitute". window_site's B-fn row (D155's seam): "the SIMD-on artifact adds only
guarded rungs over the SIMD-off text". Line 215 ("the SIMD layer changes which T-FIND rows apply, never a
cost") is true per row but the consequence (a different plan) is unstated. Fix: levels (b) and (c) price
scalar forms only; SIMD forms compete at level (a) inside the scalar-chosen plan (rungs), and U7's KA/KB
read that plan. Consequence otherwise: D147's "each layer accepted on its own" loses meaning, because the
SIMD-on plan is not the scalar plan plus rungs.

### SLOT-8 — method is chosen from measurements twice: the finder's grid-key rows and the priced level (a)
CONFIRMED (code), reach SUSPECTED. Severity: design/maintenance. Effort: medium. Subject: lines 121, 207-210, 333.
T-FIND keeps R8/R3a/R3b/R4/R1/R2 (finder.c:250-281), whose `holds` compare stated facts against measured
crossover keys (`kit.xover.<t>.WALK.<kind>`, `kit.block.W64`, `kit.lstar.W64`, `kit.gstar`, `kit.h3a/h3b`)
from the same set: a crossover is the threshold form of two per-method costs. Stage 3 adds `find.byte`/
`find.hit` cards and prices methods at level (a). Two representations of one fact (which method is
cheaper for S at this call shape) will disagree as soon as the two are measured at different times; the
design only requires them "in the same set" (line 207-210). R-33's traces show none of these rows reached
(fd rows seen: D1 1,510, R7w 1,101, D1w 143, PAIR 101, D1c 39). Fix: after stage 2, derive the crossover keys
from the cards (one fact) or retire the rows on a zero-reach census (as N14 does for the unrenderable
three), and say so; R1/R3a/R4 pick the walk, which renders, so N14's validity column does not retire them.

### SLOT-9 — T-RESUME decides nothing of its own
CONFIRMED (text). Severity: maintenance. Effort: small. Subject: lines 121, 123.
Horspool is "a METHOD: it replaces find and resume" (T-FIND) and T-RESUME's D-shift "holds only when
T-FIND chose Horspool"; D-one otherwise. The resume is a column of the method row (D176 Q2 deleted the
separate Horspool admission). Keeping a table whose rows re-read another table's answer is the
"decided twice" shape; it inflates the "six" count. Fix: resume as an action column of T-FIND rows (as
window_site's Table D rows already "carry their actions"); T-RESUME returns only when a resume is chosen
independently of the method (name the trigger).

### SLOT-10 — presence is named in two places, and D176 Q4's fold has no slot
CONFIRMED (text). Severity: design (ruling coverage). Effort: small. Subject: lines 74-76, 126.
Line 75: presence "asks the same tables with a presence price" (implying the pick over unbounded
candidates); line 126: T-PRES, first-match over `kit_pres_picks` (P0..P9). The price formula (lines
160-166) has no presence term and the pick has no presence level, so the "presence price" has no reader.
D176 Q4's one general fold ("when the chosen stop's first find ... covers the presence byte, the presence
pass is dropped") appears nowhere in the subject (grep `fold`, `dropped`: no hit for it). pcrec's own
presence-drop (`dominated`, D184 point 2) is a sibling decider on the same question. Fix: say T-PRES is
the one presence decider in stage 1, place the fold as a T-PRES row reading the plan's stop, and drop
"presence price" or define it.

### SLOT-11 — the default's price can belong to a method that will not render (N8 recreated in stage 3)
SUSPECTED. Severity: design. Effort: small. Subject: lines 150-152, 186, 286-289, 325.
Level (b)'s default is "the position the stage-1 KEY row ranks first"; the RESEED key prices only memchr
(non-memchr UNPRICED). After stage 3 item 2 (Horspool priced at level (a)) and before item 3, a RESEED
candidate's level-(a) winner can be Horspool while level (b) ranks positions by memchr cost: the very
"price belongs to a method that does not render" defect N8 names. Also two "UNPRICED" notions coexist (the
KEY's `scan_ok` gate and "no card"). Confirm by: stating, per stage-3 item, which method each level's
default plan carries; fix by making the default at (b) the KEY's position WITH its level-(a) winner.

### SLOT-12 — pricing is built while D186 and [PRICE-BAKEOFF] defer it; no D-row records the owner's direction
CONFIRMED (text). Severity: doc/design (ruling check). Effort: small (one addendum). Subject: lines 4-8, 173-178.
D186 Relations: "Pricing ([PRICE-BAKEOFF], deferred) returns only if hand-written rows start conflicting";
plan.md [PRICE-BAKEOFF] (STATE:deferred): "a measured bake-off decides where search-strategy pricing lives
... Build waits for [STREAM]". The design builds card pricing in the kit (stage 3) and cites PRICE-BAKEOFF
only as a future trigger (line 177-178). Its authority is the owner's 2026-11-02 direction (lines 4-8) and
D176 Q1/Q3 (one priced stop choice, the cost table), which predate D186. The design does reconcile it in
substance (site-local prices, no engine priced, T-PICK rows are D186 rows with an optimizer inside, which
architecture.md permits) but no D-row says so, and [PRICE-BAKEOFF]'s expected shape ("rules AND pricing,
pricing chooses within them") is exactly T-PICK + pick. Consequence: a reviewer applying D186 literally
rejects stage 3. Fix: a D186 addendum (or the design's own D-row) stating that site-local kit pricing behind
T-PICK rows is D186's choice-row form and is not [PRICE-BAKEOFF]'s placement question.

### SLOT-13 — D153 is cited for a rule it does not state
CONFIRMED. Severity: doc. Effort: trivial. Subject: line 269.
"D153: refactors are no-movers": D153 rules that in-flight refactors take PRIORITY over optimization rows
("don't live in a house we're remodeling") and that opt rows touching a remodel site sequence after it.
The no-mover property comes from the zero-mover migration practice (integration.md, window_site §5) and
D186's "neither kind". D153's real consequence for this design is worth stating instead: while stage 1 is
in flight, every opt row touching window.c/finder.c/ofsskip.c (smp04's unit change included, line 295-298)
carries a "remodel overlap" mark and waits, unless the owner rules otherwise; the design says smp04 "lands
independently of stages 1-3", which D153 would sequence after stage 1.

### SLOT-14 — the new denies and the class selection are caller-facing with no D174 name and no spec hunk
CONFIRMED (text). Severity: doc (D174, D80). Effort: small. Subject: lines 105-107, 212-215, 279, 407-415.
(a) Stage-3 denies are spelled `--memfn=no-<row>`; D174 binds NEW caller-facing names to behaviour,
"never ... lane or row ids" (the `--memfn=` namespace itself is grandfathered). (b) D80: the denies are
observable options; the spec home of existing `--memfn=` denies is tuning.md (and cli.md/registry.md list
them), but §What moves names only measures.md §5/§8. (c) "Chosen by the target ... its class's DEFAULTS
row" needs a way for a compile to declare its class; measures.md §5¶6 says "Today there is one class,
`idk` (a compile that declares none)" and no option declares one. Until it exists the class slot is a
silent default (architecture.md "No silent defaults"); Open question 2 covers only the M2 envelope.

### SLOT-15 — abi wording disagrees with itself
CONFIRMED (text). Severity: doc. Effort: trivial. Subject: lines 23-24 vs 270-272, 415.
Goal 2: stage 1 artifacts "byte-identical to main but for the abi digits" (an abi bump); §Staging: "Abi:
none if bytes are identical; an MF_SITE_ABI event only if the plan call's seam changes `mf_site`"; line 415:
"Stages 1 and 2 move nothing". Under D76/D94 a pcrec abi bump is owed only for an emitted-byte change; an
MF_SITE_ABI event is the kit seam's number. Say which number moves in stage 1 and when.

### SLOT-16 — stage 1 ships the priced pick with nothing to read it
SUSPECTED. Severity: design (D77). Effort: none if clarified. Subject: lines 79-81, 91, 266-267.
Stage 1 is "`pick` at three levels with `T-PICK = {keep}`" and the trace prints "both prices with their
bands". With `keep` alone the pick always returns the default, no card exists before stage 2, and any price
printed would come from `plan_cost.def`'s Zen 1 constants. If stage 1 builds the P/F pricing and bands, that
is built ahead of a measured need (D77, memory build-under-measurement) and is unreachable by any population
([MECH-REACH]). Confirm by asking the design which pick code stage 1 contains; leaning: stage 1 builds the
levels' defaults and the trace only; pricing lands with stage 3's first row.

## Standing questions

**SIBLING OF A FAMILY.** Members of the same "rules gate, prices choose" family exist elsewhere:
1. pcrec's landmark walk: `lmwalk_conj[]` (a first-match admission table, ten rows) then `lc_rarity`
   (lmwalk.c:231), priced with `LMWALK_K_HIT_UNMEASURED` against NEXT's counterfactual (D184);
   `req_landmark_admits` (emit_dfa.c:9064) with `pcrec_landmark_margin` (:9057).
2. [PRICE-BAKEOFF]'s expected architecture shape (Frank 2026-11-02): "policy rules ... a declared
   first-match table; pricing chooses within them".
3. This design's T-PICK + pick.
That is three members: propose ONE idiom (an admission table whose rows carry a priced argmin with a
declared default and a band rule), used by the kit (T-PICK) and by pcrec's architecture side, each with its
own costs across the D157 boundary. The design names (1) only as a "finding for main" and (2) only as a
trigger. Other siblings it does handle: the mass primitive (kit_set_sum / presence cube mass / pcrec's
`pcrec_find_set_mass`), the tie rules (U5), the run member's five spellings (U2), `find.hit` vs lmwalk's
k_hit. Unhandled: the finder's grid crossovers vs the new cards (SLOT-8); Table E vs the validity column
(SLOT-6); pcrec's `dominated` presence drop vs T-PRES (SLOT-10); window_site's phases (phase 1 decides
frame-free, phase 2 renders), which the design's step-1 "frame class" breaks (SLOT-6).

**GENERAL FORM + UNLOCKS.** General form: facts -> a candidate lattice (alternative x position x method)
-> per-candidate validity/plan tables -> a nested conservative-dominance pick (default + challenger beats
it beyond the band under EVERY rate model in a declared set) -> an admission table gating where departures
may happen. Unlocks, each with a trigger:
- A declared SET of rate models instead of the fixed pair: a caller-stated exemplar (`--analysis`
  bundle, pcrec-analyze) joins P and F, so a stated subject can admit departures the prior cannot.
  Trigger: a compile carrying an analysis bundle whose rates differ from the prior on a mover site
  (smp20's x vs '/').
- The same pick one level up, per stretch (D185's per-stretch planner): engines/routes as a fourth level
  with crossing cards. Trigger: [STREAM]'s crossing prices measured ([PRICE-BAKEOFF] revisit).
- Run-time dispatch over a target SET (A-PLAN open point 3): one plan per class arm from that class's
  cards. Trigger: a second class's set committed (Zen 1) and a caller asking for a fat binary.
- lmwalk's k_hit and the finder's crossovers DERIVED from `find.hit`/`find.byte` cards. Trigger: stage 2's
  first committed card set.
- Landmark admission priced by the kit's find price (the design's end state). Trigger: [LANDWALK-PRES] or
  [LANDWALK-EDGEPRICE] reopening.

## PROBED-AND-HELD
- Cited code locations (17 checked in the review tree): window.c :407 `a_parked_holds`, :420 the C_MEMCHR/
  C_BITMAP price, :446 `scan_ok`, :466 `a_model_choose`, :529-561 A-mass, :673 `m_margin_holds`, :1440 the E
  enum, :1592 `d_hors_holds`, :1672 B-fn's comment block; finder.c :938 `SF_WINDOW_STOP`; presence.c :222
  landmark shadow; findings.c :745, :780; kset.c :294; emit_dfa.c :1058, :7299, :9057, :9064; lmwalk.c :231;
  req.c :779-781. All hold.
- Entry fact vs Table A row (R-33, 5,124 alternative-traces): the KEY table's entry keying reproduces Table
  A on PARKED (1,857/1,857) and NONE (1,432/1,432); 200 part sites with no stated alternative all take A-mass.
  The narrowing risk of keying on entry rather than Table A's structural predicates is not reached by this
  population (only the floor gap, SLOT-3).
- U3's premise (two method deciders today): 28 sites fire `fd:PAIR` and `fn:fn-pair` on one site; `fn_rows`
  BODY decides 609 sites (548 fn-memchr, 61 fn-pair). Held.
- MARGIN reach 356 sites, M-one 1,659, M-parked 1,479; D-hors 14: the staged rows have populations.
- D157: the designer row (line 90) states facts only, never a position, method or cost; pcrec's
  `findings.c` mass copy "stays (D157)" is consistent (D157 keeps pcrec's own scalar pick). Held.
- D167 (Q-R17P-11): landmark admission stays pcrec's; the kit shadow retires only on a census. Held.
- D147 add. 9: `--memfn=no-X` stay in the kit namespace, pcrec's one axis `-fmemfn-simd` unchanged. Held
  (the D147 core rule is SLOT-7).
- D176 Q1 (relative unit, fixed-point, one cost table with a used-row check, set chosen by target/ISA),
  Q2 (Horspool a method; HORS_MIN kept only as stage 1's holds, deleted at item 2), Q3, standing rule (a new
  method adds its card; "no card = UNMEASURED, cannot challenge"). Held, except Q4 (SLOT-10) and Q5 (SLOT-5).
- D76/D94/D80 for re-measurement: a byte-moving card rev is an abi event with readers by grep and a movers
  census; measures.md §4/§5/§8 named. Held (wording gap SLOT-15, deny spec gap SLOT-14).
- One set per compile (measures.md §0, §5¶8 compound parts read P's set): the design keeps span cards and
  finder keys in one set. Held. MAX_SET as a compile budget read from limits.def (plan_cost.def :51 already
  cites it). Held.
- Architecture.md "Decisions are declared tables": a priced argmin per level with a declared default is
  permitted ("an optimizer may sit inside one row's action"). Held.

## Summary
The slot trace finds ten declared tables in stage 1, not "six plus one" (KEY, Table M and the tie table
are deciders), plus the run member and vrun's KA/KB with no table. The frame is circular and T-FIND's validity
column copies Table E; SIMD forms can move the scalar plan (D147). Ties are decided twice (D176 Q5), and
stage 3 item 1 edits the default instead of adding a T-PICK row. Ruling gaps: D186/[PRICE-BAKEOFF] need an
addendum for kit pricing, D153 is miscited, D174/D80 are unmet for the new denies, and D176 Q4's fold has no slot.
