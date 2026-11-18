# [REQ-LOOKAROUND] positive lookarounds in the run and the span check: architecture note

STATUS: ACCEPTED rev 2.1 (the manager, 2026-11-18: rev 2 after review r50, confirm critic conf-archlook "accept after small edits", its ten edits applied by lane landarch; OPEN: the owner questions context-producer-home and remodel-go; the register proposals are accepted as proposals and entered in the register at this note's landing). Rev 1: lane archlook, opus, 2026-11-18, the [ARCH-STEP] pilot on a real
feature. Review `docs/dev/reviews/2026-11-18-r50-archlook.md` (verdict RULED: NOT ACCEPTED as is; REVISE, then one
confirm critic). Rev 2: lane archlook2, opus, 2026-11-18, a FRESH architect applying findings A1-A18 as the manager
ruled them (`docs/dev/reviews/2026-11-18-r50-archlook/dispositions.md`). Each changed passage carries its tag `[r50 An]`.
FORM: full   (trigger: 11 existing decision sites touched (site map rows 1, 4, 5, 7, 9, 12, 14, 15, 17, 18, 20); mechanisms added: the pending guards and their CAT/ALT rows (T4), the TOP stage at the walk's exit, the ITEM (D168's item half), the consumed extent of the run, the `req_run_omin` fact row, the `lb_bytes` walk parameter (and `reach`, or TOP rows with an arm column: D-4), the dead fact's propagation (one home, the never family: site 21))
TREE: `T=57fcb5737dff37bd97429fb1e889ca0233d12e10` (main, 2026-11-18) for every CODE statement.   REQUIREMENTS: below, each @ its last commit at T, EXCEPT the plan row [REQ-LOOKAROUND], read at main HEAD `2843924a1` ("plan: REQ-LOOKAROUND brought current and moved to Active"), a plan.md-only commit that landed during review r50's freeze; `git diff --stat 57fcb5737 2843924a1 -- src memfn lib cli docs/spec docs/dev/guide docs/dev/decisions.md docs/design/span_arms.md` prints nothing, so no code or ruling below moved.   REGISTER READ: `docs/dev/guide/architecture.md` register @T (last changed 3c40ba007)

Every command below runs from the repository root as `git grep ... $T -- <paths>` or
`git show $T:<path>`; each section's commands follow its table (C-n ids, defined once in
"Commands" at the end, with hit counts at T). "The probe" means the main tree's
`build/pcrec -p rx --features all --emit-facts --pattern P` (binary of 2026-11-15 19:53; one
`src`/`memfn` commit, 4c8cf3c38, a kit-instrument merge, lies between it and T: C30).
"The anchor map" means `docs/dev/reviews/2026-11-18-r50-archlook/firstunit_anchors.py` run over an export of T's
`src/facts/{req,facts,kset}.c`, `src/gen/emit_dfa.c` and `tests/mech/sabotages/` (C37): it lists every sabotage
whose first `SAB_BEFORE` line falls inside a unit's moved line ranges, so binding checks are found by anchor
LOCATION, not by an identifier grep [r50 A13].

## Goals served

- **High-level rule 1 (one home per question).** The feature adds answers to three questions
  the tree already answers somewhere: "which bytes does a positive context node fix, at which
  signed offsets" (D168's context producer, whose built home was deleted at [COVER-CAP] stage 1;
  D172 names the window site a reader of it; [CTX-FACTS-NEG] plans a machine-level producer of
  the same per-offset sets: site 22), "can this run or pattern never match" (the never family:
  `PfNever`, derive.c's prune, mrl.c's minw ceiling, the `empty` LOCATE row: site 21), and "where may
  the attempts begin after a landmark hit" (two emitted copies of one move: site 15). The note
  places each new answer in an existing home or extracts the home first; where the owner's
  answer to **context-producer-home** would leave two producers, it proposes the noted-deviation
  row that answer needs [r50 A4, A8].
- **High-level rule 2 (data with its code; accessors).** It widens three shapes (`RbRuns`,
  `RbRun`/`ReqRun`, the landmark K and its offset-bound family) in their owning files, and adds one
  cross-file reader of a `Ctx` field (`lb_max`: site 20), which takes an accessor (register row 6a
  rides). `ReqRun`'s direct field reads by gen are covered by the facts module's MODULE-level
  declaration (facts.h:4-5, C36: "A consumer of a pattern fact reads it through this header and
  nothing else: value types, accessors and renderers - never a derivation"), so the 39 `whole_len`/`whole_maxoff` reads
  need no row; the NEW fields (`omin`, the consumed extent) are declared part of that interface in
  facts.h when added (D-5; the owner, ARCH-STEP.md 2026-11-18: "The rules are stronger moving
  forwards and sympathetic looking back") [r50 A3].
- **High-level rule 3 (seams).** The kit seam (a MODULE seam) needs no new field: R-38 K38-2
  delivered a negative run-span `omin` and a signed `head_max`, and R-41 (MF_SITE_ABI 29) states
  an unbounded K by name, `MF_HEAD_MAX_UNBOUNDED` (site 16) [r50 A1]. Every other crossing is a
  LAYER handoff downward (facts to gen), unchanged in direction.
- **High-level rule 4 (remodels ride along).** Five small answer-identical units land first
  (section "Remodels that land first"); one of them (RM-2) and the consumed-extent accessor that rides with L2/L3 (not an RM unit) are
  already inside the L3 text D191.1 gave its go; the other four (RM-1, RM-3, RM-5 and RM-4's one
  shared pick primitive) are new [r50 A5].
- **TRADED AGAINST: the gate's speed half.** L3's scan begins before the start offset, a per-call
  cost in a find-all regime (span_arms §5.5, §11 point 1). The gate's allowances it relies on: a
  cost the user can turn off (`-fno-req-run`, bit 31, re-specified at L3, span_arms §5.8) and
  D186's bar at each pick row a unit moves (span_arms G4). No rule-2 trade remains (A3 above).

## Requirements read

| requirement | read at | what it fixes (WHAT) |
|---|---|---|
| plan row [REQ-LOOKAROUND] (`scripts/entry REQ-LOOKAROUND -l 2`) | main HEAD 2843924a1 (brought current during the freeze; at T the row still read rev 1, see F-1) | the owner, 2026-11-05: "the run can go partially into a variable look around (the fixed part)"; "Which is also true of the span check"; 2026-11-06: the lookaround's fixed part with its offset joins the one find-the-span choice set; "Negative lookarounds only veto at FINISH". Status at HEAD: "span_arms.md is at rev 2.2 (units L1-L3); D191 (Frank 2026-11-09) gave L1 and L3 a build go, L2 after the kit's R-38 delivery plus one readiness critic; NOT built". Refs include "D172 (spans carry negative start offsets)" |
| `docs/design/span_arms.md` rev 2.2 (units L1-L3, §2, §5, §6, §8, §12-§13; its review dispositions, READY-5 among them) | 8a27e2e0b | the design-of-record; its WHAT read as requirements, its HOW checked against T below |
| D191 (decisions.md, the owner 2026-11-08/09) | 57fcb5737 | 1: "**BUILD GO** (Frank 2026-11-09, "Go on build") for the units of docs/design/span_arms.md rev 2.2 §8: E1, R1, E2, L1 and L3; L2 after the kit's delivery of R-38 plus one readiness critic on its changed text ... a unit whose census finds NO mover anywhere stops and reports." 2 (§12a): "the scan byte may come from ANY run position; the kit picks the scan position and the verify extent; the run crosses as ONE uncut span ...; nothing about consumption crosses the seam; `<PREFIX>_REQ_BYTE` keeps its meaning (a byte every match consumes), chosen by pcrec; the pcrec/kit agreement check retires." 3 (§12b): "a run outside the match is ONE run value, every reader raised together ...; the lookbehind step back is capped at the declared lookbehind length; L3 builds now, ahead of A-POSDOM, its two sites in that table's shape (§8.1)" |
| D172 (decisions.md, the owner 2026-10-21) | 57fcb5737 | "spans, each with a start offset (negative allowed), a set per position ...", and "Fixed lookbehinds and post-span lookaheads longer than 1 come with it, sourced from main's D168 producer" [r50 A4] |
| span_arms §12c (review 2026-11-09 r2, ruled) | 8a27e2e0b | "validate the entire span and finish" needs SUFFICIENT and OUTPUTS-DETERMINED as pcrec facts |
| span_arms review r3 READY-5, "FIX-NOW (the manager's form)" (span_arms.md §R3 disposition table and §3.7's listing text, C38) | 8a27e2e0b | "`dead` and `harness:<source>` are WHY VALUES, one per run, first match `dead` > `harness:` > the existing reasons; no second field"; "`dead` sits on `req_whole_run` only. A dead `req_whole_run` is `derived` ...", ... `pf_done_why` (`facts.c:169-182`) takes `dead` and `harness:` out of its `decl` list, `run_facts_checks.sh`'s status/why pairs gain the two. REVISED for the fact's HOME by the manager's r50 A8 ruling (see site 21); its LISTING consequences are KEPT [r50 A8] |
| review `docs/dev/reviews/2026-11-08-r1-spanarms.md` | dd2fe2de9 | L NOT READY at rev 0 (F1 the lookahead never meets its right neighbour; F2 guard propagation; F8 reader census; F9 the BACK bound; F15 D168) |
| `docs/dev/lanes/spanarms2_report.md` | fbcb4819c | rev 1's dispositions; the four unlocks filed as plan rows |
| `docs/design/plan_row_bodies/POSTFACT.md`, 2026-11-08 entries | 934ccc63d | span intersection (lookahead removal; lookahead to DFA) as "a general form of this row"; lookbehind removal by `\K` with an earlier scan and a floor; the end-of-match mark |
| D168 and addenda 1-3 | 57fcb5737 | ONE producer of per-offset context sets; a fixed positive lookbehind enters directly |
| plan rows [CTX-FACTS-NEG], [NEVER-MATCH], [DESC-DEAD] (`scripts/entry TAG -l 2`) | main HEAD 2843924a1 (unchanged since T) | [CTX-FACTS-NEG]: "D168 context facts at negative offsets / past the end ... (per-offset sets {set, includes-absent, exact}: `\b`, fixed positive lookbehind, width-1 negative lookbehind), to be produced from the anchored DFA the cover route reads"; trigger "a client that needs the facts: the S4 [REQ-LOOKAROUND] work or kit_proof UL-0". [NEVER-MATCH]: trigger "(D77) a corpus count ... or span_arms L1's landing (its DEAD bit makes the whole-pattern case nearly free)" [r50 A4] |
| `docs/design/cover_cap.md` rev 5.2 (stage 1 BUILT) | d96d533f2 | the span slice (D168's built home) is DELETED; the cover's context comes from the anchored machine's walk (`known.c`) |
| `memfn/include/memfn.h` MF_SITE_ABI 29 (R-38 K38-2, then R-38 Part D + R-41) | 57fcb5737 | the kit's side of span_arms §8.2 parts A and B in §12a's end-state form (site 16), and the unbounded K stated by name: "mf_site.head_max's stated "unbounded" K (R-41, MF_SITE_ABI 29): equal to pcrec's PCREC_W_UNBOUNDED ... stated by NAME (never the number)" (C16) [r50 A1] |
| `docs/dev/guide/architecture.md`, `docs/design/plan_row_bodies/ARCH-STEP.md` | 3c40ba007 | the standard; the 2026-11-17/18 rulings. The owner's words, 2026-11-18: "the key is having a defined interface vs representation. Reading a field can be part of that interface."; "I agree. Also, looking for functionality wholly dependent on eg the AST, can be built in the AST area. Eg a graph walk" (the record: such functionality "can be built in that structure's own area"; that the owning unit IS the home is the manager's reading) [r50 A9 a, b] |

VOCABULARY (the critic re-derives the site map from it): AST kinds `A_LOOK` (`u.look.neg`),
`A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV`; the run walk `pcrec_req_walk`, `rb_walk_at`,
`rb_row_into`, `rb_zero_rows`/`rb_zero_look_pos`/`RB_ZERO_*` (T3), `rr_cat`, `rr_alt`/
`rr_alt_rows`, `rb_rep_rows`/`rr_pow` (T2), `rn_better`/`rn_choice_rows`, `rn_scan_mass`, `RbRuns`,
`RbRun`, `RbVal`, `ReqWalkParams`, `walk_arms.def`/`WALK_ARM`, `RB_ROW_SCAN`; the description
`desc.h`/`pcrec_pd_*`, `PdDesc`, `PdAlpha`, `PdHead`/`pcrec_ph_*`; the facts `ReqRun`, `whole_len`,
`whole_maxoff`, `req_landmark_maxoff`, `req_byte`/`pcrec_req_pick`, `run_pin`/`pcrec_run_pin`,
`never_matches`/`PfNever`, `facts.def`, `PF_WHY_*`; the offset-bound family `RB_OFF_UNBOUNDED`,
`PCREC_W_UNBOUNDED`, `MF_HEAD_MAX_UNBOUNDED`; the never family `never_node` (derive.c),
`PCREC_MINW_MAX` (mrl.c), `locate_empty_applies`, `pcrec_dfa_accepts_nowhere`; the context producer
`span_facts`, `MkCtx`, `ctx_before`/`ctx_after`, `N_CTX`, `ctxfn.def`; the handoff `req_handoff_k`,
`req_landmark_k`, `emit_req_handoff_rest`, `emit_req_landmark_move`, `pcrec_emit_req_attempt_reentry`,
`req_handoff_entry_applies`, `req_handoff_unbounded_applies`, `handoff-attempts-entry`/`-unbounded`,
`req_landmark_admits`, `pcrec_landmark_margin`, `pcrec_emit_start_zero`/`PCREC_START0_ROUNDUP`; the
run pin's gen readers `us_run_pin`, `pf_window_of`, `walk_proves`, `ofs_test_of`,
`ofs_test_verifies_run`, `pf_run_applies_common`; the kit seam `req_pres_spans`, `req_site_define`,
`mf_pred.omin`, `mf_site.head_max`, `MF_MAX_BACK`, `mf_class.run`; the lookbehind bound `Ctx.lb_max`,
`pcrec_lb_raise`; spec `match_api.md` §6.3.7, `tuning.md` §2.28, §2.41, `facts_listing.md`
§4.1.2-§4.1.3, `findings.md` §4.
ZERO HITS at T (new shapes, C23): the guards (`lg`/`rg`: the only `lg` in `src` is an unrelated
local in `pcrec_req_info`, req.c:305-307), `cons`, `req_run_omin`, a `dead` why, `lb_bytes`
(named only in a comment, facts_derive.h:125), a `look` walk arm; `span_facts`/`MkCtx`/
`pcrec_span_walk` (C19: deleted).

REQ-OPEN: none changes WHAT the feature does. One owner question (**context-producer-home**)
changes which unit produces the item and whether a second producer is ever built, not what the
run computes; sites marked `REQ-OPEN context-producer-home` depend on it.

## Site map

| # | site | command (at T) | today | class | goal/rule |
|---|---|---|---|---|---|
| 1 | `rb_zero_rows[]` (T3), row E-5 `rb_zero_look_pos` → `RB_ZERO_UNIT`; executor `rb_zero_into` (req.c:1072-1100) | C1 | a positive lookaround in either lowering is CAT's plain width-0 unit; its body is never read (E2, built) | ROW (E-5's action becomes "unit + item"; the `look` restore arm keeps today's row) | rule "Decisions are declared tables" |
| 2 | `rb_walk_at`'s `case A_LOOK`/`case A_CTX` → `rb_row_into` (kind row TEXT ZERO) (req.c:1199-1216) | C1 | the kind-row dispatch reaches T3 | AS-IS: the item arrives as T3's row; the design adds NO `A_LOOK` arm in the switch beside the kind-row dispatch (that would be a second dispatch of one kind, the sar1mrg finding of 2026-11-10) | Act through the row |
| 3 | `RbRuns` (req.c:174) and its builders: `rr_unit` :535, `rr_none` :546, `rr_pos` :556, `rr_cat` :591, `rr_alt` :664 (`RbRuns o;` filled by whichever row applies), `rr_alt_union` :625 / `rr_alt_affix` :642, `rr_pow` :755, `rr_rep_exact` :767, `rr_rep_split` :783 (copies ONE field, `o.tail = rr_cat(w, gap, p).tail`, :788), `rb_rep_unit_val` :889 (`*v = *b`, a whole-value copy), `rb_rep_best_val` :921 (copies ONE field, `v->runs.best = b->runs.best`, :925), `rb_rep_gap_val` :940, `rb_gap_into`/`rb_assert_into`/`rb_zero_unit_into`/`rb_init` | C2, C39 | covers consumed runs only (`best`, `head`, `tail`, `all`, `maxw`); at T EVERY builder writes all five fields, field by field (`rr_unit`, `rr_pos`, `rr_cat` with `RbRuns r;`/`o;` then field writes) | WIDEN (pending guards `lg`/`rg`, the dead bit, IF D-2 places them in `RbRuns`): a field added later is silently missed by every field-by-field builder; the two one-field copies (:788, :925) need the feature's OWN added writes (the right guard from the same decomposition as the tail; the best's guards), not rows; unit RM-1 [r50 A12, A18] | rule "A shape states the inputs it covers" |
| 4 | `rr_cat` (req.c:591) | C3 | joins `l.tail` with `r.head`; `rn_better` over bests, join, head, tail | AS-IS for the consumed join; the guard steps (CAT-R/L/SET/EDGE) are a NEW declared table (T4) called from it, in the file's own row idiom (`RB_ROW_SCAN` with a restore-arm column, three tables already: `rr_alt_rows`, `rb_rep_rows`, `rb_zero_rows`) | Decisions are declared tables; Notice siblings |
| 5 | `rr_alt_rows[]`/`rr_alt_affix` (req.c:616-671) | C4 | common head/tail by `rn_common_head`/`rn_common_tail` | SHARED: the ALT guard rule is the SAME common-head/tail primitive over `lg`/`rg`; no second spelling of the union | One question, one primitive |
| 6 | `rb_rep_rows[]` (T2, req.c:986-1020) | C5 | rows 1-3 built (E1, R1); copies through `rr_pow` → `rr_cat` | AS-IS: guards travel through `rr_cat` per copy; the `m = 0` unit (`rb_init`) and the gap/best forms (`rr_none`) carry none, given RM-1 | — |
| 7 | `rn_choice_rows`/`rn_better` (the run choice, req.c:407-494), its estimate `rn_scan_mass` (req.c:417-423, whose comment says it is "the same estimate the `req_byte` pick reads"), and TOP | C6, C18 | the walk's answer is `v->runs.best` (req.c:1247); no stage after the walk | ROW for the ranking (TOP's candidates `tail ++ rg`, `lg ++ head` enter `rn_better` as runs); TOP itself is a NEW stage at the one walk exit, reading walk parameters. Whether `rn_scan_mass` ranks over every run position or over the consumed extent is a DESIGN question (D-4, D-6) [r50 A10] | Decisions are declared tables |
| 8 | `pcrec_req_walk` + `ReqWalkParams` (facts_derive.h:119-140), filled once by `pf_derive_req_walk` (facts.c:225-233) | C6 | four rows: `pos_set`, `max_pieces`, `restored`, `rate`; the struct's comment already names "L1's reach, L3's `lb_bytes`" | ROW for `lb_bytes` (a policy value). For `reach`: span_arms.md's walk-parameter table gives it ONE run-time variation, the `look` arm ("harness arm `look` → `[0, maxoff]`"; §5.8 "forces reach `[0, maxoff]`, so L2 and L3 have no separate lever"; C40), which is what `RB_ROW_SCAN`'s arm column already expresses; a `reach` parameter beside the `look` arm would be a second spelling of "is the look form restored". The table-idiom form (TOP's AHEAD/BACK candidates as rows with `arm = LOOK`) or a parameter: the design's choice, D-4 [r50 A15] | Decisions are declared tables; One table per slot |
| 9 | `walk_arms.def` | C7 | arms `empty`, `zero`, `rep`, `tie`, `alt` | ROW (a `look` arm restoring E-5's plain unit, span_arms §5.8) | — |
| 10 | `RbRun` (facts_derive.h:105-114) and `ReqRun` (facts.h:68-77); writers of `ReqRun`: the deny reset `case PF_REQ_WHOLE_RUN` (facts.c:97-100, `memset` of `pos` plus two field writes) and the derivation (facts.c:253-262, the same three writes then two); readers in facts.c also at :354-355 (K), :835-836 (listing printer), :891 (run_pin printer), :925-926 (the `RX_REQ_RUN` stamp text) | C8, C10 | a run at offsets `[0, whole_maxoff]` from the attempt start, every position consumed | WIDEN (`omin` signed, the consumed extent); both `ReqRun` writers write FIELD BY FIELD, so a new field is silently missed by the reset (the generic-writer hazard): unit RM-1, widened to every record builder in the run path [r50 A11]; `RbRun` is also the type of every head/tail/best, so a field on it makes every `rn_*` constructor a writer (D-5) | A shape states the inputs it covers |
| 11 | `facts.def` rows `REQ_WHOLE_RUN` :54, `REQ_LANDMARK_MAXOFF` :57; printers facts.c:835-870 | C11 | one row per offset fact | ROW (`req_run_omin`, span_arms §9) | Decisions are declared tables |
| 12 | the landmark K, its −1 "none" sentinel, and the bound tests of K and of the whole-run K. Sentinel writers and printer: facts.c:106 (reset), :355 (`: -1`), emit_dfa.c:9174 (`head < 0 ? -1`), printer facts.c:868 (`< 0` → `none`). TEN hand tests: emit_dfa.c:1099 (entry, `k >= PCREC_W_UNBOUNDED`), :1644 (`head_max` = `MF_HEAD_MAX_UNBOUNDED`), :7926 (re-entry, no move), :7961 (`pcrec_emit_req_attempt_reentry`), :8990 (`k < 0 \|\| k >= PCREC_W_UNBOUNDED`), :9085 (`k >= 0 && k < PCREC_W_UNBOUNDED`, the WHOLE-RUN K, see below), :9113 (`whole_maxoff >= PCREC_W_UNBOUNDED`), :9360 (stamp), facts.c:356 (why `unbounded`), :869 (printer). K's VALUE readers: `req_handoff_k` at emit_dfa.c:1087, :1640, :1644, :7901 (printed into an emitted comment), :7922, :7959, :9360, :9361; `req_landmark_k` at :8989, :9317, :11552 (trace) | C12, C33 | K is `{-1 none} ∪ [0, W_UNBOUNDED) ∪ {unbounded}`, sentinel-encoded, from TWO sources with two none-encodings: `req_handoff_k` returns `whole_maxoff` (none = `whole_len < 2`) on the whole-run branch and `req_landmark_k` (−1) otherwise. The start table ALREADY decides bounded vs unbounded by ROWS (`handoff-attempts-entry` :10725 / `handoff-attempts-unbounded` :10734), while both move emitters re-test it by hand (:1099, :7926, :7961) and carry `k > 0` chains (:1115, :1125, :7933) | WIDEN + SHARED: L3's K is of either sign (span_arms §5.4 A3), so the −1 sentinel collides, and a negative K would add an arm to the emitters' hand chain; unit RM-2. :9085 is the whole-run K; its `k >= 0` conjunct is L3's (span_arms A8), not RM-2's. K is one member of an OFFSET-BOUND family (general form section) [r50 A7] | A shape states the inputs it covers; One question, one primitive; Act through the row |
| 13 | `req_handoff_k`/`req_landmark_k` (emit_dfa.c:9154-9176) | C12 | the one spelling of K for every reader | AS-IS (already the one spelling; reads RM-2's value) | — |
| 14 | `cand_rows[]` row `handoff-attempts-entry` (emit_dfa.c:10725), predicate `req_handoff_entry_applies` (:9082-9086) | C13 | declines `whole_maxoff < 0` (vacuous at T: `whole_maxoff` is 0 or `run.off`) | ROW (span_arms A8, ADMITTED: the conjunct is deleted at L3, the row runs the signed move) | Decisions are declared tables |
| 15 | the landmark MOVE, two emitted copies: `emit_req_handoff_rest` (emit_dfa.c:1083-1134) and `emit_req_landmark_move` (:7909-7945), each then `pcrec_emit_start_zero(..., PCREC_START0_ROUNDUP)` | C14 | both assume the hit `c >= pos` (comment :1074: "THE SUBTRACTION CANNOT UNDERFLOW: `c >= posvar` always"; the re-entry's re-ask block makes it true there); L3 breaks that premise at both (span_arms A3: W-L10..W-L14). The copies differ in five ways plus one block (D-8's list) | SHARED for the ARITHMETIC only: one question ("the first position no skipped attempt could begin before, given hit `c` and K") spelled twice; unit RM-3. The two `ROUNDUP` calls stay in their callers: TWO A-POSDOM site rows as ruled (span_arms §8.1; D191.3) [r50 A6] | One question, one primitive |
| 16 | the kit presence seam: `req_pres_spans` (emit_dfa.c:1448-1482; `pcrec_memfn_wspan(sp, 0, run->whole_len, ...)` at :1469, `p[i].omin = 0` at :1479 for EVERY span, the run's included), `req_site_define`'s `s->head_max` (:1640-1644, `int64_t` since K38-2; `MF_HEAD_MAX_UNBOUNDED` at :1644 since R-41); the soundness comment :1543-1546 ("the presence facts hold no lookbehind byte") | C15, C16 | the kit ACCEPTS a negative `omin` on the run span, a signed `head_max`, and an unbounded K by name (memfn.h MF_SITE_ABI 29); pcrec states 0 for `omin` | WIDEN: the run span's start and `omin` writes (:1469, :1479) start stating the fact (members stay 0, which the kit requires); `head_max`'s writer maps RM-2's "unbounded" state onto `MF_HEAD_MAX_UNBOUNDED` at its one writer (:1644); the comment's premise is restated at L3 [r50 A1, A14] | Across the kit boundary, send facts |
| 17 | `pcrec_landmark_margin`/`req_landmark_admits` (emit_dfa.c:9277-9294), and the other K readers `req_handoff_applies` :8981, `req_landmark_hit_ppm` :9197, `pf_handoff_applies` :9309, `req_handoff_stamp` :9355; the margin's other caller `lmwalk.c:248` (passes a non-negative measured K) | C17, C41 | the margin already reads `max(K, 0)` (`k > 0 ? k : 0`, :9293; K38-2) | AS-IS (span_arms A3's READY3-2 fix is DISCHARGED at T: finding F-3); each reader reads K through `req_handoff_k`/`req_landmark_k` (site 13) [r50 A14, SITEMAP-6] | — |
| 18 | `pcrec_req_pick` (req.c:1278-1289, `req_byte`) and the trace shadow `req_set_leads_own` (emit_dfa.c:11335-11349, inside `#ifdef PCREC_CAND_TRACE`): the same expression `pcrec_find_run_scan_index(rate, run->pos, run->whole_len)` at req.c:1284 and emit_dfa.c:11345. The shadow is the EXPECTATION of the KIT's P4 (memfn/src/presence.c's set-leads, a scan member over the WHOLE run), compared by `tests/memfn/run_pres_picks.sh` (a `-DPCREC_CAND_TRACE` build) | C18, C42 | pcrec's own scan member over EVERY run position | SHARED: one primitive answers the question `req_byte` answers ("the byte every match consumes that pcrec picks"), unit RM-4. Under L2/L3 `req_byte` must stay a CONSUMED byte (D191.2): `pcrec_req_pick` reads the consumed extent. The shadow follows the kit's P4, which D191.2 lets scan ANY run position, so restricting it would diverge from P4 exactly where L2 moves; its fate (keep the whole-run reading, or retire with D191.2's "the pcrec/kit agreement check retires") is D-6 [r50 A2] | One question, one primitive |
| 19 | the run pin: `pcrec_run_pin` (kset.c:302-339) and its gen readers in emit_dfa.c, `walk_proves` :6872, `pf_window_of` :6880, `us_run_pin` :7428, `pf_run_applies_common` :7438, `ofs_test_of` :7469, `ofs_test_verifies_run` :7582 (span_arms A5 names them) | C18, C34 | picks over the whole run's exact positions and pins the maximal exact stretch; the gen readers align run position `i` with consumed offset `w + i` | ACCESSOR: the pin and its readers read the consumed extent (span_arms A5: "`pcrec_run_pin` reads `cons`"), through the accessor that lands with the unit that gives it a value (RM-4, A18) [r50 A14, A18] | accessors |
| 20 | `Ctx.lb_max` (internal.h:4115): one writer accessor `pcrec_lb_raise` (:4467-4470), one direct reader emit_dfa.c:3643-3644 (`_VALID_LB`) | C19 | the parse-time running max of lookbehind widths, characters | ACCESSOR: L3's `lb_bytes` walk parameter adds a SECOND cross-file reader (facts.c); register row 6a rides. D189's revisit trigger ([VLOOKBEHIND] stage 2, build go 2026-11-10, ordered before this feature in S4) touches this site: whether stage 2 moves what `lb_max` holds is SUSPECTED, D-11 [r50 A9 e] | A structure is read and written through its owner's accessors |
| 21 | the NEVER FAMILY ("this run or pattern can never match"): `never_matches` (`PfNever`, facts.h:285; derived kset.c:537-548 from `pcrec_dfa_accepts_nowhere`; read compile.c:3303, :3332 to emit the empty artifact); derive.c's PRUNE (derive.c header: "a `CAT` with a never item is never; an `ALT` drops never arms; ... a positive `LOOK` of never is never, a negative one EMPTY", the never leaf the empty class `never_node` :146); mrl.c's `PCREC_MINW_MAX` ("`minw == PCREC_MINW_MAX` MEANS THE CALLEE MATCHES NOTHING", read by the `ceiling` start row, emit_dfa.c:10403); the `empty` LOCATE row (`locate_empty_applies`, emit_dfa.c:4864, row :10549) | C20, C35 | three built propagations/tests of one fact, at the AST (derive.c), the minimum-width pass (mrl.c) and the final machine (`PfNever`, `empty`) | SHARED, by the MANAGER'S r50 A8 RULING (which revises his own READY-5 form of span_arms review r3, cited as such): the FACT "this run can never match" (span_arms §5.2's DEAD, `foo(?=bar)baz`) has ONE home, the never family: one propagation, taken from a primitive shared with derive.c's prune (the design names it), or a PROPOSED register row (P6) carries the merge with [DESC-DEAD]/[NEVER-MATCH] as its event. READY-5's caller-visible LISTING consequences are KEPT: the why listing on `req_whole_run` RENDERS that fact (a rendering of the one fact, never a second fact). Binding checks for the design, from READY-5: `dead` > `harness:` > the existing reasons, one why per run, no second field; `dead` on `req_whole_run` only; a dead `req_whole_run` is `derived`; `pf_done_why` takes `dead` and `harness:` out of its `decl` list; `run_facts_checks.sh`'s status/why pairs gain the two; `dead` is not `decline:dead-start` [r50 A8] | One question, one primitive; Notice siblings |
| 22 | D168's context producer: its built home, the span slice (`span_facts`, `pcrec_span_walk` in kset.c), is DELETED (C19: 0 hits); the cover's per-offset context at −1 and `k` is now `known.c`'s anchored-machine walk (`MkEnd.ctx_before`/`ctx_after`, known.h:24-25); kset's frontier still passes `N_CTX` (kset.c:141). Readers named by the record: D172's window site ("Fixed lookbehinds and post-span lookaheads longer than 1 ... sourced from main's D168 producer"); [CTX-FACTS-NEG] plans a MACHINE-level producer of the same per-offset sets, triggered by this feature | C19, C21 | no AST-level producer of a positive context node's per-offset sets exists | NEW-SEAM: the ITEM, writer in `src/facts/desc.c` under form (a), called by the run walk (reader 1, L1); later readers D172's window site, [LOOK-LOCATE], [CTX-SIDES-PRODUCER], [DD-11.5] part 1 (re-scoped). Whether [CTX-FACTS-NEG] is re-scoped to READ the item (one producer) or builds its machine producer (two producers by layer, with the contingent noted-deviation row below) is `REQ-OPEN context-producer-home` [r50 A4] | One home per question |
| 23 | the description module (`desc.h`: `pcrec_pd_unit/zero/none/pos/cat/alt/pow`; the adjacency head `PdHead`/`pcrec_ph_*`, "the module's second column": "the positions every match consumes FIRST, at offsets 0..h-1"); the module is alphabet-generic ("The alphabet is a PARAMETER (`PdAlpha`)") with two callers (req.c byte level, altnf.c code-point level); the head's repeat wall "waits for [REPEAT-RUN]" (altnf.c:183-184), whose R1 is in the code at T (req.c:732, :993) | C22, C43 | width groups of exact position sets, keeping the LAST positions; a head column keeping the FIRST | A lookahead's item at offsets `0..` is the question `PdHead` answers; a lookbehind's is the description's suffix. TWO FORMS (the design decides, ruled A17): (a) SHARED: the item reads the head column for AHEAD and the description's suffix for BEHIND (the run walk gains the head column over the byte alphabet); (b) a third operation family in desc.c with a NOTED DEVIATION row whose correcting event is L1 or L2. LEANING: (a), because the two reasons for keeping two at rev 1 (different layers, different walls) are a parameter the module already takes and a wall whose trigger has fired; under form (a) the item is built in the description's own area (the owner's words permit that: such functionality "can be built in the AST area"; the home is D-10's) [r50 A17, A9 b] | One question, one primitive, from the second caller |
| 24 | `ctxnode.c` (`pcrec_look_t3`'s `ctx-node` row: a one-character lookaround becomes `A_CTX`, ctxnode.c:96-97) | C23 | two lowerings of one construct | AS-IS: both reach T3's one predicate (`rb_zero_look_pos`, req.c:1059-1063); the ITEM row must read both, so the run is the same under `-fno-ctx-node` (span_arms §5.1) | Build the general form |
| 25 | `pcrec_emit_start_zero` calls after the moves (emit_dfa.c:1112, :7930) | C14 | `PCREC_START0_ROUNDUP` | AS-IS by ruling: no new call, no new mode, the two calls stay in their callers (span_arms §8.1: "L3 adds no mode and no call site"; D191.3) | — |
| 26 | VM route: `emit_vm.c` reads the moves only through the exported emitters (`pcrec_emit_req_attempt_reentry`, `pcrec_emit_req_byte_check`) | C24 | — | AS-IS (no VM file changes; the VM text moves with sites 14-15) | Layering at the call level |
| 27 | `Job.req_handoff_vm`, written by emitters inside the touched functions (emit_dfa.c:1098 in `emit_req_handoff_rest`, :7896 in `pf_emit_handoff`) | C25 | an emitter-to-driver flag (register row 6c, a noted deviation) | AS-IS for this feature (the write is not changed; see register lookup) | A stage-to-stage field names its writer |
| 28 | the contract: `match_api.md` §6.3.7¶6, ¶10, ¶11; `tuning.md` §2.28¶1, §2.41¶1, ¶8b; `facts_listing.md` §4.1.2¶8, ¶8b, §4.1.3; `findings.md` §4 | C26 | E2 already owns the attempt wording of §6.3.7¶6 and §2.28¶1 (span_arms §12d) | AS-IS (spec hunks, D80; the list is re-derived at design time: D-13) | D80 |

Commands for this table: C1-C26, C33-C43 (section "Commands"); hit counts there.

## Register rows looked up

Searched: `git show $T:docs/dev/guide/architecture.md | sed -n '609,633p' | grep -n -F <term>`
for each term `REQ-LOOKAROUND req.c rr_cat desc.c facts.c kset.c emit_dfa emit_vm CandRow
LOOK-LOCATE A-REV A-POSDOM VLOOKBEHIND mod_lookaround lmwalk mrl.c derive.c cand_rows handoff
landmark Job memfn ctxnode ctxfn ENGM_` (C27). Matches: rows 1, 2, 4, 6a, 6b, 6c, 7a, 7b, 9, 10, 12,
13, 14, 16; row 19 by its event ("the next new declared table"); rows 5 and 15 by their subjects.

| register row | why it matches | disposition |
|---|---|---|
| 14 Alternation folds to one owner, stage 3 | `req.c` `rr_cat`; [REQ-LOOKAROUND] named: "edits the same pass, so serialise" | NOT CARRIED, done: stage 3 + Part D LANDED 2026-11-14 (merge 9cecc3caa; [RUN-POS-SET] status at T, `scripts/entry RUN-POS-SET -l 1`: "waits: nothing in flight"), so the serialisation is discharged for stage 3; [RUN-POS-SET]'s stage 3m, still to follow, edits the same alternation fold the ALT guard rule edits. The row's status still reads "riding [RUN-POS-SET]" (finding F-4). Its own cite "`rr_cat` (`case A_LOOK` :1204)" is `rb_walk_at`'s case, not `rr_cat`'s (C1) |
| 6a Name each Job/Ctx field's writer and readers; a cross-file reader gets an accessor | site 20: L3 adds a cross-file reader of `Ctx.lb_max` | RIDES FIRST, narrowed to the one field (unit RM-5); status "riding [REQ-LOOKAROUND]" for `lb_max` only |
| 6c NOTED DEVIATION: emitters write facts the driver reads (`req_handoff_vm`) | site 27: `emit_req_handoff_rest` and its sibling are touched by RM-3/L3 | NOT CARRIED, with the reason the HOW TO USE IT asks for: the feature changes the move arithmetic, not the flag; the correction is L-sized with its own named event ([VMREC], roadmap H-FLAGS) and an abi/spec event for the caps; RM-3 must keep the write (emit_dfa.c:1098, anchored by S1711) where it is |
| 6b Stage outputs as typed records | `Job` | NOT CARRIED: "as roadmap areas migrate, never standalone"; no area migrates here |
| 4 Measure library below parse | [VLOOKBEHIND], `mod_lookaround.c` widths | NOT CARRIED: the feature adds no width walk; the item's offsets come from the description's own width groups and `RbRuns.maxw`, and `lb_bytes` reads `lb_max` (site 20) |
| 1 Start-table rows carry their recover/finish action | [LOOK-LOCATE]; `emit_dfa.c` | NOT CARRIED: no new recover or finish act (K's value moves, the acts do not). Its event is [LOOK-LOCATE] or [EARNED-SKIP] (a finish act), both unlocks below. The question "act through the chosen row's K state, or re-test it" is handed to the design (D-7, D-8) |
| 2 Engine identity asked one way | `emit_dfa.c`; its WHERE ("`fit.chosen == ENGM_*`") is touched at emit_dfa.c:8993 inside `req_handoff_applies`, the RM-2 site (`k < 0 \|\| ...` at :8990), and `pf_emit_handoff`'s `cand_finish_of(cx) == CAND_ROUTE_VM` (:7896) beside RM-3's site (C44) | NOT CARRIED: no new engine-identity test; both tests stay untouched [r50 A14] |
| 10 Shape widened for signed start offsets (`struct CandRow`) | [LOOK-LOCATE]; "trigger: span_arms unit L3 landed plus a bench cell" | NOT CARRIED: `CandRow` holds no offset K reads (emit_dfa.c:5752-5794, C28); L3 is half of the row's trigger. Note for that row: the kit's WINDOW spans start no lower than `-MF_MAX_BACK` = −8 (memfn.h:296), the presence `omin` has no bound, so a lookbehind locate wider than 8 bytes also needs the KIT's shape widened |
| 7a Decisions listed from the Job, not parsed from `#define`s | event "the next change to the facts listing or a new decision stamp": L1 and L3 change the `facts` section | NOT CARRIED: the changed rows are printed from the record (`facts.c`), not parsed by `fd_decisions`; no decision stamp is ADDED (`RX_REQ_RUN`/`RX_REQ_HANDOFF` change value only). The trigger's wording is wider than the row's shape (finding F-5) |
| 7b The artifact as typed parts | `memfn` | NOT CARRIED: no post-render rewrite |
| 9 Split the artifact emitter | `emit_dfa.c` | NOT CARRIED: "a standalone move is churn" |
| 12 Stream roadmap areas | A-POSDOM (sites 15, 25), A-REV (lookbehind hand-off), A-FACTS (`\K` report shift), A-PLAN | A-POSDOM: NOT CARRIED by the owner's ruling (D191.3, span_arms §12b: "L3 before the start-position clean-up, sites in its table shape: AGREED"); RM-3 merges the arithmetic only and keeps both sites' `ROUNDUP` calls with no new mode, so A-POSDOM's table keeps its TWO rows (span_arms §8.1) and R08/R09 do not grow. A-REV: no rows moved (ownership ruling 1: vlookbehind.md owns lookbehind admission; the item reads the BODY's description, the hoist the BRANCHES'). A-FACTS: the run is attempt-relative (span_arms §2), no report-shift reader added. A-PLAN: untouched |
| 13 VM body record-first | `emit_vm.c` | NOT CARRIED: no `emit_vm.c` change (site 26) |
| 16 A_BOL/A_EOL into A_CTX | `ctxfn.def` | NOT CARRIED: no new `A_CTX` row; the feature reads two existing functions |
| 19 One first-row walker for every table type | event "the next new declared table": T4 and TOP are new tables | NOT CARRIED: they use req.c's existing `RB_ROW_SCAN` (req.c:393) and add no walker; the row's WHERE omits `RB_ROW_SCAN`, a macro with an arm column and a fourth member (finding F-6; whether row 19 absorbs it is the manager's call) |
| 5 Kind defaults as a kindrow.def column | `rb_row_into` reads the kind row's TEXT | NOT CARRIED: no new kind |
| 15 Internal deny word | bit 31's text re-specified at L3 | NOT CARRIED: no bit added or demoted |

D-row "Revisit when" triggers on mapped sites (`scripts/entry -g` was not usable for D-rows,
`scripts/entry D168` prints "profile decisions dormant": C29; read in `decisions.md` at T):
D168 ("a consumer needs a context fact that is not a per-offset set"): NOT MET, every reader here
reads per-offset sets. D161 ("a window search needs ... an unbounded move-back"): NOT MET, L3's
move-back is capped by `lb_bytes`. D189 ("**Revisit-when:** stage 2 (backreferences in a lookbehind)
or the 255 cap's setting at [IFACE-PUSH]"): stage 2 has a build go (2026-11-10) and D194's set S4
orders it BEFORE this feature; it names the lookbehind width bound site 20's `lb_max` carries:
MET as a mapped-site trigger, relevance SUSPECTED, handed to D-11 [r50 A9 e]. D62 ("a fifth AST
analysis lands"): NOT a live trigger here; D70 names D62's discipline ("D62's discipline ...
carries over unchanged") but records no firing, and the D62 addendum ("Ruling superseded:
"multiline-`$` is a parse-resolved FLAG on the node" no longer holds") is the reason the
trigger is moot [r50 A9 f]. None other.

PROPOSED ROWS (register columns; status "riding [REQ-LOOKAROUND]" until landed). ENTERED at landing, 2026-11-18, as register rows: P1 = 23, P2 = 24, P3 = 25, P4 = 26, P5 = 27 (P1 here is not the dense-hit note's P1, which is row 21); P6 NOT entered (conditional on D-9; left for the manager):

| # | remodel | shape (rule) | where (verified by command) | event that carries it | size, gate | deletes | status |
|---|---|---|---|---|---|---|---|
| P1 | Every record builder in the run path starts from a stated value | A shape states the inputs it covers (its generic writers) | `RbRuns` builders: `rr_unit` req.c:535, `rr_pos` :556, `rr_cat` :591, `rr_alt` :664, `rr_alt_union`/`rr_alt_affix` :625/:642 (C2, C39); `ReqRun` writers: facts.c:97-100, :253-262 (C10) | [REQ-LOOKAROUND] L1 (unit RM-1; its `RbRuns` half conditional on D-2) | S, no-mover | each builder's implicit "every field is written below" contract (no defect at T: every builder writes all of today's fields) [r50 A11, A12] | riding |
| P2 | One "stated, bounded, value" for the offset-bound family, K first | A shape states the inputs it covers; One question, one primitive; Act through the row | the family (C12, C45): `RbSet.off[]` (`RB_OFF_UNBOUNDED`, facts_derive.h:81, saturated req.c:218, translated facts.c:249), `ReqSet.maxoff[]` (printer facts.c:825), `RbRun.off`, `ReqRun.whole_maxoff` (none = `whole_len < 2`; tests emit_dfa.c:9085, :9113), K (`req_landmark_maxoff`: sentinel sites facts.c:106, :355, :868, emit_dfa.c:9174; tests :1099, :1644, :7926, :7961, :8990, :9360, facts.c:356, :869) | [REQ-LOOKAROUND] L3 (unit RM-2 for K; the rest of the family at its own next touch, or with K if D-7 chooses the run's signed interval) | S, no-mover | the −1 sentinel, the hand tests RM-2 routes through one predicate | riding |
| P3 | One emitter of the landmark move ARITHMETIC | One question, one primitive | emit_dfa.c:1115-1131, :7928-7938 (C14) | [REQ-LOOKAROUND] L3 (unit RM-3); A-POSDOM keeps two site rows | S, no-mover (byte identity) | one copy of the move arithmetic | riding |
| P4 | The scan member `req_byte` answers, asked once | One question, one primitive | req.c:1284, emit_dfa.c:11345 (C18) | [REQ-LOOKAROUND] L2 or L3, whichever lands first (unit RM-4); the consumed-extent accessor with the unit that gives it a value | S, no-mover | one copy of the pick expression | riding |
| P5 | One per-offset-head primitive for the description and the item | One question, one primitive, from the second caller | `pcrec_ph_*` (desc.h, altnf.c) beside L1's item (C22, C43) | L1 (the item's AHEAD half) or L2 (the first AHEAD reader); the design chooses between this row and the noted deviation of form (b), site 23 [r50 A17] | S-M, no-mover | a second per-offset union | open |
| P6 | The never fact: one propagation for derive.c's prune and the run walk's DEAD, one home in the never family | One question, one primitive; Notice siblings | derive.c header and `never_node` :146 (C35); `PfNever` (facts.h:285, kset.c:537-548); mrl.c `PCREC_MINW_MAX` read at emit_dfa.c:10403; `locate_empty_applies` emit_dfa.c:4864 | [DESC-DEAD] or [NEVER-MATCH] (the latter's trigger names L1's landing); applies only if the design does not take the DEAD propagation from a primitive shared with derive.c's prune at L1 (D-9) [r50 A8] | S-M; L1's DEAD column itself moves no byte (D-9) | a third propagation of "never" | open (conditional) |

NOTED DEVIATIONS on touched sites: row 6c only (above, not carried).

PROPOSED noted deviations (contingent; each lands in the register only if its condition holds). ENTERED at landing, 2026-11-18, marked CONTINGENT: ND-1 = register row 28, ND-2 = register row 29:
- **ND-1 two producers of the per-offset context sets, by layer** (contingent on the owner ruling
  **context-producer-home** "by layer", i.e. [CTX-FACTS-NEG] builds its machine producer for fixed
  lookbehinds at negative offsets while L1's item produces the same sets at AST level) [r50 A4].
  What: a second producer of D168's per-offset sets. Against: high-level rule 1 (one home per
  question; D168 "ONE producer"); rule "One question, one primitive". Where: `src/facts/desc.c` (the
  item, L1) and the anchored-DFA producer [CTX-FACTS-NEG] would build beside `src/gen/known.c`'s
  walk (C21). Why small: none as filed; the deviation is NOT SMALL by the judgement section's (e)
  ("a second permanent mechanism" is NOT COVERED) unless the machine producer reads only what the
  item cannot state (`\b`, thread context), in which case the two answer different questions and no
  row is needed. Correcting event: [CTX-FACTS-NEG] re-scoped to read the item for the sets the item
  states. This is why the leaning below is the one-producer form.
- **ND-2 the item as a third family in desc.c** (contingent on the design choosing form (b) at site
  23). Against: rule "One question, one primitive, from the second caller". Where: `src/facts/desc.c`.
  Why small: one file, no new reader of another unit's structure, no seam. Correcting event: L1's
  landing or L2 (the first AHEAD reader) [r50 A17].

## Remodels that land first

Each is an answer-identical unit; none needs the feature to land; each deletes something. Each
gate line names the STREAMS its identity covers: the four byte-identity gates compare the `.c`
artifact only (coding.md, C46: "The four byte-identity gates compare the `.c` artifact ... Touch a
listing-writing buffer and you owe that arm explicitly"), so a unit that touches the facts layer
also owes the facts-listing comparison, and a unit that touches `#ifdef PCREC_CAND_TRACE` code
owes the trace build [r50 A13]. The binding checks are the anchor map's lists (C37), not an
identifier grep; each anchor is re-aimed with the move and shown RED under its plant
([MECH-REACH]). Order with the feature: each unit's CENSUS runs first, then its remodel commits,
then the feature (owner question **remodel-go**; D191.1: "a unit whose census finds NO mover
anywhere stops and reports") [r50 A5].

**RM-1 (P1) every record builder in the run path states every field** (before L1; the `RbRuns`
half is the remodel ONLY if D-2 places the guards in `RbRuns`; if D-2 chooses `RbVal`, the
generic writers are a different list (`rb_init`, `rb_cat_into`/`rb_alt_into`/`rb_gap_into`,
`rb_assert_into`, `rb_zero_unit_into`, the `rb_rep_*_val` builders, `*v = *b`) and the unit is
re-scoped to them); the `ReqRun` half is conditional on D-5 (whether the new fields are declared part
of facts.h's interface) [r50 A18].
- What changes shape: `rr_unit`, `rr_pos`, `rr_cat` and `rr_alt` start from a stated value (a
  designated initialiser or `rr_unit()`), and each `rr_alt_rows` row writes a complete value, so a
  field added later is either written or defaulted to its stated empty value; the two `ReqRun`
  writers (facts.c:97-100, :253-262) start from one stated empty `ReqRun` [r50 A11, A12]. NOT
  rows of RM-1: the one-field copies `rr_rep_split` (:788) and `rb_rep_best_val` (:925): the
  FEATURE adds its writes there (the right guard beside `tail`; the best's guards beside `best`).
  The kind-blind copy `*v = *b` (`rb_rep_unit_val`, req.c:892) is safe by construction: it copies
  a body's whole value, guards included, which is T2 row 1's rule.
- Gate: no-mover. Streams: the `.c` byte-identity gate AND the facts listing (`--emit-facts`
  over the corpus, before vs after; the design names the tool) [r50 A13].
- Size: S. Checks that bind the moved code (the anchor map, RM1 ranges req.c:530-800, :880-950;
  C37): S268, S446, S466, S807, S1910, S1915, S1916, S1917, S1918, S1919, S1923, S3129, S3130,
  S3131, S3132 (15); plus `tests/litscan/spanarms.rxt`. The facts.c `ReqRun` writers' anchors are
  found the same way at the design's base.
- Generic writers guarded: the list in site 3 and site 10.
- Separable: yes, it changes no value any builder returns today.
- Deletes: each builder's implicit "every field is written below" contract (no defect at T) [r50 A12].

**RM-2 (P2) K stated or none** (before L3; L1 and L2 produce no negative K; inside L3's go'd text:
span_arms L3 "K carries a stated/none bit, the −1 sentinel retired at every §9 site").
- What changes shape: the landmark offset carries its state (none / bounded / unbounded) beside a
  signed value; one predicate answers "stated and bounded" for the hand tests of K's own state
  (emit_dfa.c:8990, :9360, facts.c:356, :869, and the unbounded tests the move emitters and the
  `head_max` writer make, :1099, :1644, :7926, :7961); `req_landmark_k`'s `-1` (:9174) and the
  derivation's `: -1` (facts.c:355) state "none"; the "unbounded" state maps onto the kit's
  `MF_HEAD_MAX_UNBOUNDED` at its one writer (:1644) [r50 A1, A7]. Whether the emitters act through
  the chosen start row's K state (`handoff-attempts-entry` vs `-unbounded` already decide it) or
  re-test it, and whether K alone or the run's signed interval `[omin, maxoff]` carries the state,
  are D-7 and D-8. NOT in RM-2: :9085 (the whole-run K, none = `whole_len < 2`; its `k >= 0`
  conjunct is L3's, span_arms A8) and :9113 [r50 A7].
- Gate: no-mover. Streams: the `.c` gate AND the facts listing (the listing prints `none` as today,
  facts.c:868; the design names the tool) [r50 A13].
- Size: S. Binding checks (the anchor map, RM2e ranges and the K tests, C37): S467 (:8990),
  S476 (:8992), S529 (:8991), S1706 (:9085, stays with L3), S1957 (:9360), S1956 (:9113, stays with L3 like S1706), S811
  (:9293), S1707 (:9313), S1712 (:9315); plus S463 (`handoff_k_minus_one`) and S809 from RM-3's
  list where the bodies overlap; facts.c ranges: no anchor at T.
- Separable: yes, every STATED K is non-negative today (none is -1).
- Deletes: the −1 sentinel (four sites: facts.c:106, :355, :868, emit_dfa.c:9174) and the hand
  re-statements of K's state the predicate replaces.

**RM-3 (P3) one emitter of the landmark move ARITHMETIC** (before L3; manager's r50 A6 ruling, the
recommended form).
- What changes shape: the arithmetic of `emit_req_handoff_rest`'s moving block and
  `emit_req_landmark_move`'s (`target := max(pos, hit − K)`) becomes ONE emitter, parameterised
  by its variables; the two `pcrec_emit_start_zero(..., PCREC_START0_ROUNDUP)` calls STAY in their
  callers (two A-POSDOM site rows, span_arms §8.1 / D191.3). The "cannot underflow" premise
  (`c >= posvar` always) is TRUE at RM-3 and MOVES into the one emitter's comment; L3 deletes it
  when it makes K signed. The `req_handoff_vm` write (row 6c, :1098) stays in its caller. The full
  list of differences between the two copies (each a byte-identity trap) goes to D-8 [r50 A6].
- Gate: no-mover. Streams: the `.c` byte-identity gate (both sites print the same text as today).
- Size: S. Binding checks (the anchor map, RM3 ranges emit_dfa.c:1083-1134, :7909-7945, C37; S74
  is a false hit on a generic `return;`): S463 (:1087), S3075 (:1087), S1711 (:1098), S1955 (:1108),
  S471 (:1112), S470 (:1123), S809 (:7934), S813 (:7937), S814 (:7937), S1701 (:7937); and the rest
  of C31's move/K files. S471 (entry), S814 (forward re-entry) and S1701 (VM attempt re-entry) are
  three plants of ONE round-up act at three callers: they stay per caller because the calls stay
  in the callers; S470/S809 split the clamp by caller and now plant ONE emitter. The per-caller
  plant shape for the merged arithmetic (keyed on the emitter's caller parameter, or a stated
  loss of per-caller detection) is handed to the design (D-8) [r50 A6].
- Separable: yes.
- Deletes: one of two copies of the move arithmetic.

**RM-4 (P4) the scan member `req_byte` answers, asked once** (before L2 or L3, whichever lands
first; the consumed-extent ACCESSOR (not part of RM-4, below) is inside L3's go'd text: span_arms L3 "`cons` and the kit-member
read (A13, A5) ... built by whichever lands first") [r50 A2, A5, A18].
- What changes shape: one facts-layer primitive answers the question `req_byte` answers ("the
  run position pcrec picks for the byte every match consumes", today `pcrec_find_run_scan_index`
  over every position), called by `pcrec_req_pick` (req.c:1284) and, at T, by the trace shadow
  (emit_dfa.c:11345). The CONSUMED-EXTENT accessor ("which positions does every match consume")
  is NOT part of RM-4: it has no value until L2/L3 (D77) and lands with the unit that gives it one, and is conditional on D-5;
  its readers are `pcrec_req_pick` and `pcrec_run_pin` (with the pin's gen readers, site 19), never
  the trace shadow, which follows the kit's whole-run P4 (D-6) [r50 A2, A18].
- Gate: no-mover. Streams: the `.c` gate, the facts listing (`req_byte` rows), AND the trace
  build: `tests/memfn/run_pres_picks.sh` (a `-DPCREC_CAND_TRACE` build, `PICKS="set leads ..."`),
  since a default build never compiles the shadow [r50 A2, A13].
- Size: S. Binding checks (the anchor map, RM4 ranges, C37): S453 (req.c:1284, the very expression
  RM-4 replaces), S280 (kset.c:328); plus `S461_pick_none_ignores_size`,
  `tests/codegen/run_prechecks.sh`, `tests/findings/structural_check.py`,
  `tests/findings/e1_object_check.py` (C32).
- Separable: yes.
- Deletes: one copy of the pick expression; the risk that L2 restricts one picker and not the
  other (the r4 plant's failure shape, span_arms READY2-2).

**RM-5 (register row 6a, narrowed) a read accessor for `Ctx.lb_max`** (before L3).
- What changes shape: the owner of `lb_max` (internal.h, beside `pcrec_lb_raise`) answers the
  question its readers have (the declared lookbehind length, in characters); emit_dfa.c:3643-3644
  and L3's walk-parameter filler call it.
- Gate: no-mover. Streams: the `.c` gate (the emitted `#define <p>_VALID_LB` is unchanged).
- Size: S. Binding checks: S901 (`cmp11-prologue-q-reach`, anchored on emit_dfa.c:3643-3644, the
  very read RM-5 replaces; C37); `tests/assertions/run_assertions_tests.sh`'s `VALID_LB` reads; S412,
  S413, S1155 and `tests/utfcheck/check.py` read the EMITTED `#define`, unchanged [r50 A13].
- Separable: yes. Deletes: one direct cross-file field read.

Lookaround-pinning witnesses no unit moves but the feature will (found by REACH text, C47): S1887
(`(?<=abc)x`, `run=none`; at risk at L3, whose BACK candidate moves that run), S1700 and S469
(lookahead plus a run/handoff stamp; SUSPECTED for L2), S3076; S1925's REACH line does NOT go blind
at L1 (`SAB_REACH` runs on the clean tree; `xyz(?<=yz)abc` is already `xyzabc` at T and span_arms
§5.6 predicts no change at L1) [r50 A13].

Not units (needed by no part of this feature yet): P5, P6 (above); A-POSDOM's table (ruled after L3).

## The general form and its siblings

GENERAL FORM. A positive lookaround is a FACT about the subject at signed offsets from its cursor
(D168's per-offset context set): an ITEM of exact byte sets with an EXACT/SUPERSET form. Every
reader places items in its own coordinates; the run reads them as pending guards and extends
itself only at the top, at the reach its readers admit, as ONE run value with the signed interval
`[omin, maxoff]` (D191.3). In the run walk a NEGATIVE lookaround is CAT's width-0 unit since E2
(T3 row E-4, req.c:1082-1083: "`foo\bbar`, `x(?!ab)ac`, `ab\Kcd`"; the probe: `foo(?!x)bar` →
`666f6f626172`, `x(?!ab)ac` → `786163`, C30): it joins the run across itself and contributes no
bytes from its body (the owner: "Negative lookarounds only veto at FINISH") [r50 A16].

THE FAMILIES TODAY:
- The context family (C19-C23): `known.c`'s anchored-machine walk (the cover's context bytes at
  −1 and `k`; machine level, in-span; since [COVER-CAP] stage 1 the only built context producer);
  kset's frontier passing `N_CTX` per thread (kset.c:141); `ctxnode.c`'s one-character lowering to
  `A_CTX` (the reason ITEM has two lowerings); the adjacency head `PdHead` (`pcrec_ph_*`): "the
  positions every match consumes FIRST", the AHEAD half of the item's question (site 23, P5);
  [VLOOKBEHIND] stage 2's fixed-tail hoist reading the description at each BRANCH node (span_arms
  §5.2: "two readers of one description at two nodes, not two producers"); and, planned, the
  machine producer of [CTX-FACTS-NEG] (site 22, ND-1).
- The never family (C20, C35): `PfNever`; derive.c's prune; mrl.c's `PCREC_MINW_MAX` read by the
  `ceiling` row; the `empty` LOCATE row. The run walk's DEAD joins it as one propagation (site 21,
  P6) [r50 A8].
- The offset-bound family (C12, C45): `RbSet.off[]` (`RB_OFF_UNBOUNDED`), `ReqSet.maxoff[]`,
  `RbRun.off`, `ReqRun.whole_maxoff`, K; at L3 `omin` and `req_run_omin` join it. RM-2 states K
  alone; D-7 asks whether the run's signed interval is the one stated value [r50 A7].

PLANNED ROWS ON THE SAME SHAPES (each shown to fit, or the shape widened first):
| row | shape it extends | fits? |
|---|---|---|
| [CTX-FACTS-NEG] | a producer of the same per-offset sets (fixed positive lookbehind, `\b`, width-1 negative lookbehind) from the anchored DFA; trigger "a client that needs the facts: the S4 [REQ-LOOKAROUND] work or kit_proof UL-0" | NO as filed: two producers of the fixed-lookbehind sets beside the item, unless re-scoped to read the item (or the item reads it). The owner's fork, **context-producer-home**; ND-1 if two [r50 A4] |
| [NEVER-MATCH] | `never_matches`, the never family's home | YES (P6 / D-9); its trigger "span_arms L1's landing" FIRES at L1: a scheduling fact for the manager, not a build here [r50 A4] |
| [LOOK-LOCATE] | the item as a window span at a negative offset; `CandRow` (register row 10) | NO as is on the kit side: window spans start at `>= -MF_MAX_BACK` (−8, memfn.h:296); a longer lookbehind needs the kit's span shape widened at that row (named in row 10's note above). pcrec's item carries any signed offset |
| [PRES-OMIN-TRUE] | `ReqRun.omin` (true positive presence `omin`) | YES: `omin` is signed |
| [CTX-SIDES-PRODUCER] | the item read for the cover's `ctx_before`/`ctx_after` | YES on the item; its owner question is **context-producer-home** |
| [EARNED-SKIP] (status: PARKED, "wanted eventually; bigger than intended now; not in S4"; trigger "for earned skip proper (PARKED): lookaround-as-run lands ([REQ-LOOKAROUND], set S4), then a bench cell where the engine's finish is a measurable share") | a verified run that proves the attempt | NO on `ReqRun` alone: it needs SUFFICIENT and OUTPUTS-DETERMINED (span_arms §12c), facts of their own, not fields of the run [r50 A9 c] |
| [DESC-DEAD] | the dead fact, generalized (`a(?!)b`, empty classes) | YES on the never FAMILY (P6), not on `PfNever` alone: derive.c's prune already recognises the empty class as the never leaf [r50 A8] |
| [CTX-PREFILTER] | a one-character prefilter reading the item | YES (an `A_CTX` item is one term) |
| [ENG-LOOK] / [POSTFACT] span intersection | lookaround as a DFA product; lookahead removal | independent of the run's shape; the item is the FACT shadow of the contained case (span_arms §7) |
| [MATCH-KNOWN] (D142) | the proved prefix | reads the kit's verified extent (`mf_class.run`), not the item |

UNLOCKS: span_arms §10's table at 8a27e2e0b (U-dead, U-locate, U-ctxsides, U-omin, U-descguard,
U-exactwidth, ...), each with its trigger and plan row; this note adds none.

## Seams

| seam | writer | readers | facts down | facts up | new calls, layer direction | text round trip |
|---|---|---|---|---|---|---|
| the description module (desc.c) ← the run walk (req.c) | desc.c's ITEM (writer in desc.c under form (a): its head column and description suffix; form (b): a third family; site 23) | the run walk (L1); later the readers of site 22 | the body's description, the cursor side | the item: terms `{off, set}`, form, absent cell | req.c → desc.c (same layer, facts; already a caller of `pcrec_pd_*`) | an item is per-offset 256-bit sets at signed offsets: printable (a design choice whether `--emit-facts` lists it; span_arms §5.3 says no stored item until a second reader) |
| facts record → gen (`ReqRun`, `req_landmark_maxoff`, `req_byte`, `run_pin`) | facts.c `pf_derive_req_walk` and its derived rows | emit_dfa.c (39 `ReqRun` `whole_len`/`whole_maxoff` reads, C9; five direct `pos` reads, C36), kset.c | `omin`, the consumed extent (through its accessor, at L2/L3), K of either sign (RM-2) | none | none new; a LAYER handoff, one way (facts → gen), unchanged; the new fields declared in facts.h's interface when added (D-5) | yes: `--emit-facts` lists every row (`req_run_omin` new) |
| walk parameters (facts.c → req.c) | `pf_derive_req_walk` | `pcrec_req_walk` | `lb_bytes` (and `reach`, or TOP rows with an arm column: D-4) | none | facts.c → internal.h accessor (RM-5): parse-written `Ctx`, read downstream; one way | the `harness:<arms>` why token lists the restored arms (`look`) |
| pcrec → kit presence site (MODULE seam; API `memfn.h` `mf_site`/`mf_pred`; contract `memfn.h` MF_SITE_ABI 29 + `docs/design/memfn/span_runs_sheet.md`; tests `tests/memfn/site_manifest.tsv`, `tests/memfn/run_presence.sh`, `tests/memfn/run_pres_picks.sh`) | `req_pres_spans`, `req_site_define` | the kit's PRES rows and run decision | the run span's `omin` (negative under L3), `head_max` signed, an unbounded K as `MF_HEAD_MAX_UNBOUNDED`; NO consumption fact (D191.2) | `mf_class.run` (scan position, verified extent) | no new call; no new field (all exist at T) [r50 A1] | yes: the MFPRES manifest line carries `head_max` (memfn_sites.c:747-765) |
| the caller contract (stamps) | `pcrec_emit_prologue` | callers | `RX_REQ_RUN` (guard positions), `RX_REQ_HANDOFF` negative | — | — | the stamps are text by definition |
| `Job.req_handoff_vm` (gen → driver; row 6c) | `emit_req_handoff_rest`, `pf_emit_handoff` | the size-cap ladder | unchanged | — | an existing back-flow, named here and untouched | — |

Kit seam in words, no verb about the kit's use (rule "Across the kit boundary"): "the run's
position 0 may lie up to `−omin` bytes before the attempt start"; "the landmark's position-0
offset from the attempt start, of either sign, or unbounded (`MF_HEAD_MAX_UNBOUNDED`)". All are
already the kit's contract (memfn.h at T, MF_SITE_ABI 29); pcrec only begins to state values the
contract admits.

## What is deleted

- RM-1: each run-path builder's implicit "every field is written below" contract.
- RM-2: the −1 sentinel on K (facts.c:106, :355, :868; emit_dfa.c:9174) and the hand
  re-statements of K's state the one predicate replaces (D-7/D-8 decide how far that reaches).
- RM-3: one copy of the landmark move arithmetic (emit_dfa.c:1115-1131 or :7928-7938); the
  "cannot underflow" premise MOVES into the one emitter (deleted at L3, not here) [r50 A6].
- RM-4: one copy of the scan-member expression (req.c:1284 / emit_dfa.c:11345).
- RM-5: the direct `cx->lb_max` read at emit_dfa.c:3643-3644.
- The feature (L1-L3): E-5's plain-unit form as the default (it survives only as the `look`
  restore arm's row); the ctx-node / no-ctx-node run difference; `req_handoff_entry_applies`'
  `k >= 0` conjunct (A8); `p[i].omin = 0` on the run span (site 16, WIDEN); the presence comment's
  "no lookbehind byte" premise; the move's "cannot underflow" premise (L3); span_arms §8.2's kit
  request (delivered: F-2). NOT deleted: the `dead` why token; it stays as the listing's rendering
  of the never family's one fact (site 21) [r50 A8].

## What the design step must decide

| id | site | decision handed on |
|---|---|---|
| D-1 | 1, 2 | how T3's ITEM row walks the lookaround BODY (`rb_zero_into` takes a `const RbWalk *` and has no child slots; `rb_walk` needs both) without a second `A_LOOK` dispatch, and how the body's set, description and consumed runs are kept OUT of the parent (only its item and guards leave) |
| D-2 | 3 | where the guards and the dead bit live (`RbRuns` or `RbVal`), and their stored bound (span_arms §2: at `PCREC_MAX_REQ_RUN_SCAN`, kept end nearest the edge); RM-1's scope follows the answer [r50 A18] |
| D-3 | 4, 5 | T4's spelling: CAT-R, CAT-L, CAT-SET and CAT-EDGE are SEQUENTIAL steps, not first-match alternatives, so which parts are rows of a first-match table and which are fixed steps; the `look` arm's restore semantics (span_arms §5.8) |
| D-4 | 7, 8 | TOP: its place (the walk exit, `pcrec_req_walk`), its candidates' entry into `rn_choice_rows`; `reach` as TOP rows with an arm column (`RB_ROW_SCAN` passes the AHEAD/BACK rows over under the `look` arm), or a walk parameter, and why [r50 A15]; `lb_bytes`'s walk-parameter row. AND: does `rn_scan_mass` (req.c:417-423) rank runs over every run position (it ranks candidate runs, an estimate) or over the consumed extent (its comment ties it to `req_byte`'s pick, which reads the consumed extent from L2/L3)? Both readings are open [r50 A10] |
| D-5 | 10 | whether `omin` and the consumed extent are fields of `RbRun` (every `rn_*` constructor becomes a writer) or only of the walk's OUTPUT and `ReqRun`; both `ReqRun` writers (facts.c:97-100, :253-262) start from RM-1's stated empty value; the NEW fields are declared part of facts.h's interface when added ("stronger moving forwards") [r50 A3] |
| D-6 | 18, 19 | the scan-member primitive's spelling and home (req.c beside `pcrec_req_pick`, or findings.c), named by the question `req_byte` answers; the consumed-extent accessor's spelling and the unit that lands it; the trace shadow's fate: keep the whole-run reading the kit's P4 uses, or retire it with D191.2's "the pcrec/kit agreement check retires"; and the same question as D-4 for the walk's ranking (req.c:423) [r50 A2, A10] |
| D-7 | 12 | RM-2's representation of K's state; the "unbounded" state mapped onto `MF_HEAD_MAX_UNBOUNDED` at its one writer (emit_dfa.c:1644); K ALONE, or the run's signed interval `[omin, maxoff]` with one stated state and K derived from it (the offset-bound family) [r50 A1, A7] |
| D-8 | 15, 12 | RM-3's parameters and whether the emitters ACT THROUGH the chosen start row's K state (`handoff-attempts-entry` / `-unbounded` already decide it) or re-test it [r50 A7]. The full difference list between the two copies, each a byte-identity trap (read at T, C14): (1) the entry emits only under `if (k > 0 \|\| round.len > 0)` (:1115), the re-entry always emits its `if`, at `k = 0` as `%s = landmark_position;`; (2) the entry moves in place (`handoff_position -= K`), the re-entry assigns (`pos = landmark_position - K`); (3) the entry's `else handoff_position = posvar;`; (4) the re-entry's `pf_emit_ofs_reseed` splice when `f` (:7938); (5) at `k >= PCREC_W_UNBOUNDED` the entry emits a comment plus `handoff_position = posvar;` (:1099-1107), the re-entry returns with nothing (:7926-7927); and the re-ask block that precedes only the re-entry (:7922-7924). The per-caller plant shape for the merged arithmetic (S470/S809, and the three round-up plants S471/S814/S1701 that stay per caller) [r50 A6] |
| D-9 | 21 | the DEAD propagation: (a) taken from a primitive shared with derive.c's prune (a never-propagation over kinds, the empty class as the never leaf), or (b) built in T4 with P6 carrying the merge on [DESC-DEAD]/[NEVER-MATCH]. And: does L1's DEAD reach compile.c's empty-artifact readers (compile.c:3303, :3332, keyed on `PF_NEVER_MACHINE` today), or do they stay keyed on the machine value until [DESC-DEAD]/[NEVER-MATCH]'s trigger so L1 moves no byte through it? Both readings are open (the `never_matches` epoch question: the req walk is E2, `never_matches` is derived from the final machines). READY-5's listing consequences bind either way (site 21) [r50 A8, A10] |
| D-10 | 22, 23 | the item's form: (a) SHARED, the head column (`PdHead`, the FIRST positions) for the AHEAD half and the description's suffix for the BEHIND half, the run walk gaining the head column over the byte alphabet, or (b) a third family with ND-2; its bound (the description keeps the LAST positions, so a wide lookahead body would lose its HEAD terms if read from the description, span_arms §5.3 "Bounds": `PdHead` is the column that keeps the first ones) [r50 A17] |
| D-11 | 20 | the `lb_bytes` factor per encoding (span_arms §5.5: `lb_max` under `byte`, `4 · lb_max` under `utf8`) and its unit (characters vs bytes) at the accessor; whether [VLOOKBEHIND] stage 2 (D189's revisit trigger, ordered before this feature in S4) changes what `lb_max` holds before L3 reads it (SUSPECTED) [r50 A9 e] |
| D-12 | 16, PCRE2 | QUESTIONS FOR A pcre2-reader (D181), one each: (a) in UTF mode, may a lookbehind read before the start offset, and what bounds how far (the declared `max_lookbehind`, nested lookbehinds)? span_arms §5.5 MEASURED `(?<=c(?<=bc)d)e` from 3: match in non-UTF, no match in UTF; the reason is not known from code. (b) Does PCRE2's "last code unit" start optimisation ever take a unit from inside a positive lookahead? (informative only: pcrec's run is its own fact) |
| D-13 | 28 | the spec hunk list, re-derived at the design's base: E2 already owns the attempt wording of match_api §6.3.7¶6 and tuning §2.28¶1 (span_arms §12d) |
| D-14 | 16, 18 | L2's text refreshed to D191.2 and K38-2: span_arms rev 2.2's A13/§8.2 "the kit picks inside `cons`" is superseded; the consumed extent stays pcrec-internal (for `req_byte` and the pin), and the kit may scan any run position, `bar(?=baz)`'s `z` included |
| D-15 | 1-7 | re-measure span_arms §5.6/§5.7's "today" column at the design's base: E1, E2 and R1 moved it (the probe at T: `xy(?=bc)[bc]c` is `78796263/fffffeff`, i.e. `xy[bc]c`, where §5.6 says `xy`; `foo(?=bar)baz` is `666f6f62617a`, where §5.6 says `baz`; `(?<=foo)bar(\w)\1` is `626172[\w]` with `RX_REQ_HANDOFF "0"`; C30) |
| D-16 | 16 | the emitted comment at emit_dfa.c:7901 ("no match begins more than %lld bytes before it") prints K and reads wrongly at a negative K: its wording at L3 (an emitted-scaffolding change, so an abi event in that unit) |

## Open questions for the owner

1. **context-producer-home** — When a lookbehind is fixed, who states "these bytes sit at these
   offsets before the match": the lookaround work's new item, or a second, machine-level producer
   as well? Current behaviour: for `(?<=foo)bar`, nothing states that `f`, `o`, `o` sit at −3,
   −2, −1; the required run is `bar` only (the probe: `626172@0`); the cover reads its own edge
   context (the byte before and after the span) from the anchored machine. Your D168 (2026-10-18)
   says ONE producer of these per-offset sets; its home (the span slice) was deleted by the cover
   work. D172 (2026-10-21) says the window site's "Fixed lookbehinds and post-span lookaheads
   longer than 1 come with it, sourced from main's D168 producer". And a filed row,
   [CTX-FACTS-NEG], plans to produce the same sets (fixed positive lookbehind, `\b`, width-1
   negative lookbehind) from the anchored machine, with THIS feature as its trigger. The concrete
   choice: (a) ONE producer: the item built by L1 is D168's producer for fixed lookbehinds and
   lookaheads, D172's window site reads it, and [CTX-FACTS-NEG] is re-scoped to the facts the item
   cannot state (`\b`, past-the-end, thread context), or (b) TWO producers by layer: L1's item for
   AST readers and [CTX-FACTS-NEG]'s machine producer as filed, recorded as a noted deviation
   (a recorded exception to one-home-per-question) against "one home per question" with its correcting event. Example: `(?<=foo)bar` gives
   `foo` at −3..−1 from the item under (a); under (b) the same three sets also come from the
   machine, for the window site. Leaning: (a), one producer; the machine keeps only what the item
   cannot know. Either way L1 files the D168 addendum that replaces span_arms §12's text naming
   the deleted slice.
2. **remodel-go** — Does your build go of 2026-11-09 (D191: L1, L3) cover the five small
   no-change refactors this note says land first? One of them is already inside the L3 text you
   gave the go: stating K as none/bounded/unbounded instead of −1 (RM-2). Four are new: every
   run-record builder starting from a stated value (RM-1), one emitter for the landmark move's
   arithmetic (RM-3, the rounding calls staying where they are), a read accessor for the
   lookbehind length (RM-5), and one shared pick primitive for the byte `req_byte` answers
   (RM-4). Reading the consumed positions for `req_byte` and the run pin rides with L2/L3 and is
   not one of the five. The standing rule already answers part of this (high-level rule 4,
   architecture.md: remodels are "built ... FIRST, as its own answer-identical unit"), so the open
   part is only: does D191's go reach these units, which did not exist when it was given? Each changes no answer and no emitted byte (e.g. `(?<=foo)bar(\w)\1`
   compiles to identical C after RM-3); each exists so the lookaround change touches one place
   instead of two. Current behaviour: none is built; the two copies of the move both assume the
   landmark is never before the search position, which a lookbehind run breaks. Leaning: they ride
   under the unit that needs them, in this order: the unit's CENSUS first (your D191.1 rule: "a
   unit whose census finds NO mover anywhere stops and reports"), then its remodel commits, each
   gated by byte identity, then the feature; a unit that stops at its census keeps no remodel
   commits it has not landed (RM-1 with L1; RM-2, RM-3, RM-5 with L3; RM-4 with L2 or L3,
   whichever lands first).

## Commands

All at `T=57fcb5737`; `G='git grep -n -E'`. Counts are hit lines at T. Rev 1's outputs:
`$PCREC_TMPDIR/scratch/archlook/cmds.out`; rev 2's re-runs and additions:
`$PCREC_TMPDIR/scratch/archlook2/` (not committed).

- C1 `$G "rb_zero_rows|rb_zero_look_pos|RB_ZERO_" $T -- src` (19)
- C2 `$G "RbRuns o;|RbRuns r;|\*v = \*b|^static RbRuns" $T -- src/facts/req.c` (13)
- C3 `git grep -n "rr_cat" $T -- src` (10)
- C4 `$G "rr_alt_rows|rn_common_head\(|rn_common_tail\(" $T -- src` (13)
- C5 `$G "rb_rep_rows|rr_pow\b" $T -- src/facts/req.c` (8)
- C6 `$G "pcrec_req_walk|ReqWalkParams" $T -- src` (10); `git show $T:src/facts/req.c | sed -n '1235,1249p'`; `grep -n rn_choice_rows` on the same; `git show $T:src/facts/req.c | sed -n '417,423p'` (`rn_scan_mass`)
- C7 `git grep -n "WALK_ARM(" $T -- src/facts/walk_arms.def` (7)
- C8 `$G "\} RbRun;|\} ReqRun;|long long whole_maxoff" $T -- src/facts` (3); `git show $T:src/facts/facts.h | sed -n '60,77p'`
- C9 `git grep -c -E "whole_len|whole_maxoff" $T -- src` (emit_dfa.c 39, facts.c 14, facts.h 9, kset.c 3, req.c 2, src/opt/NOTES.md 1)
- C10 `$G "req_run\.(whole_len|whole_maxoff|pos)" $T -- src/facts/facts.c` (16: :98-100, :254-263, :354, :835-836, :891, :925-926; rev 1 said 8) [r50 A14]; `git show $T:src/facts/facts.c | sed -n '92,110p;225,262p'`
- C11 `git show $T:src/facts/facts.def | grep -n "REQ_"` (6)
- C12 `$G '_k\(cx\) >= PCREC_W_UNBOUNDED|k >= PCREC_W_UNBOUNDED\)|k < 0 \|\||k >= 0 &&|whole_maxoff >= PCREC_W_UNBOUNDED|req_landmark_maxoff (= -1|< 0|>= PCREC)|head < 0 \? -1|req_byte\] : -1' $T -- src/gen/emit_dfa.c src/facts/facts.c` (14: facts.c :106, :355, :356, :868, :869; emit_dfa.c :1099, :1644, :7926, :7961, :8990, :9085, :9113, :9174, :9360) [r50 A7]; `$G "k > 0" $T -- src/gen/emit_dfa.c` (6; the move chains :1115, :1125, :7933; :9293 the margin; :5436, :5438 unrelated); `$G '"handoff-attempts-(entry|unbounded)"' $T -- src/gen/emit_dfa.c` (rows :10725, :10734)
- C13 `$G "\"handoff-attempts-entry\"|^static bool req_handoff_entry_applies" $T -- src/gen/emit_dfa.c` (3)
- C14 `$G "^static void emit_req_handoff_rest|^static void emit_req_landmark_move|handoff_position - %s > %lld|landmark_position - %s > %lld" $T -- src/gen/emit_dfa.c` (5); `git show $T:src/gen/emit_dfa.c | sed -n '1064,1134p;7909,7945p'`; `git show $T:src/gen/emit_dfa.c | grep -n 'CANNOT UNDERFLOW'` (1: :1074)
- C15 `$G "p\[i\]\.omin = 0|s->head_max = " $T -- src/gen/emit_dfa.c` (3); `git show $T:src/gen/emit_dfa.c | sed -n '1466,1481p;1536,1551p'`
- C16 `git show $T:memfn/include/memfn.h | grep -n -E "^#define MF_SITE_ABI|MF_HEAD_MAX_UNBOUNDED|may be NEGATIVE|negative on the run span|int64_t +head_max"` (MF_SITE_ABI 29 at :39; `#define MF_HEAD_MAX_UNBOUNDED` at :322; rev 1 said 27) [r50 A1]
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
- C29 `scripts/entry D168 -l 1` (prints "profile decisions dormant"); `git show $T:docs/dev/decisions.md | grep -n -E "^## D(62|168|172|189|191) "`; `git show $T:docs/dev/decisions.md | grep -n "D62's discipline"` (D70's mention)
- C30 the probe on `(?<=foo)bar`, `bar(?=baz)`, `xyz(?<=yz)abc`, `a(?=b)[bc]`, `xy(?=bc)[bc]c`, `foo(?=bar)baz`, `(?<=foo)bar(\w)\1`, `foo(?!x)bar`, `x(?!ab)ac`, reading `req_whole_run`, `req_byte`, `req_landmark_maxoff`, `never_matches`, `RX_REQ_RUN`, `RX_REQ_WHY`, `RX_REQ_HANDOFF` (rev 2 re-ran `foo(?!x)bar` → `666f6f626172`, `x(?!ab)ac` → `786163`, `(?<=foo)bar` → `626172`, `foo(?=bar)baz` → `666f6f62617a`); `git log --oneline --since="2026-11-15 19:53" $T -- src memfn/src memfn/include` (1)
- C31 `git grep -l -E "landmark_position|handoff_position|req_landmark_maxoff|whole_maxoff|req_landmark_k|pcrec_landmark_margin" $T -- tests/mech/sabotages` (31); `git grep -l -E "rb_zero|RB_ZERO|rr_cat|RbRuns|rr_alt|rb_rep" $T -- tests/mech/sabotages` (20). Identifier greps: a FLOOR, superseded for binding lists by C37
- C32 `git grep -l -E "rb_zero_look_pos|rb_zero_rows|rr_cat|pcrec_req_walk|emit_req_landmark_move|emit_req_handoff_rest|req_handoff_entry_applies|pcrec_run_pin|pcrec_req_pick" $T -- tests` (17)
- C33 `$G "req_landmark_k\(|req_handoff_k\(" $T -- src` (16 lines: 2 declarations :321, :336; 2 definitions :9154, :9166; the call :9157 inside `req_handoff_k`; and the 11 reader lines listed at site 12) [r50 A7]
- C34 `$G '^static [^(]*\b(us_run_pin|pf_window_of|ofs_test_of|ofs_test_verifies_run|pf_run_applies_common|walk_proves)\(' $T -- src/gen/emit_dfa.c` (7: :6872, :6880, :7418 declaration, :7428, :7438, :7469, :7582) [r50 A14]
- C35 `$G "never_node\(|PCREC_MINW_MAX; \}|PfNever pcrec|locate_empty_applies" $T -- src` (derive.c :146 and six `never_node` returns; facts.c :647; kset.c :531, :537; emit_dfa.c :4864, :10403, :10549; one unrelated callgraph.c line); `git show $T:src/opt/derive.c | sed -n '18,22p'`; `git show $T:src/opt/mrl.c | sed -n '233,238p'` [r50 A8]
- C36 `git show $T:src/facts/facts.h | sed -n '1,6p'` (the module-level consumer declaration); `$G '(r|run)->pos\[' $T -- src/gen/emit_dfa.c` (5: :1186, :1471, :6935, :11345, :11452) [r50 A3]
- C37 the anchor map: export T (`git show $T:<file>` for the four sources; `git archive $T tests/mech/sabotages | tar -x`), then `python3 -I docs/dev/reviews/2026-11-18-r50-archlook/firstunit_anchors.py <export>`: RM1 15, RM2 (facts.c) 0, RM2e 5 (S467, S476, S529, S1706, S1957), RM3 11 (S74 a false hit), RM4a 1 (S453), RM4b 0, RM4c 1 (S280), RM5 1 (S901); with three range groups added in a scratch copy (the K tests, emit_dfa.c :7950-7966, :9108-9116, :9285-9295, :9310-9320 → S811, S1707, S1712, S1956; the run-pin readers :6868-6960, :7425-7600 → S287, S448, S1418 (+S74 false); the presence spans :1440-1485, :1536-1551 → S1101, S1102, S3048) [r50 A13]
- C38 `git show 8a27e2e0b:docs/design/span_arms.md | grep -n -E 'READY-5|dead. sits on .req_whole_run. only'` (4: :103 the §R3 disposition row, :434 and :440 the §3.7 listing text, :990 the L1 unit row) [r50 A8]
- C39 `git show $T:src/facts/req.c | grep -n -E '^static RbRuns (rr_unit|rr_pos)|o\.tail = rr_cat\(w, gap, p\)\.tail|v->runs\.best = b->runs\.best'` (4: :535, :556, :788, :925) [r50 A12]
- C40 `git show $T:docs/design/span_arms.md | grep -n -E '^\| reach|forces reach'` (2); `git show $T:src/facts/req.c | sed -n '393,398p'` (`RB_ROW_SCAN`) [r50 A15]
- C41 `$G '^static [^(]*\b(req_handoff_applies|pf_handoff_applies|req_landmark_hit_ppm|req_handoff_stamp)\(' $T -- src/gen/emit_dfa.c` (5 incl. a declaration: :8981, :9197, :9309, :9355); `$G 'pcrec_landmark_margin' $T -- src/gen/lmwalk.c` (:248) [r50 A14]
- C42 `git show $T:src/gen/emit_dfa.c | sed -n '11329,11349p'`; `git show $T:memfn/src/presence.c | sed -n '318,338p'`; `git show $T:tests/memfn/run_pres_picks.sh | grep -n -E 'PCREC_CAND_TRACE|^PICKS'` [r50 A2]
- C43 `git show $T:src/facts/desc.h | grep -n -E 'Two callers|PARAMETER|second column|consumes FIRST'` (4: :11, :17, :51, :55); `git show $T:src/opt/altnf.c | grep -n -A1 'contributes no head'` (:183-184); `git show $T:src/facts/req.c | grep -n -E 'THE POWER ARM|2-3 \(span_arms R1'` [r50 A17]
- C44 `git show $T:src/gen/emit_dfa.c | sed -n '8989,8994p'` (`fit.chosen == ENGM_VM` at :8992-8993 inside `req_handoff_applies`) [r50 A14]
- C45 `$G "RB_OFF_UNBOUNDED|whole_len < 2" $T -- src/facts src/gen/emit_dfa.c` (17: the offset-bound family's sentinels `RB_OFF_UNBOUNDED` (facts_derive.h:81, req.c:218, facts.c:249) and the whole-run none `whole_len < 2` at its readers) [r50 A7]
- C46 `git show $T:docs/dev/guide/coding.md | grep -n "four byte-identity gates"` [r50 A13]
- C47 `git grep -l -E '^SAB_REACH=.*(\(\?<=|\(\?=).*(REQ_RUN|req_whole_run|HANDOFF)' $T -- tests/mech/sabotages` (5: S469, S1700, S1887, S1925, S3076) [r50 A13]

## Findings for the manager (not owner questions)

- F-1: at T the plan row's status described span_arms rev 1 with no go; main's 2843924a1 brought
  it current during review r50's freeze (rev 2.2, D191's go, STATE:started), so that half is
  discharged. [REPEAT-RUN] still reads `STATE:not-started` though R1 is in the code at T (req.c
  "THE POWER ARM ([REPEAT-RUN], span_arms R1", C43). The current row keeps "Negative lookarounds
  give exclusions only and stay walls", which is not how the run walk treats them since E2 (they
  are CAT's width-0 unit; general form section) [r50 A16].
- F-2: span_arms §8.2's kit request is DELIVERED in §12a's end-state form (R-38 K38-2, then
  MF_SITE_ABI 29 with R-38 Part D + R-41: no cut, the kit's one run decision `mf_class.run`, a
  negative run-span `omin`, a signed `head_max`, the unbounded K stated by name
  `MF_HEAD_MAX_UNBOUNDED`, the twin admitting by `max(K, 0)`); L2's remaining condition under D191
  is its one readiness critic, on text that D-14 must refresh first [r50 A1].
- F-3: span_arms A3's margin fix (READY3-2) is already in the tree (emit_dfa.c:9293, C17).
- F-4: register row 14's status is stale (stage 3 landed 2026-11-14); [RUN-POS-SET]'s stage 3m
  will edit the same alternation fold.
- F-5: register row 7a's trigger ("the next change to the facts listing") is wider than its
  shape (the `decisions` section's `#define` parse).
- F-6: register row 19's WHERE omits req.c's `RB_ROW_SCAN`, a macro with an arm column and a
  fourth first-row walker; whether row 19 absorbs it is the manager's call.
- F-7: span_arms carries ten "*(superseded by cover_cap.md rev 4, 2026-11-15)*" markers (§5.3's
  "Where it lives" and §12's D168-addendum text among them); what is missing is the REPLACEMENT
  text naming D168's producer after [COVER-CAP] stage 1 (owner question
  **context-producer-home**) [r50 A9 d].
- F-8: gen reads `ReqRun.pos` directly at five sites (C36) while facts.h names the accessors the
  one spelling of membership: a register-row candidate, not this feature's [r50 A3].
- F-9: [REQ-EMPTYCAT]'s "next: L1 (L2/L3 after the kit's R-38)" makes L3 wait on R-38 where
  D191.1 does not (review r50's record note).
</content>
</invoke>
