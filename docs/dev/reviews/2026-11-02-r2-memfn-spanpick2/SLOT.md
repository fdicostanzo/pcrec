# SLOT lens (slot tracing) — crit-memfn-spanpick2, subject span_pick.md rev 2 (5b3bc376a)

Review tree: worktrees/crit-memfn-spanpick2 (main 959c08124). All file:line cites are that tree.

## Findings

### SLOT-1 — the emit key "(method, frame row)" is not a function: PAIR on E-find renders two different texts, chosen by B-fn, which reads `fn_rows` BODY
CONFIRMED. Severity: design (stage 1 byte identity). Effort: small (name the home). Blast radius: unit 1e, T-FRAME,
§The designer/emitter split. Subject: line 89 ("renderers select TEXT by the plan's method and frame row"), 1e
"deletes B-fn's reconciliation" (:280), ratchet member `b_fn_holds` (:292). Re-checks B2/B3: PARTLY.
- Code: `wf_find_decide` (memfn/src/window.c:1753-1755) walks `wf_brows` after `fd_find`; B-fn
  (`b_fn_holds` :1675-1684) holds only when the pick is PAIR AND the plan is the offset-skip predicate AND
  `ofs_fn_serves` (ofsskip.c:478-491) re-walks `fn_rows` BODY and takes fn-pair. Else B-pair (:1685).
- Sweep (R-33, `slot/erows.py` -> `erows.out`): E-find + fd PAIR = 101 site-traces: 28 with `fn:fn-pair`
  (B-fn, e.g. smp05 `(?:(?i:abs)|(?i:ab)S)`), 73 without (B-pair, e.g. pr09 `x[Q%]y`).
- Texts differ (2 compiles, review build): smp05 renders a separate `static inline size_t
  rx_mf1_ofsskip__body(...)` function (slot/smp05.c:60-88, plus its PREFIX SIMD rungs at -fmemfn-simd);
  pr09 renders an inline statement-expression two-stream loop (slot/pr09.c:68). Same method PAIR, same frame
  row E-find, different C.
So after 1e either the B-fn/B-pair choice survives as an unlisted renderer decider that still walks
`fn_rows` BODY (then `b_fn_holds` is not deleted and the find-method ratchet row does not fall as claimed),
or the plan needs a field (or T-FRAME splits E-find into two rows) that carries it. Fix: say which; if
T-FRAME, it is a T-FRAME row reading the plan's shape, and the ratchet's `b_fn_holds` member moves to the
frame family rather than disappearing.

### SLOT-2 — the "true inventory" still omits three live tables: `fn_rows` BODY, `fn_rows` PREFIX, and compose's `arms[]` as the frame selector of every non-plan site
CONFIRMED. Severity: design (Goal 3's count is the design's own check). Effort: small (restate). Blast radius:
Goal 3 (:28-31), §The tables (:105-128). Re-checks B3: PARTLY.
Every `kit_table` walked today (grep `kit_walk(`/`kit_table` in memfn/src): `fd` (FIND, PRES), `runcmp`,
`arms`, `fn` (BODY, PREFIX), `wfA`, `wfM`, `wfD`, `wfE`; loops: `wf_crows`, `wf_brows`, `wf_ties`. Rev 2 homes:
FIND->T-FIND, PRES->T-PRES, runcmp->T-CMP, wfA->KEY, wfM->M, wfD->T-FIND resume, wfE->T-FRAME, crows->T-VERIFY
(+T-SETTEST), ties->TIE, brows->"renderers" (SLOT-1). Left over after stage 1 by rev 2's own text:
- `fn_rows` BODY (ofsskip.c:415-416): "stays a decider" (:127-128) on OFS: a second table answering T-FIND's
  question on all 381 E-func sites (erows.out: 381/381 take `fn:fn-memchr`), yet the Goal-3 count names only
  KA/KB as untabled.
- `fn_rows` PREFIX (ofsskip.c:419-420, own denies `vrun-w32`/`vrun-w16`): rev 2 calls SIMD forms "rungs of a
  T-FIND row" but they are a separate first-match kit_table with its own walk (`fn_select` :454-471); the
  count does not name it.
- compose.c `arms[]` (:134-147, `select_arm` :263-296): rev 2 lists it only under T-FIND "replaces"; it is
  also THE frame/renderer selector for every site that never makes the plan call. Sweep, non-window sites
  (`slot/nonwindow.out`): generic 5,541, runcmp 767, precheck/precheck_assign_byte 561, mismatch_inplace 14
  site-traces. It carries a deny-bearing method choice (`precheck-assign-byte`: the landmark as one memchr vs
  the generic row, options.def:50-52), outside T-FIND, T-PRES and T-FRAME.
Fix: count them (e.g. "plus `fn_rows` BODY until OFS states a kind, the SIMD rung table, and the non-plan
frame table `arms[]`"), or say why each is outside "find the span" — the third is a legitimate exclusion
only if Goal 3 says "for plan-call sites".

### SLOT-3 — the tie and run-member families are undercounted: two inline kit tie spellings and one run-member spelling survive stage 1 unplaced
CONFIRMED. Severity: maintenance (the ratchet base and Goal 3's TIE claim). Effort: small. Blast radius: 1b, 1c,
§What stage 1 deletes U2/U5, ratchet rows "tie rules", "kit run-member spellings". Re-checks B1 (U5) and B3.
- translate's run rank, window.c:1320-1343: ranks the scanned RUN term's positions by cube mass with an
  inline tie (iterates high-to-low, strict `>`: ties to the HIGHER position = T_MASS_STRETCH's rule, not read
  from `wf_ties`); `rank_pos[0]` is the run member by another spelling (vrun.c:56-57 "observed ... rank_pos[0]
  IS KA on every PRE and OFS predicate"), `rank_pos[1]` is KB. units_inventory §2 Q1 lists it as one of U2's
  five spellings; rev 2's U2 line (:356) names only P3's `run_scan`, and the untabled pair names vrun's KA/KB
  (the reader), not this producer.
- presence.c:186-192, P3's run WINDOW: `if (w == lo_s || wm < wl)` ascending = TIE_LEFTMOST, inline. `wf_ties`
  has that very row, T_WINDOW (window.c:98-100), whose text says "no kit reader (window_site.md §9)": false,
  the kit has its own unread spelling.
- (minor) fd_pres REST order "ascending byte" (finder.c:358-361, :1078-1089) is an order rule of its own.
Stage 1 deletes `tie_over` (1b) and `run_scan`'s loop (1c). It leaves the rank's and the window's inline
ties, so "`wf_ties` the one tie table" (:121, :277) is false after stage 1, and "1 tie rule" / "1-2" are the
deletions of families whose bases are >= 4 (ties: wf_ties, tie_over, run_scan, run_window, rank) and 3
(run member: run_member, run_scan, rank). Fix: add both to 1b/1c (the window reads T_WINDOW; the rank reads
T_MASS_STRETCH and its [0] asserts `run_member`) or list them as kept with the reason.

### SLOT-4 — U10's presence half is double-booked: T-VERIFY "replaces PRES part ordering" in 1d while presence keeps its own entry and T-PRES owns the order row
CONFIRMED (text + code). Severity: design. Effort: small. Blast radius: §The tables T-VERIFY/T-PRES, 1d, §What
stage 1 deletes U10. Re-checks B4/B1: INTRODUCES-NEW (contradiction between two fixes).
- T-VERIFY's "replaces" (:111) and U10 (:364, unit 1d) claim the PRES part ordering; §The shape (:48-50, B4)
  keeps presence on its own PRES entry in stage 1, so no plan reply exists for T-VERIFY to order there; and
  T-PRES (:114) owns P4, which IS the order row (finder.c:1049-1054, "P4, the order row, asked on its own").
- The ordering code is fd_pres's chain order + coverage rule (finder.c:1064-1089: HEAD/RUN/REST, and a REST
  member a whole exact run covers is un-verified): untabled, and not in rev 2's inventory under either name.
- precheck.c `implied_by` :158-182 (R-30: a FUNC part implied by a later part is neither defined nor
  called; test-only lever `pres-window`) answers T-PRES's question ("which members a pass tests") inside a
  renderer; not N9 (N9 is the part's own memchr) and not placed.
"where byte-identical" (:111, :364) makes U10's PRES deletion unfalsifiable. Fix: move "PRES part ordering"
to T-PRES (with the chain order and `implied_by` named as its rows or as kept renderer-side deciders) and
leave U10 = Table C + ofsskip's legacy plan.

### SLOT-5 — T-VERIFY's step list drops C-bound, and E-find re-decides C-run's grouping at render
CONFIRMED. Severity: doc/maintenance. Effort: trivial. Blast radius: T-VERIFY row (:111).
- Table C has 12 rows (window.c:946-968). Rev 2 places C-meet (step 2), C-table/C-own (T-SETTEST) and eight
  steps; C-bound (:952-955, "a FULL-SET position is never a plan test", also read by `mass_domain` :531 and
  `wf_find_decide` :1730) is in none.
- `find_groups` (:1481-1500) turns C-run's `pterm` stretches into RUN terms only where `run_group_ok`
  (:1466-1473: every position core AND run-shaped) holds; `translate` (:1280-1293) groups by `pterm` alone.
  Two frames, two grouping rules for one plan: a second T-VERIFY/T-CMP decider at render. Fix: name both
  (C-bound a T-VERIFY step; the core/shape condition a C-run clause read by both renderers).

### SLOT-6 — Goal 3's decider census, as stated, cannot fail on a byte-identical second decider
CONFIRMED. Severity: design (the goal's only check). Effort: small-medium. Blast radius: Goal 3 (:29-31),
§The independent control (:405). Re-checks B3 ("name a decider/reach census"): PARTLY.
- "kit_walk reach" exists only for kit_table walks: the trace records in R-33's sweep are exactly wfA, wfM,
  wfE, wfD, fd, runcmp, arms, fn (erows.out line 1). T-VERIFY (`c_plan` :972-980, a plain loop), Table B
  (:1753-1755), TIE, the KEY choose functions, `run_member`, `kit_pres_picks`, fd_pres's chain order produce
  no reach record, so "reach over the corpus" says nothing about four of the ten tables.
- "deciding functions by grep" names no pattern and no table->function map. The inventory's own grep
  (`kit_walk` tables, `*_choose`, `*_holds`, units_inventory Goal 1) misses every decider in SLOT-3/4/5
  (translate's rank loop, presence's window loop, `implied_by`, `find_groups`, the chain order).
- Today's live example passes it: translate's rank (window.c:1320) and `run_member` (:763) both answer "the
  run member" with the same tie; they agree (vrun.c:56), are byte-identical, are not kit_walk tables and
  match no `_holds|_choose` grep.
Fix (implementable): a committed map (`decider -> table`, one line per function, kept by the unit's lane) plus
a grep for argmin shapes (`< best`/`< bm`/`tie_takes`/`TIE_`) whose every hit must be in the map under its
table, with a sabotage row (add a byte-identical copy of `run_member`'s loop; the census must go red).

### SLOT-7 — unit 1a's deletion of R8/R1/R2 retires two caller-facing denies, which its own witness and the "no pcrec abi / no-mover" framing do not cover
CONFIRMED. Severity: doc/spec (D80) + witness. Effort: small. Blast radius: 1a (:276), Goal 2's stage-1 bar,
§Staging witness (:285-288). Re-checks C8 (PLAN applied): PARTLY / INTRODUCES-NEW.
- R8 carries deny `fd-r8`, R1 and R2 `fd-ndisp` (finder.c:253, :273, :279; options.def:61-67). Both are spec
  rows: docs/spec/registry.md:158 (§6¶8a) and :168-169. The precedent (registry.md:158): when R0/R5 retired,
  "`--memfn=no-fd-r0` and `--memfn=no-fd-r5` are unknown options".
- So 1a changes a caller-observable namespace: a spec hunk is owed (D80), plus tests/memfn/finder_check.py:119,
  :493 and tests/axes/memfn_arm.py:122-125. And the per-unit witness "byte-identical on EVERY arm (... each
  `--memfn=no-X` deny ...)" (:286) cannot hold for the `no-fd-r8`/`no-fd-ndisp` arms, which become errors.
- Rev 2 says only "the namespace is unchanged (D147 add. 9)" (:100) and "zero reach by code".
Fix: 1a names the two retired denies, the registry hunk and the test edits, and its witness excludes those two
arms by name (or keeps both names as accepted no-ops, said explicitly).

### SLOT-8 — T-FIND's validity "reads T-FRAME's row contracts" while T-FRAME is asked per complete plan after T-FIND; Table E's legacy rows themselves run the finder
SUSPECTED (ordering, not yet a byte witness). Severity: design. Blast radius: §The shape step 3, T-FIND/T-FRAME
rows. Re-checks B2: PARTLY.
Today Table E is walked AFTER `wf_find_decide` (window.c:1803-1821) and E-func/E-stmt's holds call
`kit_legacy_serves` -> `select_arm` -> `fd_route` (window.c:1392 -> compose.c:281) on the translated site: a second T-FIND ask
inside T-FRAME. Rev 2 orders T-FIND -> ... -> T-FRAME per complete plan (:58-60) and makes T-FIND's validity
read T-FRAME's contracts (:110): which row's contract, before the frame is known, is unsaid. On R-33 the frame
is a function of (form, handoff, site_kind, wfloor) (erows.out: every (kind, form, handoff) group takes one E
row), so it holds in practice; by construction it needs "T-FRAME's contract-only rows are asked FIRST on
stated facts (a frame class), T-FRAME's plan-reading clauses last", which is B2's option (ii) that rev 2 says
it did not take. Would confirm: one site where E-stmt's legacy walk declines and E-find holds.

## PROBED-AND-HELD

- **Every U/N id placed once** (§What stage 1 deletes vs units_inventory §3/§4): U1 1d, U2 1c, U3 1e, U4 1b,
  U5 1b, U6 1c, U7+N10 kept, U8 out, U9 out, U10 1d (but SLOT-4), N1 1d, N2 kept, N3 1a, N4 1e, N5 1e, N6 1d,
  N7/N8/N13 kept, N9 stays, N11 1e, N12 declined, N14 1a. 24 ids, none missing, none twice. Unit table
  1a-1e cross-references agree with the id table.
- **1a "7 members"**: N3 `mf_set_terms` (terms.c, no caller) + the six rows R8/R3a/R3b/R4/R1/R2 (finder.c:250-281)
  = 7. Zero reach on R-33 (`counts.out` fd rows: D1, R7w, PAIR, D1w, D1c, P0, P3, P4 only). HELD (deny side:
  SLOT-7).
- **1b "2-3 mass variants"**: kit mass spellings are `kit_set_mass` (capped), `kit_set_sum`, `cube_mass`,
  `window_mass`, `uniform_mass` (presence.c:58-115); one primitive with a cap argument absorbs 2-3 of them;
  translate's rank and `run_member` already call `kit_set_sum`. HELD.
- **The candidate builder can carry A-model's input** (the risk: A-model reads walked spans' OWN sets,
  window.c:472, while candidates are "core positions after C-meet"). `slot/walked.py` over every RESEED
  alternative in R-33: 2,720 walked spans, all core; 470 covered by another span, merged set == own set in
  470/470. HELD on this population (by construction it is a stated-facts property; say so).
- **"T-FRAME is Table E moved"** (no new member): Table E's 4 rows, order kept. HELD (ordering: SLOT-8).
- **"The candidate builder replaces two"** (`mass_domain`, `a_model_choose`'s scan): HELD, with the KEY RESEED
  row keeping `scan_ok` as a row predicate (rev 2 says so, :126-127).
- **New TIE presence-member row** raises no family member (a row of the one table; `tie_over` goes). HELD as a
  count; the table is still not "the one" (SLOT-3).
- **A-floor / A-empty in KEY** (B1, SLOT-3 of r1): KEY now lists all five Table A rows; entry x row cross-tab
  reproduced (PARKED->A-parked 1,857, NONE->A-mass 1,432, RESEED->A-model 415 / A-floor 1,420). HELD.
- **run member a T-VERIFY output** (B3/SLOT-2 of r1): `c_plan` runs `run_member` before the rows (window.c:976),
  as rev 2 says. HELD for `run_member`; its second spelling is SLOT-3.
- **T-RESUME folded into T-FIND** (SLOT-9 of r1): Table D is walked only on E-find (1,021 wfD = 1,021 E-find
  traces), D-hors `finds` 0 (no find: Horspool replaces it), D-one otherwise. HELD as a row action column,
  provided the Horspool row sits first (D-hors is walked before `fd_find`, window.c:1738-1747).
- **OFS: no consumer kind** (B1): 381/381 E-func sites UNSTATED kind, `fd` declines, `fn` BODY takes
  fn-memchr on all 381. HELD.
- **Re-checked ids**: B1 (U5, U9, OFS, A-floor parts HELD; U10 SLOT-4), B2 (PARTLY, SLOT-1/8), B3 (PARTLY,
  SLOT-2/3/6), B4 (HELD in §The shape; contradicted by U10, SLOT-4), C8 (PARTLY, SLOT-7), E3 (HELD: 1a-1e
  each with a witness), F (see standing questions).
- Compiles used: 3 of the allowed budget (smp05, smp09 refused by the lookaround module, pr09).

## Standing questions

**(a) SIBLING OF A FAMILY.** The same shape ("facts -> declared admission rows -> a default -> (later) a priced
action -> a tie rule") appears in: (1) pcrec's lmwalk (`lmwalk_conj[]` admission table, then `lc_rarity`
priced with `LMWALK_K_HIT_UNMEASURED`); (2) landmark admission (`req_landmark_admits` + the kit shadow,
presence.c:222-245, P-landmark); (3) PRES's P2 `dominated` drop (a rate comparison inside `kit_pres_picks`,
presence.c:209-220) and P4 set-leads (a strict mass compare): these are T-PRES's own little picks, same
shape; (4) the `precheck-assign-byte` vs generic choice in `arms[]` (SLOT-2); (5) [PRICE-BAKEOFF]'s "policy
rules as a declared first-match table; pricing chooses within them" (plan.md row, Expected shape);
(6) engine/route choice (`next_keys` FIRST/NEXT CandSel), explicitly a non-goal here. Rev 2's [PICK-IDIOM] row
is the right instrument, but its trigger ("the first priced row or the bake-off's revisit") is late:
ONE-STREAM (stage 3 row 1, a HAND row) is already "admission condition + action + deny + tie" and is the
first T-PICK row; lmwalk is that shape today. Recommended trigger: the first T-PICK row's landing (ONE-STREAM),
so the row format is chosen once before a second family writes rows in its own format. Inside the kit the
family is handled consistently (KEY/M/TIE/T-PICK); across D157 it is a plan row only, which matches the
round-1 ruling (F: PLAN).

**(b) GENERAL FORM + UNLOCKS.** General form: a plan is a vector of levels (alternative, position, method,
verify order, compare/set-test forms, frame); each level has ONE declared table that lists VALID values on
stated facts; a default vector (today's) is chosen by default rows; a departure is a T-PICK row that opens
named levels and either applies a rule or a dominance test (all rate models, beyond the band); a single tie
table closes every equality; every function that answers a level is registered under that level (the census
of SLOT-6). Unlocks, each with a trigger:
- **Registered deciders make D186 classification mechanical**: a change that adds a decider outside the map
  is red at review. Trigger: stage 1's go (cheap; it is Goal 3's check done properly).
- **PRES on the same plan call** (presence's member/run-window/landmark choices become levels of the same
  vector; `tie_over`/run window via TIE). Trigger: [MEMFN-UNBOUNDED-SPANS] landing.
- **Non-plan sites (arms[]) as the same vector with fewer levels** (frame + method only): the generic/
  runcmp/mismatch/precheck choice becomes T-FRAME rows; `precheck-assign-byte` becomes a T-FIND row with its
  card. Trigger: the next kit request that adds an arm.
- **Per-target plans** (A-PLAN open point 3): one default vector per class's cards. Trigger: a second class's
  set committed.
- **lmwalk/landmark priced by the kit's `find.*` cards** through the same T-PICK row format. Trigger: stage 2's
  first committed card set, or [PICK-IDIOM] opening.

## Summary

Rev 2's stage-1 inventory is much closer but not yet "one table per slot": `fn_rows` BODY/PREFIX and the
non-plan `arms[]` table are uncounted (SLOT-2); B-fn vs B-pair makes "(method, frame row)" an insufficient emit
key (SLOT-1); two inline tie spellings and translate's run rank survive (SLOT-3); U10's PRES half contradicts
B4 (SLOT-4). Goal 3's census as written cannot fail on a byte-identical duplicate (SLOT-6). 1a retires two spec'd
denies unmentioned (SLOT-7). Id placement and the 1a/1b counts hold.
