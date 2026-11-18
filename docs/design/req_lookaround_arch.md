# [REQ-LOOKAROUND] positive lookarounds in the run and the span check: architecture note

STATUS: DRAFT (lane archlook, opus, 2026-11-18; the [ARCH-STEP] pilot on a real feature)
FORM: full   (trigger: 11 existing decision sites touched (site map rows 1, 4, 5, 7, 9, 12, 14, 15, 17, 18, 20); mechanisms added: the pending guards and their CAT/ALT rows (T4), the TOP stage at the walk's exit, the ITEM combinator (D168's item half), the consumed extent of the run, the `req_run_omin` fact row, two walk-parameter rows (reach, `lb_bytes`), the dead value)
TREE: `T=57fcb5737dff37bd97429fb1e889ca0233d12e10` (main, 2026-11-18)   REQUIREMENTS: below, each @ its last commit at T   REGISTER READ: `docs/dev/guide/architecture.md` register @T (last changed 3c40ba007)

Every command below runs from the repository root as `git grep ... $T -- <paths>` or
`git show $T:<path>`; each section's commands follow its table (C-n ids, defined once in
"Commands" at the end, with hit counts at T). "The probe" means the main tree's
`build/pcrec -p rx --features all --emit-facts --pattern P` (binary of 2026-11-15 19:53; one
`src`/`memfn` commit, 4c8cf3c38, a kit-instrument merge, lies between it and T: C30).

## Goals served

- **High-level rule 1 (one home per question).** The feature adds answers to three questions
  the tree already answers somewhere: "which bytes does a positive context node fix, at which
  signed offsets" (D168's context producer, whose ruled home was deleted at [COVER-CAP] stage 1:
  site 22), "can this pattern never match" (the `never_matches` fact: site 21), and "where may
  the attempts begin after a landmark hit" (two emitted copies of one move: site 15). The note
  places each new answer in the existing home or extracts the home first.
- **High-level rule 2 (data with its code; accessors).** It widens three shapes (`RbRuns`,
  `RbRun`/`ReqRun`, the landmark K) in their owning files, and adds one cross-file reader of a
  `Ctx` field (`lb_max`: site 19), which takes an accessor (register row 6a rides).
- **High-level rule 3 (seams).** The kit seam (a MODULE seam) needs no new field: R-38 K38-2
  delivered a negative run-span `omin` and a signed `head_max` (site 16). Every other crossing
  is a LAYER handoff downward (facts to gen), unchanged in direction.
- **High-level rule 4 (remodels ride along).** Five small answer-identical units land first
  (section "Remodels that land first").
- **TRADED AGAINST: the gate's speed half.** L3's scan begins before the start offset, a per-call
  cost in a find-all regime (span_arms §5.5, §11 point 1). The gate's allowances it relies on: a
  cost the user can turn off (`-fno-req-run`, bit 31, re-specified at L3, span_arms §5.8) and
  D186's bar at each pick row a unit moves (span_arms G4). Rule 2 is traded once, knowingly:
  `ReqRun`'s fields stay read directly by the gen layer (39 reads, C9), because the facts
  record is the declared interface (the 2026-11-18 ruling: "Reading a field can be part of that
  interface"); the new fields join that declared interface (site 10), with one accessor for the
  one question a field read would answer wrongly (the consumed extent, unit RM-4).

## Requirements read

| requirement | read at | what it fixes (WHAT) |
|---|---|---|
| plan row [REQ-LOOKAROUND] (`scripts/entry REQ-LOOKAROUND -l 2`) | 57fcb5737 (plan.md) | the owner, 2026-11-05: "the run can go partially into a variable look around (the fixed part)"; "Which is also true of the span check"; 2026-11-06: the lookaround's fixed part with its offset joins the one find-the-span choice set; negative lookarounds only veto |
| `docs/design/span_arms.md` rev 2.2 (units L1-L3, §2, §5, §6, §8, §12-§13) | 8a27e2e0b | the design-of-record; its WHAT read as requirements, its HOW checked against T below. NOTE: the brief and the plan row say "rev 1"; the file is rev 2.2 with owner rulings §12a-§12d (finding F-1) |
| D191 (decisions.md, the owner 2026-11-08/09) | 57fcb5737 | BUILD GO for E1, R1, E2, L1, L3; L2 after R-38's delivery plus one readiness critic. §12a: the scan byte may come from ANY run position; the kit picks the scan position and verify extent; the run crosses as ONE uncut span at signed offsets from the attempt start; nothing about consumption crosses the seam; `<PREFIX>_REQ_BYTE` stays a byte every match consumes, chosen by pcrec. §12b: a run outside the match is ONE run value, every reader raised together; the step back capped at the declared lookbehind length; L3 builds ahead of A-POSDOM, its sites in that table's shape |
| span_arms §12c (review 2026-11-09 r2, ruled) | 8a27e2e0b | "validate the entire span and finish" needs SUFFICIENT and OUTPUTS-DETERMINED as pcrec facts |
| review `docs/dev/reviews/2026-11-08-r1-spanarms.md` | dd2fe2de9 | L NOT READY at rev 0 (F1 the lookahead never meets its right neighbour; F2 guard propagation; F8 reader census; F9 the BACK bound; F15 D168) |
| `docs/dev/lanes/spanarms2_report.md` | fbcb4819c | rev 1's dispositions; the four unlocks filed as plan rows |
| `docs/design/plan_row_bodies/POSTFACT.md`, 2026-11-08 entries | 934ccc63d | span intersection (lookahead removal; lookahead to DFA) as "a general form of this row"; lookbehind removal by `\K` with an earlier scan and a floor; the end-of-match mark |
| D168 and addenda 1-3 | 57fcb5737 | ONE producer of per-offset context sets; a fixed positive lookbehind enters directly |
| `docs/design/cover_cap.md` rev 5.2 (stage 1 BUILT) | d96d533f2 | the span slice (D168's built home) is DELETED; the cover's context comes from the anchored machine's walk (`known.c`); "[DD-11.5]'s part 1 product ... is deleted by stage 1 ... its row needs re-scoping" |
| `memfn/include/memfn.h` MF_SITE_ABI 27 (R-38 K38-2) | 57fcb5737 | the kit's side of span_arms §8.2 parts A and B, delivered in §12a's end-state form (site 16) |
| `docs/dev/guide/architecture.md`, `docs/design/plan_row_bodies/ARCH-STEP.md` | 3c40ba007 | the standard; the 2026-11-17/18 rulings (interface vs representation; the AST grandfathered; an accessor answers a question; functionality wholly dependent on a structure lives in its area) |

VOCABULARY (the critic re-derives the site map from it): AST kinds `A_LOOK` (`u.look.neg`),
`A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV`; the run walk `pcrec_req_walk`, `rb_walk_at`,
`rb_row_into`, `rb_zero_rows`/`rb_zero_look_pos`/`RB_ZERO_*` (T3), `rr_cat`, `rr_alt`/
`rr_alt_rows`, `rb_rep_rows`/`rr_pow` (T2), `rn_better`/`rn_choice_rows`, `RbRuns`, `RbRun`,
`RbVal`, `ReqWalkParams`, `walk_arms.def`/`WALK_ARM`; the description `desc.h`/`pcrec_pd_*`,
`PdDesc`, `PdHead`/`pcrec_ph_*`; the facts `ReqRun`, `whole_len`, `whole_maxoff`,
`req_landmark_maxoff`, `req_byte`/`pcrec_req_pick`, `run_pin`/`pcrec_run_pin`,
`never_matches`/`PfNever`, `facts.def`, `PF_WHY_*`; the context producer `span_facts`,
`MkCtx`, `ctx_before`/`ctx_after`, `N_CTX`, `ctxfn.def`; the handoff `req_handoff_k`,
`req_landmark_k`, `emit_req_handoff_rest`, `emit_req_landmark_move`,
`req_handoff_entry_applies`, `handoff-attempts-entry`, `req_landmark_admits`,
`pcrec_landmark_margin`, `pcrec_emit_start_zero`/`PCREC_START0_ROUNDUP`; the kit seam
`req_pres_spans`, `req_site_define`, `mf_pred.omin`, `mf_site.head_max`, `MF_MAX_BACK`,
`mf_class.run`; the lookbehind bound `Ctx.lb_max`, `pcrec_lb_raise`; spec `match_api.md`
§6.3.7, `tuning.md` §2.28, §2.41, `facts_listing.md` §4.1.2-§4.1.3, `findings.md` §4.
ZERO HITS at T (new shapes, C23): the guards (`lg`/`rg`: the only `lg` in `src` is an unrelated
local in `pcrec_req_info`, req.c:305-307), `cons`, `req_run_omin`, a `dead` why, `lb_bytes`
(named only in a comment, facts_derive.h:125), a `look` walk arm; `span_facts`/`MkCtx`/
`pcrec_span_walk` (C19: deleted).

REQ-OPEN: none changes WHAT the feature does. One owner question (**context-producer-home**)
changes where the item producer is recorded, not what it computes; sites marked `REQ-OPEN
context-producer-home` depend on it.

## Site map

| # | site | command (at T) | today | class | goal/rule |
|---|---|---|---|---|---|
| 1 | `rb_zero_rows[]` (T3), row E-5 `rb_zero_look_pos` → `RB_ZERO_UNIT`; executor `rb_zero_into` (req.c:1072-1100) | C1 | a positive lookaround in either lowering is CAT's plain width-0 unit; its body is never read (E2, built) | ROW (E-5's action becomes "unit + item"; the `look` restore arm keeps today's row) | rule "Decisions are declared tables" |
| 2 | `rb_walk_at`'s `case A_LOOK`/`case A_CTX` → `rb_row_into` (kind row TEXT ZERO) (req.c:1199-1216) | C1 | the kind-row dispatch reaches T3 | AS-IS: the item arrives as T3's row; the design adds NO `A_LOOK` arm in the switch beside the kind-row dispatch (that would be a second dispatch of one kind, the sar1mrg finding of 2026-11-10) | Act through the row |
| 3 | `RbRuns` (req.c:174) and its generic writers: `rr_unit` :535, `rr_none` :546, `rr_pos` :556, `rr_cat` :591 (`RbRuns o;` filled field by field), `rr_alt` :664 (`RbRuns o;` filled by whichever row applies), `rr_alt_union` :625 / `rr_alt_affix` :642 (each writes a subset), `rr_pow` :755, `rr_rep_exact` :767, `rr_rep_split` :783 (`o.tail = rr_cat(...).tail`), `rb_rep_unit_val` :889 (`*v = *b`, a whole-value copy), `rb_rep_best_val`/`rb_rep_gap_val` :921/:940, `rb_gap_into`/`rb_assert_into`/`rb_zero_unit_into`/`rb_init` | C2 | covers consumed runs only (`best`, `head`, `tail`, `all`, `maxw`) | WIDEN (pending guards `lg`/`rg`, a dead bit); two builders leave unnamed fields UNINITIALISED and one copies kind-blind: unit RM-1 | rule "A shape states the inputs it covers" |
| 4 | `rr_cat` (req.c:591) | C3 | joins `l.tail` with `r.head`; `rn_better` over bests, join, head, tail | AS-IS for the consumed join; the guard steps (CAT-R/L/SET/EDGE) are a NEW declared table (T4) called from it, in the file's own row idiom (`RB_ROW_SCAN` with a restore-arm column, three tables already: `rr_alt_rows`, `rb_rep_rows`, `rb_zero_rows`) | Decisions are declared tables; Notice siblings |
| 5 | `rr_alt_rows[]`/`rr_alt_affix` (req.c:616-671) | C4 | common head/tail by `rn_common_head`/`rn_common_tail` | SHARED: the ALT guard rule is the SAME common-head/tail primitive over `lg`/`rg`; no second spelling of the union | One question, one primitive |
| 6 | `rb_rep_rows[]` (T2, req.c:986-1020) | C5 | rows 1-3 built (E1, R1); copies through `rr_pow` → `rr_cat` | AS-IS: guards travel through `rr_cat` per copy; the `m = 0` unit (`rb_init`) and the gap/best forms (`rr_none`) carry none, given RM-1 | — |
| 7 | `rn_choice_rows`/`rn_better` (the run choice, req.c:407-494) and TOP | C6 | the walk's answer is `v->runs.best` (req.c:1247); no stage after the walk | ROW for the ranking (TOP's candidates `tail ++ rg`, `lg ++ head` enter `rn_better` as runs); TOP itself is a NEW stage at the one walk exit, reading walk parameters | Decisions are declared tables |
| 8 | `pcrec_req_walk` + `ReqWalkParams` (facts_derive.h:119-140), filled once by `pf_derive_req_walk` (facts.c:225-233) | C6 | four rows: `pos_set`, `max_pieces`, `restored`, `rate`; the struct's comment already names "L1's reach, L3's `lb_bytes`" | ROW (two new walk parameters) | Decisions are declared tables |
| 9 | `walk_arms.def` | C7 | arms `empty`, `zero`, `rep`, `tie`, `alt` | ROW (a `look` arm restoring E-5's plain unit, span_arms §5.8) | — |
| 10 | `RbRun` (facts_derive.h:105-114) and `ReqRun` (facts.h:68-77); writers of `ReqRun`: the deny reset `case PF_REQ_WHOLE_RUN` (facts.c:97-100, three field writes) and the derivation (facts.c:253-262, `memset` of `pos` plus two field writes) | C8, C10 | a run at offsets `[0, whole_maxoff]` from the attempt start, every position consumed | WIDEN (`omin` signed, the consumed extent); both `ReqRun` writers write FIELD BY FIELD, so a new field is silently missed by the reset (the generic-writer hazard); `RbRun` is also the type of every head/tail/best, so a field on it makes every `rn_*` constructor a writer (design decides where the fields live: D-5) | A shape states the inputs it covers |
| 11 | `facts.def` rows `REQ_WHOLE_RUN` :54, `REQ_LANDMARK_MAXOFF` :57; printers facts.c:840-870 | C11 | one row per offset fact | ROW (`req_run_omin`, span_arms §9) | Decisions are declared tables |
| 12 | the landmark K and its −1 "none" sentinel: written facts.c:106 (reset), :354-356 (`: -1`), `req_landmark_k` emit_dfa.c:9174 (`head < 0 ? -1`); tested by hand at emit_dfa.c:8990 (`k < 0 \|\| k >= PCREC_W_UNBOUNDED`), :9085 (`k >= 0 && k < PCREC_W_UNBOUNDED`), :9360 (`>= PCREC_W_UNBOUNDED`), printer facts.c:868 (`< 0` → `none`) | C12 | K is `{-1 none} ∪ [0, W_UNBOUNDED) ∪ {unbounded}`, sentinel-encoded; three readers re-ask "stated and bounded?" by hand | WIDEN + SHARED: L3's K is of either sign (span_arms §5.4 A3), so the sentinel collides; unit RM-2 | A shape states the inputs it covers; One question, one primitive |
| 13 | `req_handoff_k`/`req_landmark_k` (emit_dfa.c:9154-9176) | C12 | the one spelling of K for every reader | AS-IS (already the one spelling; reads RM-2's value) | — |
| 14 | `cand_rows[]` row `handoff-attempts-entry` (emit_dfa.c:10725), predicate `req_handoff_entry_applies` (:9082-9086) | C13 | declines `whole_maxoff < 0` | ROW (span_arms A8, ADMITTED: the conjunct is deleted, the row runs the signed move) | Decisions are declared tables |
| 15 | the landmark MOVE, two emitted copies: `emit_req_handoff_rest` (emit_dfa.c:1083-1134: `if (handoff_position - posvar > K) handoff_position -= K; else handoff_position = posvar`) and `emit_req_landmark_move` (:7919-7940: `if (landmark_position - pos > K) pos = landmark_position - K`), each then `pcrec_emit_start_zero(..., PCREC_START0_ROUNDUP)` | C14 | both assume the hit `c >= pos` (comment :1074-1076: "THE SUBTRACTION CANNOT UNDERFLOW: `c >= posvar` always"); L3 breaks that premise at both (span_arms A3: W-L10..W-L14) | SHARED: one question ("the first position no skipped attempt could begin before, given hit `c` and K") spelled twice; unit RM-3. A-POSDOM sites, in its table shape by ruling (D191.3) | One question, one primitive |
| 16 | the kit presence seam: `req_pres_spans` (emit_dfa.c:1448-1482; `p[i].omin = 0` at :1479 for EVERY span, the run's included), `req_site_define`'s `s->head_max` (:1640-1644, `int64_t` since K38-2); the soundness comment :1543-1546 ("the presence facts hold no lookbehind byte") | C15, C16 | the kit ACCEPTS a negative `omin` on the run span and a signed `head_max` (memfn.h MF_SITE_ABI 27: "may be NEGATIVE ... the run part's candidates c satisfy max(0, lo + omin) <= c"); pcrec states 0 | AS-IS (the run span's `omin` is filled from the fact where the run span is built; members stay 0, which the kit requires); the comment's premise is restated at L3 | Across the kit boundary, send facts |
| 17 | `pcrec_landmark_margin`/`req_landmark_admits` (emit_dfa.c:9277-9294) | C17 | already reads `max(K, 0)` (`k > 0 ? k : 0`, :9293; K38-2) | AS-IS (span_arms A3's READY3-2 fix is DISCHARGED at T: finding F-3) | — |
| 18 | `pcrec_req_pick` (req.c:1278-1289, `req_byte`) and the trace shadow `req_set_leads_own` (emit_dfa.c:11335-11349): the same expression `pcrec_find_run_scan_index(rate, run->pos, run->whole_len)` at req.c:1284 and emit_dfa.c:11345; a third caller ranks runs inside the walk (req.c:423) | C18 | pcrec's own scan member over EVERY run position | SHARED + ACCESSOR: under L2/L3 `req_byte` must stay a CONSUMED byte (D191.2), so both callers must restrict to the consumed extent; unit RM-4 (the walk's ranking at :423 is a run-choice estimate and stays over every position) | One question, one primitive; accessors |
| 19 | `pcrec_run_pin` (kset.c:302-339) | C18 | picks over the whole run's exact positions and pins the maximal exact stretch | ACCESSOR (reads RM-4's consumed-extent accessor; span_arms A5) | accessors |
| 20 | `Ctx.lb_max` (internal.h:4115): one writer accessor `pcrec_lb_raise` (:4467-4470), one direct reader emit_dfa.c:3644 (`_VALID_LB`) | C19 | the parse-time running max of lookbehind widths, characters | ACCESSOR: L3's `lb_bytes` walk parameter adds a SECOND cross-file reader (facts.c); register row 6a rides | A structure is read and written through its owner's accessors |
| 21 | `never_matches` (`PfNever`, facts.h:285: `PF_NEVER_NO`, `PF_NEVER_MACHINE`; derived kset.c:537-548; read compile.c:3303, :3332 to emit the empty artifact) | C20 | "this pattern can never match" from the final machines | SHARED: span_arms §5.2's DEAD fact (`foo(?=bar)baz`) answers the same question; rev 2.2 homes it as a `why` value `dead` on `req_whole_run`, a second answer. The existing fact takes it as a value (no remodel; D-9) | One question, one primitive |
| 22 | D168's context producer: its built home, the span slice (`span_facts`, `pcrec_span_walk` in kset.c), is DELETED (C19: 0 hits); the cover's per-offset context at −1 and `k` is now `known.c`'s anchored-machine walk (`MkEnd.ctx_before`/`ctx_after`, known.h:24-25); kset's frontier still passes `N_CTX` (kset.c:141) | C19, C21 | no AST-level producer of a positive context node's per-offset sets exists | NEW-SEAM: the ITEM combinator in `src/facts/desc.c` (writer), called by the run walk (reader 1, L1); later readers [LOOK-LOCATE], [CTX-SIDES-PRODUCER], [DD-11.5] part 1 (re-scoped). `REQ-OPEN context-producer-home` | One home per question; functionality on a structure lives in its area |
| 23 | the description module (`desc.h`: `pcrec_pd_unit/zero/none/pos/cat/alt/pow`; the adjacency head `pcrec_ph_*`) | C22 | width groups of exact position sets; two callers (req.c byte level, altnf.c code-point level) | NEW-SEAM (the item combinator is the module's third operation family, over its own structure: the 2026-11-18 ruling's "a graph walk ... can be built in the AST area" applied to the description); sibling: `PdHead`, see "general form" | functionality on a structure lives in its area |
| 24 | `ctxnode.c` (`pcrec_look_t3`'s `ctx-node` row: a one-character lookaround becomes `A_CTX`, ctxnode.c:96-97) | C23 | two lowerings of one construct | AS-IS: both reach T3's one predicate (`rb_zero_look_pos`, req.c:1059-1063); the ITEM row must read both, so the run is the same under `-fno-ctx-node` (span_arms §5.1) | Build the general form |
| 25 | `pcrec_emit_start_zero` calls after the moves (emit_dfa.c:1112, :7930) | C14 | `PCREC_START0_ROUNDUP` | AS-IS by ruling: no new call, no new mode (span_arms §8.1; D191.3) | — |
| 26 | VM route: `emit_vm.c` reads the moves only through the exported emitters (`pcrec_emit_req_attempt_reentry`, `pcrec_emit_req_byte_check`) | C24 | — | AS-IS (no VM file changes; the VM text moves with sites 14-15) | Layering at the call level |
| 27 | `Job.req_handoff_vm`, written by emitters inside the touched functions (emit_dfa.c:1098 in `emit_req_handoff_rest`, :7896 in `pf_emit_handoff`) | C25 | an emitter-to-driver flag (register row 6c, a noted deviation) | AS-IS for this feature (the write is not changed; see register lookup) | A stage-to-stage field names its writer |
| 28 | the contract: `match_api.md` §6.3.7¶6, ¶10, ¶11; `tuning.md` §2.28¶1, §2.41¶1, ¶8b; `facts_listing.md` §4.1.2¶8, ¶8b, §4.1.3; `findings.md` §4 | C26 | E2 already owns the attempt wording of §6.3.7¶6 and §2.28¶1 (span_arms §12d) | AS-IS (spec hunks, D80; the list is re-derived at design time: D-13) | D80 |

Commands for this table: C1-C26 (section "Commands"); hit counts there.

## Register rows looked up

Searched: `git show $T:docs/dev/guide/architecture.md | sed -n '609,633p' | grep -n -F <term>`
for each term `REQ-LOOKAROUND req.c rr_cat desc.c facts.c kset.c emit_dfa emit_vm CandRow
LOOK-LOCATE A-REV A-POSDOM VLOOKBEHIND mod_lookaround lmwalk mrl.c cand_rows handoff landmark
Job memfn ctxnode ctxfn` (C27). Matches: rows 1, 2, 4, 6a, 6b, 6c, 7a, 7b, 9, 10, 12, 13, 14, 16;
row 19 by its event ("the next new declared table"); rows 5 and 15 by their subjects.

| register row | why it matches | disposition |
|---|---|---|
| 14 Alternation folds to one owner, stage 3 | `req.c` `rr_cat`; [REQ-LOOKAROUND] named: "edits the same pass, so serialise" | NOT CARRIED, done: stage 3 + Part D LANDED 2026-11-14 (merge 9cecc3caa; [RUN-POS-SET] status at T, `scripts/entry RUN-POS-SET -l 1`: "waits: nothing in flight"), so the serialisation is discharged. The row's status still reads "riding [RUN-POS-SET]" (finding F-4: the manager closes it). Its own cite "`rr_cat` (`case A_LOOK` :1204)" is `rb_walk_at`'s case, not `rr_cat`'s (C1) |
| 6a Name each Job/Ctx field's writer and readers; a cross-file reader gets an accessor | site 20: L3 adds a cross-file reader of `Ctx.lb_max` | RIDES FIRST, narrowed to the one field (unit RM-5); status "riding [REQ-LOOKAROUND]" for `lb_max` only |
| 6c NOTED DEVIATION: emitters write facts the driver reads (`req_handoff_vm`) | site 27: `emit_req_handoff_rest` and its sibling are touched by RM-3/L3 | NOT CARRIED, with the reason the HOW TO USE IT asks for: the feature changes the move arithmetic, not the flag; the correction is L-sized with its own named event ([VMREC], roadmap H-FLAGS) and an abi/spec event for the caps; RM-3 must keep the write where it is (the one emitter of the move takes no flag duty) |
| 6b Stage outputs as typed records | `Job` | NOT CARRIED: "as roadmap areas migrate, never standalone"; no area migrates here |
| 4 Measure library below parse | [VLOOKBEHIND], `mod_lookaround.c` widths | NOT CARRIED: the feature adds no width walk; the item's offsets come from the description's own width groups and `RbRuns.maxw`, and `lb_bytes` reads `lb_max` (site 20) |
| 1 Start-table rows carry their recover/finish action | [LOOK-LOCATE]; `emit_dfa.c` | NOT CARRIED: no new recover or finish act (K's value moves, the acts do not). Its event is [LOOK-LOCATE] or [EARNED-SKIP] (a finish act), both unlocks below |
| 2 Engine identity asked one way | `emit_dfa.c` | NOT CARRIED: no new engine-identity test; `pf_emit_handoff`'s `cand_finish_of(cx) == CAND_ROUTE_VM` (emit_dfa.c:7896) is beside RM-3's site and stays untouched |
| 10 Shape widened for signed start offsets (`struct CandRow`) | [LOOK-LOCATE]; "trigger: span_arms unit L3 landed plus a bench cell" | NOT CARRIED: `CandRow` holds no offset K reads (emit_dfa.c:5752-5794, C28); L3 is half of the row's trigger. Note for that row: the kit's WINDOW spans start no lower than `-MF_MAX_BACK` = −8 (memfn.h:296), the presence `omin` has no bound, so a lookbehind locate wider than 8 bytes also needs the KIT's shape widened |
| 7a Decisions listed from the Job, not parsed from `#define`s | event "the next change to the facts listing or a new decision stamp": L1 and L3 change the `facts` section | NOT CARRIED: the changed rows are printed from the record (`facts.c`), not parsed by `fd_decisions`; no decision stamp is ADDED (`RX_REQ_RUN`/`RX_REQ_HANDOFF` change value only). The trigger's wording is wider than the row's shape (finding F-5) |
| 7b The artifact as typed parts | `memfn` | NOT CARRIED: no post-render rewrite |
| 9 Split the artifact emitter | `emit_dfa.c` | NOT CARRIED: "a standalone move is churn" |
| 12 Stream roadmap areas | A-POSDOM (sites 15, 25), A-REV (lookbehind hand-off), A-FACTS (`\K` report shift), A-PLAN | A-POSDOM: NOT CARRIED by the owner's ruling (D191.3, span_arms §12b Q5: "L3 before the start-position clean-up, sites in its table shape: AGREED"); RM-3 keeps both sites `ROUNDUP` calls with no new mode, so R08/R09 do not grow. A-REV: no rows moved (ownership ruling 1: vlookbehind.md owns lookbehind admission; the item reads the BODY's description, the hoist the BRANCHES'). A-FACTS: the run is attempt-relative (span_arms §2), no report-shift reader added. A-PLAN: untouched |
| 13 VM body record-first | `emit_vm.c` | NOT CARRIED: no `emit_vm.c` change (site 26) |
| 16 A_BOL/A_EOL into A_CTX | `ctxfn.def` | NOT CARRIED: no new `A_CTX` row; the feature reads two existing functions |
| 19 One first-row walker for every table type | event "the next new declared table": T4 and TOP are new tables | NOT CARRIED: they use req.c's existing `RB_ROW_SCAN` (req.c:393) and add no walker; the row's WHERE omits `RB_ROW_SCAN`, a fourth member (finding F-6) |
| 5 Kind defaults as a kindrow.def column | `rb_row_into` reads the kind row's TEXT | NOT CARRIED: no new kind |
| 15 Internal deny word | bit 31's text re-specified at L3 | NOT CARRIED: no bit added or demoted |

D-row "Revisit when" triggers on mapped sites (`scripts/entry -g` was not usable for D-rows,
`scripts/entry D168` prints "profile decisions dormant": C29; read in `decisions.md` at T):
D168 ("a consumer needs a context fact that is not a per-offset set"): NOT MET, every reader here
reads per-offset sets. D161 ("a window search needs ... an unbounded move-back"): NOT MET, L3's
move-back is capped by `lb_bytes`. D62 ("a fifth AST analysis"): already fired (D70). None other.

PROPOSED ROWS (register columns; status "riding [REQ-LOOKAROUND]" until landed):

| # | remodel | shape (rule) | where (verified by command) | event that carries it | size, gate | deletes | status |
|---|---|---|---|---|---|---|---|
| P1 | Every `RbRuns` builder starts from a stated value | A shape states the inputs it covers (its generic writers) | `rr_cat` req.c:593, `rr_alt` :667 (`RbRuns o;`), `rr_alt_union`/`rr_alt_affix` :625/:642; C2 | [REQ-LOOKAROUND] L1 (unit RM-1) | S, no-mover | two uninitialised-field builders | riding |
| P2 | K as a stated value with one "stated and bounded" predicate | A shape states the inputs it covers; One question, one primitive | facts.c:106, :354, :868; emit_dfa.c:8990, :9085, :9174, :9360; C12 | [REQ-LOOKAROUND] L3 (unit RM-2) | S, no-mover (listing identical) | the −1 sentinel, three hand tests | riding |
| P3 | One emitter of the landmark move | One question, one primitive | emit_dfa.c:1115-1131, :7928-7938; C14 | [REQ-LOOKAROUND] L3 (unit RM-3); A-POSDOM inherits the one site | S, no-mover (byte identity) | one copy of the move | riding |
| P4 | pcrec's own scan member of the run asked once; the consumed extent through one accessor | One question, one primitive; accessors | req.c:1284, emit_dfa.c:11345, kset.c:302; C18 | [REQ-LOOKAROUND] L2 or L3, whichever lands first (unit RM-4) | S, no-mover | one copy of the pick expression | riding |
| P5 | One per-offset-head primitive for the description, or the reason for two | One question, one primitive | `pcrec_ph_*` (desc.h, altnf.c) beside L1's item combinator; C22 | a THIRD reader of "the positions every match of a subtree holds from its start" ([REWRITE-ADJ]'s first build, or [LOOK-LOCATE]) | S-M, no-mover | a second per-offset union | open (trigger not met: two readers at different layers and walls, see "general form") |

NOTED DEVIATIONS on touched sites: row 6c only (above, not carried). PROPOSED noted deviation:
none (the one rule-2 trade, `ReqRun`'s direct field reads, is the declared interface under the
2026-11-18 ruling, not a deviation).

## Remodels that land first

Each is an answer-identical unit with emitted bytes identical (the speed gate's proof); none
needs the feature to land; each deletes something.

**RM-1 (P1) `RbRuns` builders state every field** (before L1).
- What changes shape: `rr_cat` and `rr_alt` start `o` from a stated value (today's `rr_unit()`
  or a designated initialiser), and each `rr_alt_rows` row writes a complete value, so a field
  added later is either written or defaulted to its stated empty value, never uninitialised. The
  kind-blind copy `*v = *b` (`rb_rep_unit_val`, req.c:892) is listed as safe by construction: it
  copies a body's whole value, guards included, which is T2 row 1's rule (span_arms T2 "`m >= 1`:
  the body's").
- Gate: no-mover, byte identity; `--emit-facts` identical over the corpus.
- Size: S. Checks that bind the moved code: the 20 sabotage files that anchor in `rb_zero|RB_ZERO|
  rr_cat|RbRuns|rr_alt|rb_rep` (C31: S1905-S1929, S268, S3129-S3132, S446, S465, S466) and
  `tests/litscan/spanarms.rxt`; each anchor re-greps after the move.
- Generic writers guarded: the whole list in site 3.
- Separable: yes, it changes no value any builder returns today.
- Deletes: the two `RbRuns o;` builders' implicit contract ("every field is written below").

**RM-2 (P2) K stated or none** (before L3; L1 and L2 produce no negative K).
- What changes shape: the landmark offset carries its state (none / bounded / unbounded) beside a
  signed value, and one predicate answers "stated and bounded" for its three hand-testing readers
  (emit_dfa.c:8990, :9085, :9360); `req_landmark_k`'s `-1` (:9174) and the derivation's `: -1`
  (facts.c:354) state "none". `ReqRun.whole_maxoff` keeps its existing none state
  (`whole_len < 2`, span_arms A9).
- Gate: no-mover, byte identity; the listing prints `none` as today (facts.c:868).
- Size: S. Binding checks: `S463_handoff_k_minus_one`, `S809_reentry_k_zero`,
  `S811_k_admission_dropped` and the rest of the 31 move/K sabotage files (C31), re-grepped.
- Separable: yes, every K is non-negative today.
- Deletes: the −1 sentinel (four writes and a printer test) and three hand-spelled range tests.

**RM-3 (P3) one emitter of the landmark move** (before L3).
- What changes shape: `emit_req_handoff_rest`'s moving block and `emit_req_landmark_move`'s
  become calls of one emitter of "`target := max(pos, hit − K)`, rounded up", parameterised by
  its variables (the entry moves the hit variable in place and has an `else`; the re-entry moves
  `pos` and has none); the comment text stays each caller's. L3 then changes the arithmetic in
  ONE place (signed K, no `size_t` wrap at either sign: span_arms A3, W-L10..W-L14). The
  `req_handoff_vm` write (row 6c) stays in its caller.
- Gate: no-mover, byte identity (both sites print the same text as today).
- Size: S. Binding checks: the 31 files of C31, notably S463, S470-S472 (clamp and round-up),
  S808-S809, S1702, S1955, S3074-S3076; each anchor re-aimed at the one emitter, then each still
  shown RED under its plant ([MECH-REACH]).
- Separable: yes.
- Deletes: one of two copies of the move and its "cannot underflow" premise text.
- A-POSDOM: the one emitter is ONE site row in A-POSDOM's table (mode `ROUNDUP`), so its later
  table inherits one row instead of two.

**RM-4 (P4) the run's scan member asked once; the consumed extent through an accessor** (before
L2 or L3, whichever lands first).
- What changes shape: one facts-layer primitive answers "pcrec's own scan member of the stated
  run" (today `pcrec_find_run_scan_index` over every position), called by `pcrec_req_pick`
  (req.c:1284) and by the trace shadow (emit_dfa.c:11345); one accessor beside `pcrec_run_byte`/
  `pcrec_run_has` (facts.h) answers "which positions does every match consume" (today: all of
  them), read by that primitive and by `pcrec_run_pin` (kset.c:302). The walk's run ranking
  (req.c:423) is a run-choice estimate and does not call it.
- Gate: no-mover, byte identity (the extent is the whole run until L2/L3).
- Size: S. Binding checks: `S280_run_pin_bytes_ignored`, `S461_pick_none_ignores_size`,
  `tests/codegen/run_prechecks.sh`, `tests/findings/structural_check.py`,
  `tests/findings/e1_object_check.py` (C32).
- Separable: yes.
- Deletes: one copy of the pick expression; the risk that L2 restricts one picker and not the
  other (the r4 plant's failure shape, span_arms READY2-2).

**RM-5 (register row 6a, narrowed) a read accessor for `Ctx.lb_max`** (before L3).
- What changes shape: the owner of `lb_max` (internal.h, beside `pcrec_lb_raise`) answers the
  question its readers have (the declared lookbehind length, in characters); `emit_dfa.c:3644`
  and L3's walk-parameter filler call it.
- Gate: no-mover, byte identity. Size: S. Binding checks: `tests/assertions/run_assertions_tests.sh`'s
  `VALID_LB` reads (`git grep -n VALID_LB $T -- tests`).
- Separable: yes. Deletes: one direct cross-file field read.

Not units (needed by no part of this feature yet): P5 (above); A-POSDOM's table (ruled after L3).

## The general form and its siblings

GENERAL FORM. A positive lookaround is a FACT about the subject at signed offsets from its cursor
(D168's per-offset context set): an ITEM of exact byte sets with an EXACT/SUPERSET form. Every
reader places items in its own coordinates; the run reads them as pending guards and extends
itself only at the top, at the reach its readers admit, as ONE run value with the signed interval
`[omin, maxoff]` (D191.3). Negative lookarounds stay zero-width cuts (veto only).

THE FAMILY TODAY (C19-C23):
- `known.c`'s anchored-machine walk: the cover's context bytes at −1 and `k` (machine level,
  in-span; since [COVER-CAP] stage 1 the only built context producer).
- kset's frontier passes `N_CTX` per thread (kset.c:141).
- `ctxnode.c`: one-character lookarounds lowered to `A_CTX` (the reason ITEM has two lowerings).
- the adjacency head `PdHead` (`pcrec_ph_*`, altnf.c): "the positions every match consumes
  FIRST", per offset, read THROUGH zero-width nodes at code-point level. A lookahead's item,
  left-aligned, answers the same per-offset question for its body at byte level, from the
  DESCRIPTION rather than a separate walk. Two readers today at different layers (code point vs
  byte) with different walls (the head walls repeats): P5 records the question with a trigger.
- `never_matches` (`PfNever`): the dead value's home (site 21).
- [VLOOKBEHIND] stage 2's fixed-tail hoist reads the description at each BRANCH node
  (span_arms §5.2: "two readers of one description at two nodes, not two producers").

PLANNED ROWS ON THE SAME SHAPES (each shown to fit, or the shape widened first):
| row | shape it extends | fits? |
|---|---|---|
| [LOOK-LOCATE] | the item as a window span at a negative offset; `CandRow` (register row 10) | NO as is on the kit side: window spans start at `>= -MF_MAX_BACK` (−8, memfn.h:296); a longer lookbehind needs the kit's span shape widened at that row (named in row 10's note above). pcrec's item carries any signed offset |
| [PRES-OMIN-TRUE] | `ReqRun.omin` (true positive presence `omin`) | YES: `omin` is signed |
| [CTX-SIDES-PRODUCER] | the item read for the cover's `ctx_before`/`ctx_after` | YES on the item; its owner question is **context-producer-home** |
| [EARNED-SKIP] | a verified run that proves the attempt (trigger: "lookaround-as-run landing and then a bench cell") | NO on `ReqRun` alone: it needs SUFFICIENT and OUTPUTS-DETERMINED (span_arms §12c), facts of their own, not fields of the run |
| [DESC-DEAD] | the dead value | YES once it is a `PfNever` value (site 21); compile.c's reader already emits the empty artifact for one value |
| [CTX-PREFILTER] | a one-character prefilter reading the item | YES (an `A_CTX` item is one term) |
| [ENG-LOOK] / [POSTFACT] span intersection | lookaround as a DFA product; lookahead removal | independent of the run's shape; the item is the FACT shadow of the contained case (span_arms §7) |
| [MATCH-KNOWN] (D142) | the proved prefix | reads the kit's verified extent (`mf_class.run`), not the item |

UNLOCKS: span_arms §10's table at 8a27e2e0b (U-dead, U-locate, U-ctxsides, U-omin, U-descguard,
U-exactwidth, ...), each with its trigger and plan row; this note adds none.

## Seams

| seam | writer | readers | facts down | facts up | new calls, layer direction | text round trip |
|---|---|---|---|---|---|---|
| the description module (desc.c) ← the run walk (req.c) | desc.c's ITEM combinator | the run walk (L1); later the readers of site 22 | the body's description, the cursor side | the item: terms `{off, set}`, form, absent cell | req.c → desc.c (same layer, facts; already a caller of `pcrec_pd_*`) | an item is per-offset 256-bit sets at signed offsets: printable (a design choice whether `--emit-facts` lists it; span_arms §5.3 says no stored item until a second reader) |
| facts record → gen (`ReqRun`, `req_landmark_maxoff`, `req_byte`, `run_pin`) | facts.c `pf_derive_req_walk` and its derived rows | emit_dfa.c (39 `ReqRun` field reads), kset.c | `omin`, the consumed extent (through RM-4's accessor), K of either sign (RM-2) | none | none new; a LAYER handoff, one way (facts → gen), unchanged | yes: `--emit-facts` lists every row (`req_run_omin` new) |
| walk parameters (facts.c → req.c) | `pf_derive_req_walk` | `pcrec_req_walk` | reach, `lb_bytes` | none | facts.c → internal.h accessor (RM-5): parse-written `Ctx`, read downstream; one way | the `harness:<arms>` why token lists the restored arms (`look`) |
| pcrec → kit presence site (MODULE seam; API `memfn.h` `mf_site`/`mf_pred`; contract `memfn.h` MF_SITE_ABI 27 + `docs/design/memfn/span_runs_sheet.md`; tests `tests/memfn/site_manifest.tsv`, `tests/memfn/run_presence.sh`) | `req_pres_spans`, `req_site_define` | the kit's PRES rows and run decision | the run span's `omin` (negative under L3), `head_max` signed; NO consumption fact (D191.2) | `mf_class.run` (scan position, verified extent) | no new call; no new field (both exist at T) | yes: the MFPRES manifest line carries `head_max` (memfn_sites.c:747-765) |
| the caller contract (stamps) | `pcrec_emit_prologue` | callers | `RX_REQ_RUN` (guard positions), `RX_REQ_HANDOFF` negative | — | — | the stamps are text by definition |
| `Job.req_handoff_vm` (gen → driver; row 6c) | `emit_req_handoff_rest`, `pf_emit_handoff` | the size-cap ladder | unchanged | — | an existing back-flow, named here and untouched | — |

Kit seam in words, no verb about the kit's use (rule "Across the kit boundary"): "the run's
position 0 may lie up to `−omin` bytes before the attempt start"; "the landmark's position-0
offset from the attempt start, of either sign". Both sentences are already the kit's contract
(memfn.h at T); pcrec only begins to state values the contract admits.

## What is deleted

- RM-1: two builders' implicit "every field is written" contract.
- RM-2: the −1 sentinel on K (facts.c:106, :354, :868; emit_dfa.c:9174) and three hand-spelled
  range tests (emit_dfa.c:8990, :9085, :9360).
- RM-3: one copy of the landmark move (emit_dfa.c:1115-1131 or :7928-7938) and its
  "`c >= posvar` always" premise.
- RM-4: one copy of the scan-member expression (req.c:1284 / emit_dfa.c:11345).
- RM-5: the direct `cx->lb_max` read at emit_dfa.c:3644.
- The feature (L1-L3): E-5's plain-unit form as the default (it survives only as the `look`
  restore arm's row); the ctx-node / no-ctx-node run difference; `req_handoff_entry_applies`'
  `k >= 0` conjunct (A8); `p[i].omin = 0` on the run span; the presence comment's "no lookbehind
  byte" premise; span_arms rev 2.2's `dead` why token (replaced by a `PfNever` value, site 21);
  span_arms §8.2's kit request (delivered: F-2).

## What the design step must decide

| id | site | decision handed on |
|---|---|---|
| D-1 | 1, 2 | how T3's ITEM row walks the lookaround BODY (`rb_zero_into` takes a `const RbWalk *` and has no child slots; `rb_walk` needs both) without a second `A_LOOK` dispatch, and how the body's set, description and consumed runs are kept OUT of the parent (only its item and guards leave) |
| D-2 | 3 | where the guards and the dead bit live (`RbRuns` or `RbVal`), and their stored bound (span_arms §2: at `PCREC_MAX_REQ_RUN_SCAN`, kept end nearest the edge) |
| D-3 | 4, 5 | T4's spelling: CAT-R, CAT-L, CAT-SET and CAT-EDGE are SEQUENTIAL steps, not first-match alternatives, so which parts are rows of a first-match table and which are fixed steps; the `look` arm's restore semantics (span_arms §5.8) |
| D-4 | 7, 8 | TOP: its place (the walk exit, `pcrec_req_walk`), its candidates' entry into `rn_choice_rows`, and the reach/`lb_bytes` walk-parameter rows |
| D-5 | 10 | whether `omin` and the consumed extent are fields of `RbRun` (every `rn_*` constructor becomes a writer) or only of the walk's OUTPUT and `ReqRun`; both `ReqRun` writers (facts.c:97-100, :253-262) updated |
| D-6 | 18, 19 | RM-4's primitive and accessor spellings, and where the primitive lives (req.c beside `pcrec_req_pick`, or findings.c) |
| D-7 | 12 | RM-2's representation of K's state |
| D-8 | 15 | RM-3's parameters; how the entry's `else` branch and the re-entry's re-ask stay byte-identical |
| D-9 | 21 | the dead value as a `PfNever` value: its epoch (the req walk is E2; `never_matches` is derived from the final machines today), and that compile.c's empty-artifact readers (compile.c:3303, :3332) stay keyed on the machine value until [DESC-DEAD]'s trigger, so L1 moves no bytes through it. The manager's call if the design disagrees (an answer-free placement) |
| D-10 | 22, 23 | the item combinator's interface in desc.c (byte alphabet only, or alphabet-generic like the rest of the module); its bound (`max_pos` keeps the LAST positions, so a wide lookahead body loses its HEAD terms, span_arms §5.3 "Bounds") |
| D-11 | 20 | the `lb_bytes` factor per encoding (span_arms §5.5: `lb_max` under `byte`, `4 · lb_max` under `utf8`) and its unit (characters vs bytes) at the accessor |
| D-12 | 16, PCRE2 | QUESTIONS FOR A pcre2-reader (D181), one each: (a) in UTF mode, may a lookbehind read before the start offset, and what bounds how far (the declared `max_lookbehind`, nested lookbehinds)? span_arms §5.5 MEASURED `(?<=c(?<=bc)d)e` from 3: match in non-UTF, no match in UTF; the reason is not known from code. (b) Does PCRE2's "last code unit" start optimisation ever take a unit from inside a positive lookahead? (informative only: pcrec's run is its own fact) |
| D-13 | 28 | the spec hunk list, re-derived at the design's base: E2 already owns the attempt wording of match_api §6.3.7¶6 and tuning §2.28¶1 (span_arms §12d) |
| D-14 | 16, 18 | L2's text refreshed to D191.2 and K38-2: span_arms rev 2.2's A13/§8.2 "the kit picks inside `cons`" is superseded; the consumed extent stays pcrec-internal (for `req_byte` and the pin), and the kit may scan any run position, `bar(?=baz)`'s `z` included |
| D-15 | 1-7 | re-measure span_arms §5.6/§5.7's "today" column at the design's base: E1, E2 and R1 moved it (the probe at T: `xy(?=bc)[bc]c` is `78796263/fffffeff`, i.e. `xy[bc]c`, where §5.6 says `xy`; `foo(?=bar)baz` is `666f6f62617a`, where §5.6 says `baz`; `(?<=foo)bar(\w)\1` is `626172[\w]` with `RX_REQ_HANDOFF "0"`; C30) |

## Open questions for the owner

1. **context-producer-home** — Where does the lookaround's "fixed bytes at known offsets" fact
   live now that its ruled home is gone? D168 (yours, 2026-10-18) says ONE producer of these
   per-offset context sets, in the span slice; [COVER-CAP] stage 1 deleted that slice, and the
   cover now reads its own context (the byte before and after the span) from the anchored
   machine. Current behaviour: for `(?<=foo)bar`, nothing states that `f`, `o`, `o` sit at −3,
   −2, −1; the cover's context comes from the machine; the required run is `bar` only (the probe:
   `626172@0`). Why it matters to the shape: the lookaround unit L1 builds the first AST-level
   producer (the item, from the lookaround body's fixed-width description). Either it is D168's
   producer for every AST-level reader, with the machine-level context of a span edge left to
   the cover (two producers by LAYER, each with its own readers), or the cover's context must
   also read the item (one producer, and the cover gains a dependency on the description).
   Leaning: by layer. The item is D168's producer for AST readers (the run, [LOOK-LOCATE],
   [CTX-SIDES-PRODUCER]); the cover keeps the machine's, which already knows things the item
   cannot (`\b`, threads). L1 files the D168 addendum saying so, replacing span_arms §12's text,
   which names the deleted slice.
2. **remodel-go** — Does your build go of 2026-11-09 for the lookaround units (D191: L1, L3)
   cover the five small no-change refactors this note says land first, or does each need its own
   go? They change no answer and no emitted byte (e.g. `(?<=foo)bar(\w)\1` compiles to identical
   C after the move-arithmetic merge, RM-3); each exists only so the lookaround change touches one
   place instead of two. Current behaviour: none of them is built; the two copies of the move
   both assume the landmark is never before the search position, which a lookbehind run breaks.
   Leaning: they ride under the unit that needs them, as that lane's first commits, each gated
   by byte identity before the feature's own commit (RM-1 before L1; RM-2, RM-3, RM-5 before L3;
   RM-4 before L2 or L3).

## Commands

All at `T=57fcb5737`; `G='git grep -n -E'`. Counts are hit lines at T (scratch copy of every
output: the lane's `$PCREC_TMPDIR/scratch/archlook/cmds.out`, not committed).

- C1 `$G "rb_zero_rows|rb_zero_look_pos|RB_ZERO_" $T -- src` (19)
- C2 `$G "RbRuns o;|RbRuns r;|\*v = \*b|^static RbRuns" $T -- src/facts/req.c` (13)
- C3 `git grep -n "rr_cat" $T -- src` (10)
- C4 `$G "rr_alt_rows|rn_common_head\(|rn_common_tail\(" $T -- src` (13)
- C5 `$G "rb_rep_rows|rr_pow\b" $T -- src/facts/req.c` (8)
- C6 `$G "pcrec_req_walk|ReqWalkParams" $T -- src` (10); `git show $T:src/facts/req.c | sed -n '1235,1249p'`; `grep -n rn_choice_rows` on the same
- C7 `git grep -n "WALK_ARM(" $T -- src/facts/walk_arms.def` (7)
- C8 `$G "\} RbRun;|\} ReqRun;|long long whole_maxoff" $T -- src/facts` (3); `git show $T:src/facts/facts.h | sed -n '60,77p'`
- C9 `git grep -c -E "whole_len|whole_maxoff" $T -- src` (emit_dfa.c 39, facts.c 14, facts.h 9, kset.c 3, req.c 2)
- C10 `$G "req_run\.(whole_len|whole_maxoff|pos)" $T -- src/facts/facts.c` (8); `git show $T:src/facts/facts.c | sed -n '92,110p;225,262p'`
- C11 `git show $T:src/facts/facts.def | grep -n "REQ_"` (6)
- C12 `$G "req_landmark_maxoff = -1|req_landmark_maxoff < 0|k < 0 \|\||k >= 0 &&|head < 0 \? -1" $T -- src` (8; the compound.c, emit_code.c, emit_subst.c hits are unrelated); `$G "req_landmark_k\(|req_handoff_k\(" $T -- src/gen/emit_dfa.c`
- C13 `$G "\"handoff-attempts-entry\"|^static bool req_handoff_entry_applies" $T -- src/gen/emit_dfa.c` (3)
- C14 `$G "^static void emit_req_handoff_rest|^static void emit_req_landmark_move|handoff_position - %s > %lld|landmark_position - %s > %lld" $T -- src/gen/emit_dfa.c` (5); `git show $T:src/gen/emit_dfa.c | sed -n '1064,1134p;7909,7940p'`
- C15 `$G "p\[i\]\.omin = 0|s->head_max = " $T -- src/gen/emit_dfa.c` (3); `git show $T:src/gen/emit_dfa.c | sed -n '1536,1551p'`
- C16 `git show $T:memfn/include/memfn.h | grep -n -E "may be NEGATIVE|negative on the run span|int64_t +head_max"` (3: :238, :768, :941)
- C17 `git grep -n -F "k > 0 ? k : 0" $T -- src/gen/emit_dfa.c` (1: :9293)
- C18 `$G "pcrec_find_run_scan_index\(" $T -- src` (5); `$G "^void pcrec_run_pin|pcrec_find_pick\(rate, cand" $T -- src/facts/kset.c` (2)
- C19 `git grep -n "lb_max" $T -- src` (9); `git grep -n -i -E "span_facts|MkCtx|pcrec_span_walk" $T -- src` (0)
- C20 `$G "PF_NEVER_[A-Z]+|PfNever pcrec_never_matches" $T -- src/facts` (10); `$G "pcrec_fact_never_matches" $T -- src/core/compile.c`
- C21 `$G "uint8_t +ctx_(before|after)" $T -- src/gen/known.h` (2); `$G "N_CTX|ctxfn" $T -- src/facts/kset.c src/gen/known.c` (1)
- C22 `git show $T:src/facts/desc.h` (the `pcrec_pd_*`/`pcrec_ph_*` declarations)
- C23 `$G "CTXFN_NEXT|CTXFN_PREV" $T -- src` (3); zero-hit vocabulary: `$G "\blg\b|\brg\b|cons_lo|req_run_omin|PF_WHY_DEAD\b|lb_bytes|WALK_ARM\(LOOK" $T -- src memfn/src` (4, none a feature hit)
- C24 `$G "pcrec_emit_req_attempt_reentry|pcrec_emit_req_byte_check" $T -- src/gen/emit_vm.c` (3)
- C25 `$G "req_handoff_vm = true" $T -- src` (2)
- C26 `git show $T:docs/spec/match_api.md | grep -n "6.3.7 Windows"`; the same for `tuning.md` "2.28", "2.41" and `facts_listing.md` "4.1"
- C27 `git show $T:docs/dev/guide/architecture.md | sed -n '609,633p'` then the per-term `grep -n -F` loop above
- C28 `git show $T:src/gen/emit_dfa.c | sed -n '5752,5794p'` (`struct CandRow`)
- C29 `scripts/entry D168 -l 1` (prints "profile decisions dormant"); `git show $T:docs/dev/decisions.md | grep -n "^## D168\|^## D191"`
- C30 the probe on `(?<=foo)bar`, `bar(?=baz)`, `xyz(?<=yz)abc`, `a(?=b)[bc]`, `xy(?=bc)[bc]c`, `foo(?=bar)baz`, `(?<=foo)bar(\w)\1`, reading `req_whole_run`, `req_byte`, `req_landmark_maxoff`, `never_matches`, `RX_REQ_RUN`, `RX_REQ_WHY`, `RX_REQ_HANDOFF`; `git log --oneline --since="2026-11-15 19:53" $T -- src memfn/src memfn/include` (1)
- C31 `git grep -l -E "landmark_position|handoff_position|req_landmark_maxoff|whole_maxoff|req_landmark_k|pcrec_landmark_margin" $T -- tests/mech/sabotages` (31); `git grep -l -E "rb_zero|RB_ZERO|rr_cat|RbRuns|rr_alt|rb_rep" $T -- tests/mech/sabotages` (20)
- C32 `git grep -l -E "rb_zero_look_pos|rb_zero_rows|rr_cat|pcrec_req_walk|emit_req_landmark_move|emit_req_handoff_rest|req_handoff_entry_applies|pcrec_run_pin|pcrec_req_pick" $T -- tests` (17)

## Findings for the manager (not owner questions)

- F-1: the plan row's status ("rev 1 written ... next: the re-check round on span_arms.md rev 1")
  and the brief describe rev 1; the note is rev 2.2, and D191 gave the build go for L1 and L3 on
  2026-11-09. [REPEAT-RUN] reads `STATE:not-started` though R1 landed (journal 2026-11-09/10).
- F-2: span_arms §8.2's kit request is DELIVERED in §12a's end-state form (R-38 K38-2,
  MF_SITE_ABI 27: no cut, the kit's one run decision `mf_class.run`, a negative run-span `omin`,
  a signed `head_max`, the twin admitting by `max(K, 0)`); L2's remaining condition under D191
  is its one readiness critic, on text that D-14 must refresh first.
- F-3: span_arms A3's margin fix (READY3-2) is already in the tree (emit_dfa.c:9293, C17).
- F-4: register row 14's status is stale (stage 3 landed 2026-11-14).
- F-5: register row 7a's trigger ("the next change to the facts listing") is wider than its
  shape (the `decisions` section's `#define` parse).
- F-6: register row 19's WHERE omits req.c's `RB_ROW_SCAN`, a fourth first-row walker.
- F-7: span_arms §5.3 and §12 (the D168 addendum text) name kset's frontier as the producer's
  in-span half and the deleted slice as D168's home; both are stale after [COVER-CAP] stage 1
  (owner question **context-producer-home**).
