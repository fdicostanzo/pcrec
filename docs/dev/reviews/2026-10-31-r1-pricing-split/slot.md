# slot: slot tracing + ruling check + goals + sibling/general form (critic round pricing-split)

Critic: slot (opus), 2026-10-31. Subject: splitstudy_report.md @ 70464e9a3 (snapshot). Base: review tree
worktrees/crit-pricing-split @ a3cc4de82. Read-only; no make.

## Findings

Disclosure: reading `docs/dev/decisions.md` in the review tree with the Read tool auto-injected the review tree's
root, `docs/` and `docs/dev/` CLAUDE.md files (none denied). No denied file was opened. `docs/dev/sel_cost_census.md`
(allowed) was read; `docs/dev/optloop/sellit_read.md` (denied) was NOT opened.

Abbreviations: S = the subject snapshot; RT = review tree `worktrees/crit-pricing-split` @ a3cc4de82;
PR = `lane/memfn-pricesurvey:docs/design/memfn/pricing_requirements.md` (copy: `slot/pricing_requirements.md`).

### SLOT-1 (CONFIRMED, design; CHANGES THE RECOMMENDATION's ruling basis) Q-WR-9 is quoted with its operative clause cut out; the ruled direction is the opposite of (d)'s

- S open point 1 (and Summary item 5) quote Q-WR-9 as: "the consumer's cost enters as a per-route MEASURED constant in
  the D166 set ... and add. 6 gets a dated addendum", and read it as having "named this exact event" (the BACKEND
  comparing kit quotes with consumer rows).
- The elided words, RT `docs/dev/decisions.md` D161 add. 15, Q-WR-9: "If it fires, the consumer's cost enters as a
  per-route MEASURED constant in the D166 set, **never a pcrec price model**, and add. 6 gets a dated addendum."
- D161 add. 11 says the same thing ("no price model returns ... the only pcrec-side quantity is a MEASURED
  per-candidate fixed cost per route"), and r17b_prime.md designs it that way: P1 `priced` is a KIT row ("argmin
  {`verify` = 1, `verify` = 0} by expected cost", RT `docs/design/memfn/r17b_prime.md:787`). It reads a route-keyed
  set quantity M23 `kit.gate.byte1.DFA_SCAN.early/late/absent` (`:1945`, `:2011`).
- So in both rulings and in the kit's own design, the consumer cost flows INTO the kit as a set row (data), and the
  kit makes the choice. (d) does the reverse: the backend makes the cross-footprint choice. Q-WR-9 does not
  anticipate (d). It explicitly excludes "a pcrec price model", and (d) is one.
- Consequence: (d) needs a REVERSAL of Q-WR-9's "never a pcrec price model" clause, not the dated addendum Q-WR-9
  pre-authorized. The study's options table (Q3) has no row for the ruled shape: call it (a′) = the kit reads per-route
  measured consumer rows (A_entry) from the D166 set for its own PARKED/RESEED and stop choice, and the backend
  compares only the kit's best against NO SEARCH / reverse (which is (c)). (a′) keeps D157's direction, keeps D176
  Q1's single priced choice in the kit, and needs no frontier reply (no MF_SITE_ABI reply-shape event). Its cost:
  the kit sees consumer numbers (add. 6's data-quality reasons, SLOT-9). The recommendation must beat (a′), and the
  study never compares the two.
- Effort: a rewrite of Q3's table and open point 1. Blast radius: the recommendation's ruling basis.

### SLOT-2 (CONFIRMED on the rulings' text, design; CHANGES THE RECOMMENDATION or needs a D157 addendum S does not ask for) The frontier reply is a set of facts, but picking from it is pcrec choosing the kit's method, and the render request then carries that method back to the kit

- D157 (RT decisions.md): "pcrec states FACTS and the kit chooses FORMS ... any rule about which or how many
  positions to use is a method, and choosing methods is the kit's job". D172: "the stop choice moves to the kit as
  tables". D176 Q1: "'which stop, found how' is ONE priced choice in the kit's Table A".
- Under (d) the kit returns the non-dominated options across footprints. A footprint is "entry kind, candidate
  stops per byte, survivors, proven positions, members covered" (S Q4, S2 row). The BACKEND takes the argmin.
  Options with different entry kinds are PARKED vs RESEED. Options with different candidate rates are different
  STOPS, wherever spans are SUPERSET (D161 add. 10: no kit verify there). So the backend now picks PARKED vs RESEED,
  and on superset spans which stop. Those are exactly the kit's Table A rows (`wf_arows[]`, RT
  `memfn/src/window.c:637-648`: A-parked / A-model "reseed" / A-mass).
- The pick then has to reach the kit's renderer as "render option k". That is a pcrec->kit message naming a
  method. The owner direction in COMMON forbids exactly this ("pcrec->kit carries facts, never methods").
- S Q4's last paragraph checks only the REPLY ("the footprint fields are ... facts about the form
  (D157-compatible)"). It never checks the pick or the return message.
- Needed: either a D157 addendum (the backend may select among kit-declared options by consumer price, and the
  render request names the option), plus a D176 Q1 addendum (the stop choice is the kit's only WITHIN a footprint),
  plus a D172 addendum. Or restate (d) so the consumer quantity goes to the kit as a fact (SLOT-1's (a′)).
  S open point 1 lists D146 / add. 6 / Q-WR-9 only.

### SLOT-3 (CONFIRMED, design; CHANGES THE RECOMMENDATION's slot list) PRESENCE gets two deciders; the study's own presence unlock is already designed in the kit, and its trigger has already fired

- S RECOMMENDATION, backend: "Own the path argmin over LOCATE, **PRESENCE**, FIRST, NEXT and RETRY". The same section
  also says: "The fold stays the kit's" (open point 5), "D176 Q4 names the kit as presence's one decider", and
  presence on/off stays unpriced (Q1.4 item 1; Q4 "term: PRESENCE ... deferred, Q-WR-9").
- D176 Q4: presence and stop are "two QUESTIONS ... but ONE decider, the kit's window family". The kit's PRES slot
  exists today: `fd_pres` P2/P3/P4 (RT `memfn/src/presence.c:16-32`). pcrec's `cand_rows[]` PRESENCE rows `dominated`
  and `set-leads` only READ P2/P4's verdicts (RT `src/gen/emit_dfa.c:8540-8545`, `:8611-8622`). The priced on/off
  row is ALSO the kit's: P1 `priced`, "argmin {verify=1, verify=0} by expected cost" (RT
  `docs/design/memfn/r17b_prime.md:787`).
- So under (d) the PRESENCE slot would have three homes: the kit's PRES table (decides, P1 its designed priced row),
  `cand_rows[]` PRESENCE (renders), and the backend path argmin (the study's "priced slot"). One table per slot fails.
  Either PRESENCE leaves the backend's priced-slot list (it is a per-path TERM whose value the kit supplies: S's own
  Q4 "term: PRESENCE"), or D176 Q4 is reversed. As written, S does both.
- STALE TRIGGER: unlock 1 ("presence priced per path. Trigger: Q-WR-9's TUG cell measured losing") and open point 5
  ("resolve at Q-WR-9's trigger") treat the trigger as future. r17b_prime.md:273 and `:2350-2364` record it "FIRES ON
  THE LETTER" (KEEP loses 1.47 / 1.54 ns, 3.4-3.8%, on two TUG g8 early cells). P1 was then recorded and NOT built
  (Q-R17P-28, the kit manager's call, D77): "it never fires on a default compile". The live re-ask condition is
  "when a measured-bundle workload exists". Unlock 1 should cite that condition and P1 as its home.

### SLOT-4 (CONFIRMED, design; CHANGES the slot map, not option (d) itself) `fit_rungs[]` is an unlisted, price-ordered second decider of the strategy rows, and it applies AFTER the choice

- S names "the compile_driver retry ladder" only as the place where the engine's late validity (DFA overflow) comes
  from (Q2.2 item 2, Q5 3(iii)). S never mentions `fit_rungs[]` (grep: 0 hits).
- RT `src/core/compile.c:1268-1400`: `fit_rungs[]` has 14 rows. Under a SIZE cap, the rows that are not engine rungs
  REMOVE strategy or form choices the selection already made:
  - `drop-handoff` removes the S5 landmark handoff, FIRST/NEXT ("measured up to ~2.5x more instructions");
  - `drop-prefilter` removes the S6 VM finder ("up to ~4x slower");
  - `drop-anchored` removes the FINISH machine;
  - `drop-premul` changes the backend table form;
  - `drop-end-mark` pins the `rev-end` walk;
  - `drop-compound` drops the compound artifact.
- Their ORDER is a price. `compile.c:836`: "THE ORDER IS BY MEASURED RUN-TIME COST, cheapest first". `:1329`: "the
  size-cap rungs, cheapest first". The table is first-match, and its order encodes "which strategy loss costs least
  time".
- So after (d), FIRST/NEXT's handoff and S6 each have a second decider. It reads a time cost the path argmin does not
  see, and it runs after the argmin's pick. PR R3.2 ("No coupling is applied AFTER the choice ... makes the argmin
  compare the wrong numbers") is violated by today's ladder, and (d) leaves it so.
- General form: the ladder is a constrained argmin, minimum time subject to size <= cap, spelled as first-match over
  "drop X". Under (d) its order could be derived from the path prices: drop the strategy whose next-best fitting path
  loses least. That unifies it with the path argmin (see SLOT-14, unlock U1). Until then, S must list `fit_rungs[]` as
  the late-validity source for S5/S6 (and FINISH's anchored machine). It must also state that a dropped row forces a
  RE-RUN of the path argmin on the retry, not a fallback to the row's first-match successor.

### SLOT-5 (CONFIRMED, design; CHANGES a supporting claim, the nesting) "The path" already has a home with TWO route fields; S6 is a route pair, not an inner strategy row

- S Summary 2 / Q1.4 item 6 make "a coarser table of path families" the new unit. The tree already derives THE
  SELECTED PATH: `CandPath`, `cand_path_of` (RT `src/gen/emit_dfa.c:11828-11955`; locate_finish.md §2.7). It is "a
  value, recomputed per reader". It holds `locate` and `finish` route fields, machines `built` / `needs` /
  `members`, and the asked cells. D156 add. 2 generates every LOCATE x FINISH stamp from it. `CAND_PATH_READS`
  (`:9913-9925`) declares path reads in the reader graph. S cites `cand_nodes[]` but not `CandPath`, the path
  derivation or D156 add. 2.
- (d) inverts the derivation. Today path = f(first-match selections). Under (d), selections = renderings of the
  argmin's path. S must say that the argmin's output IS `CandPath`, or the tree holds two definitions of "the path":
  the priced one, and the derived one the stamps read. It must also say that `path-needs-unbuilt` (`:11946`, a
  trace-build oracle today) becomes a VALIDITY predicate of the argmin, since a path that needs an unbuilt machine
  is invalid.
- ROUTE has two fields. `cand_route_of` (`:3835`) is the BODY's route ("never `fit.chosen`"). `cand_finish_of`
  (`:3847`) is the finisher's. The VM hybrid is locate = DFA/ATTEMPT body, finish = VM. So S6 "VM FINDER" (S Q4) is
  not an inner strategy row on one route. It is the choice of the (locate, finish) route pair. S's nesting formula
  "min over valid routes rt of (match_phase(rt) + min over valid paths p on rt)" (Q2.2) is exact only if `rt` ranges
  over route PAIRS, and S6 then belongs to the OUTER level, not the inner strategy table. As written, S6 sits in both:
  the inner table (Q4) and, through `pf_admits[]` validity, the outer route set (Q2.4).
- Doc: S defines route citing `emit_dfa.c:9845`. That line is `CAND_ALL_ROUTES`, not the route enum, and S's
  definition ("the consumer that runs after the search") is not the tree's ("the engine of the machine the body
  runs").

### SLOT-6 (CONFIRMED, design + maintenance; does not change (d), changes its route clause) The "one-row route preference table" is a fifth member of an existing family, is not a dominance by S's own analysis, and is the case D152 says a table is wrong for

- The engine/route decision today has four homes:
  - `analyses[]` (RT `src/opt/select_engine.c:417`, AND of validity masks);
  - the `--engine=` switch (`:1436-1465`, caller);
  - the auto ternary `fit.chosen = (mask & ENGM_DFA) ? ENGM_DFA : ENGM_VM` (`:1468`, the preference; NOT a table);
  - `fit_rungs[]` `sel1-collapse`/`sel1-drop` (RT `compile.c:1283-1300`, late validity).
  `pf_admits[]` (`select_engine.c:669`) decides the route PAIR's prefilter half (SLOT-5). (d) adds a backend one-row
  table, the fifth member. Memory "forest for the trees" asks for a unification proposal at about 3 members, and S
  makes none. The general form: ONE route table whose rows are classed caller / validity / late-validity /
  preference, read by one walk.
- D152 ("When a table is the wrong tool: a single yes/no"). A one-row table with an implicit else is that case. S
  does not argue why a table is wanted there, and does not cite D152.
- S Q2.1 labels the auto rule "DOMINANCE". S Q2.2 then says it rests on a measured per-byte gap, holds "only for the
  SEARCH", and is "not proven" on match-dense subjects. A rule based on a number that is not proven is not a
  dominance under S's own clause 2 ("never a number"). Under D149 it is an UNMEASURED-DEFAULT preference and must be
  labelled so. RECOMMENDATION's "dominance basis named" names a basis S has refuted.

### SLOT-7 (CONFIRMED, design; CHANGES the seam rule) Moving the route preference to the backend makes FRONT-END passes readers of a backend pick; no seam clause allows that

- S Q2.4 (c)/(d) moves "prefer the DFA" "(logically) from `src/opt` to the backend". The engine pick
  (`job->fit.chosen`) is read BEFORE any emission by front-end AST rewrites:
  - `run_possessify` (RT `src/opt/select_engine.c:498-504`, `if (fit->chosen != ENGM_VM) return;`);
  - `run_revdet` (`:520-525`). Both are called right after the pick (`:1475-1480`, "the only steps here that need the
    engine ALREADY chosen").
  `grep -rnE 'fit(\.|->)chosen' src/opt src/core --include=*.c` finds 30 mentions in `src/opt` and `src/core` (17 of them code lines outside comments), including the driver's ladder
  predicates (`compile.c:1152`, `:1186`) and `compound.c:206`.
- The seam rule's five clauses cover validity, dominance, price, rendering and the kit. None of them covers a
  front-end TRANSFORM that reads a backend selection. Clause 4 allows only rendering to read a pick. Possessify and
  revdet are not rendering: they rewrite the AST that the VM program (and so the VM consumer's per-byte cost, S's 5x
  per-artifact variance) is built from. The price of the VM route therefore depends on front-end work that depends on
  the route pick. That is a cycle between the outer argmin and the front end, and S's "build happens between them"
  sequence (Q2.4 (c)) does not show it.
- Needed: either a sixth clause ("front-end transforms may read the route pick; the route pick never reads their
  output except through built-machine facts"), or the route preference stays in `src/opt` (the front end). The
  latter contradicts S's emit-backends argument for (c)/(d).

### SLOT-8 (CONFIRMED, doc + design; changes open point 4's trigger, not (d)) Engine pricing already has a plan row and a census; "no cell is on record" is wrong

- S Q2.2 INFERENCE: "No cell is on record showing it wrong". Open point 4: "Engine pricing stays unbuilt. Trigger: a
  both-valid pattern with the VM measured faster". S never cites `[SEL-COST]` (grep: 0).
- RT `docs/dev/plan.md line 331 (at freeze)`: `- [SEL-COST] STATE:not-started — auto's engine choice has no measured cost model`. Its
  STEP 0, RT `docs/dev/sel_cost_census.md:80-84, 193-205` (syntax@0.1, abi 39, Ryzen 1600), finds forced-VM wins over
  auto beyond 1.03x on 10 of 80 large-subject cells and 19 of 83 short-subject cells. The sharpest is `lka-pos`
  `item(?= done)`, 1.30x VM on large-subject-throughput. Caveat: the forced-VM arm also drops the prefilter, so most of
  these cells are the S6 (hybrid on/off) choice, which S calls "mostly validity" under D158 (Q2.1 / Q4 S6). That
  census is the counter-evidence: S6 has measured cost losses both ways, on cells where it is not a validity question.
- Consequence: open point 4's trigger is already met in kind, at an old abi. The right step is the existing row's
  re-read at the current abi (memory "grep plan before chartering"), not a new trigger. S6's "validity" classification
  should be narrowed to the population where the VM can give up (D158), with the rest a priced route choice.

### SLOT-9 (CONFIRMED on the rulings' text, design; consequence S does not state) D161 add. 6 dropped consumer price for reasons that moving it to the backend does not answer, and there is no staleness key for consumer cards

- D161 add. 6, reading: consumer price per route was withdrawn as "hard to gauge, fuzzy to use, box-specific, and
  **stale after every engine change**". S's answer (Q3 table, "kit contract" row) is about LOCATION: "the kit still
  never sees a consumer cost". The reasons were about the DATA, and they hold wherever the data lives.
- Staleness has no mechanism for consumer rows. D166 add. 2 carries a set STALE when "a measured form's (normalized)
  body changes" (the kit's formhash, `memfn/src/formhash.c`). A consumer card measures pcrec's own engine bodies. Two
  in-flight changes move those bodies with no form hash to notice: D182's VM records (steps (b) and (c) still to come)
  and D183's trail compaction. Every engine change would leave A_entry and the no-search per-byte rows silently stale
  and still moving picks. S Q5 item 1 checks units, not staleness.
- Add. 6 also says why consumer cost was not needed: "the residual per-false-candidate cost is removed by
  verification at the chain's last link ([KIT-VERIFY])". Where the kit verifies exactly (EXACT spans, D161 add. 10),
  survivors are the true starts for every option. The A_entry term is then equal across PARKED / RESEED, and the
  footprints coincide. So S's frontier has more than one member only on SUPERSET-span sites. S does not state this
  population, and it bounds the value of (d)'s reply-shape change. Under D77, count it first (it is a census, not a
  build).
- Needed: a D166 addendum (a consumer card's staleness key: the engine body's normalized hash, or "stale on any abi
  event touching `src/gen/emit_vm*` / `emit_dfa*`"), and the superset-span population as a stage-0 census.

### SLOT-10 (CONFIRMED, design; CHANGES open point 7's enforcement claim) The CAND_TRACE reader shadow cannot see the reads the seam rule restricts; "a general mechanism, not a new one" is wrong

- S open point 7: the seam is "enforced by declared read classes. The CAND_TRACE reader shadow's `reads`/`kask`
  mechanism can be extended to read classes per column".
- What the shadow observes (RT `src/gen/emit_dfa.c:9860-9893`, `:10698`, `:11582`, `:11613`): a predicate's read of
  another SLOT's selection (`reads[t]`, `under`/`by` deny transparency) and its kit ASKS (`kask[t]`, `kfields`).
- What the five clauses restrict, and whether the shadow sees it:
  - clause 1, "never reads a price, a rate, or a measurement-set row": rates come from `pcrec_find_byte_rate`
    (RT `src/core/findings.c:429`), called straight from predicates (`emit_dfa.c:8554`, `:8562`, `:9019`, `:10898`).
    No `cand_nodes` edge sees it.
  - clause 3, a price "never reads the pattern, the IR": fact reads go through `pf_enter` (RT `src/facts/facts.c:126`),
    whose per-fact `used` bit is a separate mechanism (Q-WR-12) with no reader identity.
  - set rows: through the measures accessors, observed by neither.
- "Per column" has no column to attach to. A row has ONE predicate: `CandRow.c` is
  `DfaCand { name, deny, applies }` (`emit_dfa.c:3859-3863`). Clauses 1 vs 4 (validity may not read a pick,
  rendering may) need the predicate SPLIT into a validity column and a rendering selector. S does not propose the
  split.
- The shadow is trace-build only (`-DPCREC_CAND_TRACE`) and dynamic: it sees only reads the corpus reaches. PR R2.4
  asks for a STRUCTURAL test ("price functions take a facts record and a set, nothing else") with a planted violation.
  The two enforcement designs differ, and S does not reconcile them.
- Clause 1's "other selections on the same path" changes meaning under (d). Today a slot read runs the other slot's
  first-match walk (`CAND_READ`). Under the path argmin it must return the HYPOTHESIZED path's row for that slot,
  so `reads`/`under`/`by`, the mechanism S proposes to extend, is itself re-specified.
- Needed: three instruments (slot reads, fact reads, rate/set reads, each with a reader class), a CandRow predicate
  split, and the choice between a structural and a dynamic check.

### SLOT-11 (CONFIRMED, design; supporting claim "seven crossings, none breaks the seam" undercounted) Existing readers that break the clauses and are missing from S's Q1 table

1. NEXT `first-class` (VM), `pf_vm_start_applies` (RT `emit_dfa.c:8022-8026`): "(D149) `|S| < 256` as the ONLY
   narrowness gate is an UNMEASURED DEFAULT: no density admission is applied, and a dense `S` ... still seeks; ... a
   MASS admission is filed behind them (Q-R5)". This is a price ("does a dense seek pay?") decided inside a validity
   predicate, a crossing of kind X. S Q1.2 lists `first-class` (VM) as "V ... no".
2. NEXT `first-memchr-bounded` / `first-class-bounded` (DFA hat), ADMISSION `T ⊊ E` (`:7872-7876`): "The
   proper-subset test with NO MARGIN is an UNMEASURED DEFAULT". It is a "narrowing pays" judgement in the validity
   predicate. It is measured in part (D148 add. 5 Q4: one- and two-byte narrowings win 6-50%), but it is still a
   price comparison. S lists these rows only as a "tactic split by |T|" (leak 2).
3. `compound_rows[]` (RT `src/core/compound.c:261`), row A1 `a1_attempt_all` (`:204-210`). It reads the PLAIN
   artifact's BOUND selection BY NAME (`!strcmp(pcrec_cand_plain_selection(...), "all")`) and its LOCATE asks, plus
   `fit.chosen`. It is a selection (plain vs compound artifact, D163) whose validity reads another artifact's picks.
   It is not rendering (clause 4), not the same path (clause 1), and S never mentions the compound. The name-string
   read is also the K84/K89 anti-pattern D152 cites ("sites selecting a row by name string").
- With SLOT-4 (`fit_rungs[]`) and SLOT-7 (possessify/revdet), S's "seven inputs cross the seam ... Every one is the
  third kind" holds for at least 9 crossings plus 3 reader classes S did not survey (the driver's ladder, the
  compound, the front-end transforms). Items 1-2 are restatable the same way S restates its seven (comparison into the
  price, facts handed over), so the seam survives them. The ladder, the compound and the transforms need clauses the
  rule does not have (SLOT-7).

### SLOT-12 (CONFIRMED, internal contradiction; design) LOCATE can never become a priced slot under S's own rules

- S Q6 stage 3: replace "LOCATE's `cover` vs `composite`" third; and "A slot is priced only when every row on it is
  measured (D166; D176's standing rule)".
- S open point 6: "`rev-end`'s price needs a bytes-walked-back estimate. There is no data: until there is, rank it
  UNMEASURED, and keep its first-match place". `rev-end` is a LOCATE row (S Q1.2), ahead of `cover` in the table.
- So LOCATE is never fully measured, cannot be priced, and stage 3's third step cannot run. If it runs anyway, LOCATE
  is a MIXED slot: one row winning by order, two by price. S defines no mixed regime (where an UNMEASURED row sits
  relative to priced ones; whether `rev-end`'s order still pre-empts a cheaper `cover`).
- PR conflicts as well. PR R4.5 says an UNMEASURED row is "declined, with that reason". S keeps it, by first-match. PR
  R1.1 puts T13 (reverse routes) in round 1 anyway. With S's rule and PR R4.5 together, `rev-end` would be DECLINED on
  every compile: a mover that disables a shipped optimization. This is a PR-as-subject finding: R1.1 + R4.5 conflict
  with D156 add. 1 (REVEND shipped) unless "declined" means "unpriced: first-match" (R1.2's wording).
- Needed: a declared mixed-slot rule. Leaning: an UNMEASURED row keeps its first-match position as a DOMINANCE-ordered
  prefix (rows above the priced block). Or else LOCATE leaves the priced list until `rev-end` has a card.

### SLOT-13 (structure CONFIRMED, outcome SUSPECTED; design) Under (d) a pick has two homes: the priced option, and the first-match rendering walk that can fall through to a different strategy

- S: "`cand_rows[]` survives as the validity and rendering table beneath it ... RENDERING may read the pick".
- Today the NEXT rows that render the kit's reply are first-match rows. Their `applies` combines F conditions with
  the reply key. `pf_run_applies_common` (RT `emit_dfa.c:7335-7344`) needs `pin.pinned`, `r->len >= 2`, `forward`, a
  non-NONE kind, then `next_key_holds(s, NK_RUN_PINNED)`. When it fails, the walk goes on to `offset-set`,
  `handoff-reentry`, `memchr`/`byte-class` (start-set scans, another strategy family), and finally `next-none`
  (NO SEARCH), the always-sound last row (D152).
- Under (d) the argmin has priced ONE option (for example a PARKED run stop). If any F conjunct of its rendering row
  fails, first-match renders a different, unpriced strategy, silently. The trace then shows a priced pick the
  artifact does not carry, which breaks G2 (PR) and S's "one trace" claim. S Q5 3(ii) covers "the kit refuses at
  render time a site it accepted at ask time", but not pcrec's own rendering walk falling through.
- Needed: rendering is a TOTAL keyed lookup from (path family, kit option) to a row, never first-match with a sound
  fallback. A miss is an internal error (the `CANDORACLE` family is the natural home: "rendered-row != priced
  option"). Witness to confirm: a site where the kit's reply says RUN_PINNED but `us_run_pin` is not pinned. Not
  probed: it needs a kit reply that today's kit, which computes both from one statement, may never produce.

### SLOT-14 (CONFIRMED family census; design/maintenance) After (d), several decision families have three or more members and S proposes no unification

"Forest for the trees" counts, RT @ a3cc4de82 plus what (d) adds:

| family | members after (d) | S names? |
|---|---|---|
| TIE rules | kit `wf_ties[]` (RT `memfn/src/window.c:47`; "every tie reads `wf_ties[]`", memfn/src/CLAUDE.md); D176 Q5 "decided by the existing declared tie rows"; [TIE-ALIGN] (plan.md line 613 (at freeze), run reader RIGHTMOST vs prefix_k LEFTMOST, "five tie rules for one pick", decision_families_survey.md:58); (d)'s backend SIMPLICITY ORDER | only the new one |
| priced argmins | kit Table A + MARGIN (D176 Q1); kit P1 (designed); (d)'s backend path argmin; the future outer route argmin; `fit_rungs[]`'s measured-cost order (SLOT-4) | two of five |
| route/engine decision | `analyses[]`, `--engine=`, the auto ternary, `fit_rungs[]` sel1 rows, `pf_admits[]`, (d)'s one-row table (SLOT-6) | three of six |
| kit-reply FACTS about its form | D161 add. 8 proven facts; D182 ruling (c)(1) "kit windows are OPAQUE WITH DECLARED EFFECTS: the kit states as facts with each delivered window what it reads and writes"; (d)'s footprint | only the footprint |
| homes for an estimation constant | the measurement set (D166); [EST-REGISTRY] (D141, "one table for every estimation weight, bias, threshold and fitted constant ... reseed thresholds ... DFA/VM cost terms"); `PLACE` | S sends `reseed_gap` (RT `src/core/internal.h:9219`) to "a row of the measurement set or go" without D141 |
| retry-slot policy | `cand_rows[]` RETRY, [START-DENSE] (plan.md line 629 (at freeze); D153 item 4: K90 + K91 + [OPT-HYB-RESEED-POLICY] are ONE retry-slot row, gated on C7) | S's Q6 "RETRY first" never cites [START-DENSE] |

- Proposals (each a merge of existing members, not a new mechanism):
  - ONE tie table shared by the kit and the backend. The simplicity order is its cross-row key, `wf_ties[]` its
    within-kit rows.
  - ONE kit-form fact record (proven / effects / footprint), designed once, inside the D176 build's MF_SITE_ABI event
    (S open point 2 already places the reply shape there).
  - ONE route table (SLOT-6).
  - D141 vs D166: say which home an estimate goes to. Leaning: a MEASURED quantity goes to the set, a RULED or
    structural constant to the registry. `reseed_gap` ("the class's calibrated crossover") is the first case.
  - [START-DENSE] is the retry slot's owner, and Q6's RETRY stage is that row's re-scope.

### SLOT-15 (CONFIRMED on the rulings' text, design; consequence S does not state) D158 under an argmin has no "denied build" to compare against; the give-up contract must hold pairwise across a slot's valid paths

- D158: "if the build with an optimization DENIED answers, the default build answers too". [GIVEUP-DIFF] / GIVEUP1
  checks deny-vs-default. In first-match, denying a row lands on a FIXED successor, so the pair is static. S Q5
  item 5 keeps this frame: a cheaper path must not give up where "its fallback" answers.
- In an argmin, the alternative to a pick is data-dependent: it is whatever is next-cheapest under the current set. A
  D166 set change moves picks automatically (D166 item 1) between ANY two valid paths. So the D158 property needed
  is: every pair of valid paths in a priced slot has an equal give-up surface, or differs only one way and the price
  is forbidden to cross it. Otherwise a set revision alone can turn answers into give-ups between two pcrec builds
  with no deny bit involved, and GIVEUP1's deny pair never sees it.
- `CG_FIXED` is declared per ROW (`emit_dfa.c:9823-9830`). The path-level rule (a priced slot admits only rows of
  one give-up class, or the argmin's valid set is filtered by "give-up surface ⊆ the slot's least") is missing from
  S's seam clause 1. A D158 addendum is needed: "a decision that moves with the measurement set never moves the
  give-up surface". This is also a check the mover census for a new set revision must run (D166's census).

### SLOT-16 (CONFIRMED on the rulings' text, design; consequence S does not state) Under (d) the SIMD switch moves pcrec's STRATEGY, which D147 and add. 6 place inside the kit

- D147 add. 6: "What sits inside SIMD-on is the kit's choice, per site". D147: the scalar layer ("the algorithm:
  what is searched, the plan, handoffs") "must be the best it can be with SIMD OFF". D176 Q1: "the SIMD layer
  changes which methods are available, not their cost".
- Under (d), kit quotes enter the BACKEND's cross-strategy argmin. A SIMD-on quote can make S2 (window search) beat
  S0 (no search) or S5 (handoff) where SIMD-off it does not, so `-fmemfn-simd` changes which STRATEGY pcrec emits,
  outside any kit site. The SIMD layer then substitutes for an algorithm choice, which D147 forbids ("never a
  substitute"), and the "scalar layer is best on its own" acceptance can no longer be read on the same strategy set.
- Needed: a D147 addendum. Either (i) the strategy argmin always prices with the SIMD-OFF quotes and SIMD only
  re-forms the chosen site (keeps D147 exactly, costs some SIMD-on optimality), or (ii) the strategy may move with
  the layer, and both layers' acceptance runs read the strategy movers. S's Q5 never mentions layers, and PR has
  no requirement for this either (PR-as-subject: missing).

### SLOT-17 (CONFIRMED on the rulings' text, design) The D146 addendum S asks for is too narrow: (d) also breaks "carries no architecture knowledge", and D146's Revisit-when has not fired

- D146: "pcrec does no cost comparison **and carries no architecture knowledge** (Q12's refinement)". S open point 1
  asks for an addendum to the first half only. Under (d) the backend owns "per-route consumer costs as measured set
  rows (A_entry, no-search per byte, reverse per byte)". Those are box-specific (D166: "Different machines give
  different absolute values"), so pcrec carries architecture knowledge as data. The selection key A ("which
  measurement set", D166 item 3) becomes a pcrec-side input, not only a kit-side one. The addendum must cover both
  halves.
- D146's own **Revisit-when**: "a delegated site's kit code is measured worse than pcrec's pre-migration form and the
  kit cannot fix it". S cites no such measurement. The trigger S relies on is the owner direction ("strategies are
  priced as declared rows"), which is a legitimate ruling source. But the addendum should say it is a NEW direction,
  not a fired revisit, so that D146's "Why" (the r2 panel: a cross-project price layer "recreates the
  measurement-regime, shared-source and recalibration problems at the project boundary") is answered. (d)'s frontier
  IS a price layer at the project boundary, and S's Q5 item 1 (one set, set id per quote) is the answer to that "Why".
  S should cite it as such.
- D146 Guard ("pcrec's own bench/alpha timings with the kit on vs off") is unaffected and remains the independent
  control (S Q5 item 2 agrees).

### SLOT-18 (CONFIRMED, design/process) D77 and D153 consequences for Q6's stages

- D77 ("when we would be better served building something later under measurement, wait"). Q6 stage 1 builds the
  path-family table, its price column and a shadow argmin BEFORE any consumer card exists ("Prerequisites before
  stage 3"). S Q6 stage 1 itself says rows with an UNMEASURED term rank "unrankable". With no no-search card, no
  A_entry and no reverse card, EVERY priced slot is unrankable, so the stage-1 shadow's census (stage 2) has nothing
  to compare. Under D77, stage 1 should follow at least one slot's complete card set. RETRY needs B + R, so its
  cards come first. S also names no measured mispick that (d) fixes; its motivation is the owner direction plus PS
  C6/C7 ("never priced"), which are absences, not losses.
- D153 ("don't live in a house we're remodeling"). Sites (d) touches and their in-flight owners:
  - the VM consumer cost: [VMREC] `STATE:started` (plan.md line 238 (at freeze)), D182 steps (b) and (c) owed;
  - the set format and consumer cards: [MEASURE-SET] `STATE:started` (plan.md line 183 (at freeze));
  - crossing 7's retirement of `req_byte` / `req_run.idx`: [MEMFN-UNBOUNDED-SPANS] `STATE:not-started`
    (plan.md line 894 (at freeze)), which S calls "already planned";
  - Table A's MARGIN and C_ENTER: the D176 build (waits for the step-0 census).
  S places only the reply shape ("designed with the D176 build"). D153 asks for the "remodel overlap" column on
  each of S's Q6 stages.
- Not a reversal of anything. A sequencing hunk.

### SLOT-19 (CONFIRMED, design/doc) D152 is the standing rationale for first-match tables, says an argmin is a different tool, and S never cites it; its attached machinery has no stated argmin form

- D152, "When a table is the wrong tool: ... a choice that is really a cost comparison across all options (an argmin
  is a planner, not first-match — D151 avoided that)". The owner direction makes "priced-argmin" acceptable, so this
  is no veto. But D152's list of what a table buys has to be re-stated for a priced slot:
  - "explicit precedence: row order is the priority": gone on priced slots, replaced by the simplicity order on ties;
  - "checkable totality and reachability ... count each row's population (K35)": in an argmin, reachability is
    SET-dependent (a row may be reachable under one set and dead under another). The structural self-check
    (`emit_dfa.c:11220`, "the STRUCTURAL SELF-CHECK of `cand_rows[]` against `cand_nodes[]`") cannot prove it
    without the set;
  - per-row deny flags, `*_WHY` stamps, `--list-axes` listing, hit counters and `--tune` positions: deny still
    works (it removes a candidate), but `--tune` positions and listing order lose meaning.
  The [LIST-TABLES] row (plan.md line 1297 (at freeze), "EVERY SELECTION TABLE LISTABLE") must list the new path-family table and
  its price column.
- Needed: a D152 addendum ("a priced slot: rows = candidates, order = the simplicity order; reachability is reported
  per set revision; the population count is per set").

### SLOT-20 (CONFIRMED, design) GOALS: S states no ranked, checkable goals; against PR §0, option (d) leaves G4 violated and G5 untestable

- S has no goals section. It works from MV and the owner direction. "Regret" appears 7 times (Q5), with no bar. G1-G5
  and PR are never cited, although PR is the round's standard (PR §10).
- Against PR §0 as the standard:
  - **G1 (good picks, regret bar):** testable under (d) (S Q5 item 2, held-out, independent). Bars are absent
    (PR O1 open).
  - **G2 (one trace explains every mispick):** S's trace with per-term components plus "margin to runner-up in band
    units" meets it. SLOT-13 is the exception: a rendering fall-through puts a pick in the trace that the artifact
    does not carry.
  - **G3 (no tuning):** (d) deletes MARGIN 2/1 and makes `reseed_gap` and the K admission measured. Two
    leftovers: the route preference that S keeps as "dominance" (SLOT-6, an unmeasured preference), and the two
    UNMEASURED-DEFAULT admissions S did not list (SLOT-11 items 1-2).
  - **G4 (one row + one card): VIOLATED by construction.** A new strategy under (d) touches the path-family table,
    `cand_rows[]` (validity + rendering rows), the total simplicity order (where it inserts), the footprint vocabulary
    if it shows the consumer a new attribute (an MF_SITE_ABI event), the kit's reply, and the trace. At least four
    homes. PR's G4 reading ("touches only its row, its card and its tests") cannot pass.
  - **G5 (<= 1% compile time): UNTESTABLE / unaddressed.** The path argmin enumerates path families times kit frontier
    options, RECOVER/FINISH are evaluated per candidate path, and the kit prices several options per site. S gives no
    size estimate (frontier "1-3, INFERENCE") and no compile-time figure. The OUTER route argmin needs machine BUILDS
    (S Q2.2 item 2), which can be multiples of today's compile.
- Effort: S should add a goals table (adopt PR §0) and score (d) and (a′) (SLOT-1) against it.

### SLOT-21 (CONFIRMED, PR as SUBJECT, design/doc) Requirements that are wrong, missing, or in conflict

1. **R2.3 FRONT END "states ... the couplings the strategy forces on the consumer (presence fold, handoff point K,
   reseed)"** conflicts with D176 Q4 ("One general fold ... ONE decider, the kit's window family") and with S (the
   kit states fold reach per option). The fold is a fact about the KIT's chosen stop. The front end cannot state it
   before the stop is chosen. (R2.3 is HELD, so this is a note for its revision.)
2. **R2.3 KIT "returns its best form's price"** is inexact under coupling C2/C3 (S Summary 4). It needs either a
   frontier (S) or the consumer quantity as a set row (Q-WR-9 / SLOT-1). PR should state which, since R3.1(b)
   already allows "named as breaking separability".
3. **R2.4 has no DOMINANCE class.** It knows applicability and price only. S's clause 2 (dominance may read facts on
   either side, never a number) is a real third class (S Q1.2's "D" rows, 19 of 51). Without it, R2.4's structural
   test would flag every dominance prune that reads a backend form fact (`one-attempt` reads "frameless program").
4. **R4.4 / O2 vs S Q5 item 4:** PR leans to interval arithmetic for a composite band, S to the root-sum-of-squares
   (RSS). RSS gives narrower bands, so fewer ties and fewer simplicity-order picks. It is a method choice that moves
   picks, and G3's grep-count test cannot see it. One must be ruled. Note: neither is a free parameter.
5. **R1.1 + R4.5 vs the shipped `rev-end`** (SLOT-12): round 1 includes T13, R4.5 declines UNMEASURED rows, and so
   `rev-end` is declined everywhere. A missing mixed-slot requirement.
6. **Missing: the size-cap ladder.** R3.2 ("No coupling is applied AFTER the choice") is violated by today's
   `fit_rungs[]` (SLOT-4). PR has no requirement placing the ladder (O3 prices code size later, but the ladder already
   trades size for time by a measured order).
7. **Missing: the SIMD layer** (SLOT-16). PR R5.5 reads both layers for verdicts, but no requirement says whether the
   strategy may differ by layer.
8. **Non-goal "choosing the engine — the engine is an INPUT fact"** is sound for round 1. It should name [SEL-COST]
   (plan.md line 331 (at freeze)) and its census (SLOT-8) as the owner of that question, so the non-goal is not read as "no data
   exists".

### SLOT-22 (CONFIRMED on S's own text, design; CHANGES the seam rule's wording) The five clauses are not consistent with each other or with S's own body

- **Clause 2 vs Q2.1/Q2.2:** see SLOT-6. "Prefer the DFA" reads a number and is called dominance.
- **Clause 3 vs Q1.4's last paragraph:** clause 3 lets a price read "only quotes, set rows, rates, and facts handed
  across". Q1.4 says two price inputs are backend FORM facts that "belong with the backend that chose the form": the
  DFA table form, and the VM frame discipline behind the 5x per-artifact variance. Those are not "handed across".
  Clause 3 must admit "the backend's own form facts", or unlock 2 (the per-artifact consumer cost) is forbidden by the
  rule it unlocks.
- **Clause 5 vs D176 Q1:** "The kit compares only options with the same consumer footprint". On SUPERSET spans,
  different stops have different candidate rates, so different footprints. So the stop choice leaves the kit there
  (SLOT-2). Clause 5 silently narrows D176 Q1.
- **Clause 1 vs clause 4 inside one predicate:** today's NEXT rows read the pick in their `applies` (`next_key_holds`).
  Under the clauses, the same function is validity (forbidden to read a pick) and rendering (allowed). It is not
  enforceable until the predicate is split (SLOT-10).
- **Missing clause (orchestration):** the driver (`compile_driver`, `fit_rungs[]`) reads validity outcomes (overflow)
  and orders retries by measured cost. No clause owns it (SLOT-4, SLOT-7).

### SLOT-23 (standing question: GENERAL FORM + UNLOCKS; design) (d)'s general form is a nested argmin in which each level returns its Pareto frontier over the properties its parent prices; its unlocks run up the nesting

- **General form.** Each level (the kit within a footprint, the backend over paths, the driver over route pairs, the
  artifact shape over plain vs compound) returns, for each combination of the properties its PARENT's cost depends
  on, its best option, with price components. The parent adds its own terms and takes the argmin. A dominance prune
  is the frontier's "never better on any property". This is the query planner's "interesting properties" pattern
  (each sub-plan's best per output property). S found one instance of it (footprint = the consumer-visible
  properties). Size, give-up class and SIMD layer are further properties of the same kind.
- **S's unlocks, checked:**
  1. "presence priced per path": wrong home and stale trigger (SLOT-3). The home is the kit's P1, re-asked when a
     measured-bundle workload exists.
  2. "per-ARTIFACT consumer cost": right. It needs clause 3 widened (SLOT-22). Its natural fact source is D182's
     typed VM records (the record kinds and counts of the body), which keeps it off the AST. Trigger unchanged.
  3. "other backends' tactic providers": right (a second backend).
  4. "multi-site joint pricing (start x reseed, C16)": right. It belongs to [START-DENSE]'s re-scope (SLOT-14).
- **Unlocks S missed, each with its trigger:**
  - U1 **the size ladder as a constrained argmin.** Size becomes a frontier property, and `fit_rungs[]`'s "cheapest
    first" order is derived from path prices instead of typed (SLOT-4). Trigger: a size-capped compile where the
    ladder's order ships a measurably slower artifact than another rung would.
  - U2 **code size priced** (PR O3): the same frontier property, giving the caller's size dial (lowsize) a priced
    meaning. Trigger: a measured bytes-for-time exchange, or a caller asking for a size/speed dial.
  - U3 **plain vs compound (D163) as an outer level.** `compound_rows[]` would read the plain artifact's frontier
    instead of its picks by name (SLOT-11 item 3). Trigger: the first priced LOCATE slot, which makes A1's name read
    unsound.
  - U4 **ONE kit-form fact record** (proven, effects, footprint: SLOT-14). Trigger: the D176 build's MF_SITE_ABI
    event. Doing it there costs one abi event instead of three.
  - U5 **the SIMD layer as a frontier property** (SLOT-16 option (ii)). Trigger: a cell where the SIMD-on strategy
    differs from the SIMD-off one and is measured faster.

### SLOT-24 (CONFIRMED on the rulings' text, design; minor) Standing question SIBLING OF A FAMILY: the "UNMEASURED -> unrankable" rule ignores the measurement set's existing fallback family (D161 add. 12, D166 add. 2)

- S Q6 stage 1: "Rows with an UNMEASURED term rank as 'unrankable (UNMEASURED: term)', never with a placeholder."
  S open point 3: "no priced slot before they exist".
- The tree already rules the unmeasured case for decision measurements. D161 add. 12: "each declared ISA has a
  GENERIC tuning class whose constants are MEASURED (the conservative envelope ...). A specific tuning class with no
  measurements falls back to generic", with provenance shown. D166 add. 2: before a second official set, "a bare
  compile reads the LATEST set". The library plan in D176 Q3 has "closest-match selection over declared fallback
  rows". PR R4.5 follows this ("A value from another box enters only through the set's declared fallback rows").
- So a consumer card enters the same family as the kit's cards. On a box without it, the generic envelope (or the
  latest set) answers, visibly, and "unrankable" is the case where NO set in the fallback chain has the row. S's
  pricing seam is a sibling of the set's class-default mechanism, and should say it reuses it rather than define its
  own UNMEASURED rule.
- Also a sibling: the kit's own "total without data" default (LINER, D162; D161 add. 11), i.e. what a selection
  does when E is absent. The backend argmin needs its own "total without data" row (the first-match order, R1.2's
  "unpriced: first-match"). S implies this in stage 1 ("first-match still decides") but does not state it as the
  steady-state default for the period when the set has no consumer rows.

### SLOT-25 (SUSPECTED, design/doc; S's leak 2, sharpened) After D161 add. 14 / Q-WR-1 the "one member vs set" rule has two homes, and pcrec's copy names a method in a stamp

- S leak 2 says the `memchr` / `byte-class` split "may be rendering only. Check before acting".
- RT: the rows `memchr` / `byte-class` (`emit_dfa.c:10397-10415`) split on `UnanchStart.kind` (ONE_BYTE vs
  BYTE_CLASS), and each stamps its `.tok` into `RX_DFA_PREFILTER` ("memchr" / "byte-class"). Q-WR-1 (D161 add. 15)
  put the same count rule in the kit: "one member -> the libc row; else the set form", labelled
  UNMEASURED-DEFAULT, and the kit's D1/D1w rows decide libc vs WALK for one member (r17b_prime.md:105-115).
- So the slot "which form scans the start set" has two deciders: the kit's D1/D1w/set rows and pcrec's first-match
  kind split. pcrec's stamp says "memchr" whether or not the kit chose the libc row. That is a D174 naming problem
  ("caller-facing names describe behaviour") if the kit picks D1w (walk).
- To confirm: compile a one-member DFA_SCAN site where the kit's row is D1w (the "anywhere else" one-member case),
  and compare `RX_DFA_PREFILTER` with `<PREFIX>_MEMFN_FORMS`. Not probed: no pattern was found that reaches D1w on
  a DFA-route NEXT site without reading kit internals. Under (d) the rule is the same: the pick's home is the kit,
  and pcrec's two rows collapse to one rendering row keyed on the kit's form.
- Probe (held on today's default): `$B -p rx -o slot/probe.c --pattern 'q\d+z'` stamps `RX_DFA_PREFILTER "memchr"`,
  `RX_MEMFN_FORMS "none"`, and the body has 2 `memchr(` calls, so the stamp matches the form on this witness. The
  suspicion is only about the D1w case, and about the two homes as a maintenance hazard.

### Ruling check summary (item 3 of the brief)

| ruling | S agrees? | addendum S asks | addendum actually needed / consequence S does not state | finding |
|---|---|---|---|---|
| D146 | partly | "no cost comparison" | also "carries no architecture knowledge"; it is a new direction, not a fired Revisit-when; the "Why" (a price layer at the boundary) is answered by Q5 item 1 and should be cited | SLOT-17 |
| D147 | not discussed | none | the SIMD switch would move pcrec's strategy; addendum (i) price with SIMD-off quotes, or (ii) the strategy moves by layer and both layers' acceptance reads it | SLOT-16 |
| D157 | reply: yes; pick: no | none | the backend's pick among kit options and the "render option k" message are pcrec choosing and naming a kit method | SLOT-2 |
| D161 add. 6 | location only | dated addendum | the reasons (box-specific, stale on engine change) hold in the backend; KIT-VERIFY confines the frontier to superset spans | SLOT-9 |
| D161 add. 11 | not cited for this | none | it already filed a pcrec-side per-route consumer cost flowing TO THE KIT, under a TUG trigger | SLOT-1 |
| D161 add. 14 / Q-WR-1 | leak 2, inference | none | the count rule has two homes | SLOT-25 |
| Q-WR-9 | misquoted | dated addendum | "never a pcrec price model" is cut by the ellipsis; (d) reverses it. The trigger fired on the letter, and P1 was recorded, not built (Q-R17P-28) | SLOT-1, SLOT-3 |
| D176 Q1 | narrowed silently | none | on superset spans, clause 5 moves the stop choice out of the kit | SLOT-2, SLOT-22 |
| D176 Q4 | yes in text, no in the slot list | none | PRESENCE in the backend's priced slots gives it two deciders | SLOT-3 |
| D176 Q5 | yes (fixed point, band) | none | "the existing declared tie rows" (`wf_ties[]`) vs the new simplicity order: one tie family | SLOT-14 |
| D158 | yes, per row | none | in an argmin the comparison base is every valid path, under every set revision | SLOT-15 |
| D166 | yes (one set) | none | consumer cards need a staleness key; the generic-class fallback applies to them | SLOT-9, SLOT-24 |
| D182 | listed, unused | none | the VM consumer cost moves under steps (b) and (c); the records are unlock 2's fact source; declared window effects are a sibling of the footprint | SLOT-9, SLOT-14, SLOT-23 |
| D153 | not cited | none | VMREC and MEASURE-SET are started, MEMFN-UNBOUNDED-SPANS is not; a remodel-overlap column is needed | SLOT-18 |
| D77 | cited for dominance slots | none | the stage-1 shadow precedes every card, so it is all "unrankable" | SLOT-18 |
| D152 (not in the brief's list) | not cited | none | an argmin is "a planner, not first-match"; the attached machinery needs re-stating | SLOT-19 |
| D141 (not in the brief's list) | not cited | none | a second home for estimation constants | SLOT-14 |

### Slot trace (item 1 of the brief): every slot / mechanism under (d) and its homes

| slot or mechanism | home S names | other homes in RT (or that (d) creates) | one home? |
|---|---|---|---|
| strategy (path family) | new path-family table | `CandPath` / `cand_path_of` (derived path, stamps per D156 add. 2) | NO, two definitions of the path (SLOT-5) |
| LOCATE | path argmin (stage 3) | `cand_rows[]` LOCATE; `rev-end` keeps first-match (open point 6) | mixed regime undefined (SLOT-12) |
| PRESENCE | path argmin | kit PRES table P0/P2/P3/P4/P9 + P1 designed (D176 Q4); `cand_rows[]` renders | NO, three (SLOT-3) |
| FIRST / NEXT handoff (S5) | path argmin | `fit_rungs[]` `drop-handoff` (size, measured-cost order) | NO, two (SLOT-4) |
| NEXT tactic (stop, entry kind) | kit (within footprint) | backend (across footprints); `cand_rows[]` NEXT first-match rendering with fall-through | NO, three (SLOT-2, SLOT-13) |
| start-set form (one member vs set) | — | `cand_rows[]` memchr/byte-class split; kit D1/D1w/set rows (Q-WR-1) | NO, two (SLOT-25, suspected) |
| RETRY | path argmin, first in stage 3 | [START-DENSE] row owns the slot's policy (D153 item 4) | ownership overlap (SLOT-14) |
| WINDOW / WIDTH / BOUND / RECOVER / FINISH | `cand_rows[]` first-match (dominance) | `fit_rungs[]` `drop-anchored` (FINISH machine) | yes, apart from the ladder's FINISH drop |
| S6 VM finder (hybrid prefilter) | inner strategy row S6 + `pf_admits[]` validity | the route pair (`cand_route_of`/`cand_finish_of`); `fit_rungs[]` `drop-prefilter`/`sel1-*` | NO, three or four (SLOT-5, SLOT-4) |
| route / engine | backend one-row preference + front-end `analyses[]` | `--engine=` switch, auto ternary, `fit_rungs[]` sel1 rows, `pf_admits[]` | NO, five or six members of one family (SLOT-6) |
| route pick's readers | rendering (clause 4) | possessify / revdet / driver / compound read `fit.chosen` | outside every clause (SLOT-7) |
| plain vs compound artifact | not mentioned | `compound_rows[]` reads plain picks by name | unlisted (SLOT-11) |
| ties | backend simplicity order | kit `wf_ties[]`; [TIE-ALIGN]; D176 Q5's "existing declared tie rows" | NO, a family of 3+ (SLOT-14) |
| consumer costs (A_entry, no-search, reverse) | backend set rows | kit `C_ENTER` (moves out, per S); route-keyed kit rows `kit.*.DFA_SCAN` in `measure_store/zen4-grid1/1/set.tsv` (kit method costs measured per consumer kind) | one after the move, but the kit's rows remain consumer-keyed |
| estimation constants (`reseed_gap`, the K admission) | measurement set | [EST-REGISTRY] (D141) | NO, two homes (SLOT-14) |
| UNMEASURED handling | "unrankable" | D161 add. 12 generic class; D166 add. 2 latest set; PR R4.5 | NO, two rules (SLOT-24) |
| enforcement of the seam | CAND_TRACE `reads`/`kask` | facts `used` bit (`pf_enter`); none for rates or set rows | three instruments needed (SLOT-10) |
| the frontier reply | kit | — | yes, but its pick violates D157 (SLOT-2) |
| `analyses[]` | front end, validity | — | yes (pure validity: an AND of masks, order for `why` only) |
| `pf_admits[]` | front end, validity rows | its default-ON row = S6's price in the backend | split across two homes (SLOT-5) |
| compile_driver retry ladder | late validity for the engine | also price-ordered strategy drops | role understated (SLOT-4) |

## PROBED-AND-HELD

- Code cites checked against RT, held:
  - `cand_rows[]` at `emit_dfa.c:10154`, ending at `:10631`: 51 rows, by count of `.c = { "` lines. The per-slot row
    names match S's table (BOUND 5, RECOVER 4, FINISH 5, WINDOW 2, WIDTH 2), so S's "19 pure V/D" holds.
  - The other emit_dfa.c cites are the ones S's argument rests on: `:4815`, `:4835`, `:7280`, `:7293-7296`,
    `:7333-7354`, `:6598-6609`, `:8540-8545`, `:8588-8615`, `:8618-8622`, `:9016-9025`, `:9775`, `:9823-9830`,
    `:9879-9891`, `:9930`, `:10025`, `:10087-10088`, `:10251-10260`, `:10869`, `:5063`.
  - Other files: `select_engine.c:417`, `:1468`, `:669` (`pf_admits[]`); `window.c:620-683` (Table A, MARGIN);
    `plan_cost.def:38` (`C_ENTER`).
  - One doc mismatch, folded into SLOT-5: `:9845` is `CAND_ALL_ROUTES`, not the route definition.
  - 23 cites held, 1 off.
- Rulings read in full: D77, D141, D146, D147 (+ addenda 2-9), D151 (+ add. 1-7), D152, D153, D157, D158 (+ add. 1),
  D161 add. 6 / 11-15, D166 (+ add. 1-2), D172, D176, D182. The study's reading of these held for: D166 (one set, set
  id per quote), D176 Q2 (HORS_MIN precedent for deleting MARGIN), D176 Q5 (fixed point), D158's give-up contract
  as validity per row. 17 rulings checked; 11 needed an addendum or change S did not state (table above).
- Q2 claims held:
  - captures force the VM (`analyses[]` `captures` row);
  - DFA overflow is late validity through the SEL-1 rungs;
  - `--engine=` is do-or-die;
  - the auto rule is a one-line ternary;
  - possessify / revdet run only after the pick (confirming that the engine choice is a front-end constraint today).
- Probes: 5 compiler runs (`ab+c`, `[ab]x+c`, `q\d+z` twice, `\wq\d+z`), outputs in `slot/probe*.c`. The stamp/form
  agreement for `q\d+z` held (SLOT-25 stays SUSPECTED). No gcc compiles, no matcher runs.
- Q-WR-9's trigger state (the coordinator's planted check) was found and is reported in SLOT-1 and SLOT-3.
- PR §0-§10 read in full. 8 requirement issues (SLOT-21). The remaining requirements (R4.1-R4.3, R4.6, R5.x, R6.x,
  R7.x, R8.x) were checked against S with no conflict found.

## STATE AT HANDOFF

- STATE: complete
- OWED: none
