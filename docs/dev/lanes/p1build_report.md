# Lane p1build — P1 landmark walk, stage 1 build (design rev 3 + the DFA hat)

Lane p1build, opus, 2026-10-29, worktree `worktrees/p1build`, branch `lane/p1build`, from main
ae1d53859. The design is `docs/dev/lanes/p1dsg3_report.md` (rev 2) with review
`docs/dev/reviews/2026-10-29-r7-landwalk3.md`, whose MANAGER RULINGS bind (every PROPOSED
disposition ACCEPTED; build go). This report's first section, "Design rev 3 (r7 fixes)", is the
lane's FIRST COMMIT: one disposition row per r7 finding, each saying what the build does. The
sections after it record the build.

## Summary

Stage 1 of the P1 landmark walk is built: design rev 3 applies every r7 fix (first commit), then
the `landmark-walk` LOCATE row with its declared admission table, the `NEXT_cf` memo and asker
split, the public deny `-fno-landmark-walk`, the size-cap rung, abi 95 (provisional) and the spec
hunks. Answers: 0 wrong in a libpcre2 differential over 16 witness patterns (1.3M subjects),
181/181 on a libpcre2-generated answer net under four configurations, identical answers on every
bench subject. Speed (instructions): 5b email x68.8 on acc-main, qnt-plus `a+b` x5.1; the N1 loss
cell +3.9%; one NEW loss cell (+31%, a PRESENCE pre-check the walk displaces; filed). utf8 rows
decline on rarity (a deviation). Owed and queued: make test, 19 mech rows, the timing window.

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

Commits on `lane/p1build` (from main ae1d53859): 00f5010f4 (design rev 3), 108f6688c (asker
split, `u.locate.gives`, the RECOVER asker, the NULL-slot refusal; no movers), 6a86bb830 (the
row, `lmwalk_conj[]`, the `NEXT_cf` memo, the ML build, the LMHIT kit site, the emitter),
8936a8156 (the `drop-landmark-walk` rung, abi 95, spec hunks; the last commit touching `src/`),
a64bcc920 (answer net, structural script, mech arm, sabotages, re-aims, census re-pins),
bb41a2d22 (the measurement card), bcf9dc3cb (evidence), e43eaf0f6 (plan rows, identity self-pin).

- **The LOCATE row `landmark-walk`** (`src/gen/emit_dfa.c` `cand_rows[]`, order `empty, rev-end,
  cover, landmark-walk, composite`), `RX_DFA_SCAN "landmark-walk"`. Per landmark hit (`memchr`
  through the kit's LMHIT site, `src/gen/memfn_sites.def`) the reverse DFA of P·L walks back from
  j+1, floored at `search_from`, keeping the minimum accepting start s*; the reach guard
  (`landmark_position < lmwalk_reach`) relocates to `composite` from s*, else the anchored verify
  runs INLINE from s* (r7 SOUND-2). New file `src/gen/lmwalk.c` holds the admission.
- **Admission `lmwalk_conj[]`**, a declared first-match conjunct table, in order: finisher-dfa,
  anchored-A, branches, split, g1, utf8-l0, exclusion, next-landmark, rarity, machine. Rarity is
  `pcrec_landmark_margin(h, m, w + LMWALK_K_HIT_UNMEASURED)` with k_hit = 10, an UNMEASURED
  default (`limits_check.sh` allowlists it as a cost-model term; the card's `lwhit` intercept is
  its future source). The trace build (`-DPCREC_CAND_TRACE`, env `PCREC_LMWALK_TRACE=1`) prints
  one `LMWALK` record per decision.
- **The `NEXT_cf` memo and the asker split** (rev 2 + r7 FIX-1/FIX-5/FIX-6): the counterfactual
  NEXT read keyed per Job, `used` restored at both fill exits; FINISH's `at_askers`; RECOVER's
  asker derived by `cand_recover_asker`; a self-check refusing any admitted selection with a NULL
  slot (`internal error: the selected path asks slot ...`).
- **The public deny `-fno-landmark-walk`** (`lib/pcrec.h` bit 57, `src/core/axes.def`), honoured
  at the row AND at the ML build gate (r7 FIX-4); masked out of `rx_info.flags` so a declining
  pattern's artifact is byte-identical under it.
- **The size-cap rung `drop-landmark-walk`**, before `drop-anchored` (`src/core/compile.c`; the
  ladder's sequence table gains its pairs, r7 FIX-3).
- **Tests:** `tests/landwalk/` (answer net 35 blocks / 181 cases from libpcre2, the generator,
  the card); `tests/codegen/run_landmark_walk.sh` (in `test-codegen`; 58 checks); mech arm
  `landwalk`; `cand_oracle_witnesses.tsv` +5 lines.
- **Measurement card** `tests/landwalk/card_lwalk.sh` ([LANDWALK-CARD]): `lwhit` (wlen 2/8/32 x
  miss/hit), `lwfit` (a + b*wlen per arm), `lwcall`; walkbytes against one forward DFA step
  measured in the same run, instructions beside; UNMEASURED without `--timed`.
- **Not built (held):** the `back_walk` fact and the D27 spec-first cell (r7: only if the manager
  rules FIX-1's general form a contract on `RX_DFA_START`; no such ruling); the selection WORLD
  (filed `[SEL-WORLD]`); the priced edge (`[LANDWALK-EDGEPRICE]`, unchanged).

## Answers

- **Answer net** `tests/landwalk/landwalk.rxt`: 181/181 under default, `-fno-landmark-walk`,
  `-fno-anchored-dfa` and `--engine=vm` (the harness on the one file; the last two re-checked at
  176 cases before the final 5 R/T cells were added, the default and deny at 181).
- **libpcre2 differential** (`docs/dev/lanes/p1build_evidence/lwdiff.py`, every subject up to
  length N over a pattern-specific alphabet, find-all): 18 runs, 16 patterns, **0 wrong** over
  1.3M subject-answers, all 16 on `landmark-walk` (byte and utf8: `[a-zé]+@x`, `[^@ ]+@x`), plus
  `[a-z]+@x` under both denies. Includes the 5b email pattern, `a+b`, `\b`/`\B`, `(?i)`, atomic and
  possessive bodies, lookbehind, the `[a-z]+@...x` overlapping-hit cell. Results:
  `p1build_evidence/diff_results.txt`. Earlier in the lane: T6 guard 0.00 s vs 5.53 s unguarded
  at n = 65,536.
- **Bench population (3 rows):** 5b mask-email walks (byte and utf8); qnt-plus `a+b` walks in byte;
  cls-s-ucp `(*UCP)a\sb` utf8 DECLINES on `rarity`, as does utf8 `a+b`: the rarity row has no
  utf8 byte prior (a uniform prior), a DEVIATION from the design's "admitted" for the utf8 rows,
  recorded here and as a decline witness, not fixed (a prior is a [MEASURE-SET] question).
  Answers on the bench subjects: identical to main (speed table `answers=same`, count and span
  hash).
- **The corpus:** OWED. The corpus census (`$PCREC_TMPDIR/scratch/p1build/census.py`, every
  unique corpus pattern through the trace build) waited on the box lock behind the queue all
  afternoon; the corpus's answers are `make test`'s (`test-corpus`), queued as `p1build-test`.

## Speed

Instructions:u per find-all pass, the walk (lane build) against main's `build/pcrec` (362f8e2e1,
abi 92; its 5b artifact is byte-identical to the lane's `-fno-landmark-walk` one but for the abi
number), median of 5 interleaved passes, `p1build_evidence/speed.sh`; answers identical on every
row. Cycles were read on a LOADED box (queue jobs running) and are NOT a timing; the timing run is
queued (`p1build-timing`, not before 2026-10-30T13:30).

| cell | subject | walk | main | main/walk |
|---|---|---|---|---|
| 5b email | acc-main (80,123 matches) | 79.57M | 5,477.6M | x68.8 |
| 5b email | acc-small (830) | 0.84M | 59.4M | x70.9 |
| 5b email | fz-me, N1 (7,946) | 101.3M | 97.6M | x0.96 (walk +3.9%) |
| 5b email | qs-200k (0) | 1.969M | 1.969M | x1.00 |
| qnt-plus `a+b` | t-1m (1,505) | 0.99M | 5.07M | x5.12 |
| qnt-plus `a+b` | t-256k (377) | 0.25M | 1.27M | x5.15 |
| `[a-z]+@x` | acc-small (0) | 0.556M | 0.426M | x0.77 (walk +31%) |

- **5b / acc-main** reads 79.57M against the design's expected 77.76M (+2.3%, outside its ±1%):
  the difference is the scan edge on the walk's loops (form `bitmap`): under `-fno-scan-edge`
  the same artifact reads 78.06M. Filed into `[LANDWALK-EDGEPRICE]`'s status (the edge COSTS 1.9%
  here, where the p1dsg twin's plain edge saved 2.4%). Answers 80123 / e97ca4d6da618f68 as expected.
- **N1 (fz-me):** the r1/r5 loss cell, walk +3.9% instructions, inside the design's x1.25 bound.
- **r5 loss cell, a new one:** `[a-z]+@x` on acc-small (830 `@`, no `@x`): the walk +31%
  instructions, because PRESENCE declines the whole-window required-run pre-check (`dominated`)
  when the walk answers presence, and that run (`@x`) is rarer than the walk's landmark (`@`).
  Filed `[LANDWALK-PRES]` (a priced PRESENCE rule; trigger: a bench/corpus cell of that shape).
- cls-s-ucp: declines (Answers), so main's artifact is unchanged but for the abi number.
- **Card smoke** (instructions, not timing): wlen 2 miss walk 2.80M vs denied 2.12M; hit 3.66M vs
  4.06M per 4 KiB; the per-hit intercept is the `--timed` run's.

## Checks and sabotages

Run in the lane and green: `make`, `make strict`; the harness on `landwalk.rxt` (above);
`tests/codegen/run_landmark_walk.sh` 58/0 (witnesses 10 walk + 12 decline, deny both ways with
byte identity on declines, reach guard 50,000 landmarks under 2 s, card smoke);
`run_rxtsource` 300/0 (census pins re-pinned: 312 files, 6298 blocks, 75694 lines, C3 skips);
`axes_registry_check` 245/0; `limits_check` 39/0; the sabotage BEFORE-count scan 0 mismatches
over every `tests/mech/sabotages/` row after the re-aims.

NOT run in the lane (box load; queued, OWED): the full `make test` (including test-codegen's
`run_dfa_stamps`/`run_codegen_tests`, `test-cand-oracle`, `run_fallback_table.sh`, the full
registry), the identity gate (B), and the mech rows below.

**Sabotages S1820-S1829** (all new, each with its suite):

| id | plant | suite |
|---|---|---|
| S1820 | `cand_recover_asker` returns the selected row (r7 FIX-1) | harness + landwalk |
| S1821 | non-overlapping hit stream (resume past the reach) | harness (`[a-z]+@...x` on `a@b@cdex`) |
| S1822 | row 1 reads the body's route, not the finisher's (T1) | harness + landwalk |
| S1823 | LOCATE's kit ask undeclared (FIX-2) | candoracle |
| S1824 | `anchored-A` admits everything (T7) | landwalk |
| S1825 | the ML keeps the first (max) start, not the min | harness |
| S1826 | the rung cells pass without attributing (FIX-3) | fallbacktable |
| S1827 | the reach guard removed (T6) | landwalk |
| S1828 | EXCLUSION dropped | landwalk |
| S1829 | the walk's deny removed from `by[NEXT]` | candoracle |

**Re-aimed** (their BEFORE text moved under this build): S238 (SAB_COUNT 4 -> 5), S693 (abi 95),
S738, S770 (r7 FIX-7), S741, S744, S777, S811, S844. The 19 rows are the queued `p1build-mech`.

## abi and spec

- **abi 92 -> 95, PROVISIONAL** (the brief's provisional number, other lanes holding 93/94; p10build claims
  96). Readers found by grep (`abi[ =_:]*92`, `(abi 92)` over src, tests, docs/spec, lib, cli,
  memfn): the `.abi` stamp, test expectations, the spec sentences, S693, and
  `docs/dev/history/abi_changelog.md` (the 95 entry). The remaining `92` hits are history
  (S283's dated figure, the recursion-identity pin's provenance chain). The landing re-numbers if
  another lane lands first.
- **Identity gate (B):** self-pinned to 8936a8156 (the last `src/` commit); the manager re-pins to
  the merge commit.
- **Spec hunks (D80), same change:** `docs/spec/tuning.md` §2.54 (new: the walk, the deny, the
  rung, the k_hit default) + TOC + tables + §5.4 row + §2.15 + §3 value;
  `docs/spec/match_api.md` §6.3.4 (the `landmark-walk` scan value, `rx_info.scan`, `dominated`,
  `UNIFORM_FOLDS` 0..10); `docs/spec/limits.md` §8.4 row 2a + §8.5; `compound.md` §A.2 row 3;
  `dec_fallback.md` §1.7 sequence row.

## STATE AT HANDOFF

- **Branch** `lane/p1build`, 11 commits over main ae1d53859 (the last two: the report and this count), clean except the untracked
  `p1build_deliver.txt`. Rulings file `p1build_rulings.md`: empty at every read (last: before the
  report commit).
- **OWED, queued** (`scripts/boxqueue add`, all `not-before 2026-10-30T13:30`):
  `710-p1build-test` (make, strict, identity gate (B) at 8936a8156, full make test via perfrun);
  `711-p1build-mech` (the 19 rows above, after p1build-test); `712-p1build-timing` (the card
  `--timed` and `speed.sh` against main and against the deny, taskset -c 7, 08:00-16:00 only).
- **OWED, not queued:** the corpus census (scratch script above; the manager's call whether to
  re-run it, `census.py PCREC_TRACE PATS OUT`, the trace build at
  `$PCREC_TMPDIR/scratch/p1build/trace/pcrec`).
- **Landing notes:** re-number abi if 95 is taken; re-pin the identity FILEPIN to the merge; the
  history index already carries this report's entry; `k_hit` stays UNMEASURED until the timing
  run's `lwfit` (then a [MEASURE-SET] row, not a constant edit).
- **Plan:** `[LANDWALK]` status updated (stays not-started in Candidates per plan_lint PL13);
  `[LANDWALK-CARD]` built; `[LANDWALK-EDGEPRICE]` status amended; `[LANDWALK-PRES]` and
  `[SEL-WORLD]` filed.
- **Deviations from the design:** utf8 rows decline on rarity (no utf8 byte prior); 5b's edge
  costs +1.9% (edge form `bitmap`); the PRESENCE pre-check loss cell.
