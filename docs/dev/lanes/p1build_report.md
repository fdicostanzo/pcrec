# Lane p1build — P1 landmark walk, stage 1 build (design rev 3 + the DFA hat)

Lane p1build, opus, 2026-10-29, worktree `worktrees/p1build`, branch `lane/p1build`, from main
ae1d53859. The design is `docs/dev/lanes/p1dsg3_report.md` (rev 2) with review
`docs/dev/reviews/2026-10-29-r7-landwalk3.md`, whose MANAGER RULINGS bind (every PROPOSED
disposition ACCEPTED; build go). This report's first section, "Design rev 3 (r7 fixes)", is the
lane's FIRST COMMIT: one disposition row per r7 finding, each saying what the build does. The
sections after it record the build.

## Summary

(Written at handoff; see STATE AT HANDOFF.)

## Design rev 3 (r7 fixes)

Rev 3 is rev 2 plus the rows below. Nothing here changes the walk's admission (rows 1-10 of rev
2's admission table) or its answers (the hit stream, s*, the seed verify, the reach guard), so by
the r7 ruling no further re-check is owed. Each row names the code the build writes; "general
form" is the reading every reader shares, never a walk-only clause.

### FIX-1 + SOUND-1: RECOVER is asked by the row whose walk runs the RECOVER block

**The defect (r7, verified):** a RECOVER cell visited through the LOWER relocate reads two fields
off the SELECTED LOCATE row (`u.locate.recover` in `dfa_search_start_of`, `.needs[].cells` in
`cand_recover_asked`) instead of off the row whose cells were visited (the relocate target,
`composite`). The walk states neither, so hand 0, a NULL RECOVER selection and a NULL dereference
in the stamp rule on every admitted compile (FIX-1); and, behind it, the RECOVER predicates gated
on the selected row's cells decline, so the relocated composite falls to `reverse-pass` (SOUND-1).

**The general form (chosen): RECOVER's ASKER is a derivation, `cand_recover_asker(cx)`.** The
LOCATE row whose walk runs the RECOVER block on this compile's path:
1. the selected LOCATE row, where its own cells on its route name RECOVER (`composite`, `rev-end`
   today: no reader moves);
2. else, where FINISH RELOCATES one of the selected row's hands (the hand's FINISH row is a
   `CAND_FIN_SEARCH` row and the hand is not the caller's `AT`, `cand_path_finish`'s own relocate
   condition), the route's FALLBACK LOCATE row, the relocate target, whose cells the closure
   visits;
3. else the selected row (it asks no RECOVER; the readers then read RECOVER's absence).

Both readers every RECOVER consumer shares read it: `dfa_search_start_of` asks RECOVER with the
asker's `u.locate.recover` hand, and `cand_recover_asked` reads the asker's cells. So the stamp
rule, `rx_info.search_form`, the composite emitter and the path closure see ONE row, the one whose
code runs. For the walk: asker `composite`, hand `EXISTS`, and `pinned` / `end-minus-width` /
`landing` are evaluated exactly as on the plain composite (SOUND-1 closed, not merely visible).
`pinned` cannot apply on an admitted pattern (R holds a non-empty literal, so R is not nullable).

Why this and not the explicit field (`.recover = EXISTS` plus RECOVER in a cell set on the walk):
the walk's own code runs no RECOVER block, so the field would be a declaration that is false of
its row, and every future relocating row would have to copy its target's declarations (the r7
lesson 1 shape). The derivation states the fact once: a relocate runs its target's cells.

**The self-check (the manager's ruling): an admitted selection with a NULL slot is REFUSED.**
`cand_path_of`, which every reader of the path and the stamp rule runs, fails the compile with an
internal error (`pcrec_ctx_fail`, release build included, so it can never reach the stamp rule)
where a cell it SELECTS in (LOCATE, RECOVER, FINISH per hand) yields no row. Today a NULL there is
silently skipped (`if (r) ...`). Its control: sabotage "RECOVER read off the selected row"
(S1820, below) makes the walk's RECOVER ask hand 0 and the self-check fires on the SOUND-1 witness;
a second control plants a LOCATE row asking RECOVER with `.recover = 0`.

**`table-recover-not-total` stops skipping an unstated hand** (r7 lesson 2): a LOCATE row whose
cells on a route name RECOVER and whose `.recover` is 0 now FAILS the check ("asks RECOVER with no
hand") instead of being skipped; a row that asks no RECOVER is still skipped. Today's rows: no
mover (`composite` EXISTS, `rev-end` WINDOW; `empty`, `cover` ask none).

**§Size corrected:** dropping the walk takes the members from "the walk's members" to "the walk's
members minus ML": {ML, MA, MF, X} → {MA, MF, X}, where X is the RECOVER row's needs, the SAME row
on both sides because the asker is `composite` on both (MR only for `reverse-pass`). So the drop
always shrinks, and LR-S12's "the drop row FIRED" holds without a shrink test.

**Acceptance cell:** `[a-z]{40}@x -fno-req-handoff`: admitted (rows 1-9 pass by hand), and
`RX_DFA_START "end-minus-width"`, as on main.

### SOUND-2 (r7): the seed verify is INLINE

The seed AT's `verify-at` is emitted as an inline anchored run of A from s*(j) inside the search
body: A's tables (as `<prefix>_match` declares them) and `emit_anchored_scan_head` +
`emit_scan_loop` over A's form, in a block that binds its own start, with no prologue (no K50
guard, no `-futf-check` validation per hit; the search body's own prologue ran once). No `_match`
call, so `entries.c`, `search_match`, the part references and `dfa_search_calls_match` are
UNTOUCHED, and rev 2's G3 item 9 is DELETED (eight generalisations remain). Acceptance cell: the
utf8 `-futf-check` twin of T6 (`[a-z]+@x -e utf8 -futf-check` over "ab@"×N hits) is linear in N.

### FIX-2 + SOUND-4: L8's start set is LOCATE's own kit ask, declared

`cand_nodes[LOCATE]` gains `kask[NEXT] = CAND_ON(DFA)` and `kfields = EXISTS | PROVEN0`, beside
rev 2's `reads[NEXT]`, `under[NEXT]`, `by[NEXT]` (five fields, not three). The memo fill makes the
start-set ask (`cand_row_scan`) with reader LOCATE, AFTER the fill's NEXT selection has returned,
so no NEXT(F|NO_LW) frame is open (`ask-while-open` passes). `table-ask-unread` holds (the kask edge
lies inside `reads`), so `table-read-cycle` is unchanged. §Checks' "no new kit ask" row is
corrected to "one new declared ask, LOCATE→NEXT on DFA". Control: sabotage S1823 (delete the
`kask` declaration) traps `undeclared-ask` in the trace build.

### FIX-3: the new rung's readers include the ladder's sequence table

`drop-landmark-walk` is a full `fit_rungs[]` row: `.act = FIT_DROP_LANDMARK_WALK` (a new `FitAct`
value; the recovery switch's retrying case and `fit_act_text` gain it, a `-Wswitch` hit anyway),
`.cells = {{ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY}, PFLW_PASS, NULL}` (it ATTRIBUTES, S238's
rule), `.retries = 1`, `.repeat = FIT_REP_ONCE`, `.fof = FIT_FOF_IN`, `.deny = 0`, `.degrading =
true`, `.on = FIT_L_SIZE`, `.sets` as rev 2 (SDR KEEP, the walk's deny OR'd in), `.note` naming the
loss. `fit_seq_legal[]` gains exactly `{DROP_LANDMARK_WALK → DROP_ANCHORED}` and
`{DROP_LANDMARK_WALK → DROP_PREMUL}` (the verifier showed `{COLLAPSE, DROP_LW}` and `{DROP_END_MARK,
DROP_LW}` unreachable). The readers moved in the same commit, FOUND BY GREP: `COMPILE_MAX_ATTEMPTS`
(+1) and its comment, `fit_tables_selfcheck`, `axes_dump.c`, `run_fallback_table.sh`,
`limits_check.sh`, `docs/design/dec_fallback.md` §1.7, `dec_fallback/row_reach.py`'s `SIZE`, the
`prefilter-collapse` row's `engine-route` desc (`--list-axes` text: "dropped the optional anchored
machine, the landmark walk, the premultiplied table or the prefilter"), limits.md §8.4. A new
S238-shaped sabotage row for the rung (S1826).

### FIX-4: the ML build gate honours the deny

The compile-time gate (`pcrec_lmwalk_admits`, called from compile.c before ML is built) tests the
row's `.c.deny` FIRST and returns false under it, so under `-fno-landmark-walk` and on every
`drop-landmark-walk` retry no PRE row runs: no memo fill, no CANDTRACE record, no facts `used`
mark, no ML build. It is named as the bit's BUILD reader beside its one SELECTION reader
(`cand_select`); the counterfactual argument is unaffected (the fill sets the bit and never runs
the gate).

### FIX-5 + SOUND-3: the memo fill restores the facts' `used` record

The fill saves `cx->job->pf.used` and restores it after the counterfactual NEXT selection and its
start-set ask, `req_pres_proof_quiet`'s shape and reason (a counterfactual world was not built,
facts_listing.md §4.1's promise). §Checks' `--emit-facts` row reads "no mover, by construction".
Witnesses `[a-z][a-z]@x`, `c[ac]t` (cover) and `[a-z]+@x$` (rev-end) keep `run_pin used no` (a
test cell).

### FIX-6: the asker trap and `at_askers` are FINISH-only

`CandSel.point` becomes `CandSel.asker`; the UNSTATED-0 trap and the `at_askers` test apply where
`r->slot == CAND_SLOT_FINISH` and the hand is `AT`, exactly where today's `point` test applies.
RECOVER asks keep their hand-only test (`CAND_HAND_WINDOW == CAND_HAND_AT` numerically, so an
unscoped test would hold RECOVER's WINDOW to `at_askers`). RECOVER's totality check's `.point =
true` becomes no asker at all (it is not a FINISH ask). Sites: 7 explicit `.point` initializers
plus `cand_path_finish`'s parameter and its calls.

### FIX-7: S770 and S738 are re-aimed

`gives[]` replaces `.fin` on the four LOCATE rows, so the plants of
`tests/mech/sabotages/S770_empty_after_revend.sh` and `S738_locate_order_swapped.sh` (anchored on
`.fin = ...`) are re-aimed in the same commit, intent unchanged (each still plants the same row
swap). "Found by grep" greps `tests/` too.

### FIX-8: the rank check's VM skip stays, and says why

`table-progress-rank` keeps `rt == CAND_ROUTE_VM` skipped, with one comment sentence: on the VM
route the FIN_SEARCH row IS the search entry (E-FC, the projected hand), not a relocate to
`composite`, so the fallback's `gives[]` does not describe it and the amended operand would pass
there vacuously.

### Held items (NOTED / DOC)

- **Memo longjmp:** the fill's options copy lives in the Job (arena), and `cx->opt` is restored on
  every exit of the fill; a `longjmp` out of a fill ends the attempt (fresh Ctx per attempt), so
  nothing reads `cx->opt` after it. Stated at the fill.
- **`FINISH.raise |= LOCATE`:** declared; no check reads a `raise` claim today. NOTED.
- **T7's oracle:** the "drop `anchored-A`" sabotage is detected by A trace-build trap
  (`path-needs-unbuilt`, or `no-row` depending on emitter order; with FIX-1's self-check, the
  release build refuses too). The sabotage row names "a refusal or a trace-build trap", not one
  check.
- **The selection WORLD unlock (PLAN):** an explicit selection world (deny bits + Job overrides)
  passed down `cand_select`/`cand_read` instead of mutated `Ctx` state, unifying the memo fill, the
  ladder's shrink test and the facts hook. Filed as a plan row with its trigger (the next
  counterfactual reader or toggle site); not built here.

### What rev 3 does NOT change

The admission table rev 2 (rows 1-10), the hit stream's fact (every occurrence, overlapping
included), s*'s definition, the reach guard and its LOWER relocate, the counterfactual read and
its lemma, the asker split's semantics, the row order (`empty, rev-end, cover, landmark-walk,
composite`), the flag (`-fno-landmark-walk`, a public deny: the walk CAN be slower on a caller's
input, N1), the stage-1 bench population (3).

### IDs

S1820-S1829 (allocated to this lane): S1820 RECOVER read off the selected row (FIX-1); S1821
non-overlapping hit stream (SOUND-2 of r5, T3); S1822 row 1 reads the body's route (T1); S1823
LOCATE's kask undeclared (FIX-2); S1824 `anchored-A` dropped (T7); S1825 max start instead of min;
S1826 the rung does not attribute (FIX-3, S238's shape); S1827 reach guard removed (T6); S1828
EXCLUSION dropped; S1829 the walk's deny removed from `by[NEXT]` (`table-read-cycle`). The build
may re-assign within the range; the final list is §Checks and sabotages.

## What was built

(In progress.)

## Answers

(In progress.)

## Speed

(In progress.)

## Checks and sabotages

(In progress.)

## abi and spec

(In progress.)

## STATE AT HANDOFF

(In progress.)
