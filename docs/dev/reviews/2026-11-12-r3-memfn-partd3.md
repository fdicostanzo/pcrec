# Review 2026-11-12 r? — memfn Part D design rev 3 (critic round memfn-partd3-1112, design mode, a NARROW RE-CHECK)

## Subject and freeze

- SUBJECT: `docs/design/memfn/part_d.md` rev 3, commit `f923a13fc` (branch lane/memfn-pdesign, head
  `6dc11bd6a` at the freeze). Rev 2 `92976462f` for diffing.
- Claim re-checked: review `docs/dev/reviews/2026-11-12-r2-memfn-partd2.md` (at `6d333a379`), its
  Rulings incl. the joint P8 ruling.
- CLIENT: `docs/design/run_pos_set_stage3_readiness.md` at `14570db62` (an ancestor of the subject;
  unchanged on main).
- BUILD TREE: main `b1c22da94`, review tree built clean (`nice make -j2`, rc 0). Rev 3 re-read its
  cites at `a8ae73be0`; only `docs/design/plan_row_bodies/COND-FAMILY.md` moved since.
- RULINGS at the freeze: decisions.md `cb375f912`, plan.md `a8ae73be0` ([RUN-POS-SET] 2026-11-12
  NOTE: P14 re-scope, P1/P8 for the stage-3 brief). Records of P3/P8/P9/P14/P15: the r2 review's
  Rulings section.
- **FREEZE DRIFT: none.** At hand-back main is `504f10e90` (six COND-FAMILY plan-body commits);
  `git diff --stat a8ae73be0 main -- docs/dev/decisions.md docs/dev/plan.md` is empty.

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| readiness (D3) | opus | Is D3 ready to build: the `run_part_terms` record and the census parser, and can the check fail and pass (K35 source independence, a non-zero population, the plants, the joint-landing floor)? | the launcher's narrow re-check: D3 was the r2 round's NOT READY unit |
| fix-induced (D0-D2) | opus | Does any `[r2pd Pn]` fix touching D0-D2 open a new answer, speed or compile finding? New reads, fields, rows and checks traced at the build tree; population recomputed for checks that two fixes touch; §2.4 witnesses hand-run. Also the two standing questions. | rev 3 is a fix round over 22 P-items |
| verifier | opus | Re-check all 15 findings (6 RDY, 9 FIX) against the build tree; ruling vs text classification | FIX-1, RDY-2 and FIX-5 needed judgment |

## Which lens caught what

- readiness: every D3 finding (RDY-1..6). Fix-induced did not look at D3.
- fix-induced: every D0-D2 finding (FIX-1..9) and the standing questions (FIX-S1..S4).
- No overlaps. The verifier REFUTED one sub-claim, RDY-2(c).

## Overall verdict (proposed): READY WITH LISTED TEXT FIXES, plus ONE joint kit + main ruling (FIX-1)

No finding is answer-level, speed-level or compile-level. All 15 are check-level or doc-level.
That is: a check that cannot red, cannot be built as written, or would red a correct build, or text
that misstates today's code. Every fix is text in part_d; the M-sized ones are FIX-5 and RDY-4.
FIX-1 needs a joint ruling that extends P8. It does not block the kit units. It does block the
stage-3 brief's §9 text, because §9 item 5's "`rdom` stays" is false after P3.

Per unit:
- **D0: ready with listed text fixes.** FIX-3 (P18's rate rule moves today's 354 sites), FIX-9 (a
  second moved window population that D0 must count).
- **D1: ready with listed text fixes.** FIX-4 (P3's floor cannot red), FIX-6 (REACH list misses
  P3's lines), FIX-7 (shared refused counter), FIX-8 (decline row literal). FIX-1's ruling before
  the stage-3 brief.
- **D2: ready with listed text fixes.** FIX-5 (every-pos card shape), FIX-2 (P23 plant's
  detector), FIX-9 (floor + plant for R beside a spelled verify-YES span).
- **D3: ready with listed text fixes.** RDY-1, RDY-2, RDY-4 are substantive: without them the
  check reads nothing on the production path, reds a correct build, or cannot be joined. RDY-3,
  RDY-5 and RDY-6 are wording and lists.

## Findings (ids from the critic files; verifier verdict; PROPOSED disposition)

### D3 (readiness)

- **RDY-1 — collect.py does NOT keep every non-REACH MFTRACE line.** `r33_sim/collect.py`
  `summarize()` keeps only END(define/run), FDROUTE and WPATH, so a `run_part_terms` record is
  dropped. The D3 check (G2 records into the parser) bypasses collect.py, so it stays green while
  the production census path carries nothing. NEW (P15 text). Verifier: HOLDS.
  **FIX-NOW** (text): D3 names collect.py's `summarize` as a changed file (keep the raw record),
  plus the re-collected sweep and the goldens it moves.
- **RDY-2 — the print site.** `wf_parts_prepare` runs in `window_route` before any row is chosen,
  from the quiet ask path and from define. "Where it hands the terms to ofsskip" names no place.
  G2's generic-pass sites (`forms == generic`, skipped by the classifier) would get census records
  with no G2 count, so the per-site equality reds a correct build. Verifier: PARTLY. (a) and (b)
  HOLD. (c), "pcrec's mf_ask doubles records", is REFUTED today: pcrec asks pre-check sites before
  the derived part is attached, and the shadow ask strips preds.
  **FIX-NOW** (text): print on the non-quiet path only (house rule compose.c:1033). Population =
  sites whose define chose the FUNC/ofsskip row (the record carries the row, or a join on
  FDROUTE/END). Generic-pass sites are named and counted separately. Drop (c).
- **RDY-3 — the census never saw derived parts.** probe.c writes a part only `if (p->nalt)`, and a
  derived part is `nalt 0` in the host's preds. census0 `units()` and vcls skip such sites. So
  "priced from its RUN term alone, silently" and "no longer writes alts/wr for a derived part"
  misstate today. D3 adds a NEW population branch. NEW. Verifier: HOLDS (the
  today_method/sim.py part was not traced).
  **FIX-NOW** (text).
- **RDY-4 — no join key, no per-site count, the print is in no unit.** The record's `art=` is the
  kit-internal trace_id (1-3 arts per G2 site), and C2's counts live in the driver keyed by site
  id. Nothing maps one to the other. D2's floors are SITE counts, not per-site unspelled-position
  counts, so "recorded from G2's counts at D2" names counts nobody produces. D2's cell does not
  list the print that p12 plants on. NEW. Verifier: HOLDS.
  **FIX-NOW** (text, D3/D2 content): a G2 per-site join line (e.g. `G2SITE id=N` after define),
  G2's per-site count from C2's MEASURED extent (K35), the print listed in one unit, and floors
  "recorded at D3's first green run".
- **RDY-5 — the joint-landing floor is undefined.** emit_sweep counts DISTINCT PATTERNS that
  differ, per (base, flag, stream). It has no count of "run parts with a wide verified position".
  collect.py's default sources are corpus+bench+s588, emit_sweep's are the corpus only. NEW.
  Verifier: HOLDS (the direction argument is INFERRED).
  **FIX-NOW** (text): name the cell (the `no-run-verify-wide` DIFFER pin at landing, base/stream),
  the census quantity in the same unit restricted to `--sources corpus`, and why census >= movers.
- **RDY-6 — readers and goldens still deferred (r1 F19 PARTLY closed).** Readers: vcls.py,
  census0.py, slot/link.py, slot/plan.py (plans TIMED cells from vcls.out: a `cn+` pair would be
  scheduled), slot/est.py. Goldens: vcls.out, census0_cards.out (byte-equal to vcls.out),
  census0.out. `settest_cls` exists twice. Verifier: HOLDS.
  **FIX-NOW** (text): list them, change both `settest_cls` copies together, and say plan.py does not
  plan `cn+`.

### D0-D2 (fix-induced)

- **FIX-1 — P3 makes the shadow's `dominated`/`rdom` disagree on every dominated no-scan run.**
  pcrec's `req_byte_dominated_by` (emit_dfa.c:8591) still requires `run_verified` on a stated run.
  After P3 the kit does not. So at stage 3 `x.(?:cat|dog)` gives pcrec `pd` 0 and the kit
  `dominated` 1. That reds the KW-8 pick census, and `run_pres_picks.sh` once F3's shape becomes a
  witness. §9 item 5's "`rdom` stays" is false after P3. Correcting pcrec's expectation needs the
  kit's findability (D157) or the reply (K35), the same bind as P8. NEW (opened by P3).
  Verifier: HOLDS (stage-3 half INFERRED). P8's ruling covers leads/rlead only.
  **RULING (joint kit + main), then FIX-NOW:** extend P8's retirement to `dominated`/`rdom` on runs
  with a non-cube position (successor controls: the P22 floor as fixed by FIX-4, plus G2's decline
  equality). Then drop "`rdom` stays". The alternative is to re-open P3. Proposed: extend P8.
- **FIX-2 — P23's combined plant names a detector that reads the planted accessor.** p7's refusal
  reads `kit_pos_spelled`, so a plant that answers "spelled" for 3 members cannot fire it. The real
  detector is C2 or the occurrence oracle. F24's floor is not stratified, so the plant's D1 reach
  goes uncounted. NEW. Verifier: HOLDS.
  **FIX-NOW** (text).
- **FIX-3 — P18's "every MEMBER" rate rule re-rates today's cube positions.** Today there is one
  `rnd(200000)` per position, on `run[j]` only. Under P18 a cube takes two draws on the MAIN rng, so
  later sites shift, and the RATE_TIES cube mass becomes exactly 50000, tying one-member positions.
  This breaks F18's "today's 354 sites byte-identical". NEW. Verifier: HOLDS.
  **FIX-NOW** (text): scope P18 to positions of 3+ members and the wide stream, and make byte
  identity of today's sites a D0 check (hash of the generated site file at the base).
- **FIX-4 — P3's floor cannot red on P3's plant.** Every G2 P2 site states
  `pres_proof = {lead, 0, 1, 1}` (`run` 1). Under that proof the rev-2 and rev-3 rules agree, so
  reverting P3 keeps the floor's count. pcrec's real proof (`run` 0) is never generated. NEW
  (P3 + P22). Verifier: HOLDS.
  **FIX-NOW** (text, D1): G2 states `run` 0 on its no-findable-position sites, and the floor counts
  those. Name the plant (P2 keeps `rs && !proof->run`).
- **FIX-5 — the `every-pos` card instance is not constructible as specified.** formhash.c's four
  shapes cannot build an ALL_PRESENT site with a derived FUNC part. `fh_render` asserts the site's
  ARM id (for a presence site, `precheck`), not the fn walk's row. A scan-less run span has >= 2
  positions (compose.c:569), so the minimum is two SET terms, not one. formhash.c:285-290 may fold
  the body into the generic loop's id. NEW (P9 + P21). Verifier: HOLDS ("deferred, not
  contradicted"). Effort M.
  **FIX-NOW** (text + a small kit design step): name the shape, the row source and the 2-term
  minimum, and say what happens on a fold.
- **FIX-6 — D1's sabotage list misses the plants on the lines P3 rewrites and on the run-mode
  rows.** P3 rewrites S286 (`else if (rs && !proof->run) dom = 0;`), S288 and S1098. S278 and S3045
  anchor the `fd_run_modes[]` rows that gain the `no_scan`/`findable` columns. D2 has a blanket
  REACH clause and D1 has none. NEW / PARTLY P13. Verifier: HOLDS (S1097/S3044/S1103/S1108/S277 not
  opened).
  **FIX-NOW** (text): REACH re-run on every presence.c/finder.c row; S286/S288 re-aimed; a new plant
  for P3's run-less branch (FIX-4's).
- **FIX-7 — `g_p2_refused` stays shared.** P6 splits the untested counter (already P2-only today),
  but `g_p2_refused++` is route-unconditional, so decline refusals satisfy `FLOOR_P2_REFUSED=70`.
  NEW. Verifier: HOLDS (consequence INFERRED).
  **FIX-NOW** (text): decline counters and floor of their own, plus `p2_untested == p2_refused`.
  (FIX-S4's per-route array is the general form; NOTED.)
- **FIX-8 — the decline row's other mandatory columns are unstated:** basis (mandatory, and printed
  in the FD record rows.tsv matches), knowledge key, step, evidence/refuted_by, and `FD_CT`
  kinds/layers. NEW (half of P20). Verifier: HOLDS; the basis choice is the kit's.
  **FIX-NOW** (text: one row literal; the critic leans to `FB_DERIVED` like P0).
- **FIX-9 — P11 leaves a second moved window population uncounted.** Alternatives with a spelled
  verify-NO R plus a spelled verify-YES span are mutated by `two_runs` today and left intact from
  D2, which puts the kit on a path no check has seen. The population EXISTS in g2_win_gen.c
  (FAM_MASS, FAM_REPORT draw both verify values); its size is unmeasured. NEW. Verifier: HOLDS as a
  gap.
  **FIX-NOW** (text): D0 counts it; D2 floors "R + spelled verify-YES, R the member" with a plant
  (`merge` taking the YES span as `m->run`).

### Standing questions (fix-induced lens)

- **FIX-S1** — the shadow-retirement family now has THREE members: scan/rwin (K38-2), leads/rlead
  (P8), dominated/rdom (FIX-1). General form: one declared shadow table, one row per MFPICK record,
  with a "reads the kit's findability" column and one retirement predicate. **PLAN** (memory
  `pcrec-forest-for-trees`: the third member is the unification point). Propose to main with the
  FIX-1 ruling. Trigger: the S2 landing that applies FIX-1.
- **FIX-S2** — P23's spelling family also has `in_stretch` and presence.c `one_member`. General
  form: one accessor returning {one, cube, wide}. **DOC**: P23's text names both and the class form.
  Unlock: C2 becomes one row.
- **FIX-S3** — C8's general form (test kind = f(need, findability)) now has 3-4 per-run special
  cases. **DOC**: add "a fourth per-run special case" to C8's triggers, or record that the
  threshold is met and the deferral is chosen.
- **FIX-S4** — per-route G2 counters. **NOTED**, folded into FIX-7.

## PROBED-AND-HELD (summary; counts in each critic file)

- fix-induced: 46/46 cites hold at the build tree; 31 readers traced (scan, decline, dominance, R
  by role, table, libc note, MFTRACE parsers). 9 witness compiles against python `re`: F2 (3,15),
  F1 subject (0,12), F3 (0,5) with dominance shown to be kit P2's (moves under
  `--memfn=no-fd-pres-g1`), P2/P9 (0,50) VM REQUIRED, F7 (4,14) default and no-window-search, cube
  case (1,6). All hand-executed through rev 3 and agreeing with its §2.4 table. Held by reasoning:
  no new clause fires on today's 354 G2 sites or today's corpus. P7's K-1 count is monotone. P12's
  two-sided pin can red. `ofs_fn_applies` has exactly three callers. P13b-e pins exist. P5 held
  (`[a-z]{8}.q` stays dominated under the G1 deny).
- readiness: 9/10 D3 cites hold (MF_TRACE build, mk_mftrace_lib.sh, vcls/census0 functions, the
  settest card at kit-grid@3, wf_parts_prepare/derive_run_part, the K-1 message, C2's EXTENT probe,
  the generic pass). 1 failed (RDY-1). `cn` = 3..7 with `\w` = 7 compares, computed. `cn+` is
  unpriced, not mis-priced (census0 forecast reports the missing card key). K35 holds IF G2 counts
  from C2's measured extent. The plants p11/p12 red by reasoning once RDY-2/RDY-4 are fixed.
- Noted, not raised: P13a's grep scope misses `r17b_prime/b3b/routed_census_b3b.py` (an ad hoc
  census, not a gate). `pick_floors.tsv` leads floors may fall under P8 (manual census).

## By-id completeness

r2 P-ids closed by rev 3, as far as these two lenses reached:
- P15 (D3): partly. The record is named and the floors are defined, but RDY-1/2/4/5 leave the check
  unbuildable as written.
- F19: PARTLY (RDY-6).
- P3 opened FIX-1 and FIX-4; P6 opened FIX-7; P9 + P21 opened FIX-5; P11 opened FIX-9; P18 opened
  FIX-3; P20 is half done (FIX-8); P23 opened FIX-2; P13 partly (FIX-6).
- No r2 finding was found NOT CLOSED in its own terms. Every finding here is a consequence of a
  fix.
- Findings: RDY-1..6, FIX-1..9, FIX-S1..S4. All 15 non-standing findings were verified (14 HOLDS,
  1 PARTLY).

## D27 recommendation

Unchanged from r2: when D1/D2 build, a spec-first author on the G2 presence family's promise (reply
level). The joint-landing D3 floor (RDY-5) is the natural spec-first target once stage 3 exists.

## Lessons for the guide (proposed)

1. Readiness lens, add: "For a record a check reads, trace BOTH paths, the check's own feed and the
   production collector. A check fed directly can stay green while the production path drops the
   record (r? partd3 RDY-1: collect.py's `summarize` kept 3 record kinds)."
2. Fix-induced lens, add: "A fix to a generator's draw rule: does it change the draw COUNT or values
   on today's population (shared rng)? 'Byte-identical today' needs its own check, a hash of the
   generated file (r? partd3 FIX-3)."
3. Readiness/soundness, add: "A trace record printed inside a function shared by a quiet query
   path and the selection path: name which path prints, and the population that excludes sites
   the counterpart never classifies (RDY-2)."
4. Fix-induced, add: "When a fix relaxes a condition, check that the floor named for it is
   generated on inputs where old and new rules DIFFER (FIX-4: G2 always stated the proof under
   which both agree)."

## Rulings (kit manager, 2026-11-12)

Overall: READY WITH LISTED TEXT FIXES, as proposed.
- FIX-NOW: RDY-1..6 and FIX-2..9.
- Process note, proposed to main for the critic skill: the readiness lens traces a new record through BOTH the check's feed and the production collector.
- No further critic round. Every finding is check- or doc-level, and the verifier refuted none that matters. Rev 4 applies them, then the design goes to main for the GO.

Decisions:
- **FIX-1: JOINT with main, PENDING.** Kit leaning: extend P8's retirement to `dominated`/`rdom` on non-cube runs, and drop §9 item 5's "rdom stays". The alternative would teach `req_byte_dominated_by` which runs have no scan, and that is the kit's findability (D157), the same bind as P8.
- **FIX-S1 (PLAN, for main):** this is the third member of the shadow-retirement family (K38-2's scan/rwin, P8's leads/rlead, now dominated/rdom). It calls for a declared shadow table: which pcrec expectations shadow which kit reply fields, each one live, retired or replaced by a named successor control.
- **FIX-1 RULED (2026-11-12, kit + main jointly):** P8's retirement extends to `dominated`/`rdom` on non-cube runs, and §9's "rdom stays" is dropped (D157). This is pcrec-side, in S2's landing. FIX-S1 is filed by main as plan row [SHADOW-TABLE], a sibling of [FACT-READS] and [ASK-DEFINE-FRAME].
