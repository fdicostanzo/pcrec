# SLOT lens: crit-memfn-sp1d (span_pick unit 1d), slot tracing, ruling check, goals

Subject e9e5f035e vs base daf6f002b. Rulings read at 442686b7b. Design: span_pick.md rev 5.2 at the subject.
I read no denied file.

## FINDINGS

### SLOT-1. R21's ratchet -1 cannot be read by its recipe; the design's 1d row contradicts its own U1. CONFIRMED. Severity: design/doc. Effort: XS for main. Blast radius: the stage-1 end total.
- R21's recipe (roadmap.md:640, unchanged at the subject): "enumerators among `^static void a_model_choose(` and `^static void a_mass_choose(` ... minus 1".
- Repro: `git show REV:memfn/src/window.c | grep -cE '^static void a_model_choose\(|^static void a_mass_choose\('` gives 2 at base and 2 at the subject. R21 reads 1 at both, so the delta is 0, not -1.
- Why it can't move: U1/N1 (span_pick.md §What stage 1 deletes) says "A-model and A-mass stay two KEY rows" until row 1. So no stage-1 unit can bring R21 to 0 under this recipe.
- What 1d actually deleted is a helper (`mass_domain`) and A-model's private span walk. Both now read `cands` (window.c:347-371). The recipe counts neither.
- The design's own rule (§Staging "Ratchet") says main re-states the recipe before the unit lands, or the lane drops the name. Neither happened: the subject leaves the roadmap untouched, as it must.
- Consequence: stage 1's forecast "ends at 3 or 4" really reads 4 or 5 until main re-states R21. A possible restatement: "position-domain or mass enumerations over `mf_walt` spans outside `cands`".
- The 1d cell's wording "R21 -1 (`mass_domain`'s copy: no row, the census map's)" is self-contradictory: is the -1 R21's, or the census map's? The census does drop `mass_domain` (decider_census.tsv, 51 -> 52 with `cands` and `kit_pick_takes` in).

### SLOT-2. The argmin family is not closed: P4's set-leads is a sixth two-candidate pick outside kit_pick_takes, the census and the backstop. CONFIRMED by reading. Severity: maintenance/design. Effort: S. Blast radius: T-PRES only, no mover.
- presence.c:183: `out->set_leads = kit_mass(rate, s->pspans[best].term[0].set, 1, KIT_MASS_SUM) < sc.mass;`
- This is an argmin over (mass) between the set pick and the run member. Its tie is implicit (strict `<`: a tie goes to the run) and has no TIE row.
- It also recomputes the mass `bs.v` already holds (presence.c:144-145).
- The census lists kit_pres_picks only by parts (set-pick, run-window, landmark), so this line belongs to no member.
- No BACKSTOP shape matches `< sc.mass`. kit.h:366-370 admits "P2 and P4 compare with no TIE row". P2 is a named exception ([1b fix R9]); P4 is not.
- The r2 review's five-member family is now unified at the RELATION level: all five ask `kit_pick_takes` (window.c:595, :626, :836, :838; presence.c:144, :169). P4 remains outside, and so does any later two-way pick.
- Suggested disposition: PLAN, either a census part `kit_pres_picks:set-leads` (T-PRES, an implicit tie to the run) or a TIE row read through kit_pick_takes. Trigger: presence joins the call, or the next T-PRES change.

### SLOT-3. U-b is only partly delivered: one before-relation, but still five loops, readers and filters. CONFIRMED. Severity: design. Effort: M, later.
- r2's U-b: "`kit_run_member` generalised to (reader, filter, tie row) becomes T-PICK's one argmin, with the cursor giving rankings for free". Trigger 1d, precondition F1.
- 1d instead adds `kit_pick_takes` (window.c:135-138), a comparison. Each member keeps its own loop: a_mass_choose (:622-628), a_model_choose (:569-601), kit_run_member (:830-841), P3's set pick (presence.c:139-146) and run window (:163-170).
- Siblings it creates: `kit_pick {pos,key,v}` (kit.h:392) is a second best-so-far struct beside 1c's `kit_member {pos,mass}`. kit_run_member converts between them at its boundary (window.c:830, :841), and its `after` filter calls the relation with its operands reversed (`!kit_pick_takes(&c, after->mass, ..., after->pos)`, :836). I checked this algebraically: it matches the base. It holds only because the TIE row is a strict order.
- F1's strictness precondition now silently covers all six call sites, but it is stated only at kit_run_member (window.c:820-828), not at kit_pick_takes.
- Acceptable for stage 1: no rule requires the full argmin before row 1. But the r2 hand-off (Trigger: 1d) is silently narrowed, not refused.
- Suggested disposition: DOC (XS): state the strict-order precondition at kit_pick_takes, and file U-b's remainder with the row-1 trigger.

### SLOT-4. Stale Table C header after C-bound and C-member became steps. CONFIRMED. Severity: doc. Effort: XS.
- window.c:793-797 still says "Three rows are applied elsewhere ...: C-meet by `merge` ..., C-bound inside C-floor and C-yes".
- At the subject:
  - C-bound is its own applied step, `c_bound` (:922-931; row :1053).
  - C-meet runs in `cands` (:347-349).
  - C-member is a listed row (:1036-1038), which the header omits.
- This is the same class as the design's ":882 stale comment" item, which 1d fixed.

### SLOT-5. The declared step list's order is not its execution order. CONFIRMED. Severity: doc/design. Effort: XS.
- wf_crows (window.c:1036-1068) lists C-member at step 0 and C-meet at step 1. In execution, C-meet runs inside `cands` before Tables A and M, and C-member (`run_member`, which reads `chosen(d)`) runs after M.
- The design's step list (span_pick.md §The tables, T-VERIFY) puts C-bound first: "C-bound ..., C-floor or C-yes, ...". The code applies it as a subtraction after C-floor/C-yes and before C-model.
- Answers are equal:
  - c_bound drops by swap (`plan_drop`), but C-run calls `c_asc` before grouping (:1001), so order is restored.
  - C-model and C-pin cannot add a full-set position: model_cost is monotone, and `shape` admits only 1-2 member sets.
- Still, "a DECLARED STEP LIST read in order" is true only for the rows whose `apply` is non-NULL. Two rows' positions (C-meet, C-member) mislead a reader.
- Suggested disposition: DOC: number C-meet 0 ("applied by the candidate builder, before KEY"), C-member 1, and note C-bound as "minus step 2's adds".

### SLOT-6. WCAND traces candidates but neither A-model's inputs nor any T-VERIFY row. SUSPECTED partial (trace). Severity: doc/design. Effort: S.
- What WCAND does not record: `mass=` is the meet's SUM mass (window.c:1103). A-model ranks the walked offsets on their OWN set's CAP mass (`w->mass`, :367), and F0's own mass (`f0_mass`) is never traced. trace_format.md:126-128 admits this ("priced on its span's OWN set").
- No `scan` column either, so a reader cannot tell which walked offsets A-model could scan.
- Example probe (tr-subject, `abc[0-9]+def`): site 1, alt 1 shows walked=1 at off 3-6 with 10-13 members and stop=1, but nothing says scan_ok=0.
- T-VERIFY writes no record (trace_format.md:132-134 "the plan's shape is WPATH's path"). WPATH's `path` (e.g. `mass+pin`) does not show C-model's picks or C-bound's drops.
- The design's trace is "every candidate, the rows walked, the incumbent and the deciding row" (§The shape), and the 1d row says "trace ... U10 = Table C + ...".
- WCAND has no reader or check: grep finds it only in gate.c, kit.h, CLAUDE.md and trace_format.md. One incumbent per site, or key matching WPATH, is unasserted.
- Suggested disposition: PLAN. Row 1's pcrec-side re-price (§The independent control) needs the walked own mass and a scan bit. Until then, note the gap in trace_format.md.

### SLOT-7. ofsskip's legacy plan (U10) has no trace in the subject. SUSPECTED vacuous, undocumented. Severity: doc. Effort: XS.
- Two places assign it to 1d: §What stage 1 deletes ("U10, N6 | T-VERIFY = Table C + ofsskip's legacy plan ... | 1d") and the 1d row ("U10 = Table C + ofsskip's legacy plan").
- ofsskip.c is not in the diff. Its verify order is "the other terms in array order" (ofsskip.c:16-18, `verify_chain` :186-200), and that order is pcrec's statement (`plan_hint`, term order). So the kit has no decider to fold, and this may be correct as a no-op.
- But no census row, comment or doc line in the subject says so. The census has no ofsskip verify-order member, so the population is uncounted (K35-style).
- Suggested disposition: DOC: one census row or design line, "ofsskip's legacy verify order is pcrec's stated term order; no kit decider; retires when legacy OFS sites become window sites".

### SLOT-8. A fourth spelling of the normal-form predicate survives (F12 folded only three), and it is dead. CONFIRMED by reading. Severity: maintenance. Effort: XS.
- ofsskip.c:130-131: `(sc->run[p->plan_pos] & ~m & 0xFF)` inside ofs_fn_applies.
- The same function's loop (ofsskip.c:110-117) already returned 0 for any RUN term failing `run_cmp_sat`, including the scanned term. So this clause is always 0 here: an unreachable fourth spelling.
- 1d converted gate.c `cl_run` (:725) and generic.c (:196) to `run_cmp_sat` / `run_pos_sat`, as F12 asked.
- Suggested disposition: PLAN with D187's U-c, or XS now: drop the clause or ask `run_pos_sat`.

### SLOT-9. The compose.c :882 comment fix enumerates the rate readers by hand and misses two. CONFIRMED. Severity: doc. Effort: XS.
- compose.c:884-885 lists "the PRES picks, KEY's A-parked/A-model/A-mass, MARGIN, D-hors".
- `grep -n 'd->rate' memfn/src/window.c` also finds T-VERIFY's run member (`run_member`, :870) and translate's run ranking (:1464). Both read the handed rates through `kit_run_member`.
- This is the D94 lesson ("every reader of the number, found by grep"). Either say "every `kit_byte_rate` caller (presence.c, window.c `decide`)" or list all of them.

### SLOT-10. F13 not done, and 1d widens the split. CONFIRMED. Severity: maintenance, low (r2 disposition NOTED).
- r2 F13: the kit-wide position primitives are split across family files, and "the natural home is 1d's one candidate builder file".
- 1d adds another kit-wide primitive, `kit_pick_takes`, to window.c; presence.c calls it at :144 and :169. Meanwhile `kit_mass` and `kit_run_set` stay in presence.c.
- NOTED-only disposition, so nothing is owed; recorded as "not done".

### SLOT-11. The census BACKSTOP again carries dead shapes (F9's pattern). CONFIRMED. Severity: maintenance, low.
- Hits per shape at the subject over memfn/src/*.{c,h,def}: `< bm` 0, `< lo` 0, `< b.mass` 0, `< after->mass` 0, `< wl` 0, `< inc` 0. Live shapes: `< best` 2, `tie_takes` 4, `TIE_` 12, `kit_walk(` 11, `pick_takes(` 8.
- F9's FIX-NOW made the shapes live at 1c, and 1d's rewrite killed five of them. They still guard against a regrown raw compare, so this is harmless. But an unlisted twin argmin written `m < cur` with no `pick_takes(` / `tie_takes` still passes, as F9 noted. SLOT-2's `< sc.mass` is a live instance.
- Census run: `python3 -I tests/memfn/decider_census.py --root <subject tree>` gives 59 passed, 0 failed, 37 hits (floor 30), 0 outside a member, all plants red.

## Rulings check (does the code agree)

- **D186 (+ add. 1, add. 2):**
  - Unit/choice split: 1d is a no-mover remodel, no choice row: agrees.
  - Add. 2 "one plan, with the trace": the reply struct is unchanged, and the alternatives considered appear only in the WCAND trace: agrees, with SLOT-6's gaps.
  - "The plan face is a PURE FUNCTION": the purity harness is built (arm_fixtures.c:1662-1937, run_finder.sh:318-368). It compares every `mf_wreply` field (all 14; memfn.h:1446-1461 checked against `pur_diff`). It covers NONE and a skewed table with ties, and three define orders with plan calls interleaved. Floor 287 matches my count: 2 x (5 + 23x5 + 20) + 7.
  - Add. 1 A1 (no priced departure): no reader of cost was added.
- **D187 (positions travel as sets):** `run_pos_sat` is a new name in the cube normal-form family that D187's end state deletes. It is interim, and F12 is ruled PLAN "folded into 1d". There is no new seam field and no new cube carried beside a set: agrees. SLOT-8 is the missed member.
- **R4/R8:**
  - U6's landmark part is unchanged, and its census row is kept.
  - translate's `pterm` grouping is kept as `translate:grouping` EXC with its retiring trigger (decider_census.tsv).
  - The 1d C-run row (window.c:1061) does not touch translate.
  - Agrees.
- **R6/R7:**
  - The purity harness and its plant are built.
  - The plant is RED: run_finder checks `checks failed` > 0.
  - The control compares the planted `--purity-control` with this build's. The design said "plant build vs base build"; "this build" is the subject, which is equivalent since base has no such mode.
  - Reach equality is the lane's claim; I did not re-run it (budget).
- **C1:** the plan calls are INTERLEAVED with the defines (k = 0..n, in-order / reversed / repeated), and the WHY is in the header: agrees.
- **C2:** after a refused define (a two-NONE site) every plan call must answer -1, asserted as breaker (a) FENCED, with compose.c's error path unchanged: agrees.
- **C7:** see SLOT-1 (R21's -1 cannot be read by its recipe).
- **Breaker table:**
  - (a) is unchanged.
  - (b) `art->nsites + 1` is still read only into gate_tctx labels (window.c:1126, :1135), and trace_cands copies M's tctx.
  - (c) trace_cands returns when `quiet`, and gate_trace_cand prints but counts nothing, so the plan call writes no WCAND and no reach.
  - (d) `consulted` is untouched.
  - Agrees.

## Items r2 handed to 1d

- **F9:** done at 1c (sp1cfix), then partly undone by 1d's rewrite. `pick_takes(` was added as a live shape and five shapes went dead again (SLOT-11).
- **F12:** done for the three named spellings (gate.c, generic.c, runcmp.c). A fourth (ofsskip.c:131) was missed (SLOT-8).
- **F13:** not done (NOTED), and 1d widens the split (SLOT-10).
- **U-b:** partly: one relation, not one argmin (SLOT-3).
- **The five-member argmin family:** all five ask `kit_pick_takes`. Outside: P4 set-leads (SLOT-2); A-model's exchange sort (T_CMODEL) and MARGIN (T_MARGIN), ruled out ("a sort and a rejection, not a pick"); P2 (named exception).

## Goals (span_pick.md §Goals, ranked)

1. Answers exact.
2. No regime slower: stage 1 means zero movers and no abi change.
3. One table per question: the census.
4. Costs measured: the end state.
5. Blind picks are the default's.

1d serves 3 (one candidate builder, one before-relation, T-VERIFY as a declared list), and spends nothing of 1 or 2:
- My probe: 104/104 SAME.
- No memfn.h or abi change in the diff.

It leaves 4 and 5 untouched, as stage 1 should, so the order is honoured. The only Goal-3 debts are SLOT-2, SLOT-7 and SLOT-8, all uncounted populations.

## Standing questions

**SIBLING OF A FAMILY.**
- `kit_pick_takes` is the THIRD member of the TIE-access family (`kit_tie_takes`, `kit_tie_member_key`, now `kit_pick_takes`). The family is coherent: the latter calls the former.
- `kit_pick` is the SECOND best-so-far struct, beside 1c's `kit_member`. They are converted at kit_run_member's boundary, and should fold into one (U-1 below).
- `run_pos_sat` is the second member of the normal-form family (`run_cmp_sat` composes it). An unconverted member remains at ofsskip.c:131.
- `gate_cand` / `gate_trace_cand` is a new trace-record sibling of SEL/ROW/END/WPATH; it has no reader.
- The argmin family over (value, tie row) is CLOSED for the five r2 named. One member remains outside kit_pick_takes: **P4's set-leads, presence.c:183** (SLOT-2). Outside by ruling: A-model's exchange sort, MARGIN, P2.

**GENERAL FORM + UNLOCKS.**
- The general form 1d points at: the plan face as (a candidate list as DATA) -> (one argmin over (value, TIE row) per level) -> (a declared step list) -> one plan. Here "value" is a mass today and a price under T-PICK. A ranking is that argmin repeated with a cursor (kit_run_member's `after`). Serialized, the candidate list is exactly the WCAND record set (manifesto principle 9).
- Unlocks:
  - **U-1:** `kit_member` folds into `kit_pick` (one struct, one `after` cursor type). Trigger: the next kit_run_member change, or U-2.
  - **U-2:** a generic `kit_argmin(n, reader, filter, row)` replaces the five loops and gives rankings via the cursor (r2's U-b remainder). Trigger: stage 3 row 1 (T-PICK's first priced row) or a sixth argmin. Precondition: F1's strict order, stated at kit_pick_takes.
  - **U-3:** P4 (and later P2) become kit_pick_takes calls with explicit TIE rows and census parts. Trigger: presence joins the call ([MEMFN-UNBOUNDED-SPANS]) or the next T-PRES change.
  - **U-4:** every mass a KEY row reads comes from `cands`: A-parked's k0 CAP mass (window.c:543), F0's mass and the walked own masses, already partly there. A-parked then carries no statement read of its own. Trigger: row 1 prices over the list.
  - **U-5:** WCAND, with walked own mass, a scan bit and the T-VERIFY row record, becomes the input of the pcrec-side python re-price (§The independent control) and a seam-as-text witness of the plan face. Trigger: row 1's independent control.
  - **U-6:** R21's restated recipe counts "statement enumerations outside `cands`", making the ratchet see what 1d deleted. Trigger: main's next roadmap §5 restatement, before stage 1 closes.

## PROBED-AND-HELD

- **Byte identity, BASE vs SUBJECT:** 26 patterns x 4 arms ("", `--engine=vm`, `-fmemfn-simd`, `-e utf8`). Patterns: the 12 lines of tests/memfn/n2_sample_patterns.txt plus 14 crafted, including smp20 `(?i)x/1234`, `zzzzzzz~J`, utf8-lead-no-cont, RESEED/walked shapes, tie shapes and dot runs. Result: 104 pairs, 104 SAME, 0 SILENT-MOVE, 0 rc differences.
- **Algebraic equivalence checked by reading** (base vs subject):
  - a_mass_choose (keys, domain and mass identical: SUM over `p->set`).
  - a_model_choose: the walked list equals the old `walked(a,j) && j != si` filter, `f0_mass` equals `mass[f0]` (CAP), and the T_MODEL tie keys are offsets.
  - kit_run_member's pick and its `after` filter (the reversed call reduces to the old `ms < after.mass || (eq && !tie(after.pos, j))`).
  - P3's set pick and run window: `at = lo_s` vs `bw.pos`. These are equal because n > MF_PRES_WINDOW and scan >= 0 imply lo_s <= hi_s.
  - C-bound as a step (equal sets: C-yes under has_stop reads yset, C-floor rd_set after its reseed; order restored by c_asc in C-run).
  - cl_run (UNSAT precedence kept) and generic.c's `run_pos_sat`.
- **The census:** green (59 passed, 0 failed; 37 hits, 0 outside a member; three plants red), run directly by python with no compile.
- **The purity harness:** read in full (sites reach A-mass, A-parked, A-model, MARGIN and the verify-YES run member). Its plant/control logic and floor arithmetic are checked. I did not run it.
- **WCAND trace:** 3 tr-subject compiles. It is quiet-gated, define-only, prints no price, and has one incumbent per site in the probes.
- **Not probed:** reach_equal (budget), G2, the purity harness run, finder_check L with WCAND present.
- **Compile count: 211** (3 traced + 208 base/subject). This is 11 OVER the 200 budget: the identity loop's count was misjudged (each pair is 2 compiles). There were no further compiles after that.
